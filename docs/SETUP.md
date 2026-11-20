# Maintaining the profile

Edit `assets/coast-banner.svg` to change the illustration. The named groups follow the scene from the sky to the foreground. The lettering is outlined, so it renders without downloading a font. Motion uses CSS inside the SVG. GitHub serves a separate still image when a viewer requests reduced motion. After editing the hero, run `python3 scripts/validate.py --refresh-still` to rebuild that image. Open `preview.html` locally to see the artwork and the current calendar together.

The **Refresh coastal calendar** workflow queries GitHub’s GraphQL contribution calendar for `Martin-Lema` each morning at 04:23 UTC. It checks that the response covers every day in the requested 365-day period. The total is the sum of those daily counts. Both calendar layouts use the same snapshot and GitHub’s contribution levels. The visibility of contributions follows GitHub’s response to the repository’s workflow token.

The scheduled job runs on the default branch and uses the built-in `GITHUB_TOKEN`. Actions must be enabled and the workflow must be allowed to push the generated SVGs to that branch. To refresh immediately, select **Actions → Refresh coastal calendar → Run workflow**. A failed API request leaves the last published calendar in place.

For a local refresh, authenticate GitHub CLI with `gh auth login` and run `python3 scripts/coast_activity.py`. Run `python3 -m unittest discover -s tests` and `python3 scripts/validate.py` to check the calendar logic, SVGs and README image references.
