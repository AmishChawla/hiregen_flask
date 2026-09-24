# Lesson images — drop in, rebuild, done

Put an image in this folder and it appears in the right lesson at the next build.

## The filename is the instruction

`<module>-<lesson>.png` — Module 4, Lesson 4 is `4-4.png`. PNG, JPG or SVG.
Anything not matching that pattern is ignored, so working files can sit here.

## Then add a row to images.csv

```
lesson,alt,caption
4-4,"A large stack of resumes resolving into a short shortlist.","Five hundred in, twenty out."
```

**Alt text is required.** An image with no alt text is withheld from the build
and named in the console report. An infographic carries real information, so a
missing alt attribute genuinely excludes someone.

Caption is optional. A caption that restates the alt text is worse than none.

## What the build does for you

- Inserts the figure after the lesson's opening paragraph
- Reads the real dimensions and writes width/height, so the page does not jump
- Generates a WebP companion and serves it via `<picture>`
- Adds `loading="lazy"` and `decoding="async"`
- Adds ImageObject schema using the alt text
- Reports coverage and missing alt text on every build

## Infographics and SVG diagrams together

Some lessons also have an inline SVG diagram. Where a lesson has both, both
appear: your infographic straight after the opening paragraph, and the SVG one
paragraph later. The SVGs usually carry detail the infographic leaves out —
actual numbers, per-step labels — so they complement rather than duplicate.

## Keep the originals in the source package

Put a copy of every lesson image in the generator's `lesson-images/` folder too,
with the same `images.csv`. A clean build seeds `assets/img/` from there, so the
images survive a rebuild from scratch.

## This folder survives rebuilds

The build regenerates everything else in `assets/`. This folder is preserved,
along with `dataset/`, `resources/` and the site README.
