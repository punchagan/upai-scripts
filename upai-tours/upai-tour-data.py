#!/usr/bin/env python3
import os
import csv
import requests

BASE_URL = 'https://upai.usetopscore.com'
CLIENT_ID = os.getenv('UPAI_CLIENT_ID')
assert CLIENT_ID, 'Need to set UPAI_CLIENT_ID envvar'


def get_tournaments(year=None):
    url = '{}{}?auth_token={}&per_page=100&type=tournament'.format(
        BASE_URL, '/api/events', CLIENT_ID
    )
    if year is not None:
        extra_params = '&start={year}-01-01&end={year}-12-31'.format(year=year)
        url = url + extra_params
    r = requests.get(url)
    tournaments = r.json()['result']
    if year is not None:
        tournaments = [
            t for t in tournaments if t['start'].startswith(str(year))
        ]
    return tournaments


def tournament_teams(tournament):
    event_id = tournament['id']
    url = '{}{}?auth_token={}&event_id={}&per_page=100'.format(
        BASE_URL, '/api/teams', CLIENT_ID, event_id
    )
    r = requests.get(url)
    teams = [team['name'] for team in r.json()['result']]
    return teams


def make_csv(participation):
    events = participation.keys()
    teams = sorted(set.union(*map(set, participation.values())))
    with open('participation.csv', 'w', newline='') as csvfile:
        fieldnames = ['team-name'] + list(events)[::-1]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for team in teams:
            team_participation = {'team-name': team}
            team_participation.update(
                {
                    event: 1 if team in participation[event] else 0
                    for event in events
                }
            )
            writer.writerow(team_participation)


if __name__ == '__main__':
    year = 2017
    tour_events = set(
        [
            'suo-2017',
            'usha-bangalore-ultimate-open-2017',
            'muo-2017',
            'usha-auo2017',
        ]
    )
    tournaments = get_tournaments(year)
    participation = {
        tournament['name']: tournament_teams(tournament)
        for tournament in tournaments
        if tournament['slug'] in tour_events
    }
    print(participation)
    make_csv(participation)
