import time

class Clock:
    """
    Stores everything to do with time in the program. Currently, provides the date and time in a formatted way.
    """

    @staticmethod
    def get_date():
        try:
            current_time = time.localtime()
            year = current_time.tm_year
            month = current_time.tm_mon
            day = current_time.tm_mday
            return f"{year}/{month:02d}/{day:02d}"
        except Exception as e:
            return "Error, could not access the date. Exception" + e

    @staticmethod
    def get_time():
        try:
            current_time = time.localtime()
            hour = current_time.tm_hour
            minute = current_time.tm_min
            second = current_time.tm_sec

            return f"{hour:02d}:{minute:02d}:{second:02d}"
        except Exception as e:
            return "Error, could not access the time. Exception" + e

    @staticmethod
    def get_date_time():
        return Clock.get_date() + " " + Clock.get_time()