from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import or_, extract, and_

from src.database.models import Contact,User
from src.schemas import ContactModel,ContactResponse

from datetime import datetime, timedelta
async def get_contacts(skip:int,limit:int, user:User, db:Session)->List[ContactResponse]:
    return db.query(Contact).filter(Contact.user_id==user.id).offset(skip).limit(limit).all()

async def get_contact(contact_id:int, user:User, db:Session)->ContactResponse:
    return db.query(Contact).filter(and_(Contact.id==contact_id, Contact.user_id==user.id)).first()

async def create_contact(body:ContactModel, user:User, db:Session)->Contact:
    contact = Contact(name=body.name,surname=body.surname,electronic_mail=body.electronic_mail,
                      phone_number=body.phone_number,birth_date=body.birth_date,
                      additional_info=body.additional_info, user=user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

async def update_contact(contact_id:int, body:Contact, user:User, db:Session):
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
    contact = db.query(Contact).filter(and_(Contact.id==contact_id, Contact.user_id==user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
        # db.refresh(contact)

    return contact

async def search_contacts(query: str, user:User, db: Session)->List[ContactResponse] | None:
    contacts = db.query(Contact).filter(
        and_(or_(
            Contact.name.ilike(f'%{query}%'),
            Contact.surname.ilike(f'%{query}%'),
            Contact.electronic_mail.ilike(f'%{query}%')
        ), Contact.user_id==user.id)
    ).all()
    return contacts

async def get_birthdays(db:Session)->List[ContactResponse]:
    now_time = datetime.now().date()
    future_time = now_time + timedelta(days=7)

    contacts = db.query(Contact).filter(
        extract('month', Contact.birth_date) == now_time.month,
        now_time.day <= extract('day', Contact.birth_date),
        extract('day', Contact.birth_date) <= future_time.day
    ).all()

    return contacts
