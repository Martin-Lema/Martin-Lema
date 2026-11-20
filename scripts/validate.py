"""Check the standalone images and their references in both profile views."""
from pathlib import Path
import argparse
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = "{http://www.w3.org/2000/svg}"
HERO = ROOT / "assets/coast-banner.svg"
STILL = ROOT / "assets/coast-banner-still.svg"


def still_frame():
    source = HERO.read_text(encoding="utf-8")
    source = re.sub(r'<style data-motion="true">.*?</style>\n', "", source, flags=re.S)
    return re.sub(r' style="animation-delay:[^"]*"', "", source)


def check_asset(name):
    path = ROOT / name
    raw = path.read_text(encoding="utf-8")
    svg = ET.fromstring(raw)
    assert svg.tag == NS + "svg" and svg.get("viewBox"), name
    assert all(svg.findtext(NS + tag) for tag in ("title", "desc")), name
    ids = [node.get("id") for node in svg.iter() if node.get("id")]
    assert len(ids) == len(set(ids)), f"Duplicate ID in {name}"
    for node in svg.iter():
        assert node.tag not in {NS + "script", NS + "image", NS + "foreignObject"}, name
        for key, value in node.attrib.items():
            assert not key.lower().startswith("on"), name
            if key.endswith("href"):
                assert value.startswith("#") and value[1:] in ids, name
    for ref in re.findall(r"url\(#([^)]*)\)", raw):
        assert ref in ids, f"Unknown paint or clip reference {ref} in {name}"
    if "@keyframes" in raw:
        assert "prefers-reduced-motion" in raw, name
    return svg


def validate():
    assets = {"assets/coast-banner.svg", "assets/coast-banner-still.svg", "assets/coast-activity.svg",
              "assets/coast-activity-mobile.svg"}
    for filename in ("README.md", "preview.html"):
        markup = (ROOT / filename).read_text(encoding="utf-8")
        refs = set(re.findall(r'assets/[a-z-]+\.svg', markup))
        assert refs == assets, f"Unexpected image references in {filename}: {refs}"
    scenes = {name: check_asset(name) for name in assets}
    assert STILL.read_text(encoding="utf-8") == still_frame(), "Rebuild the still with --refresh-still"
    def days(name):
        return [node.text for node in scenes[name].iter(NS + "title")
                if node.text and re.match(r"\d{4}-\d{2}-\d{2} · \d+$", node.text)]
    desktop = days("assets/coast-activity.svg")
    assert len(set(desktop)) == len(desktop) == 365, "Expected one cell per day"
    assert desktop == days("assets/coast-activity-mobile.svg"), "Calendar data differs"
    print("Four SVGs validated. Both calendars include the same 365 days.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-still", action="store_true", help="Rebuild the reduced-motion image from the hero")
    if parser.parse_args().refresh_still:
        STILL.write_text(still_frame(), encoding="utf-8")
    validate()
