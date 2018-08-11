#!/usr/bin/env python
from collections import namedtuple
from os.path import abspath, dirname, join
import re

import jinja2
from bs4 import BeautifulSoup

Talk = namedtuple(
    'Talk', field_names=('speaker', 'title', 'youtube', 'abstract', 'poster')
)
HERE = dirname(abspath(__file__))


def transformer(x):
    if 'youtube.com' in x:
        x = x.strip().split('=')[1]
    else:
        x = re.sub('\s+', ' ', x.strip())
    return 'Panel Discussion' if x == 'Panel' else x


def get_text(column):
    return column.get_text() if not column.find('img') else column.find(
        'img'
    ).get(
        'src'
    ).strip()


def parse_talks():
    with open(join(HERE, 'conference-brief.html')) as f:
        soup = BeautifulSoup(f, 'html.parser')
    day_1 = []
    day_2 = []
    day = None
    for row in soup.find_all('tr'):
        text = row.get_text().strip()
        if text == 'DAY 1':
            day = day_1
        elif text == 'DAY 2':
            day = day_2
        elif 'Poster' in text and 'Speaker' in text:
            continue

        else:
            day.append(row)
    return day_1, day_2


def parse_talk(talk):
    talk = [transformer(get_text(col)) for col in list(talk)[1::2]][:5]
    return Talk(*talk)


def main():
    template_dir = HERE
    loader = jinja2.FileSystemLoader(template_dir)
    env = jinja2.Environment(loader=loader)
    template = env.get_template('post-template.html.jinja')
    days = [[parse_talk(talk) for talk in day] for day in parse_talks()]
    print(template.render(days=days))


if __name__ == '__main__':
    main()
