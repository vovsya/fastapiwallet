from sqlalchemy import create_engine
import os

engine = create_engine(
    os.getenv("ENGINE_CONNECTION"),
    echo=True,
)

    