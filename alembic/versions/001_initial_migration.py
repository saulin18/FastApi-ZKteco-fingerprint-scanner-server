
from alembic import op
import sqlalchemy as sa


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    
    op.create_table('fingerprints',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fingerprint_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('image_base64', sa.Text(), nullable=False),
    sa.Column('template_data', sa.Text(), nullable=False),
    sa.Column('device_serial', sa.String(length=100), nullable=False),
    sa.Column('image_width', sa.Integer(), nullable=False),
    sa.Column('image_height', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fingerprints_id'), 'fingerprints', ['id'], unique=False)
    op.create_index(op.f('ix_fingerprints_fingerprint_id'), 'fingerprints', ['fingerprint_id'], unique=False)
    op.create_index(op.f('ix_fingerprints_device_serial'), 'fingerprints', ['device_serial'], unique=False)
    op.create_index(op.f('ix_fingerprints_timestamp'), 'fingerprints', ['timestamp'], unique=False)
    op.create_table('device_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('device_serial', sa.String(length=100), nullable=False),
    sa.Column('device_type', sa.String(length=50), nullable=True),
    sa.Column('last_connected', sa.DateTime(), nullable=True),
    sa.Column('image_width', sa.Integer(), nullable=False),
    sa.Column('image_height', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_device_info_id'), 'device_info', ['id'], unique=False)
    op.create_index(op.f('ix_device_info_device_serial'), 'device_info', ['device_serial'], unique=True)
    op.create_table('fingerprint_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fingerprint_id', sa.Integer(), nullable=False),
    sa.Column('template_data', sa.Text(), nullable=False),
    sa.Column('device_serial', sa.String(length=100), nullable=False),
    sa.Column('registered_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fingerprint_templates_id'), 'fingerprint_templates', ['id'], unique=False)
    op.create_index(op.f('ix_fingerprint_templates_fingerprint_id'), 'fingerprint_templates', ['fingerprint_id'], unique=True)
    op.create_index(op.f('ix_fingerprint_templates_device_serial'), 'fingerprint_templates', ['device_serial'], unique=False)
  


def downgrade() -> None:
   
    op.drop_index(op.f('ix_fingerprint_templates_device_serial'), table_name='fingerprint_templates')
    op.drop_index(op.f('ix_fingerprint_templates_fingerprint_id'), table_name='fingerprint_templates')
    op.drop_index(op.f('ix_fingerprint_templates_id'), table_name='fingerprint_templates')
    op.drop_table('fingerprint_templates')
    op.drop_index(op.f('ix_device_info_device_serial'), table_name='device_info')
    op.drop_index(op.f('ix_device_info_id'), table_name='device_info')
    op.drop_table('device_info')
    op.drop_index(op.f('ix_fingerprints_timestamp'), table_name='fingerprints')
    op.drop_index(op.f('ix_fingerprints_device_serial'), table_name='fingerprints')
    op.drop_index(op.f('ix_fingerprints_fingerprint_id'), table_name='fingerprints')
    op.drop_index(op.f('ix_fingerprints_id'), table_name='fingerprints')
    op.drop_table('fingerprints')
   
