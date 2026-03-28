# Frontend Guidelines

## UX Principles
- Keep recruiter focus on progress visibility and decision explainability.
- Separate operational states: pipeline, interview, decision, report.
- Preserve low cognitive load with clear step labels and timelines.

## Wireframes (Phase 5)

1. Input Screen
- Left panel: candidate form.
- Right panel: pipeline snapshot.

2. Pipeline Tracker
- Job id, global status, current step.
- Step history list with state labels.

3. Interview Screen (chat-style)
- Transcript timeline.
- Current adaptive question with focus area and difficulty.
- Structured answer textarea and submit button.

4. Results Dashboard
- Candidate summary and key extracted signals.
- Agent-wise cards: score + reasoning snippet.
- Final score + final priority.

5. Download Report
- Explicit download CTA enabled only when backend report is ready.

## Validation UX
- Disable answer submit on empty content.
- Show backend error detail if interview submission fails.
- Keep polling active until done/failed to avoid stale state.

## Accessibility
- Keep contrast-safe colors.
- Preserve semantic labels for form and interview fields.
- Ensure responsive single-column fallback on mobile.
