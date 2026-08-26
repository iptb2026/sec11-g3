from app.database.session import SessionLocal


def get_db():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
