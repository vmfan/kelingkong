/**
 * Kelingkong 2026 — ledger write layer.
 *
 * One `doPost` endpoint behind the participant web page. Handles the five
 * actions in docs/2026/operations.md: buy · task · object · post · mission.
 *
 * Deploy: Execute as ME, Who has access ANYONE. That combination is what lets
 * teams submit without a Google account — the reason this replaced the Google
 * Form, which forces a sign-in as soon as it carries a file-upload question.
 *
 * Three properties this file exists to guarantee. Read these before editing:
 *
 *   1. APPEND FIRST. The raw submission is written to `Transactions` before any
 *      pricing or validation runs. If the code below throws, the record still
 *      exists and can be reprocessed by hand. This reproduces the one virtue of
 *      the Google Form it replaced.
 *
 *   2. LOCK THE LADDER. Price depends on how many teams bought before you.
 *      Two concurrent buys that both read the same prior-buyer count would both
 *      be charged the same price and the ladder would lose a step. The
 *      read-count → append → flush sequence runs inside a script lock. Removing
 *      the lock breaks the economy silently — nothing errors, prices are just
 *      wrong.
 *
 *   3. IDEMPOTENCY. A double-tap or a network retry must not buy twice. The
 *      client sends a UUID per action; a replay returns the original result.
 *
 * See docs/2026/ledger-system.md for why the layers are split this way.
 */

const CONFIG = {
  SPREADSHEET_ID: 'SPREADSHEET_ID_SET_VIA_SCRIPT_PROPERTIES',
  PHOTO_FOLDER_ID: 'PHOTO_FOLDER_ID_SET_VIA_SCRIPT_PROPERTIES',
  TIMEZONE: 'Asia/Hong_Kong',
  DEADLINE: '2026-09-12T16:30:00+08:00',  // operations.md rundown
  ALLOWANCE: 150,                          // economy.md — starting cash per team
  TEAMS: 25,
  ESCALATION_PER_BUYER: 0.25,
  PRICE_CAP_MULTIPLE: 2.5,
  POST_COOLDOWN_MIN: 15,                   // game-posts.md, added 2026-08-18
  POST_PAYOUT: { win: 40, lose: 20 },
  OBJECT_PAYOUT: 5,
  TASK_RATE: 0.30,
  // economy.md calibration log, 2026-08-19: Kai Tak's 4 landmarks pay 50%, not 30%.
  // Board!F carries the same numbers for display, but this is what actually pays --
  // lookupLandmark reads only name/district/base_price/aliases, never the income column.
  // If one is edited the other must be too, or the page advertises a figure the ledger
  // does not honour.
  TASK_RATE_BY_DISTRICT: { 'Kai Tak': 0.50 },
  LOCK_WAIT_MS: 60000,
};

// Transactions column layout. Everything downstream (Ledger, Standings,
// Kontrol, seed_transactions.py) depends on this order.
const COL = {
  TIMESTAMP: 1, SUBMISSION_ID: 2, TEAM: 3, ACTION: 4, ITEM: 5,
  DISTRICT: 6, BASE_PRICE: 7, LADDER_POS: 8, AMOUNT: 9,
  PHOTO_URL: 10, STATUS: 11, NOTE: 12,
};
const N_COLS = 12;

/* ------------------------------------------------------------------ entry */

function doPost(e) {
  try {
    // Sent as text/plain so the browser treats it as a CORS simple request.
    // Apps Script does not answer OPTIONS, so an application/json POST would
    // fail preflight and never arrive here.
    const req = JSON.parse(e.postData.contents);
    return json(handle(req));
  } catch (err) {
    return json({ ok: false, error: 'server', message: String(err) });
  }
}

/**
 * `?data=1` serves the four participant tabs as JSON, so the page has a working data
 * source without anyone having to click through Publish-to-web four times.
 *
 * This is the fallback, not the intended path. Reads are supposed to come from published
 * CSV so that a dead script still leaves 250 people with a readable board
 * (`ledger-system.md`). Paste the CSV URLs into web/index.html's CONFIG when you have
 * them and this route stops being used.
 */
function doGet(e) {
  if (e && e.parameter && e.parameter.data) {
    return json(readParticipantTabs());
  }
  if (e && e.parameter && e.parameter.misi) {
    return json(activeMission());
  }
  return json({ ok: true, service: 'kelingkong-ledger', teams: CONFIG.TEAMS });
}

