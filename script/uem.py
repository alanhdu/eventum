from __future__ import division

import json
import datetime as dt
import time

import dateutil.parser
import requests

from app.models import Event, EventSeries, UemEvent
from app import create_app

create_app()

def get_uem_events():
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
    for uem_event in data:
        uem_id = int(uem_event["_id"])
        if not UemEvent.objects.filter(uem_id=uem_id):  # event not already registered
            u = UemEvent()
            u.location = uem_event["location_full"]
            u.uem_id = uem_id
            u.title = uem_event["title"].strip()
            if u.title.startswith("Application Development Initiative"):
                u.title = u.title[len("Application Development Initiative"):].strip()
            if u.title.startswith("ADI"):
                u.title = u.title[len("ADI")].strip()
            if u.title.startswith("-"):
                u.title = u.title[1:].strip()

            u.start = dt.datetime.strptime(uem_event["date_str"] + uem_event["start_time_str"],
                    "%m/%d/%Y%I:%M %p")
            u.end = dt.datetime.strptime(uem_event["date_str"] + uem_event["end_time_str"],
                    "%m/%d/%Y%I:%M %p")
            u.save()

def string_similarity(a, b):
    s = set(a.lower().split()) & set(b.lower().split())
    s = s - {"the", "adi", "application", "development", "initiative", "-"}
    return len(s)
def similarity(uem, adi):
    s = string_similarity(uem.title, adi.title)
    d = uem.start - dt.datetime.combine(adi.start_date, adi.start_time)
    d = abs(d.total_seconds() / (60 * 60))
    return s - d

def match_uem_adi():
    begin = dt.datetime.now()
    end = dt.datetime.now() + dt.timedelta(30)
    Events = Event.objects.filter(start_date__gte=begin.date(), end_date__lte=end.date(), uem=None)
    UemEvents = UemEvent.objects.filter(start__gte=begin, end__lte=end)

    for event in Events:
        start = dt.datetime.combine(event.start_date, event.start_time)
        end = dt.datetime.combine(event.end_date, event.end_time)

        # Fuzzy matching
        UemPossible = UemEvents.filter(start__gte=start - dt.timedelta(1),
                                       end__lte=end + dt.timedelta(1))
        if UemPossible.count() == 1:
            event.uem = UemPossible[0]
        elif UemPossible.count() > 1:
            m = (0, None)
            for possibility in UemPossible:
                if m[0] < similarity(uem=possibility, adi=event):
                    m = (similarity(uem=possibility, adi=event), possibility)
            if m[1]:
                event.uem = m[1]

        event.save()

if __name__ == "__main__":
    get_uem_events()
    match_uem_adi()
