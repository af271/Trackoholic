import json
from collections import defaultdict
from datetime import timedelta, datetime

from config import path, target_file, start_date, form, free_weekdays, workday_target, holiday_target


def date_range(start, end):
    for n in range(int((end - start).days)):
        yield start + timedelta(n)


def string_to_timedelta(s):
    t = datetime.strptime(s, "%H:%M:%S")
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)


class Target:

    def __init__(self, filename=None, end_date=None):
        self.filename = filename or target_file
        self._data = {}
        try:
            with open(path + self.filename, 'r') as json_file:
                history = json.load(json_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            print(e)
            history = dict()
        end_date = end_date or datetime.today()
        for date in date_range(start_date, end_date):
            date_str = date.strftime(form)
            self._data[date_str] = history.get(date_str, self.get_goal(date))
        self._data[end_date.strftime(form)] = self.get_goal(end_date)

    @staticmethod
    def get_goal(date):
        return holiday_target if date.weekday() in free_weekdays else workday_target

    def items(self):
        return self._data.items()

    def write(self):
        with open(path + self.filename, 'w') as json_file:
            json.dump(self._data, json_file, indent=4, sort_keys=True)

    def sum_by_tag(self):
        target_time = defaultdict(lambda: [0, timedelta(0)])
        for goal in self._data.values():
            for tag, (target_hours, spent) in goal.items():
                target_time[tag][0] += target_hours
                if spent is not None:
                    target_time[tag][1] += string_to_timedelta(spent)
        return target_time

    def update(self, date_str, time_per_tag):
        entry = self._data[date_str]
        for tag, delta in time_per_tag.items():
            if tag in entry:
                entry[tag][1] = str(delta)


