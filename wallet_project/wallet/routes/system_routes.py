from wallet_project.wallet.core.app import wallet_app
from wallet_project.wallet.db.db_init import engine
from sqlalchemy import text
from fastapi.responses import RedirectResponse

@wallet_app.get("/", tags=["Корень"])
def root():
    return RedirectResponse(url="/docs")

@wallet_app.get("/track_system/popularcurrencies", tags=["Данные системы"])
def top_currencies():
    with engine.begin() as connection:
        res = connection.execute(text(
            "SELECT COUNT(*) AS count, currency FROM wallets " \
            "GROUP BY currency " \
            "ORDER BY count DESC " \
            "LIMIT 10;"
        )).mappings().all()

    return res

