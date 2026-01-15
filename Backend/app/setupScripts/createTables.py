"""
Script to create all database tables for MoodSync application.
Run this script once to initialize your database schema.

Usage:
    python create_tables.py
"""
import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def create_tables():
    """Create all database tables defined in SQLAlchemy models."""
    
    print("🔧 Starting database table creation...")
    print(f"📍 Database URL: {settings.DATABASE_URL.split('@')[-1]}")  # Hide password
    
    try:
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=True,  # Show SQL statements
            future=True
        )
        
        # Import all models so they're registered with Base.metadata
        print("\n📦 Importing models...")
        from app.models.base import Base
        from app.models.users import User
        from app.models.auth_session import AuthSession
        # Import any other models you have here
        # from app.models.moods import Mood
        # from app.models.journal_entries import JournalEntry
        
        print("✅ Models imported successfully")
        
        # Create all tables
        print("\n🔨 Creating tables...")
        async with engine.begin() as conn:
            # Drop all tables first (optional - comment out if you want to keep existing data)
            # await conn.run_sync(Base.metadata.drop_all)
            # print("🗑️  Dropped existing tables")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created successfully")
        
        # Close the engine
        await engine.dispose()
        print("\n🎉 Database initialization complete!")
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def check_tables():
    """Verify that tables were created successfully."""
    
    print("\n🔍 Verifying tables...")
    
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine
        
        engine = create_async_engine(settings.DATABASE_URL)
        
        async with engine.connect() as conn:
            # Query to list all tables
            result = await conn.execute(text(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
                """
            ))
            
            tables = [row[0] for row in result]
            
            if tables:
                print("✅ Found the following tables:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("⚠️  No tables found in the database")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("  MoodSync Database Table Creation")
    print("=" * 60)
    
    # Run the table creation
    asyncio.run(create_tables())
    
    # Verify tables were created
    asyncio.run(check_tables())
    
    print("\n" + "=" * 60)
    print("  Done! You can now start your FastAPI server.")
    print("=" * 60)