
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from src.core.config import settings
from src.models.users.oauth_provider import OAuthProvider
from src.models.users.usuario import Usuario

# Force DB URL from .env content we read
settings.DATABASE_URL = "postgresql://postgres:243019@localhost:5432/acadify_db"

def check_oauth_tokens():
    engine = create_engine(str(settings.database_url))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("\n=== Checking OAuth Providers (Raw SQL) ===")
        with engine.connect() as connection:
            result = connection.execute(text('SELECT * FROM "OAuthProvider"'))
            providers = result.fetchall()
            
            if not providers:
                print("❌ No OAuth providers found in database!")
                return

            for p in providers:
                # p is a Row object, access by index or name depending on driver
                # Assuming standard access
                print(f"\nUser ID: {p.usuario_id}")
                print(f"Provider: {p.provider}")
                print(f"Provider Email: {p.provider_email}")
                print(f"Access Token Present: {'✅ YES' if p.access_token else '❌ NO'}")
                print(f"Refresh Token Present: {'✅ YES' if p.refresh_token else '❌ NO'}")
                if p.access_token:
                    print(f"Access Token Preview: {p.access_token[:20]}...")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_oauth_tokens()
