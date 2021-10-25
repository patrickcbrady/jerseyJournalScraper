from datetime import datetime as dt
import datetime


def get_current_week():
    return (dt.today() - datetime.timedelta(dt.today().isoweekday() % 7)).strftime("%Y-%m-%d")
