import datetime
import json
import time

import pytz
import requests
from dateutil import parser
import logging
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


def get_upcoming_ctfs(days: int) -> str:
    """Find the upcoming CTFs and print them"""

    start_time = int(time.time()) - 86400 * 10
    end_time = int(time.time()) + (days * 86400)
    url = "https://ctftime.org/api/v1/events/?limit=20&start={}&finish={}".format(start_time, end_time)
    log.debug("URL = {}".format(url))
    req = requests.get(url, headers={'User-Agent': "Otters inc."})

    if req.status_code != 200:
        return "Unable to get upcoming events :("

    upcoming_ctfs = json.loads(req.text)

    bst = pytz.timezone('Europe/London')
    now = datetime.datetime.now(tz=bst)

    msg = ""
    msg += "*Upcoming CTFs* \n\n"

    for ctf in upcoming_ctfs:
        start = parser.parse(ctf['start'])

        local_dt = start.astimezone(bst)
        local_start = bst.normalize(local_dt)
        local_start = local_start.strftime('%a %d %b %H:%M')

        end = parser.parse(ctf['finish'])
        local_dt = end.astimezone(bst)
        local_end = bst.normalize(local_dt)
        local_end = local_end.strftime('%a %d %b %H:%M')

        if end >= now:
            msg += "*{}*\n".format(ctf['title'])
            msg += "{}\t to \t{}\n".format(local_start, local_end)
            msg += "Teams: {}\n".format(ctf['participants'])
            msg += "Type: {}\n".format(ctf['format'])
            msg += "{}\n".format(ctf['url'])
            msg += "\n\n"

    msg += ""

    return msg


def get_score(args: list):
    if len(args) < 5:
        return "!score <ctf_score> <place> <best_score> <num_teams> <weight>"
    else:
        score = int(args[0])
        place = int(args[1])
        best_score = int(args[2])
        num_teams = int(args[3])
        weight = float(args[4])

        points_coef = score / best_score
        place_coef = 1 / place

        total = ((points_coef + place_coef) * weight) / (1 / (1 + (place / num_teams)))

        return "Total CTFTime points: {:.5}".format(total)


def get_team_ranking(self) -> (int, int):
    position_found = None
    points_found = -1
    add_id = 0
    lookup_add = ""

    while position_found is None and add_id < 100:
        quote_page = 'https://ctftime.org/stats/{}'.format(lookup_add)

        # This useragent needs to be randomish otherwise we get 403'd
        page = requests.get(quote_page, headers={'User-Agent': "Otters inc."})
        soup = BeautifulSoup(page.text, 'html.parser')

        data = []
        table = soup.find('table', attrs={'class': 'table table-striped'})

        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])

        for l in data:
            if len(l) > 1 and l[1] == self.team_name:
                position_found = int(l[0])
                points_found = float(l[2])

        if position_found is not None:
            break

        add_id += 1
        lookup_add = "2019?page={}".format(add_id)

    if position_found is None:
        log.error("Cannot find position in first 100 pages!")

    return position_found, points_found

