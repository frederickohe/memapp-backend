"""Store the WordPress post id on imported news."""
from alembic import op
import sqlalchemy as sa


revision = "p6q7r8s9t0"
down_revision = "o5p6q7r8s9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("news", sa.Column("wordpress_post_id", sa.String(length=32), nullable=True))
    op.add_column("news", sa.Column("wordpress_permalink", sa.String(length=500), nullable=True))
    op.create_index("ix_news_wordpress_post_id", "news", ["wordpress_post_id"], unique=True)


def downgrade():
    op.drop_index("ix_news_wordpress_post_id", table_name="news")
    op.drop_column("news", "wordpress_permalink")
    op.drop_column("news", "wordpress_post_id")
