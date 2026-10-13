from ..routers.todos import get_db, get_current_user
from fastapi import status
from ..models import Todo
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [todo_to_dict(test_todo)]


def test_read_one_authenticated(test_todo):
    response = client.get(f"/todos/{test_todo.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == todo_to_dict(test_todo)


def test_read_one_authenticated_not_found():
    response = client.get("/todos/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


def test_create_todo(test_todo):
    request_data={
        'title': test_todo.title,
        'description': test_todo.description,
        'priority': test_todo.priority,
        'completed': test_todo.completed,
    }

    response = client.post('/todos/', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.completed == request_data.get('completed')


def test_update_todo(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'completed': False,
    }

    response = client.put('/todos/1', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 1).first()
    assert model.title == 'Change the title of the todo already saved!'


def test_update_todo_not_found(test_todo):
    request_data={
        'title':'Change the title of the todo already saved!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'completed': False,
    }

    response = client.put('/todos/999', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


def test_delete_todo(test_todo):
    response = client.delete('/todos/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todo).filter(Todo.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todos/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
