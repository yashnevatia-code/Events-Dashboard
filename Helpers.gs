/**
 * ============================================================================
 *  RECYKAL — DRS EVENT INTELLIGENCE DASHBOARD
 *  Server-side helper / parsing utilities
 * ----------------------------------------------------------------------------
 *  Pure, reusable functions: sheet reading, header mapping, date normalisation,
 *  numeric extraction, blank handling and JSON-safe conversion. Keeping these
 *  here (separate from Code.gs) makes it easy to add future modules without
 *  touching the dashboard wiring.
 * ============================================================================
 */

/* ---------------------------------------------------------------------------
 * SHEET READING
 * ------------------------------------------------------------------------- */

/**
 * Open a spreadsheet + tab and return a normalised grid:
 *   { headers: [..], rows: [[raw..], ..], display: [[text..], ..] }
 * - `rows` holds RAW values (getValues) — real Date objects survive here, which
 *   the date parser needs for accurate, timezone-safe day handling.
 * - `display` holds DISPLAY values (getDisplayValues) — this is how Google Sheets
 *   renders a cell, so multi-select dropdown chips come back as readable text
 *   (e.g. "Exhibit, Speak") instead of an opaque object. Text/dropdown fields
 *   should be read from `display`; dates from `rows`.
 * - `rows[i]` and `display[i]` stay index-aligned after blank-row trimming.
 * - Dynamically detects the populated range (no hard-coded row/col counts).
 */
function readSheetGrid(spreadsheetId, sheetName) {
  if (!spreadsheetId || spreadsheetId.indexOf('PASTE_') === 0) {
    throw new Error('Spreadsheet ID for "' + sheetName +
      '" is not set. Open Code.gs and paste the real ID into CONFIG.');
  }

  var ss = SpreadsheetApp.openById(spreadsheetId);
  var sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    throw new Error('Sheet tab "' + sheetName + '" was not found in the workbook. ' +
      'Check CONFIG spelling — tab names are case-sensitive.');
  }

  var lastRow = sheet.getLastRow();
  var lastCol = sheet.getLastColumn();
  if (lastRow < 2 || lastCol < 1) {
    return { headers: [], rows: [], display: [] };
  }

  var range = sheet.getRange(1, 1, lastRow, lastCol);
  var values = range.getValues();
  var displays = range.getDisplayValues();
  var headers = values[0];

  // Trim rows that are entirely blank, keeping raw + display index-aligned.
  var rows = [];
  var display = [];
  for (var r = 1; r < values.length; r++) {
    if (isBlankRow(values[r])) continue;
    rows.push(values[r]);
    display.push(displays[r]);
  }

  return { headers: headers, rows: rows, display: display };
}


/* ---------------------------------------------------------------------------
 * HEADER MAPPING  (locate columns by name, not position)
 * ------------------------------------------------------------------------- */

/**
 * Build a lookup of normalised-header -> column index.
 * Empty / unlabelled header columns are skipped (defensive against the
 * UK sheet's blank column).
 */
function buildHeaderIndex(headers) {
  var index = {};
  (headers || []).forEach(function (h, i) {
    var key = normalizeHeader(h);
    if (key === '') return;              // skip blank/unlabelled columns
    if (!(key in index)) index[key] = i; // first occurrence wins
  });
  return index;
}

/** Resolve a desired header name to a column index, or -1 if absent. */
function resolveColumn(headerIndex, desiredName) {
  var key = normalizeHeader(desiredName);
  if (key in headerIndex) return headerIndex[key];

  // Fallback: forgiving contains-match so minor wording drift still resolves.
  var keys = Object.keys(headerIndex);
  for (var i = 0; i < keys.length; i++) {
    if (keys[i].indexOf(key) !== -1 || key.indexOf(keys[i]) !== -1) {
      return headerIndex[keys[i]];
    }
  }
  return -1;
}

/**
 * Resolve the first header that matches any name in `names` (in priority order),
 * returning its column index or -1 if none match. Used for header aliases such
 * as "Event Type / Industry" | "Event Type" | "Type" | "Industry", or
 * "Organiser" | "Organisers" | "Organizer" | "Organizers". Exact normalised
 * matches are preferred across all aliases before any fuzzy contains-match.
 */
