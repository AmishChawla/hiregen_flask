# AI Recruitment Masterclass — complete course package

Static HTML. No build step, no dependencies, no database. Upload and serve.

**Built:** 11 September 2026 · 12 modules · 73 lessons · ~40,000 words · ~4 hours reading

---

## What is in here

| Path | What it is |
|---|---|
| `index.html` | Course home — curriculum, progress tracker, three audience paths, FAQs |
| `module-1/` … `module-12/` | 73 lesson pages, one file each |
| `worked-run.html` | A real screening pass over the dataset, with the numbers |
| `resources.html` + `resources/` | 20 templates and worksheets, plus `template-pack.zip` |
| `dataset/` | `ai-recruitment-dataset.zip` — 500 synthetic resumes, job brief, human shortlist |
| `path-founder.html`, `path-agency.html`, `path-compliance.html` | Curated subsets |
| `about.html` | Authorship, conflict of interest, what to be sceptical of |
| `license.html` | Open source licence — CC BY 4.0 content, CC0 templates and dataset |
| `glossary.html` | 52 terms in plain language, each linked to the lesson that covers it |
| `changelog.html` | Dated record of revisions, and what gets reviewed how often |
| `course-map.html` | Every lesson on one page |
| `404.html` | Styled not-found page |
| `sitemap.xml` | 82 URLs |
| `assets/` | `course.css`, favicons, social card |
| `assets/img/` | Drop lesson images here — see the README in that folder |
| `_deploy/` | **Do not upload.** nginx config, robots.txt line, deployment checklist |

## Deploy

1. Upload everything except `_deploy/` to `/var/www/hiregen/academy/`.
2. Add the nginx block from `_deploy/nginx-academy.conf` **above** your app's
   catch-all `location /`.
3. Add the sitemap line from `_deploy/robots-additions.txt` to your **root**
   robots.txt. A robots file inside a subfolder does nothing.
4. Verify the five URLs listed in `_deploy/DEPLOY.md`.
5. Submit `/academy/sitemap.xml` in Search Console.

## Change these before launch

| What | Currently |
|---|---|
| Signup link | `hiregen.com/signup?ref=academy` — unverified |
| Contact address | `academy@hiregen.com` — must be a monitored inbox |
| Updated date | 21 September 2026 — change `UPDATED` in `build.py` on every revision; it drives the page dates, the schema and the sitemap together |
| Launch date | The changelog says "Published 11 September 2026". Set it to your real launch day before going live |

These live in `build.py`, in the separate generator archive
(`course-generator-source.zip`). Change them there and rebuild — they flow
through all 85 pages. Find-and-replace across the HTML also works if you would
rather not rebuild.

## Licence

Published open. Course text under **CC BY 4.0**; templates and the 500-resume
dataset under **CC0 1.0**. Full terms in `license.html`, linked from the sidebar
on every page.

**Confirm this choice before you publish.** Open licences are effectively
irrevocable once people rely on them, and the specific licences were selected on
your behalf rather than by you. If you would rather restrict commercial reuse,
or require share-alike, say so before the pages go live.

Not covered by those licences: the HireGen name and logo, third-party material
cited in the lessons, and the web fonts (Literata and IBM Plex Sans, SIL OFL).

## Lesson images in this build

Eight infographics are placed: 2.2, 3.1, 3.5, 6.3, 6.5, 7.1, 8.4 and 10.3.
Their empty margins were trimmed so the drawings render larger; the artwork
itself is unchanged. Two images from the corrections pack were held back —
9.4 and 11.2 — because they contradict their lessons. See the change notes.

## Adding lesson images

Drop a file named `<module>-<lesson>.png` into `assets/img/`, add a row to
`assets/img/images.csv` with its alt text, and rebuild. The figure is inserted
after the lesson's opening paragraph, a WebP companion is generated, dimensions
and lazy loading are set, and `ImageObject` schema is added.

Alt text is required — images without it are withheld and named in the build
report. Six lessons already have inline SVG diagrams and will ignore an image.
Full instructions in `assets/img/README.md`.

## Layout

Pages have **no header and no footer** — they are content-only, designed to sit
inside your own site template. White background, plain text. The left sidebar
contents and the breadcrumb are part of the content.

## Authorship

The course is attributed to HireGen as an organisation. No individual is named,
in the page text or in the structured data.

## Before you promote it

`resources/19-pilot-testing-pack.md` covers getting three recruiters to test the
course before you push traffic at it. It names who to ask, what to send them,
the six questions worth asking, and the two that waste everyone's time. This is
the one check that automated verification cannot replace.

## Maintenance

Two things date fastest and will make the course wrong if left:

- **Module 11, Lesson 1** — the regulatory map. Two items changed in the six
  months before publication. The EU AI Act high-risk deadline moved to
  2 December 2027; Colorado's SB 24-205 was repealed and replaced.
- **Module 8, Lesson 4** — `JobPosting` structured data requirements.

Put a quarterly reminder in a calendar. Update the date stamp when you revise,
or the "Updated" line becomes a lie.

## Dataset

All 500 resumes are synthetic. No real people, and email addresses use the
reserved `.test` domain.
