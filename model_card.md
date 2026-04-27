## Reflection

### What this project taught me about AI and problem-solving

Building a RAG system from scratch even a local, static one made the mechanics of retrieval-augmented generation concrete. The quality of retrieved context is the real bottleneck: a suggestion is only as good as the knowledge it's grounded in, and structuring that knowledge by species, task type, and keywords is its own design problem. The reliability validation layer taught me that AI-assisted systems need explicit quality gates generating output isn't enough; you need a systematic way to check whether that output actually makes sense.

Adding AI features to an existing deterministic system exposed a tension I hadn't anticipated: the original scheduler was fast and predictable, but AI suggestions introduce ambiguity. I resolved this by keeping the AI layer purely advisory where it enriches the schedule but never overrides the core algorithm. That separation made each layer independently testable, which I now see as a fundamental design principle.

---

### Limitations and Biases

**Knowledge base is static and narrow.** The RAG system retrieves from roughly 10 hand-written entries covering only dogs and cats. It has no knowledge of exotic pets, breed-specific needs, or age-related care differences (a senior dog's exercise needs differ significantly from a puppy's). Any species entered as something other than "dog" or "cat" falls through to generic tips, which may be irrelevant or mildly misleading.

**Retrieval is keyword-matched, not semantic.** The system matches task types and species labels as strings. If a user enters "stroll" instead of "walk," the dog exercise advice won't be retrieved. A real RAG system would use embeddings to match meaning, not just exact words.

**Priority scale is subjective.** The 1–5 priority system relies entirely on what the owner enters. There is no validation that a "priority 5" task is actually critical ie someone could mark grooming as priority 5 and feeding as priority 2, and the system would schedule accordingly without questioning it.

**No personalization over time.** The system has no memory between sessions. It cannot learn that a specific pet consistently skips afternoon tasks or that an owner always has less time on weekends. Every session starts from zero.

---

### Could This AI Be Misused?

This system's risk surface is low, it schedules pet care tasks, not medical treatment or financial decisions. That said, a few misuse scenarios are worth naming:

- **Over-reliance on suggestions:** An owner could follow a RAG suggestion (e.g., "walk daily for 45–60 min") without considering their specific pet's health condition. The system adds no disclaimer that advice should be verified with a vet for animals with mobility issues, heart conditions, or other medical needs.
- **Priority manipulation:** Because priority is self-reported, a user could accidentally or intentionally deprioritize genuinely critical tasks (medications, insulin injections) and the scheduler would skip them if time runs short.

**How I'd prevent this in a production version:** Add a "medical task" flag that bypasses bin-packing and is always scheduled regardless of available time. Attach a static disclaimer to all RAG suggestions: *"This is general care guidance, not veterinary advice."* Validate that tasks tagged as medications are never assigned priority below 4.

---

### What Surprised Me During Reliability Testing

The most surprising finding was how often the **boundary-minute false positive** appeared during conflict detection. I assumed that two tasks where one ends exactly when the next begins (08:00–08:15, then 08:15–08:30) would trivially be conflict-free. The original `<=` interval check flagged them as overlapping. It wasn't a logical error. It was an assumption baked into the comparison operator that I didn't consciously make. That one character (`<` vs `<=`) produced warning noise on every sequential schedule I tested, and it took examining an actual test failure to catch it.

The second surprise was that the **completeness check passed even when tasks were skipped due to overflow.** The validator checked whether mandatory tasks were in the plan object, but the scheduler's bin-packing had already quietly dropped them before validation ran. The validator was checking the wrong thing, it was confirming the plan was internally consistent, not that it was complete relative to what the owner actually needed. I fixed this by having the completeness check compare against the owner's full task list, not just what was already in the plan.

---

### Collaboration with AI During This Project

I used Claude as a design partner throughout this project, primarily for thinking through architecture decisions and catching gaps in my test coverage.

**One instance where AI help was genuinely useful:**
When I was designing the `ReliabilityValidator`, I initially had all five validation checks as methods inside the `Scheduler` class. Claude suggested splitting them into a separate `ReliabilityValidator` class and returning structured `ValidationResult` dataclass objects instead of plain strings. That turned out to be the right call and it made each check independently testable (I could call `_check_completeness()` in isolation), and it gave the UI a structured object to work with instead of parsing free-text warnings. I wouldn't have made that architectural separation without the suggestion.

**One instance where the AI's suggestion was wrong:**
When writing the RAG suggestion tests, Claude suggested asserting `len(suggestions) >= 1` to verify that at least one suggestion was returned for any pet. That seemed reasonable, but it produced a flaky test when a dog already had a walk, feeding, and grooming task scheduled, the suggestion engine correctly returned an empty list (nothing to add), which broke the assertion. The right assertion was `isinstance(suggestions, list)` with a separate targeted test for the specific suggestion content (e.g., that cats with no litter task always receive a litter box suggestion). The AI was optimizing for "something is returned" when the real requirement was "the right things are returned given context."

---