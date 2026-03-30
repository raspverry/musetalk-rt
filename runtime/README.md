# Runtime package scaffold

This scaffold follows the server-first, session-based architecture in `/docs` and separates cold-path avatar preparation from the hot speaking path.

## Directories
- `runtime/api/`: API contract and request/response handlers.
- `runtime/session/`: session and utterance state machines.
- `runtime/avatar/`: avatar preparation and cache lifecycle.
- `runtime/streaming/`: frame/event streaming interfaces.
- `runtime/metrics/`: runtime metrics emission.

This commit only creates structure and planning artifacts; no major runtime rewrites are introduced.
