"""Replace the branch catalogue with the YMCA Ghana local branches."""
import sqlalchemy as sa
from alembic import op

from core.branches.ghana_catalog import GHANA_BRANCHES, RETIRED_BRANCH_IDS

revision = "q7r8s9t0u1"
down_revision = "p6q7r8s9t0"
branch_labels = None
depends_on = None


def _upsert_branches() -> None:
    conn = op.get_bind()
    official_names = []
    for branch_id, region_id, name, address, lat, lng in GHANA_BRANCHES:
        official_names.append(name.lower())
        existing = conn.execute(
            sa.text(
                """
                SELECT id
                FROM branches
                WHERE id = :id OR lower(name) = lower(:name)
                ORDER BY CASE WHEN id = :id THEN 0 ELSE 1 END
                LIMIT 1
                """
            ),
            {"id": branch_id, "name": name},
        ).fetchone()
        params = {
            "region_id": region_id,
            "name": name,
            "address": address,
            "lat": lat,
            "lng": lng,
        }
        if existing:
            params["id"] = existing[0]
            conn.execute(
                sa.text(
                    """
                    UPDATE branches
                    SET region_id = :region_id,
                        name = :name,
                        address = :address,
                        lat = :lat,
                        lng = :lng,
                        is_active = true,
                        updated_at = now()
                    WHERE id = :id
                    """
                ),
                params,
            )
        else:
            params["id"] = branch_id
            conn.execute(
                sa.text(
                    """
                    INSERT INTO branches (
                        id, region_id, name, address, lat, lng, is_active, collects_dues, created_at
                    )
                    VALUES (
                        :id, :region_id, :name, :address, :lat, :lng, true, true, now()
                    )
                    """
                ),
                params,
            )

    placeholders = ", ".join(f":name_{index}" for index in range(len(official_names)))
    params = {f"name_{index}": name for index, name in enumerate(official_names)}
    conn.execute(
        sa.text(
            f"""
            UPDATE branches
            SET is_active = false,
                lat = NULL,
                lng = NULL,
                updated_at = now()
            WHERE lower(name) NOT IN ({placeholders})
            """
        ),
        params,
    )


def upgrade() -> None:
    _upsert_branches()


def downgrade() -> None:
    conn = op.get_bind()
    new_ids = [branch_id for branch_id, *_rest in GHANA_BRANCHES]
    new_placeholders = ", ".join(f":new_{index}" for index in range(len(new_ids)))
    conn.execute(
        sa.text(
            f"""
            UPDATE branches
            SET is_active = false,
                updated_at = now()
            WHERE id IN ({new_placeholders})
            """
        ),
        {f"new_{index}": branch_id for index, branch_id in enumerate(new_ids)},
    )
    old_placeholders = ", ".join(f":old_{index}" for index in range(len(RETIRED_BRANCH_IDS)))
    conn.execute(
        sa.text(
            f"""
            UPDATE branches
            SET is_active = true,
                updated_at = now()
            WHERE id IN ({old_placeholders})
            """
        ),
        {f"old_{index}": branch_id for index, branch_id in enumerate(RETIRED_BRANCH_IDS)},
    )
