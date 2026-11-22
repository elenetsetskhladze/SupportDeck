from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserResponse, Token, RoleUpdate
from backend.security import hash_password, verify_password, create_access_token, get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    existing_user = await db.scalar(select(User).where(User.email == user.email))

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
        role="costumer"
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
async def login(
        form: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    user = await db.scalar(select(User).where(User.email == form.username))

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[UserResponse])
async def get_users(
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    result = await db.scalars(select(User).order_by(User.id))

    return result.all()

@router.patch("/users/{user_id}/role", response_model=UserResponse)
async def change_role(
        user_id: int,
        data: RoleUpdate,
        current_user: User = Depends(require_admin),
        db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = data.role

    await db.commit()
    await db.refresh(user)

    return user