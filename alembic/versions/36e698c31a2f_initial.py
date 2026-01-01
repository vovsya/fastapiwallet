"""initial

Revision ID: 36e698c31a2f
Revises: 
Create Date: 2026-01-01 17:35:59.689851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '36e698c31a2f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(text(
        """
        CREATE TABLE users
            (
            id          SERIAL PRIMARY KEY,
            username    TEXT NOT NULL UNIQUE,
            secretpass  TEXT NOT NULL
            )
        """
    ))

    op.execute(text(
        """
        CREATE TABLE wallets
            (
            user_id     INTEGER NOT NULL REFERENCES users(id),
            currency    TEXT NOT NULL,
            ticker      TEXT NOT NULL,
            value       DECIMAL NOT NULL,
            UNIQUE      (user_id, currency),
            UNIQUE      (user_id, ticker)
            )
        """
    ))


def downgrade() -> None:
    op.execute(text(
        """   
        DROP TABLE IF EXISTS wallets;
        """
    ))

    op.execute(text(
        """   
        DROP TABLE IF EXISTS users;
        """
    ))
