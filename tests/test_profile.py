"""Synthetic fixtures are isolated in tests, never shipped as profile activity."""
import copy
import datetime as dt
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import art
import build
import github_data as gd


def fixture():
    days=[]
    for i in range(366):
        date=dt.date(2024,1,1)+dt.timedelta(days=i)
        count=i%5
        days.append({'date':date.isoformat(),'count':count,'level':count})
    return {'schema_version':1,'username':'test-account','updated_at':'2024-12-31T12:00:00+00:00',
            'period_start':'2024-01-01T00:00:00Z','period_end':'2024-12-31T23:59:59Z',
            'total_contributions':sum(d['count'] for d in days), 'restricted_contributions':0,
            'public_repositories':4,'nonfork_repositories':3,'unclassified_repositories':1,
            'primary_languages':{'Python':1,'C++':1},'days':days}

class DataTests(unittest.TestCase):
    def test_leap_calendar(self):
        data=fixture();self.assertEqual(len(gd.validate_snapshot(data)['days']),366)
        self.assertIn('2024-02-29',[d['date'] for d in data['days']])
    def test_gaps_duplicates_totals_rejected(self):
        mutations=[lambda d:d['days'].pop(4),
                   lambda d:d['days'][2].update(date=d['days'][1]['date']),
                   lambda d:d.update(total_contributions=99999),
                   lambda d:d['days'][0].update(count=-1),
                   lambda d:d.update(nonfork_repositories=500)]
        for change in mutations:
            data=fixture();change(data)
            with self.assertRaises(gd.DataError):gd.validate_snapshot(data)
    def test_wrong_owner_rejected(self):
        with self.assertRaises(gd.DataError):gd.validate_snapshot(fixture(),'another-account')
    def test_username_source(self):
        with patch.dict('os.environ',{'GITHUB_REPOSITORY_OWNER':'test-account'}):
            self.assertEqual(gd.resolve_login({'username':'INSERT_USERNAME'}),'test-account')
        for login in ['https://github.com/name','name;echo','bad--name','']:
            with self.assertRaises(gd.DataError):gd.validate_login(login)
    def test_missing_token_fails_before_request(self):
        with self.assertRaises(gd.DataError):gd.fetch('test-account','')
    def test_pagination_and_no_language(self):
        fixture_data=fixture();calls=[]
        def query(q,variables,token):
            calls.append(variables)
            if q==gd.PROFILE_QUERY:
                return {'user':{'login':'test-account','repositories':{'totalCount':4},
                    'contributionsCollection':{'startedAt':fixture_data['period_start'],
                      'endedAt':fixture_data['period_end'],'restrictedContributionsCount':0,
                      'contributionCalendar':{'totalContributions':fixture_data['total_contributions'],
                       'weeks':[{'contributionDays':[{'date':d['date'],'contributionCount':d['count'],
                         'contributionLevel':list(gd.LEVELS)[d['level']]} for d in fixture_data['days']]}]}}}}
            first=variables['cursor'] is None
            nodes=[{'primaryLanguage':{'name':'Python'}},{'primaryLanguage':None}] if first else [{'primaryLanguage':{'name':'C++'}}]
            return {'user':{'repositories':{'totalCount':3,'nodes':nodes,
                'pageInfo':{'hasNextPage':first,'endCursor':'page2' if first else None}}}}
        result=gd.fetch('test-account','test-only',query)
        self.assertEqual(result['primary_languages'],{'C++':1,'Python':1})
        self.assertEqual(result['unclassified_repositories'],1)
        self.assertEqual(len(calls),3)
    def test_graphql_errors_and_no_secret_in_message(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self):return b'{"data":null,"errors":[{"message":"private detail"}]}'
        with patch('urllib.request.build_opener') as opener:
            opener.return_value.open.return_value=Response()
            with self.assertRaises(gd.DataError) as error:gd.graphql('query {}',{},'secret-test')
            self.assertNotIn('private detail',str(error.exception))
            self.assertNotIn('secret-test',str(error.exception))

class RenderTests(unittest.TestCase):
    def setUp(self):
        self.config=json.loads((ROOT/'profile.json').read_text())
    def test_empty_state_no_fake_numbers(self):
        with tempfile.TemporaryDirectory() as folder:
            outputs=build.build(self.config,None,Path(folder))
            self.assertIn('NO ACTIVITY DATA LOADED',outputs['assets/contribution-garden.svg'])
            self.assertNotIn('assets/github-data.json',outputs)
            for path,raw in outputs.items():
                if path.endswith('.svg'):ET.fromstring(raw)
    def test_real_calendar_cells_and_all_static_variants(self):
        with tempfile.TemporaryDirectory() as folder:
            outputs=build.build(self.config,fixture(),Path(folder))
            garden=ET.fromstring(outputs['assets/contribution-garden.svg'])
            titles=[n.text for n in garden.iter('{http://www.w3.org/2000/svg}title')]
            self.assertEqual(sum(' contributions' in t for t in titles),366)
            self.assertEqual(len([p for p in outputs if p.startswith('assets/static/')]),8)
    def test_safe_custom_text_and_repository_links(self):
        config=copy.deepcopy(self.config)
        config['bio']='<script>alert(1)</script> & [trick](javascript:1)'
        config['projects'][0]={'name':'A < B','description':'Safe & readable','technologies':['C++'],
                               'repository':'https://github.com/example/project'}
        with tempfile.TemporaryDirectory() as folder:
            result=build.build(config,None,Path(folder))
            self.assertNotIn('<script>',result['README.md'])
            self.assertIn('https://github.com/example/project',result['README.md'])
        config['projects'][0]['repository']='javascript:alert(1)'
        with self.assertRaises(ValueError):build.validate_config(config)
    def test_api_failure_preserves_previous_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'profile.json').write_text(json.dumps(self.config))
            (root/'README.md').write_text('last known good')
            with patch.object(build,'ROOT',root),patch.object(sys,'argv',['build.py','--fetch']),\
                 patch.object(build,'resolve_login',return_value='test-account'),\
                 patch.object(build,'fetch',side_effect=gd.DataError('simulated API failure')):
                self.assertEqual(build.main(),1)
            self.assertEqual((root/'README.md').read_text(),'last known good')
    def test_escaping_generated_svg(self):
        art.palette(self.config['palette'])
        parsed=ET.fromstring(art.svg('A & B','<test>',art.text(10,20,'<script> & "text"'),100))
        self.assertEqual(parsed.find('{http://www.w3.org/2000/svg}title').text,'A & B')

if __name__=='__main__':unittest.main()
