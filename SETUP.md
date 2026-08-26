# DRS Event Intelligence Dashboard — Setup & Deployment

A live, dual-view (India / UK & Europe) events intelligence dashboard for Recykal,
powered directly by Google Sheets via Google Apps Script.

---

## PART 1 — Architecture

```
Google Sheets (live)          Apps Script backend            Browser (Web App)
┌───────────────────┐         ┌─────────────────────┐        ┌────────────────────┐
│ India workbook    │  read   │ Code.gs             │ JSON   │ Index.html         │
│  └ "Events List"  │────────▶│  getDashboardData() │───────▶│ Styles.html (CSS)  │
│ UK/Europe workbook│         │  getIndiaEvents()   │google. │ Scripts.html (JS)  │
│  └ "Sheet2"       │         │  getEuropeEvents()  │script. │  • KPIs            │
└───────────────────┘         │ Helpers.gs          │ run    │  • Chart.js charts │
                              │  parse/normalise    │        │  • Filters/table   │
                              └─────────────────────┘        │  • Detail drawer   │
                                                             └────────────────────┘
```

- **Single source of truth:** the two Google Sheets. The code never stores event data.
- **On every load and every 60 seconds**, the browser calls one server function
  (`getDashboardData`) via `google.script.run`. The server re-reads the sheets,
  parses them into clean JSON, and returns both datasets in one round-trip.
- **All filtering, charting and table rendering is client-side**, so filter changes
  are instant and don't hit the server.
- **Fields are located by header name**, not column number, so columns can be moved.
- **Defensive parsing** handles text dates, date ranges, `"7.5 currently"`-style
  scores, blank rows, an unlabelled UK column, and missing values (shown as `—`).
- **No spreadsheet IDs reach the browser** — all sheet access is server-side.
- Adding an event, changing a status/score/date etc. in the sheet appears
  automatically on the next refresh. **No redeployment is ever needed for data changes.**

Files:
| File | Purpose |
|------|---------|
| `Code.gs` | CONFIG, web-app entry point, `getDashboardData`, `getIndiaEvents`, `getEuropeEvents` |
| `Helpers.gs` | Reusable parsing: sheet reading, header mapping, dates, numbers, classifiers |
| `Index.html` | Page layout (nav, KPIs, filters, charts, tables, drawer, loader, footer) |
| `Styles.html` | All CSS (brand colours as CSS variables) |
| `Scripts.html` | All client JavaScript (refresh loop, charts, filters, drawer, presentation mode) |

---

## PART 2 — Google Sheet Preparation

You currently have two Excel files. Convert each to a Google Sheet:

1. Go to **drive.google.com** and sign in with your Recykal Google account.
2. Click **New → File upload** and upload `DRS Event Target List India.xlsx`.
3. In Drive, **double-click** the uploaded file to open it, then choose
   **File → Save as Google Sheets**. This creates a native Google Sheet copy.
   (You can delete or keep the original `.xlsx` — the dashboard only uses the Google Sheet.)
4. Repeat steps 2–3 for `UK Events.xlsx`.
5. Confirm the tab names:
   - India Google Sheet must contain a tab named exactly **`Events List`**.
   - UK/Europe Google Sheet must contain a tab named exactly **`Sheet2`**.
   (Tab names are case-sensitive. If yours differ, either rename the tab or update
   `CONFIG` in `Code.gs`.)
6. **Get each Spreadsheet ID** from its URL. The ID is the long code between `/d/` and `/edit`:
   ```
   https://docs.google.com/spreadsheets/d/1AbCdEf...THIS_IS_THE_ID...XyZ/edit#gid=0
                                          └──────────── Spreadsheet ID ───────────┘
   ```
   Copy the ID for the India sheet and the ID for the UK/Europe sheet — you'll paste
   them into `CONFIG`.

You do **not** need to reshape columns, add scores, or clean the data. The parser
handles the sheets as they are.

---

## PART 3 — Apps Script Files

Complete, copy-paste-ready files live in this repository:

- **`Code.gs`**  — backend + configuration
- **`Helpers.gs`** — parsing / utility functions
- **`Index.html`** — layout
- **`Styles.html`** — CSS
- **`Scripts.html`** — client JavaScript

Copy each file's contents into the matching file in your Apps Script project (Part 4).

---

## PART 4 — Setup Instructions (step by step)

**1. Create the Apps Script project**
   - Go to **script.google.com** → **New project**.
   - Rename it (top-left) to `DRS Event Intelligence`.

**2. Create and paste each file**
   Apps Script starts with one file called `Code.gs`.
   - Select all in the default `Code.gs` and replace it with the contents of **`Code.gs`** from this repo.
   - Click the **＋** next to *Files* → **Script** → name it `Helpers` → paste **`Helpers.gs`**.
   - Click **＋** → **HTML** → name it `Index` → paste **`Index.html`**.
   - Click **＋** → **HTML** → name it `Styles` → paste **`Styles.html`**.
   - Click **＋** → **HTML** → name it `Scripts` → paste **`Scripts.html`**.
   > File names must be exactly `Index`, `Styles`, `Scripts` (no `.html` typed — Apps Script adds it).

