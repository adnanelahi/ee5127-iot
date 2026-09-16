# EE5127 GitHub Pages template

Template published from the public repository https://github.com/adnanelahi/ee5127-iot. GitHub Pages is configured to build from `main` and `/docs`.

## Theme and layout

The [reference Feather Sense tutorial](https://web.cecs.pdx.edu/~gerry/class/feather_sense/setup/) uses Jekyll and Just the Docs, identifiable in its HTML stylesheet and script paths. This starter uses the same theme, pinned to release `v0.10.1`, rather than copying the reference author's text, screenshots, branding or analytics. It retains the light documentation layout, sidebar, search, heading anchors and page contents. It is not a pixel-exact copy of that site's customisations.

Theme documentation: [Just the Docs](https://just-the-docs.com/). Upstream theme licensing remains with [Just the Docs](https://github.com/just-the-docs/just-the-docs/blob/v0.10.1/LICENSE.txt).

## Files

- `docs/_config.yml`: module title, theme, search and callouts.
- `docs/index.md`: course home.
- `docs/labs/index.md`: lab overview and migration status.
- `docs/labs/lab-01-sensor-node-foundations.md`: first migrated laboratory page.
- `docs/support/`: support pages required by migrated laboratories.
- `docs/assets/images/`: approved instructional images grouped by lab.
- `docs/_sass/custom/custom.scss`: responsive images and print adjustments.
- `templates/lab.md`: blank lab skeleton, outside the published source.

Only `docs/` is the Pages source. Keep this README, templates, staff records and archives outside it. During the migration, the module `content/` directory remains a temporary source for labs not yet transferred; remove it only after the final lab has been checked and copied.

## Add a lab

1. Copy `templates/lab.md` to `docs/labs/lab-N-short-name.md` (choose the next lab number).
2. Set a unique title, numeric `nav_order` and permalink. Keep `parent: Labs` identical to the overview's title.
3. Replace the prompts with reviewed content from the authoritative module source. Preserve the agreed self-contained, unassessed lab structure.
4. Put approved images in `docs/assets/images/` and downloads in `docs/assets/downloads/`. Reference them with the examples in the skeleton; the `relative_url` filter supports repository subpaths.
5. Add the page link to the overview and the homepage table of contents will update automatically.
6. Check page contents, sidebar order, search, images, downloads, code, mobile layout and print output in a rendered preview.

GitBook-specific hint, tab and embed syntax must be converted to Jekyll-compatible Markdown/HTML when actual pages are transferred. Rewrite `.md` links to the chosen page permalinks. Do not simply copy the entire content tree or workspace into the Pages source.

## Local preview

Ruby and Bundler are required. They were not available in the current environment, so a Jekyll build and visual preview have not yet been verified. No runtime or dependency packages were installed in this project.

With Ruby and Bundler installed, run from this template directory in PowerShell:

```powershell
$env:BUNDLE_PATH = Join-Path $env:TEMP 'ee5127-jekyll-gems'
$env:BUNDLE_APP_CONFIG = Join-Path $env:TEMP 'ee5127-bundle-config'
bundle install
bundle exec jekyll serve --source docs --destination "$env:TEMP/ee5127-pages-preview" --disable-disk-cache
```

Open the localhost address printed by Jekyll. The first build needs network access to fetch the pinned remote theme. Keep dependency caches and generated output outside the working project.

## GitHub Pages setup

1. Copy only this starter directory's contents into the root of the selected repository. Do not upload the module-design workspace.
2. Set `url` to `https://USERNAME.github.io` and `baseurl` to `/REPOSITORY` in `docs/_config.yml`. For a `USERNAME.github.io` repository, use an empty `baseurl`.
3. Push the reviewed files to `main`.
4. In **Settings → Pages**, choose **Deploy from a branch**, then **main** and **/docs**, and save. GitHub builds the Jekyll source with the remote-theme plugin; no custom deployment workflow is required.
5. Check the Pages build result and review the published site, including a direct lab URL and asset downloads.

Enabling Pages publishes the material. The repository is public, so the published site and source are visible on the internet. This GitHub Pages deployment is separate from the paused GitBook upload. Review existing lab release holds before adding those labs.

See [GitHub's Jekyll Pages instructions](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/creating-a-github-pages-site-with-jekyll).
