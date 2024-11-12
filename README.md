"# homeassistant_timetree_calendar" 


Doesnt work anymore !
As i am no longer using timetree ( switched to whole Apple Ecosystem ) there is no need for me to fix the issues !


Create your Token here: https://timetreeapp.com/developers/personal_access_tokens

After that, replace the 'YOURAPIKEY' in Calendar.py with your Token


Everything else should be Fine.


For Changing the TimeZone, start Date, 
search for self._entities = timetree_object.get_upcoming_events(self._calendar.id, 'Europe/Berlin', 7).data 
in Calendar.py and change it accordingly


Create a Folder with the name: timetree in Config/custom_components
paste the files into it.

Dont forget to add:

calendar:
  - platform: timetree

To your Configuration.yaml


Credits: 
TimeTree SDK (https://pypi.org/project/timetree-sdk/) has been created by Shoya Shiraki under the MIT License
