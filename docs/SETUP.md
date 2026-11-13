# Martin Lema · Bird Universe

A complete GitHub **profile README**, with original animated pixel-art SVGs.
No website deployment, badges, external image cards or JavaScript required.
The included `preview.html` is only a convenient offline asset preview.

## Quick installation

1. Sign in to GitHub and create a **public** repository with **exactly your GitHub username** as its name. Example: if your username is `martin-example`, the repository must be `martin-example/martin-example`.
2. Download and extract the ZIP. Copy the **contents** of `martin-bird-universe/` into that repository's root. `README.md` must be at the root, not inside another folder.
3. Include the hidden `.github/` folder. In macOS Finder, press **Command + Shift + .** to see hidden files. GitHub Desktop is a convenient way to commit and push the whole folder.
4. Open `profile.json`. Replace `INSERT_USERNAME` with your username. Leave the unknown technology and project entries empty until you have chosen your real ones. If the placeholder is left unchanged, GitHub Actions automatically uses the repository owner, so the initial profile still works.
5. Commit and push the files. Open your profile at `https://github.com/YOUR_USERNAME`: the art appears immediately.
6. Open the repository's **Actions** tab, select **Grow the contribution garden**, and choose **Run workflow** on the default branch. If GitHub asks to enable workflows, enable them.
7. Wait for a successful run. It commits genuine contribution and statistics assets back into the repository. Refresh your profile; GitHub's image cache can take time to catch up.

You do **not** need a personal token for the normal public-data setup. You do **not** need GitHub Pages.

### If you already have a profile repository

Keep your existing work. Make a branch or backup first, then copy in this package and review the diff before merging. Keep your Word documents and unrelated assets. This package does not require deleting any of them. Integrate the files manually if a workflow or config with the same name already exists.

## Exact folder structure

```text
martin-bird-universe/
├── README.md                        # Ready-to-render profile; generated
├── STATIC.md                        # Entire profile without animation
├── profile.json                     # Edit your personal information here
├── preview.html                     # Local asset preview, not a deployed website
├── .gitignore
├── .github/
│   ├── dependabot.yml               # Monthly reviewable action updates
│   └── workflows/
│       └── contribution-update.yml
├── assets/
│   ├── hero-birds.svg
│   ├── about-forest.svg
│   ├── bird-species.svg
│   ├── contribution-garden.svg
│   ├── github-stats.svg
│   ├── developer-nest.svg
│   ├── exploration-map.svg
│   ├── footer-sunset.svg
│   ├── github-data.json             # Created ONLY after a real successful fetch
│   └── static/
│       ├── hero-birds.svg
│       ├── about-forest.svg
│       ├── bird-species.svg
│       ├── contribution-garden.svg
│       ├── github-stats.svg
│       ├── developer-nest.svg
│       ├── exploration-map.svg
│       └── footer-sunset.svg
├── scripts/
│   ├── art.py                       # Palette-based scenes, sprites and animation
│   ├── build.py                     # Renderer / config validation / README
│   ├── github_data.py               # GraphQL client / data validation
│   └── validate.py                  # Offline SVG and local-link checks
├── tests/
│   └── test_profile.py
└── docs/
    ├── SETUP.md
    ├── COMPATIBILITY.md
    └── SOURCES.md
```

The `github-data.json` file is intentionally absent in the initial download. Unknown data is never represented as a real zero or an invented sample calendar.

## Real contributions

The workflow authenticates to GitHub's official GraphQL API with the automatic, short-lived `GITHUB_TOKEN`.

1. `contributionsCollection.contributionCalendar` returns GitHub's own daily counts and intensity levels for its default past-year period.
2. The renderer preserves each date and its position: weeks run left to right; Sunday is at the top. The first and last week may be partial. Missing dates are rejected, not silently filled with zero.
3. Each real date becomes one garden plot. The cell colour follows GitHub's `contributionLevel`. More intense cells gain leaves and a flower. The five colour levels are GitHub categories, not fixed count thresholds.
4. Public repository totals are queried separately. Language statistics paginate **all** owned public non-fork repositories, rather than taking just the first 100.
5. Only aggregate metrics, dates, counts and levels are written to `assets/github-data.json`. No repository names or private code are saved.
6. The script renders SVGs and matching native Markdown totals. An API, permission, parsing or validation failure stops the update and preserves the previous committed snapshot.

