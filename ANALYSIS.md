# Acorn: a world worth returning to

Product analysis and implementation recommendation · 7 October 2026

## Recommendation

Build a dependable medication routine first, and let an outdoor Forest make that routine feel personal. Use one continuous world: the Forest contains the squirrel’s customizable clearing. Keep the clearing available from day one. Earn growth through recorded care; spend acorns only on cosmetic objects. Preserve all earned growth after a missed dose.

For onboarding, ship **label photo → extraction → evidence-backed review → confirmed schedule** first. Offer **user-exported medication PDF → review** alongside it. Investigate authorized record connections in parallel with product development, but do not put the first usable version behind an unconfirmed health-system partnership.

This recommendation assumes a Singapore-first launch because of the project context. The original brief does not specify a market. Record access, language coverage and medication-label conventions must be revisited for each actual launch market.

## 1. What is strong in the supplied vision

The Forest gives an abstract routine a visible history. It offers something quieter and more durable than a badge or a notification count. The squirrel gives the space continuity. Customization supports personal ownership, and a missed-dose resting state can reduce the cost of returning after a gap.

The concept also correctly distinguishes earned progress from purchases. That distinction is central to credibility. However, a Forest is a visualization of patient-reported behavior, not verified evidence that a medicine was swallowed. A clinician-facing view must expose the actual dated record, missing entries, corrections and source provenance.

The strongest loop is: **make setup easy → know what is due → record what happened → see gentle progress → return without guilt**. Social comparison and animal collecting are possible additions, not prerequisites for that loop.

## 2. Where the concept needs revision

| Supplied idea | Assessment | Proposed change |
|---|---|---|
| Three pillars: Personal Forest, Social Grove, Wildlife Sanctuary | Three overlapping destinations add navigation and scope before the core behavior is proven. | Forest, Clearing, My record. Wildlife appears in the Forest; social features are deferred. |
| Streaks as the main progress measure | A reset can make earned history feel false or lost. | Cumulative completed care days earn permanent milestones. Show continuity and gaps separately in the record. This is an explicit change to the streak-driven brief. |
| Gray Forest after a miss | Desaturation can suggest death, damage or punishment, even with reassuring copy. | Preserve foliage and objects; use softer daylight, stillness and a comfortably resting squirrel. |
| “Take now” button | Ambiguous between giving an instruction and recording an event. | “I took this dose.” Separate missed and unrecorded states. |
| Social group dose totals and visible streaks | Can expose sensitive behavior and pressure members to protect the group. | Later opt-in encouragement without medication names, missed-dose indicators, ranking or member-level streaks by default. |
| Buy tree species and unlock trees through adherence | Purchased mature trees could resemble earned progress. | Cosmetics occupy a distinct clearing; milestone trees cannot be bought, gifted or accelerated. |
| More animals unlocked by adherence | Potentially delightful but risks turning animals into dependents whose welfare is contingent on medication behavior. | Visitors remain safe, content and nondependent. Previously welcomed animals never leave as punishment. |
| Day-one squirrel, day-seven rabbit, day-fourteen fox | Useful prototype anchors, not validated behavior design. | Keep the squirrel core; validate optional wildlife before building a collection economy. |
| Milestone ladder changes between brief and image | The image changes both the species and the day-30 reward. | Preserve the original sprout / fern / pine / oak / cabin ladder for this iteration; make each a new addition to the forest rather than claiming one tree transforms into different species. |

## 3. Forest and Den: the structural decision

The Den becomes **the Clearing**, an outdoor area within the same Forest. The squirrel lives in this world from the first visit. Navigation can focus on Forest, Clearing and My record without asking the user to learn a game map.

The clearing is available immediately. Initial free personalization establishes ownership without making the patient complete a month of adherence before seeing the product’s character. A simple bench is the working cosmetic example. The day-30 cabin is an earned landmark in the outdoor forest; it does not replace the Forest tab with a room.

Rejected alternatives:

- **Two equal worlds, Forest and indoor Den:** duplicates destinations and currencies, obscures where the squirrel belongs and adds navigation for low-confidence users.
- **Den unlocked at day 30:** delays the sense of ownership and excludes people with difficult routines from a major feature.
- **Merge everything into an indoor room:** violates the literal Forest requirement.
- **Forest only, no customization:** simpler, but removes a promising source of autonomy and personal meaning. A modest clearing preserves it with little navigation cost.
- **Social-first grove:** creates consent, disclosure and group-pressure work before individual usefulness is established.

The trade-off is that an outdoor clearing may feel less intimate than an indoor den. Research should compare these two emotional experiences, rather than assuming the clearing wins for everyone.

## 4. Define the reward rules before drawing more screens

Proposed production rules:

