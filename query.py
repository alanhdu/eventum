from collections import Counter
import json
import datetime as dt

import dateutil.parser
import requests

from app.models import Event, EventSeries
from app import create_app, db

create_app()

begin = dt.datetime.now() - dt.timedelta(30)
end = dt.datetime.now() + dt.timedelta(30)

url = "http://util.columbiaesc.com/uem"
payload = {"group": "Application Development Initiative", "limit":100,
        "starts_after": str(begin), "ends_before": str(end)}
data = json.loads(requests.get(url, params=payload).text)

if data["status"] == 200:   # Good status
    data = data["data"]
else:
    raise Exception("Data scraping went wrong")


Events = Event.objects.filter(start_date__gt=begin.date(), end_date__lt=end.date())

uem_weights = Counter()
adi_weights = Counter()
for uem_event in data:
    # Remove useless information
    if uem_event["title"].startswith("Application Development Initiative"):
        # remove first 3 words
        uem_event["title"] = " ".join(uem_event["title"].split()[3:]).strip()
    if uem_event["title"].startswith("ADI"):
        uem_event["title"] = uem_event["title"][3:].strip()
    if uem_event["title"].startswith("-"):
        uem_event["title"] = uem_event["title"][1:].strip()

    uem_weights.update(set(uem_event["title"].upper().split()))

for event in Events:
    adi_weights.update(set(event.title.upper().split()))

def similarity(uem, adi):
    uv, av = set(uem.upper().split()), set(adi.upper().split())
    s = 0
    for word in uv:
        if word in av:
            s += 10.0 / (uem_weights[word] + 1) + 10.0 / (adi_weights[word] + 1)
    return s

for uem_event in data:
    start = dateutil.parser.parse(uem_event["start_time"])

    # Fuzzy matching
    lte = start.date() + dt.timedelta(1)
    gte = start.date() - dt.timedelta(1)
    possibilities = Events.filter(start_date__lte=lte, start_date__gte=gte)
    if possibilities:
        key = lambda p: similarity(uem=uem_event["title"], adi=p.title)
        adi_event = max(possibilities, key=key)
        # if there's any similarity
        if similarity(uem=uem_event["title"], adi=adi_event.title) > 0:
            print "FOUND!\t", adi_event, uem_event["title"]
        else:
            print "NOT FOUND!\t", uem_event["title"], "\t", adi_event.title
            print [p.title for p in possibilities]
    else:
        print "NOT FOUND!\t", start.date(), uem_event["title"]
