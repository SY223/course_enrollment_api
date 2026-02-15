from app.services.user_services import UserService
from app.schemas.user_schema import UserCreate
from app.core.db import users_db
import pytest

#datetime.datetime.now(datetime.UTC)

# ✅ Automatically clear DB before each test
@pytest.fixture(autouse=True)
def clear_users_db():
    users_db.clear()

def test_create_user():
    user = UserService.create_user(
        UserCreate(
            name="Bailey Paul",
            email="baileypaul@gmail.com",
            role="student"
        )
    )
    assert user.name == "bailey paul"
    assert user.email == "baileypaul@gmail.com"
    assert user.role == "student"
    assert user.id is not None


def test_get_all_users_success():
    user1 = UserService.create_user(
        UserCreate(
            name="John Doe",
            email="john@gmail.com",
            role="student"
        )
    )
    user2 = UserService.create_user(
        UserCreate(
            name="Jane Smith",
            email="jane@gmail.com",
            role="admin"
        )
    )
    users = UserService.get_all_users()
    assert len(users) == 2
    assert user1 in users
    assert user2 in users
    assert user1.email == "john@gmail.com"
    assert user2.email == "jane@gmail.com"
