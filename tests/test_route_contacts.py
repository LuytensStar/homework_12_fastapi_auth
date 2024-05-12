from unittest.mock import MagicMock
from fastapi import UploadFile
from io import BytesIO

def test_get_contacts(client, user):
    response = client.get(
        "/contacts/",
        headers={"Authorization": f"Bearer {user['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

def test_get_contact(client, user):
    response = client.get(
        f"/contacts/{user['contact_id']}",
        headers={"Authorization": f"Bearer {user['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == user["contact_id"]

def test_create_contact(client, user):
    response = client.post(
        "/contacts/",
        json={"name": "New Contact", "phone": "+1234567890"},
        headers={"Authorization": f"Bearer {user['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "New Contact"
    assert data["phone"] == "+1234567890"

def test_update_contact(client, user):
    response = client.put(
        f"/contacts/{user['contact_id']}",
        json={"name": "Updated Contact", "phone": "+0987654321"},
        headers={"Authorization": f"Bearer {user['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Updated Contact"
    assert data["phone"] == "+0987654321"

def test_delete_contact(client, user):
    response = client.delete(
        f"/contacts/{user['contact_id']}",
        headers={"Authorization": f"Bearer {user['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == user["contact_id"]

def test_search_contacts(client, user):
    response = client.get(
        "/contacts/search/",
        params={"query": "Contact"},
        headers={"Authorization": f"Bearer {user['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

def test_get_birthdays(client, user):
    response = client.get(
        "/contacts/birthdays/",
        headers={"Authorization": f"Bearer {user['access_token']}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
