import itertools
import calendar
from datetime import date, datetime, timedelta
from dateutil.rrule import rrule, DAILY

class EventCalendar(calendar.HTMLCalendar):
  """ Generate calendar markup intersposed with events. """
  def __init__(self, firstweekday=0, rows=5):
    super(calendar.HTMLCalendar, self).__init__(firstweekday)
    self.rows = rows
    self.events   = {}
    self.eventmap = {}
    self.tracks   = {}
    self.trackmap = {}

  def addevent(self, event):
    """ Add an event into the system.

    When the event is added we calculate the events place in the calendar,
    which involves iterating the entire events duration. For performance, it
    is thus best to only add events that you intend to display.

    The packing algorithm requires events be added in order of the events
    start date.
    """
    self.events[event.pk] = event
    for d in rrule(DAILY, dtstart=event.start, until=event.end):
      d = d.date()
      if not self.eventmap.get(d):
        self.eventmap[d] = {}
      track = self.gettrack(event.pk, d)
      self.eventmap[d][track] = event.pk

  def gettrack(self, event_id, date):
    """ An algorithm to pack events

    This algorithm matches that used by Google Calendar. It attempts to pack
    events into the smallest vertical space while keeping multi-day events
    in the same continuous row.
    """
    if self.trackmap.get(event_id) \
        and not self.firstweekday == date.weekday():
      track = self.trackmap[event_id]
    else:
      track = next(n for n in itertools.count() if n not in self.eventmap[date])
      self.trackmap[event_id] = track
    return track

  def formattrack(self, day, weekday, thedate, track):
    """ Render each day in the calendar.

    This relies on the event object having a render() method.
    """
    if day == 0:
      return '<td class="noday">&nbsp;</td>'
    else:
      label = '&nbsp;'
      colspan = 1
      if (self.eventmap.get(thedate)):
        if self.eventmap.get(thedate).get(track):
          event_id = self.eventmap.get(thedate).get(track)
          event = self.events[event_id]

          event_length = (event.end - thedate).days + 1
          days_left_in_week = 7 - weekday
          colspan = min(event_length, days_left_in_week)

          cell_start = thedate == event.start or not weekday
          if not cell_start:
            return ''

          label = '<div class="filled">%s</div>' % event
      return '<td colspan="%d" class="%s">%s</td>' % (colspan, self.cssclasses[weekday], label)


  def formatweek(self, theweek):
    """ Return a complete week as a set of table rows.

    This introduces the concepts of "tracks". The first track is the date,
    and all the following tracks contain the event information. The number
    of tracks is set through the constructor.
    """
    numbers = ''.join(self.formatday(d, wd) for (d, wd, date) in theweek)
    dates = '<tr class="dates">%s</tr>' % numbers

    tracks = [dates]
    for t in xrange(self.rows):
      markup = ''.join(self.formattrack(d, wd, date, t) for (d, wd, date) in theweek)
      row = '<tr>%s</tr>' % markup
      tracks.append(row)

    return "\n".join(tracks)

  def formatmonth(self, theyear, themonth, withyear=True):
    """ Return a formatted month as a table. """
    v = []
    a = v.append
    a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
    a('\n')
    a(self.formatmonthname(theyear, themonth, withyear=withyear))
    a('\n')
    a(self.formatweekheader())
    a('\n')
    for week in self.monthdays2calendar(theyear, themonth):
      weekplus = []
      for day in week:
        if day[0] == 0:
          weekplus.append((day[0], day[1], ''))
        else:
          weekplus.append((day[0], day[1], date(theyear, themonth, day[0])))
      a(self.formatweek(weekplus))
      a('\n')
    a('</table>')
    a('\n')
    return ''.join(v)


class LongCalendar(calendar.Calendar):
  """ Generate a calendar as a scrollable timeline. """
  def __init__(self, firstweekday=0, rows=5):
    super(LongCalendar, self).__init__(firstweekday)
    self.rows   = rows
    self.events = {}
    self.tracks = {}

  def addevent(self, event):
    if not self.events.get(event.start):
      self.events[start] = []
    self.events[start].append(event)

  def formatmonth(self, year, month):
    v = []
    a = v.append
    a('<table>')
    a('<tr>')
    for day in self.itermonthdates(year, month):
      a('<td>%s</td>' % day)
    a('</tr>')
    a('</table>')

    return ''.join(v)


class Event(object):
  """ Generic event class. You may use your own or extend this one. """
  pk    = None # Unique identifier for this event
  start = None
  end   = None
  title = None

  def __init__(self, pk, start, end, title):
    self.pk    = pk
    self.start = start
    self.end   = end
    self.title = title

  def __str__(self):
    return "%s" % self.title
