import json
import datetime as dt

import dateutil.parser
import requests

from app.models import Event, EventSeries
from app import create_app, db

create_app()

begin = dt.datetime.now()
end = dt.datetime.now() + dt.timedelta(30)

url = "http://util.columbiaesc.com/uem"
payload = {"group": "Application Development Initiative", "limit":100,
        "starts_after": str(begin), "ends_before": str(end)}
data = json.loads(requests.get(url, params=payload).text)

if data["status"] == 200:   # Good status
    data = data["data"]
else:
    raise Exception("Data scraping went wrong")


Events = Event.objects.filter(start_date__gte=begin.date(), end_date__lte=end.date())
uems = {}
for uem_event in data:
    start = dateutil.parser.parse(uem_event["start_time"])
    end = dateutil.parser.parse(uem_event["end_time"])
    try:
        e = Events.get(start_date=start.date(), start_time=start.time())

        uems[e] = uem_event["_id"]
        print start.date(), "\t", e, "\t", uem_event["title"]
    except Event.DoesNotExist:
        # Event.objects.text_search supported in monogengine 0.9
        print "UEM Event Not Found\t", uem_event["title"]
        same_day_events = Events.filter(start_date=start.date())
        if same_day_events:
            print Events.filter(start_date=start.date())

print

for event in Events:
    if event not in uems:
        print "No UEM_ID", event, event.start_date