function resolveColumnAlias(headerIndex, names) {
  // Pass 1: exact normalised match on any alias.
  for (var i = 0; i < names.length; i++) {
    var key = normalizeHeader(names[i]);
    if (key in headerIndex) return headerIndex[key];
  }
  // Pass 2: fall back to the forgiving contains-match, alias by alias.
  for (var j = 0; j < names.length; j++) {
    var idx = resolveColumn(headerIndex, names[j]);
    if (idx !== -1) return idx;
  }
  return -1;
}

/** Normalise a header for matching: lowercase, collapse spaces/punctuation. */
function normalizeHeader(h) {
  if (h === null || h === undefined) return '';
  return String(h)
    .replace(/ /g, ' ')       // non-breaking spaces
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')   // punctuation -> space
    .trim();
}


/* ---------------------------------------------------------------------------
 * CELL / BLANK HANDLING
 * ------------------------------------------------------------------------- */

/** Raw cell value (or '' when the column is missing). */
function cellRaw(row, colIndex) {
  if (colIndex < 0 || colIndex >= row.length) return '';
  var v = row[colIndex];
  return (v === null || v === undefined) ? '' : v;
}

/** Cleaned text for a cell: trims, normalises whitespace, '' when empty. */
function cellText(row, colIndex) {
  var v = cellRaw(row, colIndex);
  if (v instanceof Date) return toIsoDate(v);
  var s = String(v).replace(/ /g, ' ').trim();
  return s;
}

/**
 * Cleaned DISPLAY text for a cell (from getDisplayValues). Use this for
 * text / dropdown / multi-select fields so the value comes back exactly as
 * Google Sheets renders it. Missing column or blank cell -> ''.
 */
function cellDisplay(displayRow, colIndex) {
  if (!displayRow || colIndex < 0 || colIndex >= displayRow.length) return '';
  var v = displayRow[colIndex];
  if (v === null || v === undefined) return '';
  return String(v).replace(/ /g, ' ').trim();
}

/** True when every cell in a row is empty. */
function isBlankRow(row) {
  for (var i = 0; i < row.length; i++) {
    var v = row[i];
    if (v !== null && v !== undefined && String(v).trim() !== '') return false;
  }
  return true;
}


/* ---------------------------------------------------------------------------
 * NUMERIC EXTRACTION
 * ------------------------------------------------------------------------- */

/**
 * Pull the leading numeric value out of a cell.
 *  90          -> 90
 *  "83"        -> 83
 *  "7.5 currently" -> 7.5
 *  ""/text     -> null   (never guesses or fabricates)
 */
function extractNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  if (typeof value === 'number' && isFinite(value)) return value;
  var m = String(value).replace(',', '.').match(/-?\d+(\.\d+)?/);
  if (!m) return null;
  var n = parseFloat(m[0]);
  return isFinite(n) ? n : null;
}


/* ---------------------------------------------------------------------------
 * DATE NORMALISATION  (robust, JSON-safe)
 * ------------------------------------------------------------------------- */

var MONTHS = {
  jan: 0, january: 0, feb: 1, february: 1, mar: 2, march: 2, apr: 3, april: 3,
  may: 4, jun: 5, june: 5, jul: 6, july: 6, aug: 7, august: 7, sep: 8, sept: 8,
  september: 8, oct: 9, october: 9, nov: 10, november: 10, dec: 11, december: 11
};

/**
 * Parse a cell that may be a Date object, an ISO/loose date string, or a
 * date range in text form. Returns a JSON-safe descriptor:
 *   { startISO: 'YYYY-MM-DD'|'', endISO: 'YYYY-MM-DD'|'', display: 'human' }
 *
 * Handles, among others:
 *   Date(2026-09-09)          -> 09 Sep 2026
 *   "16-17 Sep 2026"          -> 16–17 Sep 2026
 *   "September 23–25, 2026"   -> 23–25 Sep 2026
 *   "9 Sep 2026"              -> 09 Sep 2026
 *   ""                        -> { '', '', '—' }
 * Never returns Excel/Sheets serial numbers.
 */
