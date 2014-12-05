"""
.. module:: UemEvent
    :synopsis: Stores Columbia's UEM data.
"""

from flask import url_for
from mongoengine import ValidationError
from app import adi, db
from app.models.fields import DateField, TimeField
import markdown

from datetime import datetime, timedelta
now = datetime.now

class UemEvent(db.Document):
    start = db.DateTimeField(required=True)
    end = db.DateTimeField(required=True)
    location = db.StringField()
    title = db.StringField()
    uem_id = db.IntField()

    def id_str(self):
        """The id of this object, as a string.

        :returns: The id
        :rtype: str
        """
        return str(self.id)

    def __unicode__(self):
        """This event, as a unicode string.

        :returns: The title of the event
        :rtype: str
        """
        return self.title

    def __repr__(self):
        """The representation of this event.

        :returns: The event's details.
        :rtype: str
        """
        return 'UemEvent(title=%r, location=%r, start=%r, end=%r)' \
                % (self.title, self.location, self.start, self.end)
