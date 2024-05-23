import redis
from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime,timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import users as repository_users

import pickle

from src.conf.config import settings

class Auth:
    """
        A class used to handle authentication related operations.

        ...

        Attributes
        ----------
        pwd_context : CryptContext
            a CryptContext object used for password hashing and verification
        SECRET_KEY : str
            a secret key used for encoding and decoding JWT tokens
        ALGORITHM : str
            the algorithm used for encoding and decoding JWT tokens
        oauth2_scheme : OAuth2PasswordBearer
            an OAuth2PasswordBearer object used for handling OAuth2 authentication
        r : redis.Redis
            a Redis object used for caching

        Methods
        -------
        verify_password(plain_password, hashed_password)
            Verifies a password against a hashed password.
        get_password_hash(password)
            Hashes a password.
        create_access_token(data, expires_delta)
            Creates an access token.
        create_refresh_token(data, expires_delta)
            Creates a refresh token.
        decode_refresh_token(refresh_token)
            Decodes a refresh token.
        get_current_user(token, db)
            Retrieves the current user based on a token.
        create_email_token(data)
            Creates an email token.
        get_email_from_token(token)
            Retrieves an email from a token.
    """

    pwd_context = CryptContext(schemes=['bcrypt'], deprecated = "auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, password=settings.redis_password, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
                Verifies a password from a hashed password.

                :param plain_password: The plain text password.
                :type plain_password: str
                :param hashed_password: The hashed password.
                :type hashed_password: str
                :return: True if the password is correct, False otherwise.
                :rtype: bool
        """
        return self.pwd_context.verify(plain_password,hashed_password)

    def get_password_hash(self, password: str):
        """
                Hashes a password.

                :param password: The plain text password.
                :type password: str
                :return: The hashed password.
                :rtype: str
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
                Creates an access token.

                :param data: The data to include in the token.
                :type data: dict
                :param expires_delta: The number of seconds until the token expires.
                :type expires_delta: Optional[float]
                :return: The access token.
                :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow()+timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow()+timedelta(minutes=15)

        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return encoded_access_token

    async def create_refresh_token(self,data: dict, expires_delta: Optional[float] = None):
        """
                Creates a refresh token.

                :param data: The data to include in the token.
                :type data: dict
                :param expires_delta: The number of seconds until the token expires.
                :type expires_delta: Optional[float]
                :return: The refresh token.
                :rtype: str
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow()+timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow()+timedelta(minutes=15)

        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
                Decodes a refresh token.

                :param refresh_token: The refresh token to decode.
                :type refresh_token: str
                :return: The email contained in the token.
                :rtype: str
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])

            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')

        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str=Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
                Retrieves the current user based on a token.

                :param token: The token to decode.
                :type token: str
                :param db: The database session.
                :type db: Session
                :return: The current user.
                :rtype: User
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY,algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload['sub']
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception

        except JWTError as e:
            raise credentials_exception

        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)

        else:
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """
                Creates an email token.

                :param data: The data to include in the token.
                :type data: dict
                :return: The email token.
                :rtype: str
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
               Retrieves an email from a token.

               :param token: The token to decode.
               :type token: str
               :return: The email contained in the token.
               :rtype: str
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
