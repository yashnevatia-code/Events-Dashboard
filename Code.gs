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
 * INDIA — read `Events List` and return an array of clean event objects.
 * Fields are located by HEADER NAME, so columns may be reordered later.
 */
function getIndiaEvents() {
  var grid = readSheetGrid(CONFIG.INDIA_SPREADSHEET_ID, CONFIG.INDIA_SHEET_NAME);
  var headerIndex = buildHeaderIndex(grid.headers);

  // Column resolver by fuzzy header name (case / spacing / punctuation safe).
  var col = function (name) { return resolveColumn(headerIndex, name); };

  var iEvent      = col('Event');
  var iStart      = col('Start Date');
  var iEnd        = col('End Date');
  var iCity       = col('City / State');
  var iType       = col('Type');
  var iScale      = col('Scale');
  var iPriority   = col('Priority');
  var iStatus     = col('Status');
  var iGov        = col('Government Stakeholders to Target');
  var iBrand      = col('Brand Stakeholders to Target');
  var iUse        = col('Strategic Use');
  var iCost       = col('Delegate Cost');
  var iSpeak      = col('Speaking Route');
  var iDemo       = col('Demo / Exhibit Route');
  var iRelevance  = col('Relevance / Business Outcome');
  var iScore      = col('Strategic Score /100');
  var iAccess     = col('Access /10');
  var iConfidence = col('Confidence');
  var iSources    = col('Sources');

  var events = [];
  var seenKeys = {}; // for subtle duplicate flagging (Event + Start Date)

  grid.rows.forEach(function (row) {
    if (isBlankRow(row)) return;

    var eventName = cellText(row, iEvent);
    if (!eventName) return; // an event with no name is not a real record

    var startInfo = parseDateFlexible(cellRaw(row, iStart));
    var endInfo   = parseDateFlexible(cellRaw(row, iEnd));

    var obj = {
      event:            eventName,
      startDate:        startInfo.startISO,          // '' when unknown
      endDate:          endInfo.startISO,
      dateDisplay:      buildDateDisplay(startInfo, endInfo),
      cityState:        cellText(row, iCity),
      type:             cellText(row, iType),
      scale:            cellText(row, iScale),
      priority:         normalizePriority(cellText(row, iPriority)),
      status:           cellText(row, iStatus),
      govStakeholders:  cellText(row, iGov),
      brandStakeholders:cellText(row, iBrand),
      strategicUse:     cellText(row, iUse),
      strategicUseTags: splitStrategicUse(cellText(row, iUse)),
      delegateCost:     cellText(row, iCost),
      speakingRoute:    cellText(row, iSpeak),
      demoExhibitRoute: cellText(row, iDemo),
      relevance:        cellText(row, iRelevance),
      strategicScore:   extractNumber(cellRaw(row, iScore)),   // number | null
      accessScore:      extractNumber(cellRaw(row, iAccess)),  // handles "7.5 currently"
      confidence:       cellText(row, iConfidence),
      sources:          cellText(row, iSources),
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
  var iWebsite = col('Website Link');
  var iSpeakers= col('List of Speakers');
  var iSponsors= col('List of Sponsors');
  var iTheme   = col('Event Theme / Agenda');
  var iRemarks = col('Remarks');

  var events = [];

  grid.rows.forEach(function (row) {
    if (isBlankRow(row)) return;

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
      website:           cellText(row, iWebsite),
      speakers:          cellText(row, iSpeakers),
      sponsors:          cellText(row, iSponsors),
      theme:             theme,
      remarks:           cellText(row, iRemarks)
    });
  });

  return events;
}
