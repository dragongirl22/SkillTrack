# SkillTrack — Learn With Communities Campaign

A Flask web app for checking Google Skills public profiles against a 10-badge campaign goal.

## Run locally on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py app.py
```

Open http://127.0.0.1:5000.

## CSV format

The required column is `Google Skills Profile URL`. Optional columns include `Student`, `Name`, `Email`, and `[INFO]`. The included sample CSV demonstrates the campaign format.

## Verification behavior

- Profiles are checked sequentially with a configurable delay and retry handling.
- The parser counts visible `Earned <month> <day>, <year>` labels in the returned public-profile HTML.
- HTTP 401/403/404/410 and rate-limit responses are reported separately.
- A profile that cannot be read is shown as unverified; it is not treated as zero badges.
- Demo mode displays fictional values and must not be used as actual campaign results.

Google may change its profile markup or delivery behavior. Validate the live parser against the supplied reference profiles before relying on results. If Google serves profile content only after client-side JavaScript, this Requests-based parser will need a browser-rendering approach.

## Deployed as a public link (Render)

This file was then pushed as a repo on GitHub and then linked to web service deployment on render, the link for which is:
https://skilltrack-bmar.onrender.com

## Notes

SkillTrack is an independent project and is not affiliated with Google. Avoid uploading sensitive personal data; the app only needs profile URLs and optional display names.


## Snapshot checks and private profiles

SkillTrack is designed for on-demand campaign progress snapshots, not continuous background monitoring. Upload the roster and run a new check whenever an updated view is needed. Profiles that return an explicit private/access-restricted response or a recognizable private-profile notice are labelled **Private profile**; their badge count remains blank and is excluded from averages rather than being treated as zero. A profile may be made public and checked again later.

## Campaign insights

The dashboard includes an achievement rate calculated only from profiles with verified badge counts, a roster breakdown (completed, in progress, zero badges, private, and other unverified), and a top-three leaderboard that only lists students with at least one verified badge. Unverified/private profiles are excluded from the achievement rate and leaderboard so they are not misrepresented as having zero badges. Students with zero badges are also omitted from the leaderboard; if only one or two students have started, only those students appear.


### Student names in the results

If your CSV includes a student name column (for example `Student`, `Name`, `Student Name`, or `Full Name`), SkillTrack displays that name. If the CSV only contains Google Skills profile URLs, SkillTrack uses the public display name returned by the profile when available, instead of showing generic labels such as `Profile 1`. If a profile cannot be read, the fallback label remains so the row is still identifiable.
