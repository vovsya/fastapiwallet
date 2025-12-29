from sqlalchemy import create_engine, text
import os

engine = create_engine(
    os.getenv("ENGINE_CONNECTION"),
    echo=True,
)

with engine.begin() as connection:
    users_creation = connection.execute(text(
        """
        CREATE TABLE IF NOT EXISTS users
            (
            id          SERIAL PRIMARY KEY,
            username    TEXT NOT NULL UNIQUE,
            secretpass  TEXT NOT NULL
            )
        """
    ))

    wallets_creation = connection.execute(text(
        """
        CREATE TABLE IF NOT EXISTS wallets
            (
            user_id    INTEGER REFERENCES users(id),
            currency    TEXT NOT NULL,
            ticker      TEXT NOT NULL,
            value       DECIMAL NOT NULL,
            UNIQUE      (user_id, currency),
            UNIQUE      (user_id, ticker)
            )
        """
    ))

    