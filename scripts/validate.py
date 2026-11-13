#!/usr/bin/env python3
"""Offline SVG safety, accessibility, reference and size checks."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
SVG='{http://www.w3.org/2000/svg}'

def validate(root=ROOT):
    files=sorted((root/'assets').rglob('*.svg'))
    assert len(files)==16, f'Expected 16 SVGs, found {len(files)}'
    for file in files:
        raw=file.read_text(encoding='utf-8');tree=ET.fromstring(raw)
        assert file.stat().st_size<150_000, f'Asset too large: {file.name}'
        assert tree.find(SVG+'title') is not None and tree.find(SVG+'desc') is not None
        ids=[node.attrib['id'] for node in tree.iter() if 'id' in node.attrib]
        assert len(ids)==len(set(ids)), f'Duplicate IDs in {file.name}'
        for node in tree.iter():
            assert node.tag not in {SVG+'script',SVG+'foreignObject',SVG+'image',SVG+'a'}
            for k,v in node.attrib.items():
                assert not k.lower().startswith('on'),f'Event handler in {file.name}'
                if k.endswith('href'):
                    assert v.startswith('#') and v[1:] in ids,f'Unresolved or external reference: {v}'
        assert '@import' not in raw and 'http://' not in raw.replace('http://www.w3.org/2000/svg','')
        if file.parent.name=='static':assert '@keyframes' not in raw
        else:assert 'prefers-reduced-motion' in raw
    for name in ['README.md','STATIC.md']:
        md=(root/name).read_text(encoding='utf-8')
        for ref in re.findall(r'src="([^"]+)"',md):assert (root/ref).is_file(),ref
        for ref in re.findall(r'\]\(([^)]+)\)',md):
            if not ref.startswith('https://'):
                assert (root/ref.split('#')[0]).exists(),ref
    return files

if __name__=='__main__':
    files=validate()
    print(f'Validated {len(files)} standalone SVGs and all local README links.')
    print(f'Animated assets: {sum(p.stat().st_size for p in files if p.parent.name!="static")/1024:.1f} KiB total.')
