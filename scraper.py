import pandas as pd
from bs4 import BeautifulSoup
import requests
import datetime
import locale
import itertools
from dateutil.parser import parse

locale.setlocale(locale.LC_TIME, 'nl_NL')
CURRENT_WEEK = datetime.date.today().isocalendar()[1]
CLASS_NAME = "AEITO19AO-A"
pd.options.mode.use_inf_as_na = True


def get_day() -> str:
    now = datetime.datetime.now()
    day = now.strftime("%A").capitalize()
    date = now.strftime("%d-%m")
    return f"{day} {date}"

def get_id() -> str:
    for i in range(1, 100):
        url = f"https://rooster.horizoncollege.nl/rstr/ECO/AMR/400-ECO/Roosters/c/{CURRENT_WEEK}/c000{i:02d}.htm"
        page = requests.get(url)
        parsed_html = BeautifulSoup(page.text)
        class_info = parsed_html.select("body > center > font:nth-child(2)")
        if not class_info:
            continue
        class_name = class_info[0].text.strip()
        class_id = f"c000{i:02d}"
        if class_name == CLASS_NAME:
            write_id(class_id)
            return class_id

def local_id():
    with open("id.txt", "r") as file:
        return file.read()

def write_id(id):
    with open("id.txt", "w") as file:
        file.write(id)

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def get_schedule():
    URL = f"https://rooster.horizoncollege.nl/rstr/ECO/AMR/400-ECO/Roosters/c/37/{local_id()}.htm"
    tables = pd.read_html(URL, header=0)
    df = tables[0]
    df = df.where(df.notnull(), 0)
    df.rename(columns={"Unnamed: 0": "Uur"})
    df = df.rename(columns={"Unnamed: 0": "Uur"})
    for a, b in itertools.combinations(df, 2):
        adata = a.split()
        bdata = b.split()
        if adata[0] == bdata[0]:
            try:
                if (df[a] == df[b]).all():
                    df = df.drop(b, axis=1)
            except:
                continue
    return df

def is_time_between(begin_time, end_time, check_time=None):
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:
        return check_time >= begin_time or check_time <= end_time
    
def get_lesson(df, time, day=get_day()):
    for count, v in enumerate(df["Uur"]):
        d = v.split()
        if is_time_between(parse(d[1]), parse(d[2]), parse(time)):
            rooster = df.filter(regex=day)
            return format_lesson(rooster.iloc[count])

def format_lesson(d):
    info = {}
    # pauze, wat is na de pauze?
    if d is None:
        schedule = get_schedule()
        a = get_lesson(schedule, "10:25")
        format_lesson(a)
    else:
        d = dict(d)
        for key in d:
            les = d[key].split()
            info["docent"] = les[0]
            i = 0
            if "ALK" in les or "HOORN" in les:
                if "ALK" in les:
                    i = len(les) - 1 - les[::-1].index('ALK')
                elif "HOORN" in les:
                    i = len(les) - 1 - les[::-1].index('HORN')
                info["les"] = " ".join(les[1:i])
                info["lokaal"] = les[i+1]
            else:
                info["docent"] = ""
                info["lokaal"] = ""
                info["les"] = d[key]
        return info


schedule = get_schedule()
get_lesson(schedule, "10:21")
