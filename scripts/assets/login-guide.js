/* 상세 업무 처리 — 로그인 · 구글 계정 안내 (ops-manual 이 01 실행센터에 덧붙이는 코드)
   · 구글 링크: 어느 계정으로 열어야 하는지 이름표를 붙이고, ?authuser=<이메일> 로 그 계정으로 바로 연다.
     (authuser 번호는 브라우저마다 달라서 쓰지 않는다. 로그인 안 된 계정이면 구글이 로그인 화면을 띄운다.)
   · 관리자 링크: 「로그인 필요 — 비밀번호는 직접」 표시.
   · 「실행 요청문 복사」 전: 이 업무에 필요한 로그인 체크리스트. 확인 안 된 곳이 있으면 한 번 더 묻는다.
   계정 매핑은 2026-09-30 두 계정(와이즈 u/0 · 오션블루 u/1)으로 각 링크를 직접 열어 확인한 결과다. */
(function () {
  var ACCT = {
    ocean: { name: '오션블루 구글', email: 'dev@oceanbleu.co.kr' },
    wise: { name: '와이즈 구글', email: 'wisemanroot@gmail.com' }
  };
  /* 구글 문서·폴더 id → 계정. both = 두 계정 모두 열림, none = 두 계정 모두 권한 없음 */
  var GID = {
    '1azwDHc2YTYAr80YK-cKyaZ2-AosNK9Fyt-LuAbVCf_c': 'both',   /* 2026년 헬스케어 데이터 관리 */
    '19P6ZrG_wjHI8t2uDkDSycuPc2Dvs99N_DtrefMzhGk8': 'both',   /* 건강뉴스 스크립트 */
    '1peCBYOxvvToF86Q5CFZEBr71Gtag9KgI': 'ocean',             /* LGU+ 배너 가이드 */
    '1X1bpeg9L43qSSLtehtmFsv3kizOzA-qh': 'wise',              /* 11. 디자인 › _광고 */
    '1iOBc4Yk6GOJH4q8C9r3qS-jfkvbB8mUa': 'wise',              /* 외부가입창 가이드 폴더 */
    '11hyp9D9ivGAla219ac9MDfzjGgJdMVCM': 'wise',              /* [3사] 가이드 문서 */
    '1aQ7XeI0AYa5JcZQ1-7STFQVeoVmKe5qk': 'wise',              /* 03. 헬스케어 › 03.운영 */
    '1RpIONK2IeerZ73TyH6gb-Sr2vb0W-NjP': 'wise',              /* 퀴즈 등록 양식 */
    '1WrHE6WfbxP-eBRxblYM4SqmJnrhnFSoJ': 'none'               /* LGU+ 전달 양식 폴더 — 두 계정 모두 404 */
  };
  var ADMIN = [
    [/adm\.passhealthcare\.com/, '오션 관리자', 'https://adm.passhealthcare.com'],
    [/admin\.firstmindcare\.com/, 'MINDCARE 관리자', 'https://admin.firstmindcare.com'],
    [/34\.64\.151\.248:8501/, '분석도구 (인증 30분 유지)', 'http://34.64.151.248:8501'],
    [/developer\.pincrux\.com/, '핀크럭스 관리자', 'https://developer.pincrux.com/login.html']
  ];

  function classify(href) {
    var u; try { u = new URL(href, location.href); } catch (e) { return null; }
    if (/analytics\.google\.com$/.test(u.host)) return { kind: 'google', acct: 'ocean' };
    if (/^(docs|drive)\.google\.com$/.test(u.host)) {
      var m = u.pathname.match(/\/d\/([\w-]{20,})|\/folders\/([\w-]{20,})/);
      var id = m && (m[1] || m[2]);
      return { kind: 'google', acct: (id && GID[id]) || 'unknown' };
    }
    for (var i = 0; i < ADMIN.length; i++) if (ADMIN[i][0].test(u.host + u.pathname)) return { kind: 'admin', name: ADMIN[i][1], home: ADMIN[i][2] };
    return null;
  }
  function withAccount(href, acct) {
    var u = new URL(href, location.href);
    u.searchParams.set('authuser', ACCT[acct].email);
    if (/analytics\.google\.com$/.test(u.host) && !u.hash) u.hash = '#/a276347105p475743220/reports/intelligenthome';
    return u.toString();
  }
  function tagText(c) {
    if (c.kind === 'admin') return ['admin', '로그인 필요 · 비밀번호는 직접 입력'];
    if (c.acct === 'ocean' || c.acct === 'wise') return [c.acct, ACCT[c.acct].name + ' · ' + ACCT[c.acct].email];
    if (c.acct === 'both') return ['both', '구글 계정: 오션블루·와이즈 모두 가능'];
    if (c.acct === 'none') return ['warn', '두 구글 계정 모두 권한 없음 — 담당자 확인 필요'];
    return ['warn', '구글 계정 미확인'];
  }

  /* ---------- 링크 꾸미기 ---------- */
  function decorate(root) {
    (root || document).querySelectorAll('a[href]').forEach(function (a) {
      if (a.dataset.lg === '1' || a.closest('.appbar') || a.closest('.lg-box')) return;
      var c = classify(a.getAttribute('href'));
      if (!c) return;
      a.dataset.lg = '1';
      if (c.kind === 'google' && (c.acct === 'ocean' || c.acct === 'wise')) a.href = withAccount(a.getAttribute('href'), c.acct);
      var t = tagText(c), b = document.createElement('span');
      b.className = 'lg-tag lg-' + t[0];
      b.textContent = t[1];
      a.appendChild(b);
    });
  }

  /* ---------- 로그인 체크리스트 ---------- */
  function needsFor(skill) {
    var need = [], seen = {};
    ((skill && skill.links) || []).forEach(function (k) {
      var l = (window.OPS_LINKS || {})[k]; if (!l || !l.url) return;
      var c = classify(l.url); if (!c) return;
      var key, row;
      if (c.kind === 'admin') { key = c.name; row = { key: key, label: c.name, note: '비밀번호·인증번호는 담당자가 직접 입력', url: c.home }; }
      else if (c.acct === 'ocean' || c.acct === 'wise') { key = c.acct; row = { key: key, label: ACCT[c.acct].name + ' 로그인', note: ACCT[c.acct].email, url: withAccount(l.url, c.acct) }; }
      else return;
      if (!seen[key]) { seen[key] = 1; need.push(row); }
    });
    return need;
  }
  function currentSkill() {
    var h = document.querySelector('main h2'); var name = h && h.textContent.trim();
    return (window.OPS_SKILLS || []).filter(function (s) { return s.name === name; })[0];
  }
  var done = {};   /* 업무 이름 → { 시스템: true } — 창을 닫으면 초기화(로그인은 매번 다시 확인) */
  function renderChecklist() {
    var btn = document.getElementById('copyPacket'); if (!btn) return;
    var skill = currentSkill(); var need = needsFor(skill);
    var box = document.getElementById('lgBox');
    var sig = (skill && skill.id) + '|' + need.map(function (n) { return n.key; }).join(',');
    if (box && box.dataset.sig === sig) return;
    if (box) box.remove();
    if (!need.length) return;
    var st = done[skill.id] = done[skill.id] || {};
    box = document.createElement('div');
    box.id = 'lgBox'; box.className = 'lg-box'; box.dataset.sig = sig;
    box.innerHTML = '<b>실행 전에 로그인할 곳</b><span class="lg-sub">Claude가 이 화면들을 대신 여는데, 로그인이 풀려 있으면 중간에 멈춥니다. 먼저 열어서 로그인해 두세요.</span>' +
      need.map(function (n) {
        return '<label class="lg-row"><input type="checkbox" data-k="' + n.key + '"' + (st[n.key] ? ' checked' : '') + '>' +
          '<span class="lg-name">' + n.label + '</span><span class="lg-note">' + n.note + '</span>' +
          '<a class="lg-open" href="' + n.url + '" target="_blank" rel="noopener">열어서 로그인 ↗</a></label>';
      }).join('');
    box.addEventListener('change', function (e) { if (e.target.dataset.k) st[e.target.dataset.k] = e.target.checked; });
    var actions = btn.closest('.actions');
    actions.parentNode.insertBefore(box, actions);
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('#copyPacket'); if (!btn) return;
    var skill = currentSkill(); if (!skill) return;
    var st = done[skill.id] || {};
    var left = needsFor(skill).filter(function (n) { return !st[n.key]; }).map(function (n) { return '· ' + n.label + (n.key.indexOf('@') < 0 && ACCT[n.key] ? ' (' + ACCT[n.key].email + ')' : ''); });
    if (left.length && !confirm('아직 로그인 확인을 안 한 곳이 있습니다.\n\n' + left.join('\n') + '\n\n로그인하지 않으면 Claude가 중간에 멈춥니다. 그래도 요청문을 복사할까요?')) {
      e.preventDefault(); e.stopImmediatePropagation();
    }
  }, true);

  var css = document.createElement('style');
  css.textContent =
    '.lg-tag{display:inline-block;margin-left:8px;padding:1px 7px;border-radius:999px;font-size:11px;font-weight:600;line-height:1.6;vertical-align:middle;white-space:nowrap}' +
    '.lg-ocean{background:#e3eefb;color:#1d4f91}.lg-wise{background:#e8f4ea;color:#23663a}.lg-both{background:#eef1f4;color:#4b5563}' +
    '.lg-admin{background:#fff4dd;color:#8a5a00}.lg-warn{background:#fde2e1;color:#9b1c1c}' +
    '@media (prefers-color-scheme:dark){.lg-ocean{background:#1c2c44;color:#9cc3f5}.lg-wise{background:#1b3222;color:#9ad9a8}.lg-both{background:#262c36;color:#c3cad3}.lg-admin{background:#3a2e12;color:#f2c76b}.lg-warn{background:#3d1a1a;color:#f3a3a3}}' +
    '.lg-box{margin:10px 0 12px;padding:12px 14px;border:1px solid rgba(138,90,0,.35);border-radius:10px;background:rgba(255,244,221,.5)}' +
    '@media (prefers-color-scheme:dark){.lg-box{background:rgba(58,46,18,.45)}}' +
    '.lg-box b{display:block;font-size:13.5px}.lg-sub{display:block;font-size:12px;opacity:.8;margin:2px 0 8px}' +
    '.lg-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:5px 0;font-size:13px;cursor:pointer}' +
    '.lg-name{font-weight:600}.lg-note{opacity:.75;font-size:12px}.lg-open{margin-left:auto;font-size:12px;font-weight:600}';
  document.head.appendChild(css);

  function tick() { decorate(document); renderChecklist(); }
  new MutationObserver(function () { clearTimeout(tick.t); tick.t = setTimeout(tick, 60); }).observe(document.body, { childList: true, subtree: true });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', tick); else tick();
})();
