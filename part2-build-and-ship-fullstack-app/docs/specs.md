# Collaborative System Design Interview Platform — Specification

A live interview tool: the interviewer creates a session link, candidates join, and everyone
draws on one shared canvas in real time.

## 1. Core flows

**Interviewer**
1. Signs in.
2. Creates an interview session — gets a shareable link and a short join code.
3. Opens the board, can start with a blank canvas or a saved template.
4. Sees who is in the room, follows each person's cursor.
5. Ends the session; the board is saved and viewable later.

**Candidate**
1. Opens the link, types a display name (no account needed).
2. Lands straight on the shared board with edit rights.
3. Draws, drags components, connects them, writes notes.

**Observers** (optional extra interviewers) join with a view-only variant of the link.

## 2. The canvas

Everything below lives on one infinite, pannable, zoomable canvas.

**System design shapes** (drag from a left-hand palette):
- Service / generic box
- Client (web, mobile)
- Database (SQL, NoSQL, cache)
- Queue / stream
- Load balancer
- API gateway
- CDN
- Object storage
- LLM / model call
- External third-party API
- Group / boundary box (region, VPC, microservice cluster)
- Sticky note and plain text label

Each shape: editable label, secondary sub-label (e.g. "Postgres, 3 replicas"), resize,
recolor from a fixed palette, duplicate, delete.

**Connections**
- Drag from any shape's edge handle to another shape to create an arrow.
- Arrow styles: solid, dashed, bidirectional, no arrowhead.
- Optional label on the arrow (e.g. "gRPC", "write path", "10k rps").
- Arrows reroute automatically when shapes move.

**Freeform drawing**
- Pen with a few thicknesses and colors.
- Eraser.
- Straight line, rectangle, ellipse as quick sketch primitives.
- Freehand strokes are normal canvas objects: selectable, movable, deletable.

**General canvas tools**
- Select, multi-select (marquee + shift-click), move, group.
- Undo / redo, per-user.
- Copy/paste, snap-to-grid toggle, alignment guides.
- Zoom to fit, reset view.
- Export the board as PNG.

## 3. Real-time collaboration

- Any number of participants edit the same board simultaneously; changes appear instantly.
- Live cursors with each person's name and color.
- Presence list showing who's connected.
- Selection highlights so you can see what someone else is manipulating.
- Late joiners load the current board state, then receive live updates.
- Edits are merged conflict-free, so two people working on different parts never overwrite
  each other; simultaneous edits to the same shape settle on last-write.
- Reconnects automatically after a dropped network, re-syncing missed changes.

## 4. Session management

- Interviewer dashboard: list of sessions with title, candidate name, date, status
  (draft / live / completed).
- Each session stores: title, role being interviewed for, private interviewer notes,
  the board, and participant list.
- Private notes panel visible only to the interviewer during the live session.
- Read-only replay/review of a completed board after the interview.
- Link can be revoked or expired.

## 5. Access rules

- Interviewer accounts are authenticated.
- Candidates join anonymously via the link token — no signup.
- Only people holding the link can read or edit that board.
- Interviewer-only actions: create/end session, revoke link, private notes,
  remove a participant, delete the board.

## 6. Screens

1. Sign in
2. Session dashboard (list + create)
3. Session setup (title, role, template)
4. Join screen (name entry from the link)
5. Board (canvas, palette, toolbar, presence bar, notes panel)
6. Session review (read-only board + notes)

## 7. Technical notes

- Frontend: React on TanStack Start; canvas rendered with a dedicated whiteboard engine
  handling shapes, arrows, and freehand strokes in one scene graph.
- Backend: Lovable Cloud — auth for interviewers, database for sessions/boards/participants,
  realtime channels for cursor + document sync.
- Board state persisted as a document blob plus incremental updates, snapshotted
  periodically so reloads are fast.
- Row-level security scopes sessions to their owner; anonymous access is granted by a
  signed link token validated server-side.

## 8. Suggested build order

1. Design system + dashboard + session creation with shareable link.
2. Board canvas with shapes, labels, arrows, select/move.
3. Freeform drawing tools.
4. Real-time sync: presence, cursors, shared document.
5. Persistence, review mode, export, link revocation.

## Open questions

- Should candidates see the interviewer's palette, or a reduced one?
- Do you want a built-in timer and prompt/question panel on the board?
- Is video/audio needed in-app, or will you run it over Zoom/Meet alongside?
