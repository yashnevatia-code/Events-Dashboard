/**
 * ============================================================================
 *  RECYKAL — DRS EVENT INTELLIGENCE DASHBOARD
 *  Backend entry points (Google Apps Script)
 * ----------------------------------------------------------------------------
 *  Google Sheets are the single source of truth. This backend reads the live
 *  sheets on every request, parses them defensively into clean JSON objects,
 *  and hands them to the web app. Nothing about the data is hard-coded here —
 *  rows, statuses, cities, countries and counts are all derived at read time.
 *
 *  You only ever need to edit the two spreadsheet IDs in CONFIG below.
 *  Helper/parsing utilities live in Helpers.gs.
 * ============================================================================
 */

/* ---------------------------------------------------------------------------
 * 1. CONFIGURATION  — the ONLY block you normally need to touch.
 * ------------------------------------------------------------------------- */
const CONFIG = {
  // Both datasets currently live in ONE workbook ("Upcoming Events Dashboard
  // Backend"), so both IDs are the same. If you later split them into two
  // separate workbooks, just change the IDs.

  // India dataset ----------------------------------------------------------
  INDIA_SPREADSHEET_ID: '1KXmRyQtRDB7epcdFFWvMaoXkck76sHccgPQ403TnICI',
  INDIA_SHEET_NAME: 'India DRS Events',

  // UK & Europe dataset ----------------------------------------------------
  EUROPE_SPREADSHEET_ID: '1KXmRyQtRDB7epcdFFWvMaoXkck76sHccgPQ403TnICI',
  EUROPE_SHEET_NAME: 'UK & Europe Events',

  // Frontend auto-refresh cadence (seconds) --------------------------------
  AUTO_REFRESH_SECONDS: 60
};


/* ---------------------------------------------------------------------------
 * 2. WEB APP ENTRY POINT
 * ------------------------------------------------------------------------- */
function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('Recykal — DRS Event Intelligence')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

/**
 * Lets Index.html pull in Styles.html and Scripts.html as separate files.
 * Usage inside Index.html:  <?!= include('Styles'); ?>
 */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}


/* ---------------------------------------------------------------------------
 * 3. PUBLIC SERVER FUNCTIONS  (called from the browser via google.script.run)
 * ------------------------------------------------------------------------- */

/**
 * Single round-trip the frontend uses: returns BOTH datasets plus a server
 * timestamp. One request per refresh keeps things simple and reliable.
 */
function getDashboardData() {
  var out = {
    india: { events: [], error: null },
    europe: { events: [], error: null },
    syncedAt: new Date().toISOString(),
    autoRefreshSeconds: CONFIG.AUTO_REFRESH_SECONDS
  };

  // Each dataset is isolated: one failing sheet must never blank the other.
  try {
    out.india.events = getIndiaEvents();
  } catch (e) {
    out.india.error = String(e && e.message ? e.message : e);
  }
  try {
    out.europe.events = getEuropeEvents();
  } catch (e) {
    out.europe.error = String(e && e.message ? e.message : e);
  }

  return out;
}

/**
 * INDIA — read the `India DRS Events` tab and return clean event objects.
 *
 * Only the retained fields of the revised data model are exposed. Removed
 * fields (Priority, Brand Stakeholders, Delegate Cost, Speaking Route,
 * Demo/Exhibit Route, Strategic Score, Access Score, Confidence) are NOT read
 * or returned, so they can never surface in the UI — the columns can stay in
 * the sheet untouched.
 *
 * Columns are located by HEADER NAME (with aliases), never by fixed position,
 * so reordering columns in Google Sheets does not break the dashboard.
 * Text/dropdown fields are read from DISPLAY values so multi-select Strategic
 * Use comes back as readable text; dates are read from RAW values so day
 * handling stays timezone-safe.
 */