function parseDateFlexible(value) {
  var empty = { startISO: '', endISO: '', display: '—' };
  if (value === null || value === undefined || value === '') return empty;

  // 1) Native Date object from Sheets.
  if (value instanceof Date && !isNaN(value.getTime())) {
    var iso = toIsoDate(value);
    return { startISO: iso, endISO: '', display: formatHuman(value) };
  }

  var s = String(value).replace(/ /g, ' ').trim();
  if (!s) return empty;

  // 2) Pure numeric string that is clearly NOT a serial we trust -> keep as text.
  //    (We deliberately do not convert bare serial numbers to dates.)

  // 3) Range like "16-17 Sep 2026" / "September 23–25, 2026".
  var range = parseDateRange(s);
  if (range) return range;

  // 4) Single loose date ("9 Sep 2026", "2026-09-09", "Sep 9 2026", etc.).
  var single = parseSingleDate(s);
  if (single) {
    return {
      startISO: toIsoDate(single),
      endISO: '',
      display: formatHuman(single)
    };
  }

  // 5) Unparseable: preserve original text so nothing is lost or invented.
  return { startISO: '', endISO: '', display: s };
}

/** Try "D–D Mon YYYY" or "Month D–D, YYYY" style ranges. */
function parseDateRange(s) {
  var dash = '[\\-\\u2013\\u2014]'; // -, –, —

  // Pattern A: "16-17 Sep 2026"  (day range, then month, year)
  var a = new RegExp('^(\\d{1,2})\\s*' + dash + '\\s*(\\d{1,2})\\s+([A-Za-z]{3,9})\\.?\\s+(\\d{4})$');
  var mA = s.match(a);
  if (mA) {
    var mo = MONTHS[mA[3].toLowerCase()];
    if (mo !== undefined) {
      var y = +mA[4];
      var d1 = new Date(y, mo, +mA[1]);
      var d2 = new Date(y, mo, +mA[2]);
      return rangeDescriptor(d1, d2);
    }
  }

  // Pattern B: "September 23–25, 2026"  (month, day range, year)
  var b = new RegExp('^([A-Za-z]{3,9})\\.?\\s+(\\d{1,2})\\s*' + dash + '\\s*(\\d{1,2}),?\\s+(\\d{4})$');
  var mB = s.match(b);
  if (mB) {
    var mo2 = MONTHS[mB[1].toLowerCase()];
    if (mo2 !== undefined) {
      var y2 = +mB[4];
      var d1b = new Date(y2, mo2, +mB[2]);
      var d2b = new Date(y2, mo2, +mB[3]);
      return rangeDescriptor(d1b, d2b);
    }
  }

  // Pattern C: cross-month "16 Sep – 18 Oct 2026"
  var c = new RegExp('^(\\d{1,2})\\s+([A-Za-z]{3,9})\\.?\\s*' + dash +
                     '\\s*(\\d{1,2})\\s+([A-Za-z]{3,9})\\.?\\s+(\\d{4})$');
  var mC = s.match(c);
  if (mC) {
    var mo3a = MONTHS[mC[2].toLowerCase()];
    var mo3b = MONTHS[mC[4].toLowerCase()];
    if (mo3a !== undefined && mo3b !== undefined) {
      var y3 = +mC[5];
      var d1c = new Date(y3, mo3a, +mC[1]);
      var d2c = new Date(y3, mo3b, +mC[3]);
      return rangeDescriptor(d1c, d2c);
    }
  }
  return null;
}

function rangeDescriptor(d1, d2) {
  return {
    startISO: toIsoDate(d1),
    endISO: toIsoDate(d2),
    display: formatHumanRange(d1, d2)
  };
}