**3. Paste the India Spreadsheet ID**
   In `Code.gs`, in the `CONFIG` block, replace `PASTE_INDIA_GOOGLE_SHEET_ID_HERE`
   with your India Google Sheet ID (from Part 2). Keep the quotes.

**4. Paste the UK/Europe Spreadsheet ID**
   In the same `CONFIG` block, replace `PASTE_UK_EUROPE_GOOGLE_SHEET_ID_HERE`
   with your UK/Europe Google Sheet ID.
   > These two lines are the **only** things you normally edit.

**5. Permissions required**
   - Click **Save** (💾).
   - Click **Run** (▶) on the `getDashboardData` function once.
   - Google will ask you to **authorise**: choose your Recykal account →
     *Advanced* → *Go to DRS Event Intelligence (unsafe)* → **Allow**.
     (This is normal for your own script; it needs permission to read your Sheets.)
   - Required scope: read access to Google Sheets you own/can access.

**6. How to test (before deploying)**
   - With authorisation done, in the editor pick `getIndiaEvents` → **Run** →
     open **Execution log**: you should see no errors.
   - Do the same for `getEuropeEvents`.
   - If you see *"Spreadsheet ID … is not set"* or *"Sheet tab … not found"*,
     re-check the IDs and tab names in `CONFIG`.

**7. Deploy as a Web App**
   - Top-right **Deploy → New deployment**.
   - Click the gear → **Web app**.
   - **Description:** `DRS Event Intelligence v1`
   - **Execute as:** **Me** (your Recykal account) — so it can read the Sheets.
   - **Who has access:** **Anyone within [your Recykal Workspace]** (recommended).
   - Click **Deploy**, authorise if prompted, and copy the **Web app URL**.
   - Open that URL — the dashboard loads.

**8. Deployment security settings — which to choose**
   - ✅ **Recommended:** *Execute as: Me* + *Access: Anyone within your organisation*.
     Colleagues open the link with their Recykal Google login; outsiders cannot.
   - ⚠️ *Access: Only myself* — only you can view it (good for private testing).
   - 🚫 **Do NOT choose** *Anyone / Anyone with the link (outside the org)* — that would
     expose the dashboard on the public internet.
   > To update code later, **Deploy → Manage deployments → Edit (✏) → Version: New version → Deploy**.
   > Data/row changes never need redeployment — only code changes do.

---

## PART 5 — Testing Checklist

- [ ] **India data loads** — KPI cards + charts + table populate on open.
- [ ] **UK/Europe data loads** — switch to the UK & Europe tab; content populates.
- [ ] **Filters work** — search, month, priority/country, status/entry, etc. narrow results.
- [ ] **Reset Filters** clears every control and restores full data.
- [ ] **Charts work** — all charts render; scatter tooltip shows Event/Date/Priority/scores/use.
- [ ] **Table works** — sortable columns of data appear, duplicates flagged with `DUP`.
- [ ] **Detail drawer works** — click any row/upcoming card → right-side drawer opens with
      all long-text fields; Sources/Website links are clickable; ✕ / overlay / Esc closes it.
- [ ] **Sheet edits appear automatically** — change a status or score in the Google Sheet,
      wait ≤60s (or click Refresh) → dashboard reflects it. No redeploy.
- [ ] **Manual Refresh** — the Refresh Data button spins and updates "Last synced".
- [ ] **60-second auto-refresh** — leave it open; "Last synced" updates each minute.
- [ ] **Presentation Mode** — hides filters, enlarges charts, keeps KPIs + nav.
- [ ] **Responsiveness** — resize to laptop/tablet widths; charts don't overflow,
      table scrolls horizontally only when needed.
- [ ] **Graceful errors** — if a sheet is unreachable, a banner shows and the other
      dataset still works; last good data is retained.

---

## PART 6 — Future Expansion Notes (not built in V1)

The architecture is intentionally layered so new modules slot in without a rebuild:

| Future field/module | Where it plugs in |
|---|---|
| **Owner / Action Owner** | Add the column to the sheet → add one `col('Owner')` line + field in `getIndiaEvents()` (Code.gs). It flows through as `e.owner`; add a table column in `Index.html`/`Scripts.html` and a filter option. |
| **Next Action** | Same pattern — map the header in the getter, add a `detailItem('Next Action', e.nextAction)` line in the drawer. |
| **Action Deadline** | Map with `parseDateFlexible` (reuse the existing date engine), then reuse `daysAway()` for an "overdue / due-in-N-days" indicator. |
| **Budget** | Add `budget: extractNumber(cellRaw(row, col('Budget')))`; add a KPI via the existing `kpi()` helper and a chart via `drawChart()`. |
| **Government pipeline / Brand pipeline** | New Apps Script getters (e.g. `getGovPipeline()`) reading a new tab; add a new nav button + a new `<main class="view">` block; wire it in `wireNav()` and `renderActiveView()`. The refresh loop and chart manager already generalise. |
| **Event outcome / ROI** | New fields on the event object + a dedicated view or drawer section; ROI can be computed client-side from budget + outcome using the same client-side pattern as scores. |

Guiding rules for later work: **map by header name**, **return JSON objects** (never raw
2D arrays), **classify on the client**, and **register new charts through `drawChart()`**
so they destroy/rebuild cleanly on refresh.

---

_Recykal | DRS Event Intelligence • Data source: Live Google Sheets_
