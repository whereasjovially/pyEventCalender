from pyeventcalendar import Event, EventCalendar
from datetime import date

def __main__():
  cal = EventCalendar()
  cal.addevent(Event(start=date(2011, 3, 4), end=date(2011, 3, 6), title="Rome"))
  cal.addevent(Event(start=date(2011, 3, 4), end=date(2011, 3, 6), title="Paris"))
  print cal.formatmonth(2011, 3)
