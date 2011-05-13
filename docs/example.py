import sys
from pyeventcalendar import Event, EventCalendar
from datetime import date
import calendar

def main():
  cal = EventCalendar(calendar.MONDAY, rows=3)
  cal.addevent(Event(pk=1, start=date(2011, 3, 3), end=date(2011, 3, 6), title="Rome"))
  cal.addevent(Event(pk=2, start=date(2011, 3, 4), end=date(2011, 3, 14), title="Paris"))
  cal.addevent(Event(pk=3, start=date(2011, 3, 10), end=date(2011, 3, 16), title="Venice"))
  print cal.formatmonth(2011, 3)

if __name__ == "__main__":
  sys.exit(main())
