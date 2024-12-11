from app import app, db
from models import Venue, Event
from sqlalchemy import text

def create_indexes():
    with db.engine.connect() as connection:
        try:
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_event_date ON Event(date);"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS idx_event_venue_id ON Event(venue_id);"))
            print("Indexes created successfully.")
        except Exception as e:
            print(f"Error creating indexes: {e}")

if __name__ == "__main__":
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully.")

        # Create indexes
        create_indexes()
