from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Venue(db.Model):
    venue_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)

class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer)
    description = db.Column(db.Text)
    invited_count = db.Column(db.Integer, default=0)
    accepted_count = db.Column(db.Integer, default=0)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.venue_id'))
    venue = db.relationship('Venue', backref=db.backref('events', lazy=True))
