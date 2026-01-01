from sqlalchemy import create_engine, text
import os

engine = create_engine(
    os.getenv("ENGINE_CONNECTION"),
    echo=True,
)

    