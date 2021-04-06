# meetinginviteapi

meeting invite can be sent by api post method call. 

requirements: uvicorn, fastapi, python 3.8, postmarker, email(standard library), icalendar, pytz

add "the postmarker server token and sender signature mail id "


Input: 
{
  "attendees": "string",
  "subject": "string",
  "start_hour": "string",
  "start_min": "string",
  "day": "string",
  "month": "string",
  "year": "string"
}