1. A scheduled dose has states: upcoming, due, unrecorded, patient-reported taken, patient-reported missed, or clinician-directed change/pause. The last category needs a distinct workflow; it is not implemented in this prototype.
2. A day qualifies for growth when all applicable scheduled doses have been reported taken. For several medicines, the denominator and cut-off rules must be explicit. PRN regimens need different progress rules and are excluded from the simple daily loop.
3. Do not mark a dose “missed” merely because there is no log. Offer a retrospective check-in.
4. Permanent milestones reflect cumulative completed care days. A separate calendar shows gaps honestly. This avoids claiming an uninterrupted streak while preserving earned growth.
5. Corrections change the underlying record and any associated reward transaction. Repeated taps and edits cannot create extra acorns. A production reward ledger must handle corrections even after currency has been spent.
6. Never offer purchases or gifts that erase a missed entry or add adherence days.
7. A medication change must version the schedule and preserve past events. Historical records must not be regenerated from the latest schedule.

The prototype uses a seeded seven-day Forest and one current dose to make the states reviewable. It is not an implementation of this full accounting system.

## 5. The missed-dose moment

The emotional sequence should be: acknowledge what happened → preserve belonging → give a clear way forward. The screenshot’s “It’s a resting day” risks implying that missing medication was an intentional rest day. Use a factual sentence first: **“This dose is recorded as missed.”** Follow it with **“Everything you’ve grown is still here.”**

The squirrel can curl up or sit quietly, but should not cry, look sick, go hungry or turn away. Trees retain their color. No broken streak alarm, public feed event, debt or disappearing asset. The user can correct the log.

Do not give generic catch-up instructions. Medication-specific missed-dose guidance requires an appropriate, verified source and separate clinical review. The prototype points to the medicine’s instructions or pharmacist/care team and never recommends doubling, taking late or waiting until tomorrow.

## 6. Fastest realistic prescription-to-schedule path

“No typing” is a useful aspiration. **No review** is a different and unjustified promise. A good importer minimizes transcription while keeping confirmation of name, formulation, strength, dose, route, frequency, timing and currentness visible.

| Route | What it can remove | Main constraint | Recommendation |
|---|---|---|---|
| On-device OCR of pharmacy label | Re-entering printed text | Glare, curved labels, small type, multiple labels, unclear instructions | First working route; available without a health-system contract |
| AI vision extraction | Layout interpretation and field mapping | Plausible but wrong values; privacy and vendor governance; output still requires validation | Evaluate against the OCR baseline on representative consented/de-identified labels |
| Exported health-record PDF | Photographing or typing information already held digitally | Historical records, incomplete directions, multi-medication layout | Practical secondary path now |
| Authorized structured health-record API | Repeated entry across several medicines | Access agreements, identity/consent, actual data coverage, stale/conflicting records | Partnership track; show only when a real authorized integration exists |
| Manual entry | Nothing, but offers recovery | Entry burden and transcription error | Always offer as a fallback; apply the same review rules |

For a legible, simple label, the proposed path has four visible tasks: choose/capture file, check draft, check time, confirm. The prototype does not claim a measured completion time. Benchmark time-to-confirmed-correct-schedule against manual entry before claiming a speed improvement.

### What the Singapore sources establish