/**
 * `?misi=1` — the currently open surprise-mission window, if any.
 *
 * Deliberately not served from the published-CSV path the other participant tabs
 * use: Publish-to-web recaches on Google's own schedule (minutes, not seconds),
 * which would silently eat into a team's 20-minute window before the countdown
 * box on the page ever appeared. This is a live read instead, on its own polling
 * interval, independent of `doPost` — reads and writes are meant to fail
 * independently (`ledger-system.md`).
 *
 * `now`/`deadline` are epoch milliseconds, not sheet-locale strings, so the page
 * can compute a clock-skew-corrected countdown from its own fetch time rather
 * than trusting the browser's clock against a display string.
 */
function activeMission() {
  const ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  const sh = ss.getSheetByName('Missions');
  const rows = sh.getDataRange().getValues().slice(1);
  const now = Date.now();

  let active = null;
  rows.forEach(r => {
    const id = String(r[0]).trim();
    if (!id) return;
    const issuedAt = r[2] instanceof Date ? r[2].getTime() : null;
    const deadline = r[3] instanceof Date ? r[3].getTime() : null;
    if (issuedAt === null || deadline === null) return;
    if (now < issuedAt || now > deadline) return;
    // Two windows should never overlap in practice (the committee broadcasts
    // one at a time), but if they do, prefer whichever was issued last rather
    // than erroring.
    if (!active || issuedAt > active.issuedAt) {
      active = { issuedAt: issuedAt, id: id, text: String(r[1]),
                 deadline: deadline, penalty: Number(r[4]) || 0 };
    }
  });

  if (!active) return { active: false };
  return {
    active: true,
    mission_id: active.id,
    text: active.text,
    now: now,
    deadline: active.deadline,
    penalty_kd: active.penalty,
  };
}

function readParticipantTabs() {
  const ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  const grab = function (name) {
    const sh = ss.getSheetByName(name);
    const rows = sh.getLastRow();
    const cols = sh.getLastColumn();
    if (rows < 2 || cols < 1) return [];
    return sh.getRange(1, 1, rows, cols).getValues();
  };
  return {
    ok: true,
    ts: new Date().toISOString(),
    harga: grab('harga'),
    milik: grab('milik'),
    tim: grab('tim'),
    klasemen: grab('klasemen'),
    aktivitas: grab('aktivitas'),
  };
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/* ----------------------------------------------------------------- handle */

function handle(req) {
  const team = Number(req.team);
  const action = String(req.action || '').toLowerCase();
  const item = String(req.item || '').trim();
  const submissionId = String(req.submissionId || '').trim();
  const key = String(req.key || '').trim();

  if (!submissionId) return { ok: false, error: 'no_submission_id' };
  if (!(team >= 1 && team <= CONFIG.TEAMS)) return { ok: false, error: 'bad_team' };
  if (['buy', 'task', 'object', 'post', 'mission'].indexOf(action) === -1) {
    return { ok: false, error: 'bad_action' };
  }
  // Opened BEFORE the lock on purpose. This is a round trip that does not need to be
  // serialised, and every millisecond spent inside the lock is a millisecond every other
  // team spends queueing behind it. Measured 2026-08-19: the critical section is what
  // caps throughput, not the request rate.
  const ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);

  // Stops the cheap version of spoofing: typing/guessing another team's number and
  // submitting as them. Checked before Transactions is touched at all, same as
  // bad_team/bad_action above — a spoofed request never gets journaled. If a team's
  // key isn't in TeamKeys yet, this fails closed (rejects), not open.
  const expectedKey = lookupTeamKey(ss, team);
  if (!expectedKey || key !== expectedKey) {
    return { ok: false, error: 'bad_key',
             message: 'Kode tim tidak cocok — scan ulang QR di peta kalian.' };
  }

  const tx = ss.getSheetByName('Transactions');

  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(CONFIG.LOCK_WAIT_MS);
  } catch (err) {
    return { ok: false, error: 'busy', message: 'Coba lagi sebentar lagi.' };
  }

  let result;
  let row;
  try {
    const log = readLog(tx);

    const replay = log.find(r => r.submissionId === submissionId);
    if (replay) {
      return { ok: replay.status === 'ok', replay: true, amount: replay.amount,
               balance: balanceOf(log, team), message: 'Sudah tercatat.' };
    }

    // --- APPEND FIRST. Everything after this point can fail safely. ---
    // setValues on lastDataRow()+1 WRITES INTO an existing blank row. Do not
    // switch this to insertRowAfter or a Sheets API append with INSERT_ROWS:
    // inserting a row rewrites every absolute reference that points below it,
    // and Board/Ledger/Standings would silently start counting from the wrong
    // row. Their formulas use full-column refs so they survive it, but nothing
    // else in the workbook is guaranteed to.
    row = lastDataRow(tx) + 1;
    tx.getRange(row, 1, 1, N_COLS).setValues([[
      new Date(), submissionId, team, action, item,
      '', '', '', 0, '', 'pending', '',
    ]]);
    SpreadsheetApp.flush();

    result = price(ss, log, { team, action, item, req });

    // One write, not two: columns F..L in a single round trip.
    tx.getRange(row, COL.DISTRICT, 1, 7).setValues([[
      result.district || '', result.basePrice || '',
      result.ladderPos || '', result.amount || 0, '',
      result.ok ? 'ok' : 'rejected', result.note || '',
    ]]);
    // Flush inside the lock: a concurrent execution must see this row when it
    // counts prior buyers, or two teams get charged the same ladder price.
    SpreadsheetApp.flush();

    result.balance = balanceOf(log, team) + (result.ok ? result.amount : 0);
  } finally {
    lock.releaseLock();
  }

  // Photo goes to Drive outside the lock — it is the slowest step and holding
  // the lock through it would serialise every team behind one upload.
  if (row && req.photo) {
    try {
      tx.getRange(row, COL.PHOTO_URL)
        .setValue(savePhoto(req.photo, team, action, item, submissionId));
    } catch (err) {
      // A failed photo must not void a valid transaction. Kontrol flags it.
      // Include err.message: a bare 'UPLOAD_FAILED' hides causes like a GCP project missing
      // the Drive API, which is otherwise only found by redeploying with debug logging.
      tx.getRange(row, COL.PHOTO_URL).setValue('UPLOAD_FAILED: ' + err.message);
    }
  }

  return result;
}

