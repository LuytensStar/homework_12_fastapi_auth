import unittest
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel

from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1, email="test@mail.com")

    async def test_get_user_by_email(self):
        self.session.query().filter().first.return_value = self.user
        result = await get_user_by_email(email="test@mail.com", db=self.session)
        self.assertEqual(result, self.user)

    @patch("src.repository.users.Gravatar")
    async def test_create_user(self, mock_gravatar):
        mock_gravatar.return_value.get_image.return_value = "avatar_url"
        body = body = UserModel(id=1, username="testuser", email="test@mail.com", password="password")
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.email, body.email)
        self.assertTrue(hasattr(result, "id"))
        self.assertEqual(result.avatar, "avatar_url")

    async def test_update_token(self):
        await update_token(user=self.user, token="new_token", db=self.session)
        self.assertEqual(self.user.refresh_token, "new_token")

    async def test_confirmed_email(self):
        self.session.query().filter().first.return_value = self.user
        await confirmed_email(email="test@mail.com", db=self.session)
        self.assertTrue(self.user.confirmed)

    async def test_update_avatar(self):
        self.session.query().filter().first.return_value = self.user
        result = await update_avatar(email="test@mail.com", url="new_avatar_url", db=self.session)
        self.assertEqual(result.avatar, "new_avatar_url")

if __name__ == '__main__':
    unittest.main()