**Contributions are not the same as commits.** GitHub applies its own contribution eligibility and date rules; qualifying issues, pull requests, reviews and other activity can contribute. Your profile's selected calendar year or your browser's local date may differ from this API window. The actual returned date range is printed beneath the garden.

### Optional private contribution aggregates

Start with the default public-data workflow. It is the least complicated setup.

GitHub's documented private/internal contribution visibility depends on the user and authentication scope. If you deliberately want private activity aggregates published in your public profile:

1. In your GitHub profile's **Contribution settings**, enable showing private contributions if appropriate.
2. Create an expiring **classic personal access token** with the optional **`read:user`** scope described by GitHub for `ContributionsCollection`. Do not grant broad `repo` access just for this profile.
3. Add it under repository **Settings → Secrets and variables → Actions → New repository secret**, named **`PROFILE_READ_TOKEN`**.
4. Rerun the workflow. This token is used for the GraphQL query only. The automatic repository token still performs the commit.

The renderer publishes only the returned daily aggregates, not private repository identities. Authenticated API results and anonymously visible GitHub profile counts are not guaranteed to be identical. Account policies, organisation restrictions, SSO and token permissions can affect visibility. A fine-grained token is not a drop-in mapping for the classic `read:user` scope; use GitHub's current permission documentation if choosing one.

Never paste a token into `profile.json`, a workflow file, a README, a URL, a screenshot or a chat. Delete/rotate optional tokens when no longer needed.

## Enable GitHub Actions

- The workflow must be committed to your **default branch**. It detects that branch; `main` is not hard-coded.
- Repository **Settings → Actions → General** must allow the official `actions/checkout` action. An organisation policy may restrict this.
- The job declares `contents: write`, needed to commit the generated files. If GitHub refuses the push, check the repository's Workflow permissions and organisation policy.
- Protected branches and rulesets can reject bot commits. Do not weaken protection blindly; use an approved pull-request process or generate locally and commit through your normal review process.
- Scheduled runs occur at **04:23 UTC daily**: 05:23 in Switzerland in winter, 06:23 in summer. GitHub may delay or drop a scheduled job. Manual runs remain available.
- GitHub can automatically disable schedules on public repositories after 60 days of inactivity. Re-enable the workflow in Actions if that happens.
- The workflow never runs on `pull_request_target`; untrusted PR code is not given a write token. The checkout action is pinned to a verified full commit SHA, and Dependabot proposes updates.
- Automatic commits use the GitHub Actions bot identity, not Martin's, so normal generator updates are not authored as your personal development activity.
- Bot pushes made with `GITHUB_TOKEN` do not recursively trigger this workflow. Its push path filter also excludes generated files.

## Customise your profile

### Technologies

Edit only the `items` arrays in `profile.json`; empty arrays produce clearly labelled placeholders:

```json
{"category": "LANGUAGES", "items": ["YOUR_LANGUAGE", "ANOTHER_LANGUAGE"]}
```

Those are examples to replace, not claims about Martin's current stack. Keep three categories. The signs use short labels; the native README prints the full lists so they remain readable on mobile.

### Featured projects

Fill a project entry with your real information:

```json
{
  "name": "YOUR_PROJECT_NAME",
  "description": "YOUR_ONE_SENTENCE_DESCRIPTION",
  "technologies": ["YOUR_TECHNOLOGY"],
  "repository": "https://github.com/YOUR_USERNAME/YOUR_REPOSITORY"
}
```

Keep three destinations. Blank entries are explicitly marked. A configured repository must use a real `https://github.com/OWNER/REPO` URL. Link syntax is validated, but the generator does not verify that a repository exists or is public: open each configured link while logged out.

The map is decorative. GitHub treats an embedded SVG as one image: separate clickable destinations inside that image cannot be relied on. Real, keyboard-accessible repository links live immediately below it in native Markdown.

