from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel

async def get_user_by_email(email:str, db:Session)->User:
    """
       Retrieves a user by their email.

       :param email: The email of the user to retrieve.
       :type email: str
       :param db: The database session.
       :type db: Session
       :return: The requested user.
       :rtype: User
    """
    return db.query(User).filter(User.email == email).first()

async def create_user(body: UserModel, db:Session)->User:
    """
        Creates a new user.

        :param body: The user data to create.
        :type body: UserModel
        :param db: The database session.
        :type db: Session
        :return: The created user.
        :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()

    except Exception as e:
        print(e)

    new_user = User(**body.dict(), avatar = avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

async def update_token(user:User, token: str | None, db:Session)->None:
    """
        Updates the refresh token of a specific user.

        :param user: The user to update the token for.
        :type user: User
        :param token: The new refresh token.
        :type token: str | None
        :param db: The database session.
        :type db: Session
    """
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    """
        Confirms the email of a specific user.

        :param email: The email of the user to confirm.
        :type email: str
        :param db: The database session.
        :type db: Session
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

async def update_avatar(email, url: str, db: Session) -> User:
    """
        Updates the avatar of a specific user.

        :param email: The email of the user to update the avatar for.
        :type email: str
        :param url: The new avatar URL.
        :type url: str
        :param db: The database session.
        :type db: Session
        :return: The updated user.
        :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