/** Parse a single loose date without relying on Excel serials. */
function parseSingleDate(s) {
  // ISO first: 2026-09-09
  var iso = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
  if (iso) {
    var d = new Date(+iso[1], +iso[2] - 1, +iso[3]);
    if (!isNaN(d.getTime())) return d;
  }

  // "9 Sep 2026" or "9 September 2026"
  var dmy = s.match(/^(\d{1,2})\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})$/);
  if (dmy) {
    var mo = MONTHS[dmy[2].toLowerCase()];
    if (mo !== undefined) return new Date(+dmy[3], mo, +dmy[1]);
  }

  // "Sep 9, 2026" / "September 9 2026"
  var mdy = s.match(/^([A-Za-z]{3,9})\.?\s+(\d{1,2}),?\s+(\d{4})$/);
  if (mdy) {
    var mo2 = MONTHS[mdy[1].toLowerCase()];
    if (mo2 !== undefined) return new Date(+mdy[3], mo2, +mdy[2]);
  }

  // dd/mm/yyyy or dd-mm-yyyy (assume day-first for UK/India context)
  var num = s.match(/^(\d{1,2})[\/\-.](\d{1,2})[\/\-.](\d{2,4})$/);
  if (num) {
    var yr = +num[3]; if (yr < 100) yr += 2000;
    var d3 = new Date(yr, +num[2] - 1, +num[1]);
    if (!isNaN(d3.getTime())) return d3;
  }
  return null;
}

/** Date -> 'YYYY-MM-DD' in the script timezone (JSON-safe, stable). */
function toIsoDate(d) {
  if (!(d instanceof Date) || isNaN(d.getTime())) return '';
  return Utilities.formatDate(d, Session.getScriptTimeZone() || 'GMT', 'yyyy-MM-dd');
}

/** Date -> '09 Sep 2026'. */
function formatHuman(d) {
  if (!(d instanceof Date) || isNaN(d.getTime())) return '—';
  return Utilities.formatDate(d, Session.getScriptTimeZone() || 'GMT', 'dd MMM yyyy');
}

/** Two dates -> '09–11 Sep 2026' (collapses shared month/year). */
function formatHumanRange(d1, d2) {
  if (isNaN(d1.getTime())) return formatHuman(d2);
  if (isNaN(d2.getTime())) return formatHuman(d1);
  var tz = Session.getScriptTimeZone() || 'GMT';
  var sameMonth = d1.getFullYear() === d2.getFullYear() && d1.getMonth() === d2.getMonth();
  var sameYear = d1.getFullYear() === d2.getFullYear();
  if (sameMonth) {
    return Utilities.formatDate(d1, tz, 'dd') + '–' +
           Utilities.formatDate(d2, tz, 'dd MMM yyyy');
  }
  if (sameYear) {
    return Utilities.formatDate(d1, tz, 'dd MMM') + '–' +
           Utilities.formatDate(d2, tz, 'dd MMM yyyy');
  }
  return formatHuman(d1) + '–' + formatHuman(d2);
}

/** Combine India's separate Start/End columns into one display string. */
function buildDateDisplay(startInfo, endInfo) {
  var s = startInfo.startISO ? new Date(startInfo.startISO) : null;
  var e = endInfo.startISO ? new Date(endInfo.startISO) : null;
  if (s && e && startInfo.startISO !== endInfo.startISO) {
    return formatHumanRange(s, e);
  }
  if (s) return formatHuman(s);
  if (startInfo.display && startInfo.display !== '—') return startInfo.display;
  return '—';
}


/* ---------------------------------------------------------------------------
 * DOMAIN CLASSIFIERS  (dashboard-derived, clearly NOT source data)
 * ------------------------------------------------------------------------- */

/* ---- INDIA: status normalisation (single canonical implementation) -------- */

/**
 * Normalise a Status value into a comparison KEY only:
 *   'In Progress' / ' in  progress ' / 'IN PROGRESS' -> 'in progress'
 * Lowercase, trim, collapse internal whitespace. This is for KPI/filter
 * comparisons; the ORIGINAL source label is what we display to users.
 */
function normalizeStatusKey(text) {
  if (text === null || text === undefined) return '';
  return String(text).replace(/ /g, ' ')
    .replace(/\s+/g, ' ').trim().toLowerCase();
}

/* ---- INDIA: Strategic Use multi-select parsing (single canonical impl) ----- */

// The recognised Strategic Use selections. Order defines display order.
var STRATEGIC_USE_VALUES = ['Delegation Only', 'Exhibit', 'Speak'];