### Text and name

Edit the English strings in `profile.json`. The large name is built from custom pixel paths, so there are no remote font dependencies. `scripts/art.py` contains the `FONT` mapping if you need extra letters. Personal text is escaped before rendering. The `bio` is always available as selectable text outside the illustration.

### Colours

Edit the named hex colours in `profile.json` under `palette`, then rebuild. Every scene and bird uses the same palette. Preserve useful contrast between `ink`/`deep` and `paper`/`cream`. Avoid changing the orange/blue/white identifiers so radically that the bird species become hard to recognise.

### Birds and animation

- `SPRITES` in `scripts/art.py` contains the actual pixel maps. Each letter maps to one palette colour; `.` is transparent.
- `kingfisher`: long bill, blue crown/back, orange belly; a slow head movement.
- `robin`: rounded breast and warm face; a small two-hop return cycle. This recurring trail companion also leaves footprints on the shore.
- `owl`: broad head, paired facial discs, mottled feathers; a sparse blink.
- `seagull`: slender body, white/grey wings, dark tips; up/mid/down/mid wing frames and independent flight speeds.
- `hummingbird`: slim bill, compact green body and coloured throat; fast discrete wing motion and a small hover loop. Its presence belongs to this imagined world, not a claim that hummingbirds live wild in Switzerland.

The stylesheet is internal to each SVG. It is never applied to GitHub's page. Nested groups keep movement, sprite scale and wing motion independent. Clouds and waves loop back smoothly; flying gulls reset outside the frame. `prefers-reduced-motion` disables all animations. `STATIC.md` uses separate animation-free assets even on clients that ignore the media query.

### Rebuild locally

Python **3.9 or later**, no third-party packages:

```sh
python3 scripts/build.py
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
```

The default command keeps an existing real data snapshot; it does not access the network. On Windows, `py -3` can replace `python3`.

For a live fetch, supply `GH_TOKEN` or `GITHUB_TOKEN` securely through your environment, then run:

```sh
python3 scripts/build.py --fetch
```

If you already use an authenticated GitHub CLI locally, this avoids putting the token in shell history:

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/build.py --fetch
```

Set your real username in `profile.json` for a local fetch. To intentionally remove a cached account snapshot and return to the empty state:

```sh
python3 scripts/build.py --reset-data
```

`README.md`, `STATIC.md`, `preview.html` and SVGs are generated files. Edit `profile.json` for content or `scripts/` for layout, then rebuild. Manual README edits would be overwritten on the next successful workflow run.

## Verify the real GitHub rendering

1. Confirm `README.md` is in a public `USERNAME/USERNAME` repository.
2. Visit your profile, not just the repository file browser. All eight illustrations should load.
3. Look for gulls crossing the hero, the robin hopping, the owl blinking and gentle waves. Animation is intentionally quiet; an owl blink can take several seconds.
4. Check Chrome/Edge, Firefox and Safari if available. Check an actual narrow phone viewport. Essential prose, stats and project links stay native Markdown even when the art becomes small.
5. Enable Reduce Motion in your operating system. Inspect the profile again; use **Still version** if your client does not propagate the preference to SVG images.
6. Inspect **Actions → Grow the contribution garden**. A successful run creates `assets/github-data.json` and a bot commit. Ensure the account and printed date range are yours.
7. Compare a few dates in the snapshot with GitHub's contribution calendar for the same period and visibility context. A raw JSON link is available through the repository for exact values; per-cell tooltips are not promised inside an `<img>`.
8. Open every featured repository link while logged out. Verify placeholders have been replaced only with accurate information.
9. Check light and dark GitHub themes. Artwork has its own opaque backgrounds and does not rely on the surrounding theme.
10. If old data persists, confirm the bot commit exists before blaming the API. GitHub proxies/caches images; a refresh is not a guaranteed immediate cache purge.

See [COMPATIBILITY.md](COMPATIBILITY.md) for the complete checklist and limitations, and [SOURCES.md](SOURCES.md) for technical references.
