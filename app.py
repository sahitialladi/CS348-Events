from flask import Flask, render_template, request, redirect, url_for
from config import Config
from models import db, Event, Venue
from sqlalchemy import text
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def index():
    events = Event.query.all()
    venues = Venue.query.all()
    return render_template('events.html', events=events, venues=venues)

@app.route('/event/create', methods=['POST'])
def create_event():
    description = request.form['description']
    date_str = request.form['date']
    time_str = request.form['time']
    duration = request.form.get('duration', type=int)
    invited_count = request.form.get('invited_count', type=int)

    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    try:
        time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError:
        time = datetime.strptime(time_str, "%H:%M:%S").time()

    new_venue_name = request.form.get('new_venue')
    venue_id = request.form.get('venue_id')

    if new_venue_name:
        new_venue = Venue(name=new_venue_name, location="Unknown")
        db.session.add(new_venue)
        db.session.flush()
        venue_id = new_venue.venue_id

    new_event = Event(
        description=description,
        date=date,
        time=time,
        duration=duration,
        invited_count=invited_count,
        venue_id=venue_id
    )
    db.session.add(new_event)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/event/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    venues = Venue.query.all()

    if request.method == 'POST':
        date_str = request.form['date']
        time_str = request.form['time']
        duration = request.form.get('duration', type=int)
        invited_count = request.form.get('invited_count', type=int)  # New field

        event.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        try:
            event.time = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            event.time = datetime.strptime(time_str, "%H:%M:%S").time()

        event.description = request.form['description']
        event.duration = duration
        event.invited_count = invited_count  # Update invited count

        new_venue_name = request.form.get('new_venue')
        venue_id = request.form.get('venue_id')

        if new_venue_name:
            new_venue = Venue(name=new_venue_name, location="Unknown")
            db.session.add(new_venue)
            db.session.flush()
            event.venue_id = new_venue.venue_id
        elif venue_id:
            event.venue_id = venue_id

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_event.html', event=event, venues=venues)


@app.route('/event/rsvp/<int:event_id>', methods=['POST'])
def rsvp_event(event_id):
    event = Event.query.get_or_404(event_id)
    rsvp_status = request.form.get('rsvp_status')

    if rsvp_status == 'yes':
        event.accepted_count += 1
    elif rsvp_status == 'no' and event.accepted_count > 0:
        event.accepted_count -= 1

    db.session.commit()
    return redirect(url_for('index'))

@app.route('/event/delete/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/report', methods=['GET', 'POST'])
def report():
    venues = Venue.query.all()
    report_data = None

    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        venue_id = request.form.get('venue_id') or None

        query = text("""
        SELECT date,
               AVG(duration) AS avg_duration,
               AVG(invited_count) AS avg_invited,
               AVG(accepted_count) AS avg_accepted,
               (COALESCE(AVG(accepted_count), 0) * 1.0 / NULLIF(COALESCE(AVG(invited_count), 0), 0)) AS avg_attendance_rate
        FROM Event
        WHERE (:start_date IS NULL OR date >= :start_date)
          AND (:end_date IS NULL OR date <= :end_date)
          AND (:venue_id IS NULL OR venue_id = :venue_id)
        GROUP BY date;
        """)

        report_data = db.session.execute(query, {
            "start_date": start_date,
            "end_date": end_date,
            "venue_id": venue_id
        }).fetchall()

    return render_template('report.html', venues=venues, report_data=report_data)

if __name__ == '__main__':
    app.run(debug=True)
