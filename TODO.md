# TODO - Fix desktop scrolling/layout

- [ ] Inspect current CSS layout rules affecting scrolling/reachability.
- [ ] Apply minimal CSS-only changes in `frontend/style.css`:
  - Make `.app-container` fit viewport (height:100vh) and layout center/overflow not clip inner scroll.
  - Ensure `.app-body` middle area flexes correctly and allows nested scroll containers (`min-height:0`).
  - Ensure `.chat-section` + `.chat-window` and `.sidebar-section` scroll independently.
  - Remove overflow clipping that prevents reaching the Reminder widget (e.g. `.reminders-widget`).
  - Keep footer/header visually fixed and ensure it never overlaps.
- [ ] Verify no horizontal scrolling (add rules if needed).
- [ ] Run app in browser / sanity check at 1366×768, 1600×900, 1920×1080.

