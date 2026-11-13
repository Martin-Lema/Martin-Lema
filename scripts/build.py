#!/usr/bin/env python3
"""Rebuild the complete profile: python3 scripts/build.py [--fetch]."""
import argparse
import html
import json
import os
from pathlib import Path
import re
import sys
import art
from github_data import DataError, atomic_write, fetch, resolve_login, validate_snapshot

ROOT=Path(__file__).resolve().parents[1]

def validate_config(config):
    for key,limit in [('name',22),('role',52),('qualification',50),('location',30),('bio',1000)]:
        value=config.get(key)
        if not isinstance(value,str) or not value.strip() or len(value)>limit:
            raise ValueError(f'{key} must be a non-empty string of at most {limit} characters.')
    if any(c.upper() not in art.FONT for c in config['name']):
        raise ValueError('The name uses a character missing from scripts/art.py FONT. Add its 5x7 glyph first.')
    if len(config['technologies'])!=3 or len(config['projects'])!=3:
        raise ValueError('Keep three technology categories and three project destinations.')
    for entry in config['technologies']:
        if not isinstance(entry['category'],str) or len(entry['category'])>24:raise ValueError('Technology category is too long.')
        if not isinstance(entry['items'],list) or any(not isinstance(x,str) or not x.strip() for x in entry['items']):raise ValueError('Technology items must be non-empty strings.')
    for project in config['projects']:
        for key in ['name','description','repository']:
            if not isinstance(project[key],str):raise ValueError('Project fields must be strings.')
        if not isinstance(project['technologies'],list) or any(not isinstance(t,str) for t in project['technologies']):raise ValueError('Project technologies must be strings.')
        repo=project['repository']
        if repo and not re.fullmatch(r'https://github\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+/?',repo):
            raise ValueError('Repository must be an https://github.com/OWNER/REPO URL.')
        if repo and (not project['name'] or not project['description']):raise ValueError('Add a project name and description with its repository link.')
    for name,c in config['palette'].items():
        if not re.fullmatch(r'#[0-9A-Fa-f]{6}',c):raise ValueError('Invalid palette colour: '+name)
    return config

def safe(value):
    # HTML-escape plain text, then neutralise Markdown syntax.
    result=html.escape(str(value),quote=True)
    return re.sub(r'([\\`*_{}\[\]()#+.!|>~-])',r'\\\1',result).replace('\n',' ')

def image(name,alt):
    return f'<p align="center">\n  <img src="assets/{name}.svg" width="1200" alt="{html.escape(alt,quote=True)}">\n</p>'

def readme(config,data):
    bio=safe(config['bio'])
    out=['<!-- Generated from profile.json by scripts/build.py. Edit the config, then rebuild. -->',
         image('hero-birds',config['name']+' — Apprentice Application Developer in Switzerland. A pixel coast with drifting clouds and flying birds.'),
         '<p align="center"><sub>S W I T Z E R L A N D &nbsp; / &nbsp; C O D E &nbsp; / &nbsp; C U R I O S I T Y</sub></p>',
         '### A little about me',bio,
         image('about-forest','The forest desk: a small terminal, tall pines and a hopping robin.'),
         image('bird-species','Five distinct residents: a kingfisher, robin, blinking owl, wing-flapping seagull and hovering hummingbird.'),
         '<p align="center"><sub>Five little residents. One shared world.</sub></p>',
         '### The Contribution Garden',
         image('contribution-garden','Real GitHub contributions, one day per garden plot. Darker foliage means higher GitHub contribution intensity.' if data else 'The contribution garden is awaiting its first GitHub data update. No activity is fabricated.'),
         image('github-stats','GitHub contribution total, public repositories, active days and primary repository languages.' if data else 'GitHub statistics are not connected yet.')]
    if data:
        total=data['total_contributions'];active=sum(d['count']>0 for d in data['days'])
        out+=[f'**{total:,} contributions** · **{data["public_repositories"]:,} public repositories** · **{active} active days**',
              f'<sub>Calendar: {data["days"][0]["date"]} to {data["days"][-1]["date"]}. Updated {data["updated_at"][:10]} UTC. [View on GitHub](https://github.com/{data["username"]}?tab=overview).</sub>',
              '<details>\n<summary>How these observations are counted</summary>\n',
              'Contributions and active days use the calendar period above. These are contributions, not just commits. Public repositories include forks. Primary language counts cover all owned public non-fork repositories, including archived repositories. Each repository counts once; these are not proficiency scores or proportions of code written by me.',
              '| Primary language | Repositories |\n| :--- | ---: |']
        out += [f'| {safe(name)} | {count} |' for name,count in sorted(data['primary_languages'].items(),key=lambda x:(-x[1],x[0]))]
        if not data['primary_languages']:out+=['| No primary-language data | — |']
        out += [f'\nRepositories without a detected primary language: {data["unclassified_repositories"]}.',
                'The calendar contains only what GitHub returned to the authenticated workflow. Private activity visibility depends on account settings and token permissions. The garden uses GitHub’s own intensity levels. [Data and accessibility notes](docs/COMPATIBILITY.md).\n\n</details>']
    else:
        out+=['<sub>Awaiting the first GitHub update. [Connect the garden](docs/SETUP.md#real-contributions).</sub>']
    out+=['### The Developer\'s Nest',image('developer-nest','Three editable signs for languages, tools and things I am exploring.')]
    for category in config['technologies']:
        items=', '.join(safe(x) for x in category['items']) or '[Add your technologies in profile.json]'
        out.append('**'+safe(category['category'].title())+':** '+items)
    out+=['### The Exploration Map',image('exploration-map','A woodland path with three numbered destinations. Project links follow below.')]
    for i,p in enumerate(config['projects'],1):
        if p['repository']:
            out += [f'**0{i} / [{safe(p["name"])}]({p["repository"]})**',safe(p['description']),
                    '<sub>'+(' · '.join(html.escape(x) for x in p['technologies']) or 'Technologies to be added')+'</sub>']
        else:
            out += [f'**0{i} / [Your project name]**',
                    '[Add a short description and your technologies.] · [Set this destination](docs/SETUP.md#featured-projects)']
    out += [image('footer-sunset','Always learning. Always building. Always exploring. Martin Lema. Pixel sunset, gulls, waves and a blinking owl.'),
            '<p align="center"><sub>Always learning. Always building. Always exploring.</sub></p>',
            '<p align="center"><sub>[Still version](STATIC.md) · [Field guide](docs/SETUP.md)</sub></p>']
    # Markdown does not parse inside raw HTML blocks, so use native links in the final line.
    out[-1]='[Still version](STATIC.md) · [Field guide](docs/SETUP.md)'
    return '\n\n'.join(out)+'\n'