/**
 * Parse a multi-select Strategic Use cell into structured, reliable data.
 * The cell may hold one or several selections in any common representation:
 *   "Exhibit, Speak"  |  "Speak\nExhibit"  |  "Delegation Only; Speak"  |  "Exhibit / Speak"
 * Returns:
 *   {
 *     values: ['Exhibit','Speak'],   // recognised selections, canonical labels
 *     canSpeak: true,                // contains Speak
 *     canExhibit: true,              // contains Exhibit
 *     delegationOnly: false          // contains Delegation Only
 *   }
 * Unrecognised tokens are preserved in `values` as-is (so a future option still
 * appears), but no tags are derived or inferred from other columns.
 */
function parseStrategicUse(text) {
  var out = { values: [], canSpeak: false, canExhibit: false, delegationOnly: false };
  if (text === null || text === undefined || String(text).trim() === '') return out;

  // Split on commas, semicolons, slashes, pipes and line breaks.
  var tokens = String(text).split(/[,;/|\n\r]+/);
  tokens.forEach(function (tok) {
    var t = tok.replace(/ /g, ' ').replace(/\s+/g, ' ').trim();
    if (!t) return;
    var lower = t.toLowerCase();
    var canonical = t; // default: keep the token as written
    if (lower === 'speak' || lower.indexOf('speak') !== -1) { canonical = 'Speak'; out.canSpeak = true; }
    else if (lower.indexOf('delegation') !== -1) { canonical = 'Delegation Only'; out.delegationOnly = true; }
    else if (lower.indexOf('exhibit') !== -1) { canonical = 'Exhibit'; out.canExhibit = true; }
    if (out.values.indexOf(canonical) === -1) out.values.push(canonical);
  });
  return out;
}

/** Classify UK entry text into Free | Paid | Mixed | Other. */
function classifyEntryType(text) {
  if (!text) return 'Other';
  var t = String(text).toLowerCase();
  var hasFree = t.indexOf('free') !== -1;
  var hasPaid = t.indexOf('paid') !== -1 || t.indexOf('€') !== -1 ||
                t.indexOf('£') !== -1 || /\bfee\b/.test(t) || t.indexOf('ticket') !== -1 ||
                t.indexOf('pass') !== -1 && t.indexOf('free') === -1;
  if (hasFree && hasPaid) return 'Mixed';
  if (hasFree) return 'Free';
  if (hasPaid) return 'Paid';
  return 'Other';
}

/** Whether a UK record counts as RVM-relevant (display flag OR strong language). */
function isRvmRelevant(rvmDisplay, relevanceText) {
  var d = String(rvmDisplay || '').toLowerCase();
  if (d.indexOf('yes') !== -1) return true;
  var r = String(relevanceText || '').toLowerCase();
  if (!r) return false;
  var strong = ['rvm', 'reverse vending', 'deposit return', 'drs', 'drct',
                'take-back', 'takeback', 'container return'];
  return strong.some(function (k) { return r.indexOf(k) !== -1; });
}

/**
 * Dashboard-only RVM/business categorisation for UK/Europe events.
 * Keyword logic over Relevance + Theme. This is a classification for grouping,
 * NOT a value read from the sheet, and NOT a score.
 */
function classifyRvmCategory(relevanceText, themeText) {
  var t = (String(relevanceText || '') + ' ' + String(themeText || '')).toLowerCase();
  if (!t.trim()) return 'General / Other';

  if (/(rvm|reverse vending|deposit return|drs|container return|take-?back)/.test(t))
    return 'Direct RVM opportunity';
  if (/(retail|supermarket|convenience|grocery|fmcg|store)/.test(t))
    return 'Retail opportunity';
  if (/(policy|regulat|government|epr|legislat|parliament|defra)/.test(t))
    return 'DRS / Policy opportunity';
  if (/(recycl|waste|circular|resource|sustainab|packaging)/.test(t))
    return 'Recycling / Waste opportunity';
  if (/(technology|iot|automation|ai|robot|digital|innovation)/.test(t))
    return 'Technology opportunity';
  return 'General / Other';
}
