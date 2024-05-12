import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session
from sqlalchemy import or_, extract, and_

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactResponse

from datetime import datetime, timedelta

from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    delete_contact,
    search_contacts,
    get_birthdays,
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(id=1, name="test", surname="test surname", electronic_mail="test@mail.com", phone_number="1234567890", birth_date=datetime.now().date(), additional_info="test info")
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.name, body.name)
        self.assertEqual(result.surname, body.surname)
        self.assertEqual(result.electronic_mail, body.electronic_mail)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birth_date, body.birth_date)
        self.assertEqual(result.additional_info, body.additional_info)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_found(self):
        body = Contact(name="test", surname="test surname", electronic_mail="test@mail.com", phone_number="1234567890", birth_date=datetime.now(), additional_info="test info")
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = Contact(name="test", surname="test surname", electronic_mail="test@mail.com", phone_number="1234567890", birth_date=datetime.now(), additional_info="test info")
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_delete_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_search_contacts_found(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await search_contacts(query="test", user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_search_contacts_not_found(self):
        self.session.query().filter().all.return_value = []
        result = await search_contacts(query="test", user=self.user, db=self.session)
        self.assertEqual(result, [])

    async def test_get_birthdays(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await get_birthdays(db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_birthdays_empty(self):
        self.session.query().filter().all.return_value = []
        result = await get_birthdays(db=self.session)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
