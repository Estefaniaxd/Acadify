"""Add OAuth token fields

Revision ID: add_oauth_tokens
Revises: add_google_resources
Create Date: 2025-11-23 10:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_oauth_tokens'
down_revision = 'add_google_resources'
branch_labels = None
depends_on = None


def upgrade():
    # Add token fields to OAuthProvider table
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('OAuthProvider')]
    
    if 'access_token' not in columns:
        op.add_column('OAuthProvider', sa.Column('access_token', sa.String(length=2048), nullable=True))
    
    if 'refresh_token' not in columns:
        op.add_column('OAuthProvider', sa.Column('refresh_token', sa.String(length=2048), nullable=True))
        
    if 'token_expiry' not in columns:
        op.add_column('OAuthProvider', sa.Column('token_expiry', postgresql.TIMESTAMP(timezone=True), nullable=True))
        
    if 'client_id' not in columns:
        op.add_column('OAuthProvider', sa.Column('client_id', sa.String(length=512), nullable=True))
        
    if 'client_secret' not in columns:
        op.add_column('OAuthProvider', sa.Column('client_secret', sa.String(length=512), nullable=True))


def downgrade():
    # Remove token fields
    op.drop_column('OAuthProvider', 'client_secret')
    op.drop_column('OAuthProvider', 'client_id')
    op.drop_column('OAuthProvider', 'token_expiry')
    op.drop_column('OAuthProvider', 'refresh_token')
    op.drop_column('OAuthProvider', 'access_token')
