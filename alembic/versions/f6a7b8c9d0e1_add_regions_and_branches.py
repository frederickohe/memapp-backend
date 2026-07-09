"""Add regions, branches, and branch scoping fields."""
from alembic import op
import sqlalchemy as sa

revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None

REGIONS = [
    ("reg_greater_accra", "Greater Accra"),
    ("reg_ashanti", "Ashanti"),
    ("reg_eastern", "Eastern"),
    ("reg_volta", "Volta"),
    ("reg_western", "Western"),
]

BRANCHES = [
    ("br_hq_accra", "reg_greater_accra", "National Headquarters", "Castle Road, Adabraka, Accra (P.O. Box GP738)", 5.5565, -0.2132),
    ("br_ttc_accra", "reg_greater_accra", "Accra YMCA Technical Training Centre", "Adabraka, Accra", 5.5578, -0.2145),
    ("br_regional_accra", "reg_greater_accra", "Greater Accra Regional YMCA", "Accra", 5.6037, -0.187),
    ("br_regional_ashanti", "reg_ashanti", "Ashanti Regional YMCA", "Kumasi", 6.692, -1.623),
    ("br_regional_eastern", "reg_eastern", "Eastern Regional YMCA", "Koforidua", 6.094, -0.259),
    ("br_regional_volta", "reg_volta", "Volta Regional YMCA", "Ho", 6.612, 0.47),
    ("br_regional_western", "reg_western", "Western Regional YMCA", "Takoradi", 4.896, -1.767),
    ("br_vti_takoradi", "reg_western", "Vocational Training Institute", "Takoradi", 4.901, -1.759),
]


def upgrade():
    op.create_table(
        "regions",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "branches",
        sa.Column("id", sa.String(length=20), nullable=False),
        sa.Column("region_id", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("address", sa.String(length=300), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lng", sa.Float(), nullable=True),
        sa.Column("president_id", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["president_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("users", sa.Column("branch_id", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("assigned_region_id", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("assigned_branch_id", sa.String(length=20), nullable=True))
    op.create_foreign_key("fk_users_branch_id", "users", "branches", ["branch_id"], ["id"])
    op.create_foreign_key("fk_users_assigned_region_id", "users", "regions", ["assigned_region_id"], ["id"])
    op.create_foreign_key("fk_users_assigned_branch_id", "users", "branches", ["assigned_branch_id"], ["id"])

    op.add_column("programs", sa.Column("branch_id", sa.String(length=20), nullable=True))
    op.create_foreign_key("fk_programs_branch_id", "programs", "branches", ["branch_id"], ["id"])

    op.add_column("volunteer_hours_submissions", sa.Column("branch_id", sa.String(length=20), nullable=True))
    op.create_foreign_key(
        "fk_vhs_branch_id",
        "volunteer_hours_submissions",
        "branches",
        ["branch_id"],
        ["id"],
    )

    regions_table = sa.table(
        "regions",
        sa.column("id", sa.String),
        sa.column("name", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(regions_table, [{"id": rid, "name": name, "is_active": True} for rid, name in REGIONS])

    branches_table = sa.table(
        "branches",
        sa.column("id", sa.String),
        sa.column("region_id", sa.String),
        sa.column("name", sa.String),
        sa.column("address", sa.String),
        sa.column("lat", sa.Float),
        sa.column("lng", sa.Float),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        branches_table,
        [
            {
                "id": bid,
                "region_id": region_id,
                "name": name,
                "address": address,
                "lat": lat,
                "lng": lng,
                "is_active": True,
            }
            for bid, region_id, name, address, lat, lng in BRANCHES
        ],
    )


def downgrade():
    op.drop_constraint("fk_vhs_branch_id", "volunteer_hours_submissions", type_="foreignkey")
    op.drop_column("volunteer_hours_submissions", "branch_id")
    op.drop_constraint("fk_programs_branch_id", "programs", type_="foreignkey")
    op.drop_column("programs", "branch_id")
    op.drop_constraint("fk_users_assigned_branch_id", "users", type_="foreignkey")
    op.drop_constraint("fk_users_assigned_region_id", "users", type_="foreignkey")
    op.drop_constraint("fk_users_branch_id", "users", type_="foreignkey")
    op.drop_column("users", "assigned_branch_id")
    op.drop_column("users", "assigned_region_id")
    op.drop_column("users", "branch_id")
    op.drop_table("branches")
    op.drop_table("regions")
