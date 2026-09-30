/* =========================================================================
   월 정산 워크벤치 — 서버 저장 계층 (Supabase)
   워크벤치 화면은 그대로 두고, 저장 위치만 브라우저 → 서버로 옮긴다.

   · 입력값·설정 JSON  → 테이블 public.stl_docs (key, data)
   · 기존 양식 · CTN 파일 → 스토리지 버킷 stl-files
   · 브라우저(localStorage·IndexedDB)는 오프라인 대비 사본으로 계속 쓴다.
   · 같은 문서를 둘이 고치면 나중에 저장한 쪽이 남는다(마지막 저장 우선).
     다른 사람이 저장한 내용은 창을 다시 보거나 30초마다 확인해 가져온다.
   스키마는 supabase/settlement.sql 참고.
   ========================================================================= */
window.STL_SYNC = (function () {
  var URL_ = 'https://moizzusdaeerswjbnini.supabase.co';
  var KEY = 'sb_publishable_t-fQzBc2Vz6LYeOuv5Bwzg_E2nlJXI_';
  var TABLE = 'stl_docs', BUCKET = 'stl-files';
  var H = { apikey: KEY, Authorization: 'Bearer ' + KEY };

  var cache = {};        // key → data (서버에서 읽어 온 것)
  var stamp = {};        // key → updated_at
  var queue = {};        // 저장 대기
  var timer = null, inflight = 0, online = false, lastErr = '';
  var onRemote = null;   // 다른 사람이 바꾼 값을 받았을 때 부를 함수

  function chip() { return document.getElementById('stlSync'); }

  function paint() {
    var el = chip(); if (!el) return;
    var txt, warn = false;
    if (!online) { txt = '서버 연결 안 됨 — 이 브라우저에만 저장'; warn = true; }
    else if (inflight || Object.keys(queue).length) txt = '서버에 저장 중…';
    else txt = '서버 저장됨';
    el.textContent = txt;
    el.className = 'chip' + (warn ? ' warn' : '');
    el.title = lastErr || (online ? 'Supabase stl_docs · stl-files' : '');
  }

  function req(path, opt) {
    opt = opt || {};
    opt.headers = Object.assign({}, H, opt.headers || {});
    return fetch(URL_ + path, opt);
  }

  /* ---------- 문서(JSON) ---------- */
  async function pull() {
    var r = await req('/rest/v1/' + TABLE + '?select=key,data,updated_at');
    if (!r.ok) throw new Error('불러오기 실패 (' + r.status + ')');
    var rows = await r.json(), changed = [];
    rows.forEach(function (row) {
      if (stamp[row.key] !== row.updated_at) changed.push(row.key);
      cache[row.key] = row.data;
      stamp[row.key] = row.updated_at;
      try { localStorage.setItem(row.key, JSON.stringify(row.data)); } catch (e) {}
    });
    return changed;
  }

  function flush() {
    clearTimeout(timer);
    timer = setTimeout(async function () {
      var keys = Object.keys(queue);
      if (!keys.length) return;
      var body = keys.map(function (k) { return { key: k, data: queue[k], updated_at: new Date().toISOString() }; });
      queue = {}; inflight++; paint();
      try {
        var r = await req('/rest/v1/' + TABLE + '?on_conflict=key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Prefer: 'resolution=merge-duplicates,return=representation' },
          body: JSON.stringify(body)
        });
        if (!r.ok) throw new Error(await r.text());
        (await r.json()).forEach(function (row) { stamp[row.key] = row.updated_at; cache[row.key] = row.data; });
        online = true; lastErr = '';
      } catch (e) {
        online = false; lastErr = String(e).slice(0, 300);
        body.forEach(function (row) { if (!(row.key in queue)) queue[row.key] = row.data; });
      } finally { inflight--; paint(); }
    }, 700);
  }

  /* ---------- 파일(엑셀·CTN) ---------- */
  async function putFile(path, blob, type) {
    var r = await req('/storage/v1/object/' + BUCKET + '/' + encodeURI(path), {
      method: 'POST',
      headers: { 'Content-Type': type || 'application/octet-stream', 'x-upsert': 'true' },
      body: blob
    });
    if (!r.ok) throw new Error(await r.text());
    return true;
  }

  async function getFile(path) {
    var r = await req('/storage/v1/object/' + BUCKET + '/' + encodeURI(path));
    if (r.status === 404 || r.status === 400) return null;
    if (!r.ok) throw new Error('파일 내려받기 실패 (' + r.status + ')');
    return r;
  }

  async function delFile(path) {
    try { await req('/storage/v1/object/' + BUCKET + '/' + encodeURI(path), { method: 'DELETE' }); } catch (e) {}
  }

  return {
    /* 워크벤치 부팅 전에 한 번 — 서버 값을 모두 읽어 온다. */
    async init(opts) {
      onRemote = (opts || {}).onRemote || null;
      var head = document.querySelector('header.top .grow');
      if (head && !chip()) {
        var el = document.createElement('span');
        el.id = 'stlSync'; el.className = 'chip'; el.textContent = '서버 확인 중…';
        head.parentNode.insertBefore(el, head.nextSibling);
      }
      try { await pull(); online = true; }
      catch (e) { online = false; lastErr = String(e).slice(0, 300); }
      paint();

      // 다른 사람이 저장한 내용 가져오기 — 창을 다시 볼 때, 그리고 30초마다.
      var refresh = async function () {
        if (document.hidden || Object.keys(queue).length || inflight) return;
        try {
          var changed = await pull();
          online = true; paint();
          if (changed.length && onRemote) onRemote(changed);
        } catch (e) { online = false; paint(); }
      };
      window.addEventListener('focus', refresh);
      setInterval(refresh, 30000);
      return online;
    },

    online: function () { return online; },
    get: function (k) { return k in cache ? cache[k] : undefined; },
    push: function (k, v) { cache[k] = v; queue[k] = v; paint(); flush(); },

    /* 파일 */
    async fileGet(path) {
      var r = await getFile(path);
      if (!r) return null;
      var meta = {};
      try { meta = JSON.parse(decodeURIComponent(r.headers.get('x-stl-meta') || '')) || {}; } catch (e) {}
      return { buf: await r.arrayBuffer(), meta: meta };
    },
    async filePut(path, buf, type) { return putFile(path, new Blob([buf]), type); },
    async jsonGet(path) {
      var r = await getFile(path);
      if (!r) return null;
      try { return await r.json(); } catch (e) { return null; }
    },
    async jsonPut(path, obj) { return putFile(path, new Blob([JSON.stringify(obj)]), 'application/json'); },
    fileDel: delFile
  };
})();
