from typing import List, Union
from fastapi import APIRouter,HTTPException,Depends,status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Contact,User
from src.repository import contacts as repository_contacts
from src.schemas import ContactModel,ContactResponse
from src.services.auth import auth_service


router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/', response_model=List[ContactResponse])
async def get_contacts(skip: int=0 , limit:int =100, db: Session=Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip,limit,current_user,db)
    return contacts

@router.get('/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id :int, db: Session=Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)
                      ):
    contact = await repository_contacts.get_contact(contact_id,current_user,db)
    if contact is None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return contact

@router.post('/', response_model=ContactResponse)
async def create_contact(body:ContactModel, db: Session=Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    return await repository_contacts.create_contact(body,current_user,db)

@router.put('/{contact_id}', response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete('/{contact_id}', response_model=ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get('/search/',response_model=List[ContactResponse])
async def search_contacts(query:str, db: Session=Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)
                          ):
    contacts = await repository_contacts.search_contacts(query,current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no contacts with such regex')
    return contacts

@router.get('/birthdays/', response_model= List[ContactResponse])
async def get_birthdays(db: Session=Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_birthdays(current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no contacts with such birthday')
    return contacts