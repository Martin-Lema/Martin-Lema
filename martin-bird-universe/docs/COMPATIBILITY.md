# Compatibility and metric definitions

## Delivery checklist

- [x] Standalone SVG assets referenced by relative `<img>` paths.
- [x] No scripts, iframes, embedded HTML, external fonts, external SVG references or remote image-card services.
- [x] The same hand-drawn palette and sprite system across eight scenes.
- [x] Five recognisably different pixel bird anatomies and behaviours.
- [x] CSS keyframes live inside SVG assets; no CSS is injected into GitHub's page.
- [x] Meaningful SVG titles/descriptions and README image alt text.
- [x] Separate animation-free SVGs and `STATIC.md`.
- [x] Reduced-motion CSS stops all animated layers where supported.
- [x] Important introduction, metrics, stack and project links also appear as native text.
- [x] Genuine data is authenticated, paginated, validated and date-labelled.
- [x] No fabricated metrics or sample contribution activity in delivered assets.
- [x] API failure leaves the last committed render intact.
- [x] Credential values are never stored in generated files or logged by the scripts.
- [x] Explicit workflow permissions, pinned checkout, no force push and no untrusted PR trigger.
- [ ] Run the workflow with Martin's real account (requires your username/repository).
- [ ] Verify the published profile in actual desktop/mobile GitHub clients.
- [ ] Confirm account-specific private activity behaviour if you enable it.

The checked items are implementation properties and offline automated checks. They are not a claim that the supplied package has already been deployed or authenticated to your GitHub account.

## What the numbers mean

| Observation | Source | Meaning / limitation |
| :--- | :--- | :--- |
| Contributions | GraphQL contributionCalendar.totalContributions | Total for the returned calendar period; not lifetime commits |
| One garden plot | contributionDays.date / contributionCount | Exactly one real API date, one daily count |
| Growth / colour | contributionDays.contributionLevel | GitHub's five intensity categories, not a fixed numeric scale |
| Active days | Count of returned dates with count > 0 | Calculated from actual daily values; not a current streak |
| Public repositories | User.repositories privacy PUBLIC / ownerAffiliations OWNER | Includes owned forks and archived repositories; excludes private repos |
| Primary languages | primaryLanguage on all owned PUBLIC non-fork repos | Number of repositories whose primary language is X; not bytes, proficiency or personal authorship |
| Unclassified repositories | null primaryLanguage | Counted separately; never labelled as an invented language |
| Update timestamp | Successful fetch time, UTC | A snapshot; not a live request from the visitor's browser |

No external service is needed. Visitors never need a token. The scheduled builder needs GitHub GraphQL authentication; the default automatic Actions token handles public data. Private/internal aggregate visibility may require the user's account settings and optional `read:user` scope. No private repo names are requested by this implementation.

## Rendering limitations

- GitHub sanitises README HTML. Page-level CSS, JavaScript, interactive SVG DOM and arbitrary layouts are not available. A README cannot change the surrounding GitHub profile interface.
- SVGs loaded as images disable JavaScript and restrict external resources. This package deliberately uses self-contained geometry and internal animation styles.
- Current mainstream desktop browser engines commonly render internal SVG CSS animation in an image. GitHub mobile apps, email/print views, thumbnails, proxies and future sanitisation changes may show a static image. No universal animation guarantee is possible.
- Embedded SVG text scales with the image rather than reflowing. At phone size, fine environmental captions and individual days will be small. Important content is repeated in native Markdown; open the image to inspect artwork at full size.
- Pixel geometry is exact at its native grid. Responsive fractional scaling can soften edges differently between browsers; `crispEdges` requests sharp rendering but does not enforce an integer physical-pixel zoom.
- Per-cell `<title>` text exists in the SVG file. Hover tooltips, nested links and tab stops inside an SVG used as an image are not reliable. Use GitHub's original calendar or the JSON snapshot for per-day inspection; native README links remain usable.
- Reduced-motion media queries depend on client/browser propagation into images. Separate static files are provided for a dependable manual alternative.
- System monospace fonts handle small scene captions; large pixel lettering is encoded as vector paths. Font metrics can differ slightly by platform.
- Self-contained backgrounds keep contrast predictable in GitHub light/dark themes. There is no theme-following gradient or filter dependency.
- A profile snapshot can lag behind GitHub because of scheduled-run delays, API visibility, eventual consistency or image caching. The date is printed, and failed updates are visible in Actions.
- The included local `preview.html` presents the SVG assets. It is not a full GitHub Markdown renderer and does not prove how GitHub sanitises or caches the published README.

## API and automation limitations

- The calendar uses GitHub's default past-year window, which can cross calendar years and include partial weeks. The UI date range is taken from returned dates, not assumed to be exactly 365 days.
- GraphQL API primary/secondary rate limits and authentication rules apply. GitHub documents 1,000 points/hour/repository for typical Actions `GITHUB_TOKEN` use. This daily builder makes a small profile query plus one query per 100 non-fork public repositories.
- Transient network/HTTP 429/5xx failures retry briefly, then fail. Authentication errors and GraphQL errors do not produce a fake fallback calendar.
- A page count or calendar mismatch fails validation, so a repository changing mid-pagination may require rerunning.
- Scheduled runs only operate on the default branch; GitHub may disable schedules after 60 days of public-repository inactivity.
- Branch protection can reject direct bot commits. A concurrent edit may also cause a safe rebase/push failure; rerun after resolving it. No force push is used.
- Editing the username with an old snapshot causes a validation failure until the new account is fetched or the old data is explicitly reset.
- `PROFILE_READ_TOKEN`, if used, is a personal credential with an expiry. Its permission requirements differ from fine-grained tokens and can be affected by organisational policy.

## Validation performed for this delivery

The 12 offline unit tests pass, including leap-year dates, missing/duplicate days, total mismatches, account identity, pagination, null primary languages, GraphQL failures, text escaping and preservation of the last good render. All 16 SVG files parse as XML; internal references, alt text sources, standalone restrictions, static variants and local README links were checked. The eight animation assets total about 149 KiB. The still illustrations were rendered locally with the macOS image renderer and visually inspected. The authenticated GitHub workflow and actual GitHub-hosted animation remain to be verified after installation; a username and profile repository were not supplied.
