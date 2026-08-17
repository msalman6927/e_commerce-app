"""cart routes have created

Revision ID: adce58a05a0c
Revises: 474eff7441eb
Create Date: 2026-08-17 06:10:26.643777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'adce58a05a0c'
down_revision: Union[str, Sequence[str], None] = '474eff7441eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)
    op.create_table('cart_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cart_items_id'), 'cart_items', ['id'], unique=False)

    # pehle foreign key hatao
    op.drop_constraint('products_category_id_fkey', 'products', type_='foreignkey')

    # phir Category drop karo
    op.drop_index(op.f('ix_Category_id'), table_name='Category')
    op.drop_table('Category')

    # phir products update karo
    op.add_column('products', sa.Column('stock', sa.Integer(), nullable=False))
    op.add_column('products', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.alter_column('products', 'price', existing_type=sa.INTEGER(), type_=sa.Float(), existing_nullable=False)
    op.alter_column('products', 'category_id', existing_type=sa.INTEGER(), nullable=False)
    op.create_foreign_key(None, 'products', 'categories', ['category_id'], ['id'], ondelete='CASCADE')
    op.drop_column('products', 'stock_quantity')
    op.drop_column('users', 'roles')


def downgrade() -> None:
    op.add_column('users', sa.Column('roles', sa.VARCHAR(length=20), server_default=sa.text("'user'::character varying"), autoincrement=False, nullable=False))
    op.add_column('products', sa.Column('stock_quantity', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'products', type_='foreignkey')
    op.create_foreign_key(op.f('products_category_id_fkey'), 'products', 'Category', ['category_id'], ['id'], ondelete='SET NULL')
    op.alter_column('products', 'category_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('products', 'price', existing_type=sa.Float(), type_=sa.INTEGER(), existing_nullable=False)
    op.drop_column('products', 'created_at')
    op.drop_column('products', 'stock')
    op.create_table('Category',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('Category_pkey')),
    sa.UniqueConstraint('name', name=op.f('Category_name_key'), postgresql_include=[], postgresql_nulls_not_distinct=False)
    )
    op.create_index(op.f('ix_Category_id'), 'Category', ['id'], unique=False)
    op.drop_index(op.f('ix_cart_items_id'), table_name='cart_items')
    op.drop_table('cart_items')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_table('categories')