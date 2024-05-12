from typing import List, Union
from fastapi import APIRouter,HTTPException,Depends,status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Contact,User
from src.repository import contacts as repository_contacts
from src.schemas import ContactModel,ContactResponse
from src.services.auth import auth_service

from fastapi_limiter.depends import RateLimiter


router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.get('/', response_model=List[ContactResponse],
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))]
            )
async def get_contacts(skip: int=0 , limit:int =100, db: Session=Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
        Retrieves a list of contacts for the current user with specified pagination parameters.

        :param skip: The number of contacts to skip.
        :type skip: int
        :param limit: The maximum number of contacts to return.
        :type limit: int
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: A list of contacts.
        :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.get_contacts(skip,limit,current_user,db)
    return contacts

@router.get('/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id :int, db: Session=Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)
                      ):
    """
       Retrieves a specific contact for the current user.

       :param contact_id: The ID of the contact to retrieve.
       :type contact_id: int
       :param db: The database session.
       :type db: Session
       :param current_user: The current user.
       :type current_user: User
       :return: The requested contact.
       :rtype: ContactResponse
    """
    contact = await repository_contacts.get_contact(contact_id,current_user,db)
    if contact is None:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return contact

@router.post('/', response_model=ContactResponse)
async def create_contact(body:ContactModel, db: Session=Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
        Creates a new contact for the current user.

        :param body: The contact data to create.
        :type body: ContactModel
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: The created contact.
        :rtype: ContactResponse
    """
    return await repository_contacts.create_contact(body,current_user,db)

@router.put('/{contact_id}', response_model=ContactResponse)
async def update_contact(body: ContactModel, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
        Updates a specific contact for the current user.

        :param body: The contact data to update.
        :type body: ContactModel
        :param contact_id: The ID of the contact to update.
        :type contact_id: int
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: The updated contact.
        :rtype: ContactResponse
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete('/{contact_id}', response_model=ContactResponse)
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
        Deletes a specific contact for the current user.

        :param contact_id: The ID of the contact to delete.
        :type contact_id: int
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: The deleted contact.
        :rtype: ContactResponse
    """
    contact = await repository_contacts.delete_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.get('/search/',response_model=List[ContactResponse])
async def search_contacts(query:str, db: Session=Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)
                          ):
    """
        Searches for contacts for the current user based on a query string.

        :param query: The query string to search for.
        :type query: str
        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: A list of contacts that match the query string.
        :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.search_contacts(query,current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no contacts with such regex')
    return contacts

@router.get('/birthdays/', response_model= List[ContactResponse])
async def get_birthdays(db: Session=Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
        Retrieves a list of contacts for the current user who have birthdays within the next week.

        :param db: The database session.
        :type db: Session
        :param current_user: The current user.
        :type current_user: User
        :return: A list of contacts with upcoming birthdays.
        :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.get_birthdays(current_user, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no contacts with such birthday')
    return contacts