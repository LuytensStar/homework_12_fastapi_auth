from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract, and_

from src.database.models import Contact,User
from src.schemas import ContactModel,ContactResponse

from datetime import datetime, timedelta
async def get_contacts(skip:int,limit:int, user:User, db:Session)->List[ContactResponse]:
    """
        Retrieves a list of contacts for a specific user with specified pagination parameters.

        :param skip: The number of contacts to skip.
        :type skip: int
        :param limit: The maximum number of contacts to return.
        :type limit: int
        :param user: The user to retrieve contacts for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: A list of contacts.
        :rtype: List[ContactResponse]
    """
    return db.query(Contact).filter(Contact.user_id==user.id).offset(skip).limit(limit).all()

async def get_contact(contact_id:int, user:User, db:Session)->ContactResponse:
    """
       Retrieves a specific contact for a specific user.

       :param contact_id: The ID of the contact to retrieve.
       :type contact_id: int
       :param user: The user to retrieve the contact for.
       :type user: User
       :param db: The database session.
       :type db: Session
       :return: The requested contact.
       :rtype: ContactResponse
    """
    return db.query(Contact).filter(and_(Contact.id==contact_id, Contact.user_id==user.id)).first()

async def create_contact(body:ContactModel, user:User, db:Session)->Contact:
    """
        Creates a new contact for a specific user.

        :param body: The contact data to create.
        :type body: ContactModel
        :param user: The user to create the contact for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The created contact.
        :rtype: Contact
    """
    contact = Contact(name=body.name,surname=body.surname,electronic_mail=body.electronic_mail,
                      phone_number=body.phone_number,birth_date=body.birth_date,
                      additional_info=body.additional_info, user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id:int, body:Contact, user:User, db:Session):
    """
       Updates a specific contact for a specific user.

       :param contact_id: The ID of the contact to update.
       :type contact_id: int
       :param body: The contact data to update.
       :type body: Contact
       :param user: The user to update the contact for.
       :type user: User
       :param db: The database session.
       :type db: Session
       :return: The updated contact.
       :rtype: Contact
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id==user.id)).first()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.electronic_mail = body.electronic_mail
        contact.phone_number = body.phone_number
        contact.birth_date = body.birth_date
        contact.additional_info = body.additional_info
        db.commit()

    return contact

async def delete_contact(contact_id:int, user:User, db:Session):
    """
       Deletes a specific contact for a specific user.

       :param contact_id: The ID of the contact to delete.
       :type contact_id: int
       :param user: The user to delete the contact for.
       :type user: User
       :param db: The database session.
       :type db: Session
       :return: The deleted contact.
       :rtype: Contact
    """
    contact = db.query(Contact).filter(and_(Contact.id==contact_id, Contact.user_id==user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
        # db.refresh(contact)

    return contact

async def search_contacts(query: str, user:User, db: Session)->List[ContactResponse] | None:
    """
        Searches for contacts for a specific user based on a query string.

        :param query: The query string to search for.
        :type query: str
        :param user: The user to search contacts for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: A list of contacts that match the query string.
        :rtype: List[ContactResponse] | None
    """
    contacts = db.query(Contact).filter(
        and_(or_(
            Contact.name.ilike(f'%{query}%'),
            Contact.surname.ilike(f'%{query}%'),
            Contact.electronic_mail.ilike(f'%{query}%')
        ), Contact.user_id==user.id)
    ).all()
    return contacts

async def get_birthdays(db:Session)->List[ContactResponse]:
    """
       Retrieves a list of contacts who have birthdays within the next week.

       :param db: The database session.
       :type db: Session
       :return: A list of contacts with upcoming birthdays.
       :rtype: List[ContactResponse]
    """
    now_time = datetime.now().date()
    future_time = now_time + timedelta(days=7)

    contacts = db.query(Contact).filter(
        extract('month', Contact.birth_date) == now_time.month,
        now_time.day <= extract('day', Contact.birth_date),
        extract('day', Contact.birth_date) <= future_time.day
    ).all()

    return contacts
