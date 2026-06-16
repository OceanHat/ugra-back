"""Script to create an admin user."""

from sqlalchemy.orm import Session
from src.database import SessionLocal, engine, Base
from src.users.models import User
from src.users.enums import UserRole
from src.auth.utils import get_password_hash


def create_admin(
    email: str,
    password: str,
    full_name: str
) -> None:
    """Create an admin user.
    
    Args:
        email: Admin email
        password: Admin password
        full_name: Admin full name
    """
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            
            # Update to admin role if not already
            if existing_user.role != UserRole.ADMIN:
                existing_user.role = UserRole.ADMIN
                existing_user.hashed_password = get_password_hash(password)
                db.commit()
                print(f"User {email} updated to admin role.")
            return
        
        # Create new admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"ID: {admin_user.id}")
        print(f"Email: {admin_user.email}")
        print(f"Role: {admin_user.role}")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--email", required=True, help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--name", required=True, help="Admin full name")
    
    args = parser.parse_args()
    
    create_admin(
        email=args.email,
        password=args.password,
        full_name=args.name
    )
