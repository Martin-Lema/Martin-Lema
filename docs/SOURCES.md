# Research notes and references

Consulted for this implementation on 13 November 2026. Artwork and pixel maps are original; no bird sprites, profile artwork or palettes were copied from other artists.

## GitHub documentation

- [Managing your profile README](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme): public repository named after the user, root README.
- [Attaching files — supported media formats](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files): GitHub-supported SVG media.
- [GraphQL Users reference](https://docs.github.com/en/graphql/reference/users): ContributionCalendar, ContributionCalendarDay, ContributionsCollection, user repositories, private/internal visibility and optional read:user scope.
- [GraphQL rate and query limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api): authentication-based limits and GITHUB_TOKEN limits.
- [Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows): schedule/default-branch behaviour, delays and inactivity rules.
- [Disabling and enabling a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows): re-enabling inactive schedules.
- [Managing Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository): repository policy and permissions.
- [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use): least privilege and immutable action references.
- [actions/checkout v6.1.0](https://github.com/actions/checkout/releases/tag/v6.1.0) and [verified pinned commit](https://github.com/actions/checkout/commit/d23441a48e516b6c34aea4fa41551a30e30af803): the included workflow pins this official commit. Dependabot can propose newer releases.

## Browser and artistic research

- [MDN: SVG as an image](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image): JavaScript and external resource restrictions in image contexts.
- [MDN: prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion): motion preference handling.
- [Lospec's subpixel-animation tutorial index](https://lospec.com/pixel-art-tutorials/tags/subpixel): reviewed as an index to artists' work, including Pedro Medeiros; guided the principle of sparse motion and readable silhouettes. No source artwork was imported.
- [GitHub profile design gallery](https://github.com/roypriyanshu02/awesome-github-profile-readme): surveyed layout patterns for inspiration; this profile intentionally uses one original visual world rather than mixing unrelated third-party cards.

Research supports the implementation choices; it cannot replace a live run on the owner's GitHub account. Exact current behaviour remains subject to GitHub and browser changes.
