# Acorn design handoff

## Native Figma work

Existing file: https://www.figma.com/design/hJ1fXuN9vmmoMX3mk1v6Wa

Claude is assigned the native Figma completion and interaction wiring. Codex owns this local prototype and analysis. Status must be confirmed from the completed file; a file link alone does not prove its flows are wired.

## Local editable vectors

Import `storyboard.svg` for the full overview, or the 12 files in `figma-screens/` separately. These contain vector shapes and text. Install Fraunces and Plus Jakarta Sans for matching typography. Imported SVGs are static until interactions are connected; they are a portable handoff and do not replace the live local app.

## Tokens

| Token | Value |
|---|---|
| Background | `#FAF6ED` |
| Paper surface | `#FFFCF5` |
| Primary text/button | `#402C22` |
| Secondary text | `#74685B` |
| Forest accent | `#45634B` |
| Border | `#E3DACB` |
| Caution fill | `#F6ECD5` |
| Heading | Fraunces Medium, 31–35 px |
| Body | Plus Jakarta Sans, 14–16 px |
| Button | Plus Jakarta Sans Semibold, 14 px |
| Reference frame | 390 × 844 px |
| Horizontal padding | 24 px |
| Button height | 52 px |
| Corners | 10–17 px |

## Connections

| Origin | Interaction | Destination |
|---|---|---|
| 01 Forest | Add medicine | 02 Add |
| 01 Forest | Record dose | 07 Log |
| 02 Add | Scan label | 03 Scan |
| 02 Add | Import PDF | 10 PDF |
| 03 Scan | Choose/sample image | Reading → 04 Review |
| 04 Review | Confirm matching fields | 05 Time |
| 04 Review | Missing printed time | 11 Reminder |
| 04 Review | Unsupported/unclear instructions | 09 Hold |
| 05 Time / 11 Reminder | Confirm schedule | 06 Saved |
| 06 Saved | Back to Forest | 01 Forest with medicine |
| 07 Log | I took this dose | Growing confirmation → 01 Forest |
| 07 Log | I missed this dose | 08 Rest |
| 08 Rest | Correct log | 07 Log |
| 09 Hold | Try clearer label | 03 Scan |
| 10 PDF | Import | Review or Hold depending on content |
| Forest navigation | Clearing | 12 Clearing |

The app also includes manual entry, provenance/details disclosure, a future connection explanation, a personal record and JSON export. The vector storyboard deliberately summarizes the main paths.

## Required state semantics

- Unrecorded and missed are different states.
- A draft is never an active reminder.
- Original extracted directions are retained separately from edited/confirmed directions.
- A patient reminder preference is never relabeled as a prescribed time.
- Missing clock time has no default value.
- Daily, interval, PRN, taper and weekly instructions require different models. The local implementation only supports the narrow daily case.
- The resting Forest preserves earned trees and their color; the squirrel remains comfortable.
- Cosmetics cannot affect the medication record or milestone progress.
- Future record integration must remain explicitly unconnected until authorized access actually exists.

## Lightweight presentation script

“We focused on two moments that determine whether Acorn becomes useful: getting a medicine into the app, and returning after a difficult day.

“The quickest route we can demonstrate today is a photo of a pharmacy label. This prototype actually reads the image locally. It then shows the source directions beside editable details. If the directions are incomplete or outside the supported simple daily case, it stops before making a schedule.

“There is also a practical route from existing records: HealthHub lets patients download a medication record as a PDF. We can read that file, but must confirm that the information is still current. We have not established a direct production API connection, so that is a partnership track rather than a promise on the onboarding screen.

“Once confirmed, the schedule leads straight into the Forest. We propose one outdoor world, with a customizable clearing available from day one. The squirrel belongs there; earned trees cannot be bought. A missed dose is recorded honestly, and the Forest pauses without losing what the person has grown.

“The next step is to observe whether adults can confirm a correct schedule, notice a deliberately seeded extraction error and understand the difference between a prescribed time and their own reminder preference. That evidence should guide wider medication support and any social features.”
