from wallet.schemas.classes import UserData, Token, ProfileDeletion
from wallet.db.db_init import engine
from fastapi import Depends, HTTPException, status, Body
from wallet.core.app import wallet_app
from sqlalchemy import text
from wallet.security.auth import pwd_context, verify_password, create_access_token, get_current_user, OAuth2PasswordRequestForm


@wallet_app.post("/register", tags=["Профиль"])
def create_user(userinfo: UserData):
    hashed_pass = pwd_context.hash(userinfo.password.get_secret_value())
    with engine.begin() as connection:
        exists = connection.execute(text(
            """
            SELECT 1 FROM users WHERE username = :username
            """
        ), {"username": userinfo.username}).scalar_one_or_none()
    
    if exists != None:
        raise HTTPException(status_code=409, detail="Пользователь с таким именем уже существует")
        
    with engine.begin() as connection:
        user_creation = connection.execute((text(
            """
            INSERT INTO users (username, secretpass) VALUES(:username, :secretpass)
            """
        )), {"username": userinfo.username, "secretpass": hashed_pass})
    
    return {"Вы зарегистрировались": "Теперь Вы можете авторизоваться"}

@wallet_app.post("/login", response_model=Token, tags=["Профиль"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with engine.begin() as connection:
        db_pass = connection.execute(text(
            "SELECT secretpass FROM users WHERE username = :name"
        ), {"name": form_data.username}).scalar_one_or_none()
       
    if not db_pass or not verify_password(form_data.password, db_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@wallet_app.get("/profile", tags=["Профиль"])
def get_profile_info(current_user: str = Depends(get_current_user)):
    with engine.begin() as connection:
        data = connection.execute(text(
            """
            SELECT id, username FROM users WHERE username = :current_user
            """
        ), {"current_user": current_user}).mappings().all()
    
    return {"данные пользователя": data}

@wallet_app.delete("/profile/delete", tags=["Профиль"])
def delete_profile(
    current_user: str = Depends(get_current_user),
    user_info: ProfileDeletion = Body(..., description="Введите пароль 2 раза и введите 'ПОДТВЕРДИТЬ'")
    ):

    if user_info.confirm != "ПОДТВЕРДИТЬ":
        raise HTTPException(status_code=401, detail="Требуется подтверждение")
    
    if user_info.password1 != user_info.password2:
        raise HTTPException(status_code=401, detail="Пароли не совпадают")
    
    with engine.begin() as connection:
        db_password = connection.execute(text(
            """
            SELECT secretpass FROM users
            WHERE username = :username
            """
        ), {"username": current_user}).scalar_one_or_none()

        if not db_password or not verify_password(user_info.password1.get_secret_value(), db_password):
            raise HTTPException(status_code=401, detail="Неверный пароль")
    
        connection.execute(text(
            """
            DELETE FROM wallets
            WHERE user_id = (SELECT id FROM users WHERE username = :username);
            """
        ), {"username": current_user})

        connection.execute(text(
            """
            DELETE FROM users
            WHERE username = :username;
            """
        ), {"username": current_user})

    return {"Аккаунт": "Удален"}


