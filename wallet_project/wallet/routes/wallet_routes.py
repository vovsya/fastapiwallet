from wallet.core.app import wallet_app
from sqlalchemy import text
from wallet.db.db_init import engine
from fastapi import Depends, Query, HTTPException, Body
from wallet.security.auth import get_current_user
from wallet.schemas.classes import ValueChange
from decimal import Decimal


@wallet_app.get("/homepage", tags=["Кошелёк"], description="Посмотреть кошелёк")
def info(current_user: str = Depends(get_current_user)):
    with engine.begin() as connection:
        stmt = text(
            "SELECT id, username FROM users WHERE username = :username"
        )
        person = connection.execute(stmt, {"username": current_user}).mappings().all()

        money = connection.execute(text(
            """
            SELECT currency, ticker, value FROM wallets wl
            INNER JOIN users us ON us.id = wl.user_id
            WHERE us.username = :username
            """
        ), {"username": current_user}).mappings().all()

    return {"Ваш аккаунт": person, "Ваш кошелёк": money}

@wallet_app.post("/mywallet/addcurrency", description="Добавить валюту", tags=["Кошелёк"])
def add_currency(currency_name: str = Body(desciption="Укажите название валюты"), ticker: str = Body(description="Укажите тикер валюты"), current_user: str = Depends(get_current_user)):
    with engine.begin() as connection:
        exists = connection.execute(text(
            """
            SELECT 1 FROM users
            INNER JOIN wallets ON users.id = wallets.user_id
            WHERE username = :current_user AND
            (currency = :currency_name OR ticker = :ticker)
            LIMIT 1
            """
        ), {"current_user": current_user, "currency_name": currency_name, "ticker": ticker}).scalar_one_or_none()
    
    if exists != None:
        raise HTTPException(status_code=409, detail="Валюта уже добавлена или тикер занят.")

    with engine.begin() as connection:
        creation = connection.execute(text(
            """
            INSERT INTO wallets(user_id, currency, ticker, value)
            VALUES(
                (SELECT id FROM users WHERE username = :current_user),
                :currency_name,
                :ticker,
                0
            )
            ON CONFLICT (user_id, currency) DO NOTHING;  
            """
        ), {"current_user": current_user, "currency_name": currency_name, "ticker": ticker})
    return {"добавление": "совершено"}

@wallet_app.patch("/mywallet/changevalue", description="Изменить баланс валюты", tags=["Кошелёк"])
def change_value(ticker: str = Body(description="Укажите тикер"), change: Decimal = Body(desciption="Укажите сумму"), current_user: str = Depends(get_current_user), choice: ValueChange = Query(..., description="Выберите действие")):
    if choice == ValueChange.MINUS:
        change *= -1

    with engine.begin() as connection:
        new_value = connection.execute(text(
            """
            UPDATE wallets
            SET value = value + :add
            WHERE ticker = :ticker AND user_id = (SELECT DISTINCT id FROM users WHERE username = :current_user)
            AND value + :add >= 0
            RETURNING value;
            """
        ), {"add": change, "ticker": ticker, "current_user": current_user}).scalar_one_or_none()
    
    if new_value is None:
        raise HTTPException(status_code=401, detail="Недостаточно монет")
    
    if change >= 0:
        return {"добавление": "успешно"}
    else:
        return {"Валюта": "убрана"}

@wallet_app.delete("/mywallet/deletecurrency", description="Удалить валюту из кошелька", tags=["Кошелёк"])
def delete_currency(ticker: str = Body(desciption="Укажите тикер"), current_user: str = Depends(get_current_user)):
    with engine.begin() as connection:
        exists = connection.execute(text(
            """
            DELETE FROM wallets WHERE ticker = :ticker AND user_id = (SELECT DISTINCT id FROM users WHERE username = :current_user)
            RETURNING *
            """
        ), {"current_user": current_user, "ticker": ticker}).one_or_none()
    
    if exists is None:
        raise HTTPException(status_code=404, detail="Монеты нет в кошельке")
    
    return {"Валюта": "удалена"}

@wallet_app.put("/mywallet/defaultvalues", description="Обнулить баланс валют", tags=["Кошелёк"])
def default_values(current_user: str = Depends(get_current_user)):
    with engine.begin() as connection:
        connection.execute(text(
            """
            UPDATE wallets
            SET value = 0
            WHERE user_id = (SELECT id FROM users WHERE username = :username)
            """
        ), {"username": current_user})
    
    return {"Баланс": "Обнулен"}

@wallet_app.delete("/mywallet/deletewallet", description="Очистить кошелек", tags=["Кошелёк"])
def delete_wallet(current_user: str = Depends(get_current_user)):
    with engine.begin() as connection:
        connection.execute(text(
            """
            DELETE FROM wallets
            WHERE user_id = (SELECT id FROM users WHERE username = :username)
            """
        ), {"username": current_user})
    
    return {"Кошелек": "очищен"}