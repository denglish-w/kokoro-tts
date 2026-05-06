# Gradio State Management Skill

This skill assists with managing persistent and session state in the Kokoro TTS Gradio UI.

## Persistent Settings (BrowserState)
- **Goal**: Save user preferences (voice, speed) across browser sessions.
- **Implementation**:
  1. Add `gr.BrowserState(key="...")` to the UI components.
  2. Map the component value to the state in the `create_ui` function.
  3. Ensure the `BrowserState` is included in the output of the relevant event handlers.

## Session State (State)
- **Goal**: Store transient data (e.g., current generation progress) during a single session.
- **Implementation**: Use `gr.State()` for data that shouldn't persist across refreshes.

## Best Practices
- Use unique keys for `BrowserState` to avoid collisions.
- Always provide a default value for states.
- Validate state data before using it in engine calls.