function getIndiaEvents() {
  var grid = readSheetGrid(CONFIG.INDIA_SPREADSHEET_ID, CONFIG.INDIA_SHEET_NAME);
  var headerIndex = buildHeaderIndex(grid.headers);
  var alias = function (names) { return resolveColumnAlias(headerIndex, names); };

  var iEvent     = alias(['Event', 'Event Name']);
  var iStart     = alias(['Start Date']);
  var iEnd       = alias(['End Date']);
  var iCity      = alias(['City / State', 'City/State', 'City']);
  var iType      = alias(['Event Type / Industry', 'Event Type', 'Type', 'Industry']);
  var iScale     = alias(['Scale']);
  var iStatus    = alias(['Status']);
  var iOrganiser = alias(['Organiser', 'Organisers', 'Organizer', 'Organizers']);
  var iGov       = alias(['Government Stakeholders to Target', 'Government Stakeholders']);
  var iUse       = alias(['Strategic Use']);
  var iRelevance = alias(['Relevance / Business Outcome', 'Relevance / Business Outcomes', 'Relevance']);
  var iSources   = alias(['Sources', 'Source']);

  var events = [];
  var seenKeys = {}; // for subtle duplicate flagging (Event + Start Date)

  grid.rows.forEach(function (row, i) {
    if (isBlankRow(row)) return;
    var disp = grid.display[i];

    var eventName = cellDisplay(disp, iEvent);
    if (!eventName) return; // an event with no name is not a real record

    // Dates from RAW values (real Date objects) for accurate parsing.
    var startInfo = parseDateFlexible(cellRaw(row, iStart));
    var endInfo   = parseDateFlexible(cellRaw(row, iEnd));

    // Strategic Use from DISPLAY value (multi-select safe).
    var useText = cellDisplay(disp, iUse);
    var use = parseStrategicUse(useText);

    var obj = {
      event:            eventName,
      startDate:        startInfo.startISO,   // '' when unknown / TBD
      endDate:          endInfo.startISO,
      dateDisplay:      buildDateDisplay(startInfo, endInfo),
      dateText:         cellDisplay(disp, iStart), // raw display text (e.g. "TBD")
      cityState:        cellDisplay(disp, iCity),
      eventType:        cellDisplay(disp, iType),
      scale:            cellDisplay(disp, iScale),
      status:           cellDisplay(disp, iStatus),   // exact source label
      organiser:        cellDisplay(disp, iOrganiser), // '' when blank/absent
      govStakeholders:  cellDisplay(disp, iGov),
      strategicUse:     useText,                       // exact source string
      strategicUseTags: use.values,                    // parsed multi-select
      canSpeak:         use.canSpeak,
      canExhibit:       use.canExhibit,
      delegationOnly:   use.delegationOnly,
      relevance:        cellDisplay(disp, iRelevance),
      sources:          cellDisplay(disp, iSources),
      duplicate:        false
    };

    var key = (obj.event + '||' + obj.startDate).toLowerCase();
    if (seenKeys[key]) obj.duplicate = true;
    seenKeys[key] = true;

    events.push(obj);
  });

  return events;
}

/**
 * UK & EUROPE — read `Sheet2` and return clean objects.
 * Defensive: skips the unlabelled/blank header column, tolerates text dates,
 * date ranges, and missing values. No fake scores are invented.
 */
function getEuropeEvents() {
  var grid = readSheetGrid(CONFIG.EUROPE_SPREADSHEET_ID, CONFIG.EUROPE_SHEET_NAME);
  var headerIndex = buildHeaderIndex(grid.headers); // blank headers already skipped

  var col = function (name) { return resolveColumn(headerIndex, name); };

  var iName    = col('Event Name');
  var iDate    = col('Date');
  var iLocation= col('Location');
  var iCountry = col('Country');
  var iEntry   = col('Entry (Free or Paid)');
  var iProcess = col('Entry Process');
  var iAbout   = col('About the Event');
  var iRvm     = col('RVM Display (Yes/No)');
  var iRvmRel  = col('Relevance to RVM Business');
  var iReps    = col('Planned Representatives');
  var iRegStat = col('Registration Status');
  var iOrganiser = resolveColumnAlias(headerIndex,
                    ['Organiser', 'Organisers', 'Organizer', 'Organizers']); // new; may be -1
  var iWebsite = col('Website Link');
  var iSpeakers= col('List of Speakers');
  var iSponsors= col('List of Sponsors');
  var iTheme   = col('Event Theme / Agenda');
  var iRemarks = col('Remarks');

  var events = [];

  grid.rows.forEach(function (row, i) {
    if (isBlankRow(row)) return;
    var disp = grid.display[i];

    var name = cellText(row, iName);
    if (!name) return;

    var dInfo = parseDateFlexible(cellRaw(row, iDate));

    var entryRaw = cellText(row, iEntry);
    var relevanceRvm = cellText(row, iRvmRel);
    var theme = cellText(row, iTheme);

    events.push({
      eventName:         name,
      startDate:         dInfo.startISO,
      endDate:           dInfo.endISO || dInfo.startISO,
      dateDisplay:       dInfo.display,               // preserves text ranges as-is
      location:          cellText(row, iLocation),
      country:           cellText(row, iCountry),
      entry:             entryRaw,
      entryType:         classifyEntryType(entryRaw), // Free | Paid | Mixed | Other
      entryProcess:      cellText(row, iProcess),
      about:             cellText(row, iAbout),
      rvmDisplay:        cellText(row, iRvm),
      relevanceRvm:      relevanceRvm,
      rvmRelevant:       isRvmRelevant(cellText(row, iRvm), relevanceRvm),
      rvmCategory:       classifyRvmCategory(relevanceRvm, theme), // dashboard-derived
      plannedReps:       cellText(row, iReps),
      registrationStatus:cellText(row, iRegStat),
      organiser:         cellDisplay(disp, iOrganiser), // '' when blank/absent
      website:           cellText(row, iWebsite),
      speakers:          cellText(row, iSpeakers),
      sponsors:          cellText(row, iSponsors),
      theme:             theme,
      remarks:           cellText(row, iRemarks)
    });
  });

  return events;
}
