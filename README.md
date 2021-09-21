"# homeassistant_timetree_calendar" 


Create your Token here: https://timetreeapp.com/developers/personal_access_tokens

After that, replace the 'YOURAPIKEY' in Calendar.py with your Token


Everything else should be Fine.


For Changing the TimeZone, start Date, search for self._entities = timetree_object.get_upcoming_events(self._calendar.id, 'Europe/Berlin', 7).data in Calendar.py and change it accordingly
