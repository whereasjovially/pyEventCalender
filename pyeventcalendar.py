import itertools
import calendar
from datetime import date, datetime, timedelta
from dateutil.rrule import rrule, DAILY


class EventCalendar(calendar.HTMLCalendar):
    """ Generate calendar markup intersposed with events. """
    def __init__(self, firstweekday=0, rows=5):
        super(calendar.HTMLCalendar, self).__init__(firstweekday)
        self.rows = rows
        self.eventmap = {}
        self.trackmap = {}


    def addevent(self, event):
        """ Add an event into the calendar.

        When the event is added we calculate the events place in the calendar,
        which involves iterating the entire events duration. For performance, it
        is thus best to only add events that you intend to display.

        The packing algorithm requires events be added in order of the events
        start date.
        """
        for d in rrule(DAILY, dtstart=event.start, until=event.end):
            d = d.date()
            if not self.eventmap.get(d):
                self.eventmap[d] = {}
            track = self.gettrack(event, d)
            self.eventmap[d][track] = event


    def gettrack(self, event, date):
        """ An algorithm to pack events.

        This algorithm matches that used by Google Calendar. It attempts to pack
        events into the smallest vertical space while keeping multi-day events
        in the same continuous row.
        """
        if self.trackmap.get(event) \
                and not self.firstweekday == date.weekday():
            track = self.trackmap[event]
        else:
            track = next(n for n in itertools.count() if n not in self.eventmap[date])
            self.trackmap[event] = track
        return track


    def formattrack(self, day, weekday, thedate, track):
        """ Render each day in the calendar. """
        label = '&nbsp;'
        colspan = 1
        eventmap = self.eventmap.get(thedate)
        if eventmap:
            event = eventmap.get(track)
            if event:
                start_of_week = not weekday

                # Don't start a cell if it's covered by a colspan
                event_cell_start = thedate == event.start or start_of_week
                if not event_cell_start:
                    return ''

                # Work out the colspan if we're starting a new event
                event_length = (event.end - thedate).days + 1
                days_left_in_week = 7 - weekday
                colspan = min(event_length, days_left_in_week)

                # Add some classes to provide visual cues for events spanning weeks
                classes = getattr(event, 'classes', [])
                if thedate != event.start and start_of_week: classes = classes + ['cl']
                if event_length > days_left_in_week: classes = classes + ['cr']

                label = '<div class="%s">%s</div>' % (' '.join(classes), event)
        return '<td colspan="%d">%s</td>' % (colspan, label)


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
        for week in self.monthdatescalendar(theyear, themonth):
            weekplus = []
            wd = 0
            for day in week:
                weekplus.append((day.day, wd, day))
                wd += 1
            a(self.formatweek(weekplus))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


class Event(object):
    """ Generic event class.

    You may use your own class or extend this one, but your object must be
    hashable.

    The required parameters are start and end, both of the type datetime.date.
    When rendering the calendar, the object's __str__ method is called. Extra
    classes can be added to the label by adding them to self.classes.
    """
    start   = None
    end     = None
    title   = None
    classes = []

    def __init__(self, start, end, title, group):
        self.start   = start
        self.end     = end
        self.title   = title
        self.classes = classes

    def __str__(self):
        return "%s" % self.title
