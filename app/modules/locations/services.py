
def create_location(user_id: int, latitude: float, longitude: float) -> dict:
    try:
        from app.core.database import SessionLocal
        from app.modules.auth.models import Loaction
        session = SessionLocal()
        try:
            db_location = Loaction(
                user_id=user_id,
                latitude=latitude,
                longitude=longitude
            )
            session.add(db_location)
            session.commit()
            session.refresh(db_location)
            print(f"✓ Location for user {user_id} saved to database")
            return {
                "id": db_location.id,
                "user_id": db_location.user_id,
                "latitude": db_location.latitude,
                "longitude": db_location.longitude,
                "timestamp": db_location.timestamp
            }
        except Exception as db_err:
            session.rollback()
            print(f"⚠ Database error: {db_err}")
            raise
        finally:
            session.close()
    except Exception as e:
        print(f"⚠ Could not save location: {e}")
        raise