HealthHub documents PDF downloads from prescription-record details. It also says available records can omit information and should be checked against current professional instructions. This makes patient-directed file import a concrete near-term option, with reconciliation still required. [HealthHub documentation](https://support.healthhub.sg/hc/en-us/articles/60045642695961-Track-and-Refill-Medications-Seamlessly)

NEHR access is described for authorized healthcare professionals providing care. The research did not establish a public third-party consumer API that Acorn can simply connect to. Patient visibility in HealthHub should not be presented as authorization for Acorn to retrieve the same data. [NEHR access information](https://www.healthinfo.gov.sg/nehr/)

HealthX offers sandbox APIs, including FHIR interfaces. Sandbox availability is useful for exploration; it does not demonstrate production access to a particular patient’s medication records. [HealthX API documentation](https://innovation.healthx.sg/features/apis/)

FHIR Dosage has concepts for free-text directions, timing, as-needed use, route and dose. Preserve those distinctions in Acorn’s model instead of flattening every record into a daily clock time. A data standard alone does not grant access. [FHIR R4 Dosage](https://hl7.org/fhir/R4/dosage.html)

## 7. OCR versus a vision model

This deliverable uses Apple Vision locally because it can demonstrate real text recognition without an API key or third-party prescription upload. PDFKit reads embedded PDF text first; scanned pages use OCR. A narrow parser then extracts a candidate, and the patient reviews it.

This is a **feasibility spike**, not a production clinical parser. It supports English, a single medicine, an explicit strength and simple once-daily oral tablet/capsule instructions. It holds ambiguous, PRN, tapering and unsupported instructions. Multiple medicines, liquids, injections, complicated calendars and medication reconciliation need dedicated development.

A production comparison should run identical documents through local OCR plus parsing and one or more approved vision models. Measure exact field accuracy, unsupported-case abstention, patient correction rates, latency and cost. Count dangerous substitutions separately: mg versus mcg, 0.5 versus 5, once weekly versus daily, and prescribed dose versus package strength. A confident-looking UI must not conceal uncertain evidence.

Model output should satisfy a typed schema, preserve source spans and pass deterministic consistency checks. Missing fields must remain missing. A second model repeating the first model’s answer is not independent clinical verification.

## 8. Schedule data and boundary cases

The working JSON export includes medicine display name, strength, dose, route, original directions, frequency, times, time zone, timing provenance, source method, extracted text and patient confirmation time. It explicitly marks clinical verification and notifications as false. Start/end dates are currently null: the prototype does not generate dated courses.

Production schema extensions should include ingredient/product identifiers with coding provenance; dosage form; normalized dose amount/unit; structured timing and bounds; PRN indications; maximum-dose instructions only when explicitly sourced; start/end dates; prescriber and record timestamps; field-level evidence; unresolved issues; versioned confirmation; source-record identifiers; and reconciliation status.

Required boundary decisions:

- **“Once daily” without a time:** ask for a reminder preference, labeled as the patient’s choice.
- **“Every eight hours”:** preserve intervals; do not map to three convenient meal times.
- **“As needed”:** no automatic repeating dose events.
- **Taper or alternating days:** structured multi-phase plan, or hold for clarification.
- **Dates/duration:** no inference from dispensing quantity; finite courses need explicit bounds.
- **Duplicate/conflicting records:** compare sources and dates; never select an apparent winner silently.
- **Missed or unreadable strength/unit:** block progression until corrected.
- **Multiple medicines:** review separate items, then reconcile the full list.
- **Time-zone travel/DST:** retain schedule semantics and ask how reminders should adapt; not implemented here.
- **Refill or new prescription:** ask whether it updates an existing medicine before creating a duplicate.

## 9. Accessibility and adult tone

Fraunces provides warmth in headings; Plus Jakarta Sans keeps forms and navigation legible. Cream and brown remain the base, with muted greens for the world. Avoid pixel-font body text, tiny game badges and dense economy controls.

Use explicit labels, stable navigation, visible focus, generous touch targets, reduced-motion support, plain language and text alongside icons. Review critical instructions with older adults and people with low digital confidence. The desktop prototype includes annotations outside the phone; these are presentation material, not patient-facing product content.

Small metadata in this prototype still needs a device-level readability pass before production. Native text scaling, screen-reader reading order, localized directions and multi-language labels require implementation and evaluation on the target platform.

## 10. Lightweight usability study

Recruit across the age range, with deliberate inclusion of people who use multiple medicines and people who are less comfortable with technology. Use fictional labels for the first study. Obtain appropriate consent before any real medication data is used.

Tasks: import a simple label; correct a wrong strength; handle daily directions with no time; respond to PRN directions; distinguish missed from unrecorded; return after a gap; find the record; personalize the clearing without confusing it with earned progress.

Observe whether people understand which values came from the label, which are their own preferences, whether they notice a seeded extraction error, and what they believe happened to the squirrel after a miss. Ask them to explain the result in their own words before prompting.

Metrics: completion without help, corrected errors, uncorrected critical errors, abandonment, time to a correct confirmed schedule, ease of returning after a miss, and understanding of the reward rules. These are proposed measurements, not results from a study already run.

## 11. Delivery sequence

1. Demonstrate a single-medication scan/review/save flow and the Forest’s taken/missed states. **This package.**
2. Validate with target users and a medication-domain reviewer. Fix comprehension and parsing failures before widening supported instructions.
3. Add multi-medicine reconciliation, schedule versioning, dated courses, notification permissions and delivery behavior on the actual mobile platform.
4. Benchmark local OCR and approved vision models on representative documents. Establish release criteria and monitoring.
5. Pursue health-system integration after confirming partner access, scopes, consent, data coverage and operational requirements.
6. Evaluate wildlife and social support only after individual setup and return behavior are useful.

The highest-value next evidence is whether a patient can quickly confirm a correct schedule and return after a missed dose without feeling punished. More collectible content cannot substitute for that evidence.

## 12. Deliverable boundaries

Working: localhost app, actual image OCR and PDF text/OCR pipeline, editable draft review, conservative hold state, reminder preference, session-only schedule export, Forest, clearing, dose logging and missed-dose resting state.

Not connected: real HealthHub/NEHR account access, pharmacy systems, AI vision API, mobile push notifications, backend accounts, real multi-medication adherence analytics or clinician verification.

Figma handoff: editable SVG storyboard and individual screens, plus flow and token specifications. This package does not claim a finished native Figma prototype. At the user’s latest request, Claude resumed the native Figma work while Codex completed the local implementation and this analysis. Native Figma completion is tracked separately.
