# Acorn — write-up

A medication routine app where recorded care grows a calm, personal forest. This repo holds a working local prototype and the analysis behind it. The full product critique is in [ANALYSIS.md](ANALYSIS.md); this page is the short version.

## Approach

**Product first, then the fun.** The core loop is: make setup easy → know what is due → record what happened → see gentle progress → come back without guilt. The forest visualises that loop; it is not the loop.

**Structural changes to the brief.**
- One world, three tabs: **Forest** (today's care), **Clearing** (the squirrel's customisable space, open from day one), **My record** (honest dated history). Social Grove and a wildlife collection are deferred.
- Growth is counted in cumulative care days, so a missed dose never erases what was earned. Gaps show in the record, not as a dead or grey forest.
- "Take now" became "I took this dose", with separate *missed* and *unrecorded* states.
- Acorns buy cosmetics only. They never add growth days or change the medication record.

**Onboarding: label → draft → review → schedule.** The fastest path that works without a health-system partnership:

1. The browser sends a label photo or PDF to a local Python server (`server.py`, standard library only, bound to 127.0.0.1).
2. A Swift helper (`ocr.swift`) reads it with **Apple Vision** (accurate mode, English), respecting the photo's EXIF orientation so sideways phone photos read upright. For PDFs, **PDFKit** uses embedded text first and only OCRs scanned pages. Nothing goes to the cloud. The temporary file is deleted afterwards.
3. `label_parser.py` turns the text lines into one draft per medicine. It copes with how real labels are written:
   - **Layout:** directions wrapped across lines, a name split from its strength ("AMOXICILLIN" / "500MG"), name and directions on one row (records and tables), and repeated labels (a bottle beside its label).
   - **OCR slips:** run-together words ("TAKE1CAPSULE"), "l tablet" for "1 tablet", "ONE (1)" and "tablet(s)".
   - **Frequency:** once to four times daily in words, digits or abbreviations (BD, TDS, QID, OM, ON), "morning and night", mealtimes, and every 4, 6, 8, 12 or 24 hours.
   - **Doses:** tablets, capsules, halves, ml, drops, puffs, sprays, sachets and patches, plus the route.
   - **Extras:** clock times ("8am", "21:30"), course length ("for 10 days" → end date), and food instructions ("after meals").
4. Anything that needs interpretation is **held** and nothing is scheduled: as needed/PRN, dose ranges ("1–2 tablets"), "then", tapering, weekly, "up to", "as directed", injections and unit doses, and intervals that don't divide a day.
5. Everything else goes to **review**, with warnings rather than a hold when something is uncertain: hard-to-read text, a missing name, dose or frequency, a route filled in as "by mouth" for a tablet, or other medicine-like text on the label. A record listing several medicines shows a picker so they're set up one at a time.
6. On review, the person checks the draft against their label and confirms. The server re-checks the edited fields with the same parser (strength vs. name, dose vs. directions, route), so the rules exist in one place. If the label has no clock times, Acorn suggests times for the person to adjust. Interval schedules keep exact spacing from the first dose they choose.

**Safety stance.** No review step means no schedule. The prototype never gives missed-dose advice; it points to the pharmacist or care team.

## Part A — integration routes

| Route | What it removes | Main constraint | Assessment |
|---|---|---|---|
| On-device OCR of the pharmacy label | Retyping printed text | Glare, curved labels, small type, several medicines per label, unclear directions | **Built.** Works today with no partner or API key. |
| User-exported health-record PDF (e.g. HealthHub) | Photographing or typing data already held digitally | Records can be historical or incomplete; layouts with several medicines | **Built (single medicine).** HealthHub documents PDF download of prescription records, so this is a realistic near-term route. Reconciliation is still needed. |
| AI vision model extraction | Layout interpretation and field mapping | Wrong values that look plausible; privacy and vendor governance; output must still be validated | **Not built.** Benchmark against the OCR baseline on consented or de-identified labels before adopting. |
| Authorised structured API (NEHR / HealthX / FHIR) | Re-entering several medicines | Access agreements, identity and consent, actual data coverage, stale or conflicting records | **Partnership track.** NEHR is for authorised professionals. No public consumer API was found. HealthX sandbox FHIR APIs are useful for exploration but don't give production patient access. |
| Manual entry | Nothing, but a guaranteed fallback | Effort and transcription errors | **Always offered**, with the same review rules. |

**Recommendation.** Ship label OCR plus PDF import now and pursue an authorised record connection in parallel. Don't make the first usable version wait on an unconfirmed partnership. Whatever the source, model the data on FHIR Dosage (free-text directions, timing, as-needed, route, dose), so that a later API integration slots in without flattening everything into "daily at 08:00". A data standard by itself doesn't grant access.

Sources: [HealthHub medication records](https://support.healthhub.sg/hc/en-us/articles/60045642695961-Track-and-Refill-Medications-Seamlessly) · [NEHR access](https://www.healthinfo.gov.sg/nehr/) · [HealthX APIs](https://innovation.healthx.sg/features/apis/) · [FHIR R4 Dosage](https://hl7.org/fhir/R4/dosage.html)

## What I could not do, and why

- **Real health-record access (HealthHub/NEHR).** There is no public third-party consumer API, and production access needs a partnership, consent and identity work beyond a prototype.
- **AI vision extraction.** I avoided sending prescription images to a third-party API without governance or an approved vendor. Local OCR proves feasibility with no keys or uploads.
- **Complex prescriptions.** Injections, tapering, PRN, dose ranges and weekly schedules are held, not parsed. Getting them wrong is dangerous, and they need clinical review to get right.
- **Persistence, accounts and push notifications.** The schedule lives in browser memory and can be exported as JSON. There is no backend, no reminder service and no mobile app.
- **Cross-platform OCR.** It relies on Apple Vision, so it only runs on macOS.
- **User testing.** No time-to-correct-schedule or return-after-miss measurements yet, so the prototype makes no speed or adherence claims.
- **Native Figma prototype.** The handoff is editable SVG screens (`figma-screens/`, `storyboard.svg`), not a wired Figma prototype.

## What I would build next

1. **A mobile app with on-device OCR** (Vision on iOS, ML Kit on Android) plus local notifications, so reminders actually fire.
2. **A versioned schedule and dose ledger.** Medication changes preserve history. Corrections update rewards, and repeated taps can't mint acorns.
3. **A labelled test set of real (consented, de-identified) labels**, to measure the parser instead of relying on synthetic cases, with field-level evidence and pharmacist review of the rules.
4. **An extraction benchmark:** OCR + rules vs. a vision model on the same de-identified labels. Measure field accuracy, abstention on unsupported cases, user correction rate and dangerous substitutions (mg/mcg, 0.5/5, weekly/daily).
5. **A lightweight usability study** (ANALYSIS.md §10): can someone confirm a correct schedule quickly, and come back after a miss without feeling punished?
6. **Health-record integration**, once partner access, scopes and consent are confirmed.
7. Only after that: wildlife and opt-in social encouragement.

## Run it

macOS with Swift Command Line Tools and Python 3. See [README.md](README.md).

```sh
swiftc -module-cache-path /tmp/acorn-swift-cache ocr.swift -o ocr
python3 server.py   # then open http://127.0.0.1:8765
```

All medication data in the repo is fictional. This is not a clinical product.
