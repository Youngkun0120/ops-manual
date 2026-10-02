/* =========================================================================
   운영업무 접수 현황 탭 (#/intake) — 운영 요청을 한 장의 시트에 접수하고 모아서 처리한다.

   · 항목: 접수 일자 · 접수 시간 · 요청자 · 긴급(Y/N) · 접수자 · 요청 내용 · 처리 기한 · 처리 결과(Y/N) · 메모
   · 정렬: 오늘(이후) 접수 건을 위에, 지난 날짜 건을 아래에 — 두 묶음 모두 일자 · 시간 오름차순.
   · 저장: 정산 워크벤치와 같은 Supabase 테이블 public.stl_docs 에 **한 건당 한 줄**(key = ops.intake.<id>).
     건마다 따로 저장하므로 두 사람이 서로 다른 건을 동시에 고쳐도 덮어쓰지 않는다(같은 건은 나중 저장 우선).
     다른 사람이 바꾼 내용은 30초마다 · 창으로 돌아올 때 가져온다. 서버에 못 닿으면 이 브라우저에 임시 보관.
   · 접근 제한 없음(정산 워크벤치와 같은 사용자 결정) — 사이트 링크를 아는 사람은 읽고 쓸 수 있다.
   ========================================================================= */
(function () {
  var URL_ = 'https://moizzusdaeerswjbnini.supabase.co';
  var KEY = 'sb_publishable_t-fQzBc2Vz6LYeOuv5Bwzg_E2nlJXI_';
  var TABLE = 'stl_docs', PREFIX = 'ops.intake.';
  var H = { apikey: KEY, Authorization: 'Bearer ' + KEY };
  var LS_CACHE = 'ops.intake.cache', LS_ME = 'ops.intake.me', LS_FILTER = 'ops.intake.filter';

  var rows = {};        // id → row
  var queue = {};       // id → row(저장 대기) | null(삭제 대기)
  var timer = null, poll = null, inflight = 0, online = null, lastErr = '';
  var filter = 'all';

  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function pad(n) { return String(n).padStart(2, '0'); }
  function today() { var d = new Date(); return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function nowHM() { var d = new Date(); return pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }
  function root() { return document.getElementById('intakeRoot'); }
  function saveCache() { ls(LS_CACHE, JSON.stringify(rows)); }

  /* ---------- 서버 ---------- */
  function req(path, opt) {
    opt = opt || {};
    opt.headers = Object.assign({}, H, opt.headers || {});
    return fetch(URL_ + path, opt);
  }

  async function pull() {
    try {
      var r = await req('/rest/v1/' + TABLE + '?select=key,data&key=like.' + encodeURIComponent(PREFIX + '*'));
      if (!r.ok) throw new Error('불러오기 실패 (' + r.status + ')');
      var list = await r.json(), seen = {};
      list.forEach(function (x) {
        var id = x.key.slice(PREFIX.length); seen[id] = 1;
        if (id in queue || editing(id)) return;           // 내가 고치는 중인 건은 건드리지 않는다
        rows[id] = Object.assign({ id: id }, x.data);
      });
      Object.keys(rows).forEach(function (id) { if (!seen[id] && !(id in queue) && !rows[id]._local) delete rows[id]; });
      online = true; lastErr = '';
      saveCache();
    } catch (e) { online = false; lastErr = String(e).slice(0, 200); }
    if (root() && !document.activeElement.closest('#intakeRoot tbody')) render(); else paintChip();
  }

  function flush() {
    clearTimeout(timer);
    timer = setTimeout(async function () {
      var ids = Object.keys(queue); if (!ids.length) return;
      var batch = queue; queue = {}; inflight++; paintChip();
      try {
        var up = ids.filter(function (id) { return batch[id]; }).map(function (id) {
          var d = Object.assign({}, batch[id]); delete d.id; delete d._local;
          return { key: PREFIX + id, data: d, updated_at: new Date().toISOString() };
        });
        if (up.length) {
          var r = await req('/rest/v1/' + TABLE + '?on_conflict=key', {
            method: 'POST', headers: { 'Content-Type': 'application/json', Prefer: 'resolution=merge-duplicates,return=minimal' },
            body: JSON.stringify(up)
          });
          if (!r.ok) throw new Error(await r.text());
          up.forEach(function (u) { var id = u.key.slice(PREFIX.length); if (rows[id]) delete rows[id]._local; });
        }
        var del = ids.filter(function (id) { return !batch[id]; });
        if (del.length) {
          var r2 = await req('/rest/v1/' + TABLE + '?key=in.(' + del.map(function (id) { return '"' + PREFIX + id + '"'; }).join(',') + ')', { method: 'DELETE' });
          if (!r2.ok) throw new Error(await r2.text());
        }
        online = true; lastErr = '';
      } catch (e) {
        online = false; lastErr = String(e).slice(0, 200);
        ids.forEach(function (id) { if (!(id in queue)) queue[id] = batch[id]; });
      } finally { inflight--; saveCache(); paintChip(); }
    }, 600);
  }

  function put(id) { queue[id] = Object.assign({}, rows[id]); saveCache(); flush(); paintChip(); }
  function editing(id) { var a = document.activeElement; return !!(a && a.closest && a.closest('tr[data-id="' + id + '"]')); }

  /* ---------- 정렬 · 상태 ---------- */
  function key(r) { return (r.date || '9999-99-99') + ' ' + (r.time || '99:99'); }
  function groups() {
    var t = today(), list = Object.keys(rows).map(function (id) { return rows[id]; });
    if (filter === 'open') list = list.filter(function (r) { return r.done !== 'Y'; });
    if (filter === 'urgent') list = list.filter(function (r) { return r.urgent === 'Y' && r.done !== 'Y'; });
    list.sort(function (a, b) { return key(a) < key(b) ? -1 : key(a) > key(b) ? 1 : 0; });
    return {
      now: list.filter(function (r) { return !r.date || r.date >= t; }),
      past: list.filter(function (r) { return r.date && r.date < t; })
    };
  }
  function overdue(r) { return r.done !== 'Y' && r.due && r.due < today(); }

  /* ---------- 화면 ---------- */
  function paintChip() {
    var el = document.getElementById('intakeSync'); if (!el) return;
    var n = Object.keys(queue).length, txt, cls = 'ik-chip';
    if (online === null) txt = '서버 확인 중…';
    else if (!online) { txt = '서버 연결 안 됨 — 이 브라우저에 임시 보관'; cls += ' warn'; }
    else if (inflight || n) txt = '저장 중…';
    else txt = '서버 저장됨';
    el.textContent = txt; el.className = cls; el.title = lastErr;
  }

  function yn(field, v) {
    return '<select class="ik-yn' + (v === 'Y' ? ' y-' + field : '') + '" data-f="' + field + '" aria-label="' + (field === 'urgent' ? '긴급 여부' : '처리 결과') + '">' +
      '<option value="N"' + (v !== 'Y' ? ' selected' : '') + '>N</option><option value="Y"' + (v === 'Y' ? ' selected' : '') + '>Y</option></select>';
  }

  function tr(r) {
    var cls = (r.done === 'Y' ? 'is-done' : '') + (r.urgent === 'Y' && r.done !== 'Y' ? ' is-urgent' : '') + (overdue(r) ? ' is-overdue' : '');
    return '<tr data-id="' + esc(r.id) + '" class="' + cls + '">' +
      '<td><input type="date" data-f="date" value="' + esc(r.date) + '"></td>' +
      '<td><input type="time" data-f="time" value="' + esc(r.time) + '"></td>' +
      '<td><input type="text" data-f="requester" value="' + esc(r.requester) + '" placeholder="요청자"></td>' +
      '<td class="c">' + yn('urgent', r.urgent) + '</td>' +
      '<td><input type="text" data-f="receiver" value="' + esc(r.receiver) + '" placeholder="접수자"></td>' +
      '<td class="ik-body"><textarea data-f="body" rows="1" placeholder="요청 내용">' + esc(r.body) + '</textarea></td>' +
      '<td><input type="date" data-f="due" value="' + esc(r.due) + '"' + (overdue(r) ? ' title="처리 기한이 지났습니다"' : '') + '></td>' +
      '<td class="c">' + yn('done', r.done) + '</td>' +
      '<td class="ik-memo"><textarea data-f="memo" rows="1" placeholder="메모">' + esc(r.memo) + '</textarea></td>' +
      '<td class="c"><button class="ik-del" data-act="del" title="이 건 삭제" aria-label="삭제">×</button></td>' +
      '</tr>';
  }

  function section(label, list, empty) {
    var h = '<tr class="ik-sec"><td colspan="10">' + label + ' <span>' + list.length + '건</span></td></tr>';
    if (!list.length) return h + '<tr class="ik-empty"><td colspan="10">' + empty + '</td></tr>';
    return h + list.map(tr).join('');
  }

  function stats() {
    var all = Object.keys(rows).map(function (id) { return rows[id]; }), t = today();
    var open = all.filter(function (r) { return r.done !== 'Y'; });
    return { todayN: all.filter(function (r) { return r.date === t; }).length, open: open.length,
      urgent: open.filter(function (r) { return r.urgent === 'Y'; }).length, over: open.filter(overdue).length };
  }

  function render() {
    var el = root(); if (!el) return;
    var g = groups(), s = stats(), t = today();
    var d = new Date(), wk = '일월화수목금토'[d.getDay()];
    el.querySelector('.ik-stats').innerHTML =
      '<span>오늘 접수 <b>' + s.todayN + '</b></span><span>미처리 <b>' + s.open + '</b></span>' +
      '<span class="' + (s.urgent ? 'hot' : '') + '">긴급 미처리 <b>' + s.urgent + '</b></span>' +
      '<span class="' + (s.over ? 'hot' : '') + '">기한 지남 <b>' + s.over + '</b></span>';
    el.querySelector('tbody').innerHTML =
      section('오늘 · ' + (d.getMonth() + 1) + '/' + d.getDate() + '(' + wk + ')', g.now, '오늘 접수된 건이 없습니다. 「+ 접수 추가」로 기록하세요.') +
      section('지난 내역', g.past, filter === 'all' ? '지난 내역이 없습니다.' : '조건에 맞는 지난 건이 없습니다.');
    el.querySelectorAll('.ik-filter button').forEach(function (b) { b.classList.toggle('on', b.getAttribute('data-filter') === filter); });
    el.querySelectorAll('textarea').forEach(grow);
    paintChip();
  }

  function grow(ta) { ta.style.height = 'auto'; ta.style.height = Math.min(ta.scrollHeight, 220) + 'px'; }

  function add() {
    var id = uid();
    rows[id] = { id: id, date: today(), time: nowHM(), requester: '', urgent: 'N', receiver: ls(LS_ME) || '', body: '', due: '', done: 'N', created_at: new Date().toISOString(), _local: 1 };
    if (filter !== 'all') filter = 'all';
    put(id); render();
    var f = root().querySelector('tr[data-id="' + id + '"] [data-f="requester"]'); if (f) f.focus();
  }

  function csv() {
    var g = groups(), list = g.now.concat(g.past);
    var head = ['접수 일자', '접수 시간', '요청자', '긴급 여부', '접수자', '요청 내용', '처리 기한', '처리 결과', '메모'];
    var q = function (v) { v = String(v == null ? '' : v); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };
    var text = '﻿' + [head].concat(list.map(function (r) { return [r.date, r.time, r.requester, r.urgent || 'N', r.receiver, r.body, r.due, r.done || 'N', r.memo]; }))
      .map(function (a) { return a.map(q).join(','); }).join('\r\n');
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], { type: 'text/csv;charset=utf-8' }));
    a.download = '운영업무_접수현황_' + today() + '.csv';
    document.body.appendChild(a); a.click(); a.remove();
  }

  /* ---------- 진입점 (index.html renderRoute 에서 부른다) ---------- */
  window.renderIntake = function () {
    return '<div id="intakeRoot" class="ik">' +
      '<div class="ik-head"><div><h1>운영업무 접수 현황</h1>' +
      '<p>운영 요청을 받는 즉시 한 줄로 접수하고, 모아서 한 번에 처리합니다. 오늘 접수 건이 위, 지난 날짜 건이 아래에 놓입니다(각각 일자·시간 오름차순).</p></div>' +
      '<span id="intakeSync" class="ik-chip">서버 확인 중…</span></div>' +
      '<div class="ik-bar"><button class="ik-add" data-act="add">+ 접수 추가</button>' +
      '<div class="ik-filter" role="group" aria-label="보기"><button data-filter="all">전체</button><button data-filter="open">미처리</button><button data-filter="urgent">긴급 미처리</button></div>' +
      '<div class="ik-stats"></div><button class="ik-csv" data-act="csv">CSV 내려받기</button></div>' +
      '<div class="ik-wrap"><table class="ik-sheet"><colgroup><col style="width:150px"><col style="width:118px"><col style="width:110px"><col style="width:78px"><col style="width:110px"><col><col style="width:150px"><col style="width:84px"><col style="width:220px"><col style="width:40px"></colgroup>' +
      '<thead><tr><th>접수 일자</th><th>접수 시간</th><th>요청자</th><th class="c">긴급 여부</th><th>접수자</th><th>요청 내용</th><th>처리 기한</th><th class="c">처리 결과</th><th>메모</th><th></th></tr></thead>' +
      '<tbody></tbody></table></div>' +
      '<div class="ik-foot">입력하면 바로 서버에 저장됩니다(링크를 아는 사람은 누구나 보고 고칠 수 있음). 다른 사람이 적은 내용은 30초마다 자동으로 반영됩니다. 접수자 이름은 이 브라우저가 기억해 다음 접수 때 미리 채웁니다.</div>' +
      '</div>';
  };

  window.initIntake = function () {
    var el = root(); if (!el) return;
    filter = ls(LS_FILTER) || 'all';
    if (!Object.keys(rows).length) { try { rows = JSON.parse(ls(LS_CACHE) || '{}') || {}; } catch (e) { rows = {}; } }
    render(); pull();
    clearInterval(poll);
    poll = setInterval(function () { if (!root()) { clearInterval(poll); return; } pull(); }, 30000);

    el.addEventListener('click', function (e) {
      var b = e.target.closest('[data-act],[data-filter]'); if (!b) return;
      if (b.dataset.filter) { filter = b.dataset.filter; ls(LS_FILTER, filter); render(); return; }
      if (b.dataset.act === 'add') add();
      else if (b.dataset.act === 'csv') csv();
      else if (b.dataset.act === 'del') {
        var id = b.closest('tr').dataset.id, r = rows[id];
        if (!confirm('이 건을 삭제할까요?\n\n' + (r.date || '') + ' ' + (r.requester || '') + ' — ' + String(r.body || '').slice(0, 60))) return;
        delete rows[id]; queue[id] = null; saveCache(); flush(); render();
      }
    });
    el.addEventListener('input', function (e) {
      var f = e.target.dataset.f, tr_ = e.target.closest('tr[data-id]'); if (!f || !tr_) return;
      var id = tr_.dataset.id; if (!rows[id]) return;
      rows[id][f] = e.target.value;
      if (e.target.tagName === 'TEXTAREA') grow(e.target);
      if (f === 'receiver' && e.target.value.trim()) ls(LS_ME, e.target.value.trim());
      put(id);
    });
    el.addEventListener('change', function (e) {
      var f = e.target.dataset.f; if (!f) return;
      // 날짜 · 시간 · Y/N 이 바뀌면 줄 위치나 색이 바뀌므로 다시 그린다
      if (f === 'date' || f === 'time' || f === 'urgent' || f === 'done' || f === 'due') render();
    });
    if (!window.__ikFocus) { window.__ikFocus = 1; window.addEventListener('focus', function () { if (root()) pull(); }); }
  };
})();
