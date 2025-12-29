from wallet.core.app import wallet_app
from wallet.db.db_init import engine
from sqlalchemy import text

@wallet_app.get("/track_system/popularcurrencies")
def top_currencies():
    with engine.begin() as connection:
        res = connection.execute(text(
            "SELECT currency FROM wallets " \
            "GROUP BY currency " \
            "ORDER BY COUNT(*) DESC " \
            "LIMIT 10;"
        )).mappings()

    return {"Самые популярные валюты": res}