def preview_html(markdown):
    # Lightweight standalone QA preview: no JS or network dependencies. Native
    # GitHub rendering remains authoritative; this intentionally is not a GFM parser.
    images=re.findall(r'<img [^>]+>',markdown)
    sections=[]
    for img in images:
        sections.append('<section>'+img+'</section>')
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Martin Lema — asset preview</title><style>body{margin:0;background:#f6f1e3;color:#183d43;font:16px system-ui}'
        'main{max-width:1000px;margin:32px auto;padding:16px}img{display:block;width:100%;height:auto}section{margin:28px 0}'
        'header{padding:12px 0}a{color:inherit}@media(max-width:600px){main{margin:0;padding:12px}}</style>'
        '<main><header>Martin Lema / Bird Universe<br><small>Local asset preview. Open README.md on GitHub for the full profile, selectable text and project links.</small></header>'
        +''.join(sections)+'</main></html>\n')

def build(config,data,outdir=ROOT):
    validate_config(config)
    if data:validate_snapshot(data)
    art.palette(config['palette'])
    scenes={'hero-birds':art.hero(config),'about-forest':art.about(config),'bird-species':art.species(),
            'contribution-garden':art.garden(data),'github-stats':art.stats(data),'developer-nest':art.nest(config),
            'exploration-map':art.exploration(config),'footer-sunset':art.footer(config)}
    # Render all content in memory first; malformed input cannot partly overwrite assets.
    outputs={}
    for name,args in scenes.items():
        outputs[f'assets/{name}.svg']=art.svg(*args)
        outputs[f'assets/static/{name}.svg']=art.svg(*args,static=True)
    md=readme(config,data)
    outputs['README.md']=md
    outputs['STATIC.md']=md.replace('src="assets/','src="assets/static/').replace('[Still version](STATIC.md)','[Animated version](README.md)')
    outputs['preview.html']=preview_html(md)
    if data:outputs['assets/github-data.json']=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    for path,body in outputs.items():atomic_write(outdir/path,body)
    return outputs

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch',action='store_true',help='Fetch authenticated real data before rendering.')
    parser.add_argument('--reset-data',action='store_true',help='Explicitly discard the cached account snapshot and show the empty state.')
    args=parser.parse_args()
    if args.fetch and args.reset_data:parser.error('--fetch and --reset-data are mutually exclusive')
    try:
        config=validate_config(json.loads((ROOT/'profile.json').read_text(encoding='utf-8')))
        snapshot=ROOT/'assets/github-data.json';data=None
        if args.fetch:
            login=resolve_login(config)
            token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
            data=fetch(login,token)
        elif snapshot.exists() and not args.reset_data:
            data=validate_snapshot(json.loads(snapshot.read_text(encoding='utf-8')),
                None if config['username']=='INSERT_USERNAME' else config['username'])
        build(config,data)
        if args.reset_data and snapshot.exists():snapshot.unlink()
        print('Built 8 animated SVGs, 8 still SVGs, README.md, STATIC.md and preview.html.')
        print('Real GitHub snapshot loaded.' if data else 'Honest empty state: no GitHub activity data loaded.')
        return 0
    except (DataError,ValueError,KeyError,OSError) as error:
        print('Build failed: '+str(error),file=sys.stderr);return 1

if __name__=='__main__':
    raise SystemExit(main())
