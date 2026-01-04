from fastapi.testclient import TestClient
from wallet_project.wallet.core.app import wallet_app
from sqlalchemy import text
from wallet_project.wallet.db.db_init import engine


client = TestClient(wallet_app)

erase_db = text("""
    TRUNCATE TABLE wallets, users RESTART IDENTITY CASCADE;
""")

def test_registration():

    res1 = client.post("/register", data={"username": "vital1", "password": "hutrnijekmosw"})

    assert res1.status_code == 200

    with engine.begin() as connection:
        connection.execute(wallets_erase)
        connection.execute(users_erase)

