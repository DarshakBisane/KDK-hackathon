from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import User
from app.schemas.schemas import UserRegister, UserLogin, TokenResponse
from app.utils.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if email already registered
    existing_user = db.query(User).filter(User.email == user_data.email.lower().strip()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please log in."
        )

    # Validate password confirmation if provided
    if user_data.confirm_password and user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and confirm password do not match."
        )

    # Hash password and create user
    hashed_pwd = get_password_hash(user_data.password)
    new_user = User(
        name=user_data.name.strip(),
        email=user_data.email.lower().strip(),
        password_hash=hashed_pwd,
        education=user_data.education or "B.Tech Computer Science",
        student_status="Student"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "education": new_user.education,
            "student_status": new_user.student_status,
            "target_career_id": new_user.target_career_id,
        }
    )


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    email_clean = login_data.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password. Please check your credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "education": user.education,
            "student_status": user.student_status,
            "target_career_id": user.target_career_id,
            "target_career_name": user.target_career.name if user.target_career else None
        }
    )