/* ------------------------------------------------------------------ rules */

function price(ss, log, ctx) {
  const { team, action, item } = ctx;

  // operations.md: the photo is required on every action, including `buy`. Without it a
  // team could earn task money at one landmark and buy a different one it never visited,
  // which undercuts the whole point of getting teams to see parts of Hong Kong. Exempt
  // `post`, which is submitted by stationed staff who witnessed the heat themselves.
  if (action !== 'post' && !ctx.req.photo) {
    return { ok: false, amount: 0, note: 'no photo', error: 'no_photo',
             message: 'Foto tim di lokasi wajib disertakan.' };
  }

  if (new Date() > new Date(CONFIG.DEADLINE)) {
    return { ok: false, amount: 0, note: 'after deadline',
             error: 'closed', message: 'Pengiriman sudah ditutup jam 16:30.' };
  }

  if (action === 'object') {
    if (log.some(r => r.team === team && r.action === 'object'
                   && r.item === item && r.status === 'ok')) {
      return { ok: false, amount: 0, note: 'duplicate object',
               error: 'duplicate', message: 'Objek ini sudah pernah dikirim.' };
    }
    return { ok: true, amount: CONFIG.OBJECT_PAYOUT,
             message: '+' + CONFIG.OBJECT_PAYOUT + ' KD' };
  }

  if (action === 'mission') {
    const mission = lookupMission(ss, item);
    if (!mission) {
      return { ok: false, amount: 0, note: 'unknown mission: ' + item,
               error: 'unknown_item', message: 'Misi tidak dikenal.' };
    }
    if (log.some(r => r.team === team && r.action === 'mission'
                   && r.item === mission.id && r.status === 'ok')) {
      return { ok: false, amount: 0, note: 'duplicate mission',
               error: 'duplicate', message: 'Misi ini sudah pernah dikirim.' };
    }
    // Deliberately rejected, not accepted-but-late: `status` stays out of "ok",
    // which is exactly the condition Standings' penalty formula treats as
    // "never completed" (see docs/2026/missions-build-spec.md, section 3). The append
    // above already wrote the raw submission before this check ran, so the
    // banker queue and the photo both still exist for review.
    if (mission.deadline && new Date() > mission.deadline) {
      return { ok: false, amount: 0, note: 'after mission deadline',
               error: 'closed', message: 'Waktu misi ini sudah habis.' };
    }
    return { ok: true, amount: 0, message: 'Misi tercatat.' };
  }

  if (action === 'post') {
    const outcome = String(ctx.req.outcome || '').toLowerCase();
    if (!(outcome in CONFIG.POST_PAYOUT)) {
      return { ok: false, amount: 0, note: 'bad outcome', error: 'bad_outcome' };
    }
    const cooldownMs = CONFIG.POST_COOLDOWN_MIN * 60 * 1000;
    const recent = log.filter(r => r.team === team && r.action === 'post'
                                && r.item === item && r.status === 'ok'
                                && (Date.now() - r.timestamp.getTime()) < cooldownMs);
    if (recent.length) {
      return { ok: false, amount: 0, note: 'cooldown', error: 'cooldown',
               message: 'Tim ini baru main di pos ini. Tunggu satu sesi.' };
    }
    const paid = CONFIG.POST_PAYOUT[outcome];
    return { ok: true, amount: paid, message: '+' + paid + ' KD' };
  }

  // buy / task both need the landmark
  const lm = lookupLandmark(ss, item);
  if (!lm) {
    return { ok: false, amount: 0, note: 'unknown landmark: ' + item,
             error: 'unknown_item', message: 'Landmark tidak dikenal.' };
  }

  if (action === 'task') {
    if (log.some(r => r.team === team && r.action === 'task'
                   && r.item === lm.name && r.status === 'ok')) {
      return { ok: false, amount: 0, district: lm.district, basePrice: lm.basePrice,
               note: 'duplicate task', error: 'duplicate',
               message: 'Tugas di landmark ini sudah dikerjakan.' };
    }
    // economy.md: 30% of base price, rounded to the nearest 5 -- except Kai Tak at 50%.
    const rate = CONFIG.TASK_RATE_BY_DISTRICT[lm.district] || CONFIG.TASK_RATE;
    const income = Math.round(lm.basePrice * rate / 5) * 5;
    return { ok: true, amount: income, district: lm.district,
             basePrice: lm.basePrice, message: '+' + income + ' KD' };
  }

  // action === 'buy'
  if (log.some(r => r.team === team && r.action === 'buy'
                 && r.item === lm.name && r.status === 'ok')) {
    return { ok: false, amount: 0, district: lm.district, basePrice: lm.basePrice,
             note: 'duplicate buy', error: 'duplicate',
             message: 'Tim kalian sudah memiliki landmark ini.' };
  }

  const priorBuyers = log.filter(r => r.action === 'buy' && r.item === lm.name
                                   && r.status === 'ok').length;
  const multiple = Math.min(CONFIG.PRICE_CAP_MULTIPLE,
                            1 + CONFIG.ESCALATION_PER_BUYER * priorBuyers);
  const cost = Math.round(lm.basePrice * multiple);
  const balance = balanceOf(log, team);

  if (cost > balance) {
    return { ok: false, amount: 0, district: lm.district, basePrice: lm.basePrice,
             ladderPos: priorBuyers + 1, note: 'insufficient funds',
             error: 'insufficient', cost: cost, balance: balance,
             message: 'Uang tidak cukup: butuh ' + cost + ' KD, sisa ' + balance + ' KD.' };
  }

  return { ok: true, amount: -cost, district: lm.district, basePrice: lm.basePrice,
           ladderPos: priorBuyers + 1, cost: cost,
           titleholder: priorBuyers === 0,
           message: '−' + cost + ' KD' + (priorBuyers === 0 ? ' · pemegang title!' : '') };
}

