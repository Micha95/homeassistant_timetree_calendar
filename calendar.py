"""Support for calendars based on timetree."""
from datetime import datetime, time, timedelta
import logging
import sys
import os
sys.path.append(os.getcwd())
from .timetree_sdk import TimeTreeApi


import voluptuous as vol

from homeassistant.components.calendar import PLATFORM_SCHEMA, CalendarEventDevice
from homeassistant.const import (
	CONF_ID, 
	CONF_NAME,
	CONF_TOKEN,
	STATE_UNKNOWN,
	STATE_UNAVAILABLE,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.template import DATE_STR_FORMAT
from homeassistant.util import Throttle, dt

_LOGGER = logging.getLogger(__name__)


MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=15)
timetree_object = False

def setup_platform(hass, config, add_entities, discovery_info=None):
	"""Set up the entities platform."""
	global timetree_object
	timetree_object = TimeTreeApi('YOURAPIKEY')
	calendars = timetree_object.get_calendars()
	calendar_devices = []
	for calendar in calendars.data:
		calendar_devices.append(
		EntitiesCalendarDevice(
			hass,
			calendar
		)
		)
	add_entities(calendar_devices)
	

class EntitiesCalendarDevice(CalendarEventDevice):
	"""A device for getting calendar events from entities."""

	def __init__(
		self,
		hass,
		calendar
	):
		"""Create the Todoist Calendar Event Device."""
		self.data = EntitiesCalendarData(
			hass,
			calendar
		)
		self._cal_data = {}
		self._name = calendar.attributes.name

	@property
	def event(self):
		"""Return the next upcoming event."""
		return self.data.event

	@property
	def name(self):
		"""Return the name of the entity."""
		return self._name

	def update(self):
		"""Update all Calendars."""
		self.data.update()


	async def async_get_events(self, hass, start_date, end_date):
		"""Get all events in a specific time frame."""
		return await self.data.async_get_events(hass, start_date, end_date)

	@property
	def device_state_attributes(self):
		"""Return the device state attributes."""
		if self.data.event is None:
			# No tasks, we don't REALLY need to show anything.
			return None

		return {}


class EntitiesCalendarData:
	"""
	Class used by the Entities Calendar Device service object to hold all entity events.

	This is analogous to the GoogleCalendarData found in the Google Calendar
	component.

	The 'update' method polls for any updates to the entities. This is throttled to every
	MIN_TIME_BETWEEN_UPDATES minutes.
	"""

	def __init__(
		self,
		hass,
		calendar
	):
		"""Initialize an Entities Calendar Project."""
		self.event = None

		self._hass = hass
		self._name = calendar.attributes.name
		self._calendar = calendar
		global timetree_object
		self._entities = timetree_object.get_upcoming_events(self._calendar.id, 'Europe/Berlin', 7).data

		self.all_events = []


	async def async_get_events(self, hass, start_date, end_date):
		"""Get all tasks in a specific time frame."""
		events = []
		for entity in self._entities:
			start = entity.attributes.start_at
			start = dt.parse_datetime(start)
			end = entity.attributes.end_at
			end = dt.parse_datetime(end)

			if start is None:
				continue
			if start_date < start < end_date:
				allDay = entity.attributes.all_day
				event = {
					"uid": entity.id,
					"summary": entity.attributes.title,
					"start": { "date": start.strftime('%Y-%m-%d') } if allDay else { "dateTime": start.isoformat() },
					"end": { "date": end.strftime('%Y-%m-%d') } if allDay else { "dateTime": end.isoformat() },
					"allDay": allDay,
				}
				events.append(event)
		return events

	@Throttle(MIN_TIME_BETWEEN_UPDATES)
	def update(self):
		"""Get the latest data."""
		self._entities = timetree_object.get_upcoming_events(self._calendar.id, 'Europe/Berlin', 7).data
		events = []
		for entity in self._entities:
			start = entity.attributes.start_at
			start = dt.parse_datetime(start)
			end = entity.attributes.end_at
			end = dt.parse_datetime(end)

			if start is None:
				continue
			allDay = entity.attributes.all_day
			event = {
				"uid": entity.id,
				"summary": entity.attributes.title,
				"start": { "date": start.strftime('%Y-%m-%d') } if allDay else { "dateTime": start.isoformat() },
				"end": { "date": end.strftime('%Y-%m-%d') } if allDay else { "dateTime": end.isoformat() },
				"allDay": allDay,
			}
			events.append(event)

		events.sort(key=lambda x: x["start"]["date"] if x["allDay"] else x["start"]["dateTime"] )

		next_event = None
		if events:
		  next_event = events[0]
		self.event = next_event