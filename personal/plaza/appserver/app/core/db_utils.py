from sqlalchemy.exc import IntegrityError


def commit_or_409(db):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
