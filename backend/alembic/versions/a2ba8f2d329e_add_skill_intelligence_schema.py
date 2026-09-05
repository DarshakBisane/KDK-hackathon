"""add_skill_intelligence_schema

Revision ID: a2ba8f2d329e
Revises: daa18c4d6206
Create Date: 2026-09-05 11:00:36.180463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2ba8f2d329e'
down_revision: Union[str, Sequence[str], None] = 'daa18c4d6206'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns to skills table
    op.add_column('skills', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('skills', sa.Column('first_detected_at', sa.DateTime(), nullable=True))
    op.add_column('skills', sa.Column('last_updated_at', sa.DateTime(), nullable=True))
    op.add_column('skills', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('skills', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # 2. Add new columns to career_skills table
    op.add_column('career_skills', sa.Column('proficiency_required', sa.String(length=50), server_default='Intermediate', nullable=True))
    op.add_column('career_skills', sa.Column('confidence', sa.Float(), server_default='1.0', nullable=True))
    op.add_column('career_skills', sa.Column('last_updated_at', sa.DateTime(), nullable=True))

    # 3. Create skill_aliases table
    op.create_table(
        'skill_aliases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('alias', sa.String(length=100), nullable=False),
        sa.Column('source', sa.String(length=50), server_default='manual', nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_aliases_id'), 'skill_aliases', ['id'], unique=False)
    op.create_index(op.f('ix_skill_aliases_skill_id'), 'skill_aliases', ['skill_id'], unique=False)
    op.create_index(op.f('ix_skill_aliases_alias'), 'skill_aliases', ['alias'], unique=True)

    # 4. Create skill_evidence table
    op.create_table(
        'skill_evidence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('career_id', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('evidence_text', sa.Text(), nullable=True),
        sa.Column('mention_count', sa.Integer(), server_default='1', nullable=True),
        sa.Column('confidence', sa.Float(), server_default='1.0', nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['career_id'], ['careers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_evidence_id'), 'skill_evidence', ['id'], unique=False)
    op.create_index(op.f('ix_skill_evidence_skill_id'), 'skill_evidence', ['skill_id'], unique=False)
    op.create_index(op.f('ix_skill_evidence_career_id'), 'skill_evidence', ['career_id'], unique=False)
    op.create_index(op.f('ix_skill_evidence_source'), 'skill_evidence', ['source'], unique=False)
    op.create_index(op.f('ix_skill_evidence_detected_at'), 'skill_evidence', ['detected_at'], unique=False)

    # 5. Create skill_trends table
    op.create_table(
        'skill_trends',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('career_id', sa.Integer(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False),
        sa.Column('mention_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('growth_percentage', sa.Float(), server_default='0.0', nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['career_id'], ['careers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('skill_id', 'career_id', 'period', name='uq_skill_trends_skill_career_period')
    )
    op.create_index(op.f('ix_skill_trends_id'), 'skill_trends', ['id'], unique=False)
    op.create_index(op.f('ix_skill_trends_skill_id'), 'skill_trends', ['skill_id'], unique=False)
    op.create_index(op.f('ix_skill_trends_career_id'), 'skill_trends', ['career_id'], unique=False)
    op.create_index(op.f('ix_skill_trends_period'), 'skill_trends', ['period'], unique=False)


def downgrade() -> None:
    # 1. Drop skill_trends
    op.drop_index(op.f('ix_skill_trends_period'), table_name='skill_trends')
    op.drop_index(op.f('ix_skill_trends_career_id'), table_name='skill_trends')
    op.drop_index(op.f('ix_skill_trends_skill_id'), table_name='skill_trends')
    op.drop_index(op.f('ix_skill_trends_id'), table_name='skill_trends')
    op.drop_table('skill_trends')

    # 2. Drop skill_evidence
    op.drop_index(op.f('ix_skill_evidence_detected_at'), table_name='skill_evidence')
    op.drop_index(op.f('ix_skill_evidence_source'), table_name='skill_evidence')
    op.drop_index(op.f('ix_skill_evidence_career_id'), table_name='skill_evidence')
    op.drop_index(op.f('ix_skill_evidence_skill_id'), table_name='skill_evidence')
    op.drop_index(op.f('ix_skill_evidence_id'), table_name='skill_evidence')
    op.drop_table('skill_evidence')

    # 3. Drop skill_aliases
    op.drop_index(op.f('ix_skill_aliases_alias'), table_name='skill_aliases')
    op.drop_index(op.f('ix_skill_aliases_skill_id'), table_name='skill_aliases')
    op.drop_index(op.f('ix_skill_aliases_id'), table_name='skill_aliases')
    op.drop_table('skill_aliases')

    # 4. Drop columns from career_skills
    op.drop_column('career_skills', 'last_updated_at')
    op.drop_column('career_skills', 'confidence')
    op.drop_column('career_skills', 'proficiency_required')

    # 5. Drop columns from skills
    op.drop_column('skills', 'updated_at')
    op.drop_column('skills', 'created_at')
    op.drop_column('skills', 'last_updated_at')
    op.drop_column('skills', 'first_detected_at')
    op.drop_column('skills', 'description')
