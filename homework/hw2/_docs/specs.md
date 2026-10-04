# TableHop - Product Specification

## 1. Overview & Vision
**TableHop** is a modern, responsive restaurant waitlist management tool designed to streamline front-of-house operations, eliminate crowded entryways, and improve guest communication. It enables restaurant hosts to seamlessly manage walk-in queues, match parties to available tables, trigger simulated SMS arrival alerts, and provide guests with real-time mobile queue tracking.

---

## 2. Personas & Use Cases

### 2.1 Restaurant Host / Maitre D'
* **Quick Walk-in Intake:** Quickly add walk-in guests with name, party size, phone number, and special seating requests.
* **Intelligent Wait Estimation:** View auto-suggested wait times based on queue depth, with the flexibility to manually override.
* **Queue Lifecycle Management:** Update party status (`Waiting` ➔ `Notified` ➔ `Seated` ➔ `Cancelled` / `No-Show`).
* **Table Matching:** Seat parties at appropriately sized available tables and release tables when guests depart.
* **Simulated Notifications:** Notify guests via in-app simulated SMS alerts with a full notification log audit trail.
* **Operational Visibility:** Monitor real-time KPIs (Active Queue, Average Wait Time, Total Parties Seated Today).

### 2.2 Walk-in Guest
* **Live Status Tracker (`/waitlist/:id`):** Access a mobile-friendly tracking link to see their live position in line and estimated wait time.
* **Self-Service Leave Line:** Cancel their spot immediately if plans change, freeing up capacity for other guests.

---

## 3. Scope & Phasing

### Phase 1: Homework 2 MVP (Current Scope)
1. **Host Dashboard:**
   * Waitlist queue table with live status badges.
   * Add Party modal with auto-suggested wait time calculation (~10 min per waiting party) and manual override.
   * 3 KPI summary cards: Active Parties Waiting, Average Quoted Wait Time, Total Seated Today.
2. **Table Inventory & Matching:**
   * Pre-seeded tables (e.g., T1–T6 with 2-top, 4-top, and 6-top capacities).
   * Seating modal to assign an available table fitting the party size.
   * "Clear Table" action to return occupied tables to available status.
3. **Simulated Notification Engine:**
   * "Notify Guest" action triggers simulated SMS dispatch.
   * In-app Notification Log drawer displaying recipient phone, message text, and timestamp.
4. **Guest Tracker Page (`/waitlist/:id`):**
   * Mobile-first view showing party name, party size, current status, queue position (e.g., "#2 in line"), and estimated wait time.
   * One-click "Leave Line" cancellation button.

### Phase 2: Future Roadmap (Deferred)
* Real SMS delivery via Twilio integration.
* Interactive 2D drag-and-drop table floor plan layout.
* Historical wait-time machine learning prediction and shift-turnover analytics.
* Multi-station host sync via WebSockets.

---

## 4. Data Models

### 4.1 Party (Waitlist Entry)
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string (UUID) | Unique identifier |
| `guest_name` | string | Name of primary guest |
| `party_size` | integer | Number of guests (1–12) |
| `phone_number` | string | Contact phone number |
| `notes` | string (optional) | Special requests (e.g., high chair, booth, birthday) |
| `quoted_wait_min` | integer | Estimated wait time in minutes |
| `status` | string (enum) | `waiting`, `notified`, `seated`, `cancelled`, `no_show` |
| `table_id` | string (optional) | Assigned table identifier when seated |
| `created_at` | datetime | Timestamp when party was added |
| `notified_at` | datetime (optional) | Timestamp when notification was sent |
| `seated_at` | datetime (optional) | Timestamp when party was seated |

### 4.2 Table
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string | Unique table identifier (e.g., `T1`, `T2`) |
| `name` | string | Display label (e.g., "Table 1 (Booth)") |
| `capacity` | integer | Maximum seating capacity (2, 4, 6) |
| `status` | string (enum) | `available`, `occupied` |
| `current_party_id` | string (optional) | ID of seated party |

### 4.3 Notification Log Entry
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string (UUID) | Unique log ID |
| `party_id` | string | Referenced party ID |
| `phone_number` | string | Target phone number |
| `message` | string | Content of simulated SMS |
| `sent_at` | datetime | Timestamp when message was triggered |

---

## 5. API Specification (REST / OpenAPI)

### Waitlist Endpoints
* `GET /api/waitlist` - List all parties (supports filter by `status`).
* `POST /api/waitlist` - Create a new party.
* `GET /api/waitlist/{party_id}` - Retrieve party details (used by guest tracker).
* `PATCH /api/waitlist/{party_id}/status` - Update party status (`waiting`, `notified`, `seated`, `cancelled`, `no_show`).
* `POST /api/waitlist/{party_id}/notify` - Trigger simulated notification and update status to `notified`.
* `POST /api/waitlist/{party_id}/cancel` - Self-service cancellation by guest or host.

### Table Endpoints
* `GET /api/tables` - List all tables and occupancy statuses.
* `POST /api/tables/{table_id}/seat` - Seat a party at a table (payload: `{ party_id }`).
* `POST /api/tables/{table_id}/clear` - Free an occupied table.

### Operations & Analytics
* `GET /api/notifications` - Retrieve list of simulated notifications.
* `GET /api/analytics/summary` - Get KPI metrics (`active_waiting`, `avg_wait_min`, `total_seated_today`).

---

## 6. Frontend Architecture & Design System
* **Framework:** React + Vite (TypeScript).
* **Styling:** Tailwind CSS with a clean, dark-mode slate & amber hospitality aesthetic.
* **Layout:**
  * **Top Bar:** TableHop brand, system clock, notification center drawer toggle.
  * **KPI Bar:** 3 metric summary cards.
  * **Main Content Area:** Split layout — Active Waitlist Queue (70%) + Table Management & Floor Status (30%).
  * **Guest View (`/waitlist/:id`):** Dedicated standalone route formatted for mobile screens.
* **State Management:** Centralized API service layer (`frontend/src/services/api.ts`) designed to run in Mock Mode initially, then switch to the live FastAPI backend via `VITE_API_URL`.

---

## 7. Backend Architecture
* **Framework:** FastAPI (Python 3.11+).
* **Package Management:** `uv`.
* **Database:**
  * Phase 1 Prototype: In-memory dictionary store.
  * Phase 1 Production: SQLite with SQLAlchemy ORM.
* **Testing:** Pytest with HTTP test client covering status transitions, table capacity rules, and cancellation flows.