/* ------------------------------------------------------------------ state */

// Last row the SCRIPT has written, measured from column A (timestamp) alone.
//
// Deliberately not getLastRow(). getLastRow() is the last row with anything in
// it in ANY column, and column M (`diperiksa`) is a checkbox operators tick by
// hand. A stray click on an empty row 1500 would push getLastRow() to 1500 and
// every subsequent transaction would land 1400 rows below the journal. Column A
// is written only here, so it cannot be moved by an operator.
function lastDataRow(tx) {
  const col = tx.getRange(1, 1, tx.getMaxRows(), 1).getValues();
  let last = col.length;
  while (last > 0 && col[last - 1][0] === '') last--;
  return last;
}


function readLog(tx) {
  // lastDataRow, not getLastRow: this runs inside the lock, and getLastRow would
  // read every blank row down to a stray operator checkbox on each request.
  const last = lastDataRow(tx);
  if (last < 2) return [];
  return tx.getRange(2, 1, last - 1, N_COLS).getValues().map(r => ({
    timestamp: r[COL.TIMESTAMP - 1] instanceof Date ? r[COL.TIMESTAMP - 1] : new Date(0),
    submissionId: String(r[COL.SUBMISSION_ID - 1]),
    team: Number(r[COL.TEAM - 1]),
    action: String(r[COL.ACTION - 1]),
    item: String(r[COL.ITEM - 1]),
    amount: Number(r[COL.AMOUNT - 1]) || 0,
    status: String(r[COL.STATUS - 1]),
  }));
}

