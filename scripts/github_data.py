"""Fetch an honest, minimal GitHub snapshot using only Python's standard library.

Only dates, counts, contribution levels and aggregate repository language counts
are saved. No repository names, private source code, email addresses or tokens.
"""
import datetime as dt
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request
from collections import Counter

ENDPOINT = 'https://api.github.com/graphql'
LEVELS = {'NONE':0,'FIRST_QUARTILE':1,'SECOND_QUARTILE':2,'THIRD_QUARTILE':3,'FOURTH_QUARTILE':4}
PROFILE_QUERY = '''query Profile($login: String!) {
  user(login: $login) {
    login
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection {
      startedAt endedAt restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}'''
LANGUAGE_QUERY = '''query Languages($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, privacy: PUBLIC,
                 ownerAffiliations: OWNER, isFork: false,
                 orderBy: {field: NAME, direction: ASC}) {
      totalCount nodes { primaryLanguage { name } }
      pageInfo { hasNextPage endCursor }
    }
  }
}'''

class DataError(RuntimeError):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise DataError('Refusing an API redirect; credentials were not forwarded.')

def validate_login(login):
    if not isinstance(login,str) or not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', login):
        raise DataError('Set username to your GitHub username (not a URL).')
    if '--' in login:
        raise DataError('Invalid GitHub username.')
    return login

def resolve_login(config):
    candidate=config['username']
    if candidate == 'INSERT_USERNAME':
        candidate=os.environ.get('GITHUB_REPOSITORY_OWNER','')
    return validate_login(candidate)

def graphql(query, variables, token):
    request=urllib.request.Request(ENDPOINT,
        data=json.dumps({'query':query,'variables':variables}).encode(),
        headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json',
                 'Content-Type':'application/json','User-Agent':'Martin-Bird-Universe/1.0'},
        method='POST')
    opener=urllib.request.build_opener(NoRedirect())
    for attempt in range(3):
        try:
            with opener.open(request, timeout=30) as response:
                payload=json.load(response)
            if payload.get('errors'):
                # Do not print response bodies or tokens to workflow logs.
                raise DataError('GitHub GraphQL rejected the request. Check username, token permissions and rate limits. Last snapshot preserved.')
            if not isinstance(payload.get('data'),dict):
                raise DataError('GitHub returned no usable data. Last snapshot preserved.')
            return payload['data']
        except urllib.error.HTTPError as exc:
            if exc.code in (429,500,502,503,504) and attempt<2:
                time.sleep(2**(attempt+1));continue
            raise DataError(f'GitHub HTTP {exc.code}. Check Actions logs, API availability and token permissions. Last snapshot preserved.') from None
        except (urllib.error.URLError,TimeoutError):
            if attempt<2:
                time.sleep(2**(attempt+1));continue
            raise DataError('GitHub API could not be reached. Last snapshot preserved.') from None
        except json.JSONDecodeError:
            raise DataError('GitHub returned invalid JSON. Last snapshot preserved.') from None
    raise DataError('GitHub API retry limit reached.')

def validate_snapshot(data, login=None):
    """Reject incomplete/malformed calendars instead of drawing invented cells."""
    if not isinstance(data,dict) or data.get('schema_version')!=1:
        raise DataError('Unsupported snapshot schema.')
    validate_login(data['username'])
    if login and data['username'].lower()!=login.lower():
        raise DataError('Snapshot belongs to a different username; run an authenticated update.')
    days=data['days']
    if not isinstance(days,list) or not 1<=len(days)<=367:
        raise DataError(
    f"Unexpected calendar: type={type(days).__name__}, "
    f"days={len(days) if isinstance(days, list) else 'not a list'}"
)
    previous=None
    for day in days:
        current=dt.date.fromisoformat(day['date'])
        if previous and (current-previous).days!=1:
            raise DataError('Calendar dates must be consecutive and unique.')
        previous=current
        if type(day['count']) is not int or day['count']<0:
            raise DataError('Invalid contribution count.')
        if type(day['level']) is not int or not 0<=day['level']<=4:
            raise DataError('Invalid contribution level.')
        if (day['count']==0)!=(day['level']==0):
            raise DataError('Contribution count and level disagree.')
    for key in ['total_contributions','public_repositories','restricted_contributions','nonfork_repositories','unclassified_repositories']:
        if type(data[key]) is not int or data[key]<0:raise DataError('Invalid aggregate: '+key)
    if sum(d['count'] for d in days)!=data['total_contributions']:
        raise DataError('Daily counts do not match the API total; refusing an incomplete calendar.')
    languages=data['primary_languages']
    if not isinstance(languages,dict) or any(not isinstance(k,str) or type(v) is not int or v<1 for k,v in languages.items()):
        raise DataError('Invalid primary-language counts.')
    if sum(languages.values())+data['unclassified_repositories']!=data['nonfork_repositories']:
        raise DataError('Language pagination is incomplete.')
    for key in ['updated_at','period_start','period_end']:
        dt.datetime.fromisoformat(data[key].replace('Z','+00:00'))
    return data

def fetch(login, token, query_fn=graphql):
    validate_login(login)
    if not token:raise DataError('Set GH_TOKEN or GITHUB_TOKEN. GraphQL requires authentication.')
    user=query_fn(PROFILE_QUERY,{'login':login},token).get('user')
    if not user:raise DataError('No GitHub user found for the configured username.')
    collection=user['contributionsCollection'];calendar=collection['contributionCalendar']
    days=[{'date':day['date'],'count':day['contributionCount'],'level':LEVELS[day['contributionLevel']]}
          for week in calendar['weeks'] for day in week['contributionDays']]
    langs=Counter();cursor=None;seen=set();repo_count=0;unclassified=0
    while True:
        result=query_fn(LANGUAGE_QUERY,{'login':login,'cursor':cursor},token)['user']['repositories']
        for node in result['nodes']:
            repo_count+=1
            if node['primaryLanguage']:langs[node['primaryLanguage']['name']]+=1
            else:unclassified+=1
        page=result['pageInfo']
        if not page['hasNextPage']:break
        cursor=page['endCursor']
        if not cursor or cursor in seen:raise DataError('Repeated pagination cursor. Last snapshot preserved.')
        seen.add(cursor)
    # Detect repository additions/deletions during pagination; a later run can retry.
    if repo_count!=result['totalCount']:raise DataError('Repository list changed during pagination. Run the update again.')
    data={'schema_version':1,'username':user['login'],'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
          'period_start':collection['startedAt'],'period_end':collection['endedAt'],
          'total_contributions':calendar['totalContributions'],
          'restricted_contributions':collection['restrictedContributionsCount'],
          'public_repositories':user['repositories']['totalCount'],
          'nonfork_repositories':repo_count,'unclassified_repositories':unclassified,
          'primary_languages':dict(sorted(langs.items())), 'days':days}
    return validate_snapshot(data,login)

def atomic_write(path, contents):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    try:
        temp.write_text(contents,encoding='utf-8');os.replace(temp,path)
    finally:
        if temp.exists():temp.unlink()
