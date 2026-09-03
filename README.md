# content-pack

## What this repo is

This repo is the one source of truth for Snehanshn Chowdhury's facts: resume, projects, awards, links, and hobbies.
Three surfaces consume it: the SSH site, `snehanshn-site` on Vercel, and the `SnehanshnC` GitHub profile README.
Facts are stored here once, structured, and keyed by permanent slugs.
Each surface keeps its own display mapping - tone, styling, ordering - in its own repo.

## The section files

- `identity.yaml` - name, role, education, the shared tagline pool, and the skills list.
- `work.yaml` - work history entries, one per role, with highlights and links.
- `projects.yaml` - three top-level keys: `projects` (project writeups), `awards` (a flat list of hackathon and competition results, each referencing a project by slug), and `programs` (non-hackathon recognition, such as YC Startup School).
- `links.yaml` - the five canonical handles: github, linkedin, devpost, devfolio, ssh.
- `hobbies.yaml` - two top-level keys: `shows` (what Snehanshn watches) and `hobbies` (everything else).

Each section file has a matching schema in `schema/`, and both are validated together by `scripts/validate.py`.

## Slug stability

Every entity in this pack - work entries, projects, awards, programs, links, shows, hobbies - is keyed by a slug.
Slugs are permanent identifiers.
They are never renamed and never reused, even if the underlying fact is edited or the display copy changes.
Consumers key their own display mappings (tone, icons, ordering, jokes) on these slugs, so a slug rename would silently break every downstream surface.
If a fact turns out to be wrong, fix the fact in place; do not delete and recreate the slug.

## Consumption

Every surface consumes this repo's `main` branch at build time.
A push here propagates to all downstream surfaces automatically: there is no publish step in this repo.
A surface that needs to freeze its content pins a specific commit instead of tracking `main`.
Propagation triggers - build hooks, GitHub Actions, deploy hooks - live in each consuming repo, never in this one.
This repo only produces validated facts; it does not know or care who reads them.

## The derived-aggregates rule

Aggregate claims, such as a hackathon win count or a career-length win-loss record, are always derived from the itemized `awards` list at render time.
They are never hand-written, including inside this repo's own data files.
If a surface wants to say "3x HackRU," it computes that number by counting matching `awards` entries; this pack never stores the number "3" directly.
This rule exists because hand-written aggregates drift out of sync with the itemized facts the moment either one changes.

## What is deliberately per-surface

The following are never in this pack, by design, because they belong to each consumer's own presentation layer:

- Tone and voice.
- Curation and ordering of which facts to show and in what sequence.
- Visual metaphor: color, iconography, motifs, theming mechanics.
- Easter eggs and jokes.

Display mappings for all of the above live in each consumer's own repo, keyed by the slugs defined here.
This repo has no opinion on how a fact is presented, only on whether it is true.

## What never goes in the pack

- Phone number.
- Email address.
- GPA and coursework (resume-only, never published here).
- Hand-written aggregate claims (see the derived-aggregates rule above).
- Dead or unregistered domains; only working URLs are stored.

## Identity tone directive

Where this pack does carry framing (for example, in `identity.yaml`'s role and taglines), the positioning is AI and full-stack engineering.
It is never latency- or quant-flavored.
Latency and trading-infrastructure detail belongs only inside Yuno's own entries in `work.yaml` and `projects.yaml`, not in the shared identity framing.

## CI as the sole gate

Every push to this repo runs schema validation in `.github/workflows/validate.yml`.
`scripts/validate.py` checks every section file against its JSON Schema and reports all errors, not just the first.
It also checks slug uniqueness within every slug-keyed list, and that every cross-reference (an award's `project`, `work`'s `algora` entry, and `hobbies`' `meme-culture` entry) resolves to a real project slug.
A bad edit fails this check and cannot merge, so it cannot propagate to any downstream surface.
This makes CI the sole gate on what counts as a fact in this pack.
