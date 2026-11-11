from itertools import count

from fastapi import APIRouter, HTTPException

from app.schemas.user import UserCreate, UserResponse, UserUpdate


class User:
    _id_generator = count(1)
    _users: dict[int, "User"] = {}

    def __init__(self, name: str, email: str, age: int, is_active: bool = True):
        self.id = next(User._id_generator)
        self.name = name
        self.email = email
        self.age = age
        self.is_active = is_active

        User._users[self.id] = self

    @classmethod
    def get_by_id(cls, user_id: int) -> "User | None":
        return cls._users.get(user_id)


router = APIRouter()


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
)
def create_user(data: UserCreate) -> UserResponse:
    email = str(data.email).lower()

    if any(user.email == email for user in User._users.values()):
        raise HTTPException(
            status_code=409,
            detail="Email already exists",
        )
    user = User(
        name=data.name,
        email=email,
        age=data.age,
        is_active=data.is_active,
    )

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        is_active=user.is_active,
    )


@router.get("/users", response_model=list[UserResponse])
def get_users() -> list[UserResponse]:
    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            age=user.age,
            is_active=user.is_active,
        )
        for user in User._users.values()
    ]


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int) -> UserResponse:
    user = User.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        is_active=user.is_active,
    )


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int) -> None:
    user = User.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    del User._users[user_id]


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate) -> UserResponse:
    user = User.get_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    updates = data.model_dump(exclude_unset=True)

    if "email" in updates:
        email = str(updates["email"].lower())
        updates["email"] = email

        if any(
            other_user.email == email and other_user.id != user_id
            for other_user in User._users.values()
        ):
            raise HTTPException(
                status_code=409,
                detail="Email already exists",
            )

    for key, value in updates.items():
        setattr(user, key, value)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        age=user.age,
        is_active=user.is_active,
    )
