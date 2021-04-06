import uuid
from postmarker.core import PostmarkClient
from email.mime.base import MIMEBase
from datetime import datetime
import datetime as dt
import icalendar
import pytz
from email.encoders import encode_base64
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="meeting invite")


class Details(BaseModel):
    attendees: str = None
    subject: str = None
    start_hour: str = None
    start_min: str = None
    day: str = None
    month: str = None
    year: str = None


@app.post('/test/')
async def send_meeting_invite(params: Details):
    subj = params.subject
    start_hour = int(params.start_hour)
    start_minute = int(params.start_min)
    start_day = int(params.day)
    start_month = int(params.month)
    start_year = int(params.year)
    attendee_email = params.attendees

    start_date = dt.datetime(start_year, start_month, start_day)
    # return start_date

    organiser_email = 'from mail id'
    time_now = datetime.now()
    description = 'join the event created for you on' + str(time_now)
    reminder_hours = 15

    tz = pytz.timezone("Asia/Calcutta")
    # Build the event itself
    cal = icalendar.Calendar()
    cal.add('PRODID', '-//Microsoft Corporation//Outlook MIMEDIR//EN')
    cal.add('VERSION', '2.0')

    event = icalendar.Event()
    # event.add(
    #     "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN={0}".format(attendee_email),
    #     "mailto:{0}".format(attendee_email)) only for having the option to accept the meeting with the pop up.
    event.add("ATTENDEE", attendee_email)  # comment if you want to have the above line.
    event.add("organizer;CN={0}".format(organiser_email), "mailto:{0}".format(organiser_email))
    event.add('summary', subj)
    event.add('category', "EVENT")
    event.add('description', description)
    event.add('location', 'India')
    event.add('dtstart', tz.localize(dt.datetime.combine(start_date, dt.time(start_hour, start_minute, 0))))
    event.add('dtend', tz.localize(dt.datetime.combine(start_date, dt.time(start_hour + 1, start_minute, 0))))
    event.add('dtstamp', tz.localize(dt.datetime.combine(start_date, dt.time(start_hour, start_minute, 0))))
    event.add('priority', 3)
    event['uid'] = uuid.uuid1()  # Generate some unique ID
    event.add('sequence', 0)
    event.add('status', "CONFIRMED")
    event.add('TRANSP', 'OPAQUE')

    # custom set up alarm
    alarm = icalendar.Alarm()
    alarm.add('description', "Reminder")
    # The only way to convince Outlook to do it correctly
    alarm.add("TRIGGER;RELATED=START", "-PT{0}M".format(reminder_hours))
    alarm.add("ACTION", "DISPLAY")
    event.add_component(alarm)
    cal.add_component(event)

    # generate the ics file
    filename = "invitedev.ics"
    part = MIMEBase('text', 'calendar', method='REQUEST', name=filename, component="VEVENT")
    part.set_payload(cal.to_ical())
    encode_base64(part)
    # part.add_header('Content-Disposition', 'attachment; filename={0}'.format(filename))
    part.add_header('Content-Description', filename)
    part.add_header('Content-class', "urn:content-classes:calendarmessage")
    part.add_header('Filename', filename)
    part.add_header('Path', filename)
    # print("Part : \n",part)

    # send the mail
    mailer = PostmarkClient(server_token='-----server token ---------')
    mailer.emails.send(
        From=organiser_email,
        To=attendee_email,
        Subject=subj,
        HtmlBody=description,
        Attachments=[part]
    )
    return event
    # return "mailed successfully"
