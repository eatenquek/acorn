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
2. A Swift helper (`ocr.swift`) reads it with **Apple Vision** (accurate mode, English). For PDFs, **PDFKit** uses embedded text first and only OCRs scanned pages. Nothing goes to the cloud. The temporary file is deleted afterwards.
3. A deliberately narrow rule-based parser pulls out the medicine name, strength, dose, route, time and frequency.
4. The parser flags the draft for clarification when OCR confidence is below 0.8, when the directions are complex (as needed, taper, "then", every N hours, for N days, BID/TID), or when they don't exactly match "Take [n] tablet(s) by mouth (at HH:MM) daily".
5. A flagged draft is held ("Let's not guess") and nothing is scheduled. A clean draft goes to a review screen. The user checks it against their prescription and confirms, then chooses a time if the label has none.

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
- **Complex prescriptions.** Multiple medicines per label, liquids, injections, tapering, PRN and weekly schedules are held, not parsed. Getting them wrong is dangerous, and they need clinical review to get right.
- **Persistence, accounts and push notifications.** The schedule lives in browser memory and can be exported as JSON. There is no backend, no reminder service and no mobile app.
- **Cross-platform OCR.** It relies on Apple Vision, so it only runs on macOS.
- **User testing.** No time-to-correct-schedule or return-after-miss measurements yet, so the prototype makes no speed or adherence claims.
- **Native Figma prototype.** The handoff is editable SVG screens (`figma-screens/`, `storyboard.svg`), not a wired Figma prototype.

## What I would build next

1. **A mobile app with on-device OCR** (Vision on iOS, ML Kit on Android) plus local notifications, so reminders actually fire.
2. **A versioned schedule and dose ledger.** Medication changes preserve history. Corrections update rewards, and repeated taps can't mint acorns.
3. **Broader parsing, behind the same hold rule:** twice daily, multiple medicines and liquids, with field-level evidence and pharmacist review of the rules.
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
