#!/usr/bin/env python

import os
from datetime import datetime
import argparse
import requests

parser = argparse.ArgumentParser(description='Show issues closed on a week')
parser.add_argument('org', type=str, help='an organization name')
# parser.add_argument('week', type=int, help='a number of week')
args = parser.parse_args()
org = args.org
# week = args.week

token_file = 'token.txt'
if not os.path.exists(token_file):
    raise RuntimeError('{file} is not exists'.format(file=token_file))
if not os.path.isfile(token_file):
    raise RuntimeError('{file} is not a regular file'.format(file=token_file))
with open(token_file, 'r') as f:
    token = f.read().strip()

# year = datetime.now().strftime('%Y')
# since = datetime.strptime('{}-W{}-1'.format(year, week), "%G-W%V-%w")
# until = datetime.strptime('{}-W{}-1'.format(year, week + 1), "%G-W%V-%w")

session = requests.Session()
headers = {
    'Accept': 'application/vnd.github.v3+json',
    'Authorization': 'token ' + token,
}

r = session.get('https://api.github.com/orgs/{}/members'.format(org), headers=headers)
org_members = set()
for user in r.json():
    org_members.add(user['login'])

while 'next' in r.links:
    next_url = r.links['next']['url']
    r = session.get(next_url, headers=headers)
    for user in r.json():
        org_members.add(user['login'])

r = session.get('https://api.github.com/orgs/{}/repos'.format(org), headers=headers)
org_repos = []
for repo in r.json():
    org_repos.append(repo['name'])

while 'next' in r.links:
    next_url = r.links['next']['url']
    r = session.get(next_url, headers=headers)
    for repo in r.json():
        org_repos.append(repo['name'])

params = {
    'filter': 'all',
    'state': 'open',
    'sort': 'popularity',
    # 'since': since.isoformat(timespec='seconds'),
}

pull_requests = []

for repo in org_repos:
    base_url = 'https://api.github.com/repos/{}/{}/pulls'.format(org, repo)
    r = session.get(base_url, headers=headers, params=params)

    data = []
    data.extend(r.json())

    while 'next' in r.links:
        next_url = r.links['next']['url']
        r = session.get(next_url, headers=headers)
        data.extend(r.json())

    for pull in data:
        # closed_at = datetime.strptime(pull['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
        # if closed_at < since or closed_at >= until:
        #     continue
        if pull['user']['login'] in org_members:
            continue

        title = pull['title'].strip()
        result = {
            'url': pull['html_url'],
            'title': title,
            'repo': repo,
        }

        pull_requests.append(result)

# print(pull_requests)
for pull in pull_requests:
    print('{}: {} [{}]'.format(pull.repo, pull.title, pull.url))
