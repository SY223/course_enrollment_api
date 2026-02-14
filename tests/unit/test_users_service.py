from app.services.user_services import UserService



def test_create_user():
    created_user = UserService.create_user(
        name="Bailey Paul", 
        email="baileypaul@gmail.com", # type: ignore
        role="student" # type: ignore
    )
    assert created_user.name == "Bailey Paul"
    assert created_user.email == "baileypaul@gmail.com"


def test_create_user_missing_title():
    try:
        UserService.create_user(
            email="baileypaul@gmail.com", # type: ignore
            role="student" # type: ignore
        ) # type: ignore
    except ValueError as e:
        assert str(e) == "Name is required"

def test_get_user_by_id():
    created_user = UserService.create_user(
        name="Bailey Paul", 
        email="baileypaul@gmail.com",
        role="student"
    )
    fetched_user = UserService.get_user_by_id(created_user.id)

    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.name == "Bailey Paul"
    assert fetched_user.email == "baileypaul@gmail.com"