function balanceOf(log, team) {
  return log
    .filter(r => r.team === team && r.status === 'ok')
    .reduce((sum, r) => sum + r.amount, CONFIG.ALLOWANCE);
}

/**
 * Board is the landmark reference table, seeded from data/landmarks.csv.
 * Matches on canonical_name first, then the pipe-separated aliases column —
 * the 2025 sheets spell the same place several ways and docs/2025/data-audit.md
 * items 8-9 record the drift. Cached because it never changes during the day.
 */
function lookupLandmark(ss, name) {
  const cache = CacheService.getScriptCache();
  let index = cache.get('board');
  if (!index) {
    const rows = ss.getSheetByName('Board').getDataRange().getValues().slice(1);
    const built = {};
    rows.forEach(r => {
      const canonical = String(r[0]).trim();
      if (!canonical) return;
      const entry = { name: canonical, district: String(r[1]).trim(),
                      basePrice: Number(r[2]) };
      built[norm(canonical)] = entry;
      String(r[3] || '').split('|').forEach(a => {
        if (a.trim()) built[norm(a)] = entry;
      });
    });
    index = JSON.stringify(built);
    cache.put('board', index, 21600);
  }
  return JSON.parse(index)[norm(name)] || null;
}

/**
 * TeamKeys is a manually-populated operator tab (team | key), generated by
 * scripts/generate_team_keys.py and pasted in once before the event — never edited
 * live, so it's cached the same way and for the same reason as Board.
 */
function lookupTeamKey(ss, team) {
  const cache = CacheService.getScriptCache();
  let index = cache.get('teamKeys:v2');
  if (!index) {
    // Sheet not created yet (pre-event setup) reads as "no team has a key" rather than
    // throwing, so a missing tab fails every team closed with the normal bad_key message
    // instead of a raw server error.
    const sh = ss.getSheetByName('TeamKeys');
    const rows = sh ? sh.getDataRange().getValues().slice(1) : [];
    const built = {};
    rows.forEach(r => {
      const t = Number(r[0]);
      const k = String(r[1] || '').trim();
      if (t && k) built[t] = k;
    });
    index = JSON.stringify(built);
    cache.put('teamKeys:v2', index, 21600);
  }
  return JSON.parse(index)[team] || null;
}

/**
 * Missions is tiny (~4 rows/day, committee-populated live) and freshness matters
 * more than the read cost, so this is not cached the way `Board` is.
 */
function lookupMission(ss, missionId) {
  const sh = ss.getSheetByName('Missions');
  const rows = sh.getDataRange().getValues().slice(1);
  for (const r of rows) {
    const id = String(r[0]).trim();
    if (id && id === missionId) {
      return { id: id, deadline: (r[3] instanceof Date) ? r[3] : null };
    }
  }
  return null;
}

function norm(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]/g, '');
}

function savePhoto(dataUrl, team, action, item, submissionId) {
  const m = /^data:(image\/[a-z+]+);base64,(.*)$/i.exec(dataUrl);
  if (!m) throw new Error('photo is not a data URL');
  const blob = Utilities.newBlob(
    Utilities.base64Decode(m[2]), m[1],
    ['tim' + team, action, item.replace(/[^\w -]/g, ''), submissionId.slice(0, 8)]
      .join('_') + '.jpg');
  return DriveApp.getFolderById(CONFIG.PHOTO_FOLDER_ID).createFile(blob).getUrl();
}
