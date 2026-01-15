"""
Database seeding script to create initial test user.
Run this script to populate your database with seed data.

Usage:
    python seed_db.py
"""
import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.models.base import Base
from app.models.users import User
from app.models.auth_session import AuthSession
from app.core.security import hash_password


async def init():
    """Initialize database and create seed data."""
    
    print("=" * 60)
    print("🌱 Database Seeding Script")
    print("=" * 60)
    
    # Create engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,  # Show SQL queries
        future=True
    )
    
    # Create session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    try:
        # Create all tables
        print("\n🔨 Creating database schemas...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database schemas created!")
        
        # Create session for seeding
        async with AsyncSessionLocal() as session:
            # Get seed data from environment or use defaults
            email = os.getenv("SEED_EMAIL", "chimarokeumunna98@gmail.com")
            password = os.getenv("SEED_PASSWORD", "12345678")
            
            print(f"\n👤 Checking for existing user: {email}")
            
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"⚠️  User already exists: {existing_user.email}")
                print(f"   Name: {existing_user.first_name} {existing_user.last_name}")
                print(f"   ID: {existing_user.user_id}")
            else:
                # Create new user with hashed password
                print(f"\n🔐 Hashing password...")
                hashed_password = hash_password(password)
                
                print(f"✨ Creating new user...")
                user = User(
                    first_name="David",
                    last_name="Umunna",
                    email=email,
                    password_hash=hashed_password,
                    is_active=True,
                    is_verified=True  # Auto-verify seed user
                )
                
                session.add(user)
                await session.commit()
                await session.refresh(user)
                
                print(f"✅ User created successfully!")
                print(f"   Name: {user.first_name} {user.last_name}")
                print(f"   Email: {user.email}")
                print(f"   ID: {user.user_id}")
            
            # Fetch and display all users
            print("\n📋 All users in database:")
            print("-" * 60)
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if users:
                for idx, u in enumerate(users, 1):
                    print(f"{idx}. {u.first_name} {u.last_name} ({u.email})")
                    print(f"   ID: {u.user_id}")
                    print(f"   Active: {u.is_active} | Verified: {u.is_verified}")
                    print(f"   Created: {u.createdAt}")
                    print("-" * 60)
            else:
                print("No users found in database")
        
        print("\n🎉 Seeding complete!")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Close connections
        await engine.dispose()
        print("\n👋 Database connections closed")


if __name__ == "__main__":
    print("\nStarting database seeding...")
    asyncio.run(init())
    print("\nDone! You can now start your FastAPI server.\n")