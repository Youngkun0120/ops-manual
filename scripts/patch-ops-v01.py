#!/usr/bin/env python3
"""전임자 최종판 「01_운영실행센터_Claude확장형.html」(2026-09-28)을 상세 업무 처리(ops-center.html)로 쓴다.

    python3 scripts/patch-ops-v01.py <01_운영실행센터_Claude확장형.html 경로>

원본은 그대로 두고 두 군데만 고쳐서 ops-center.html 로 저장한다(멱등).
  1) 업무 바로 열기 — 매뉴얼의 「이 업무 실행하기」가 넘기는 주소(#/유형/서비스/통신사/<업무 id> 또는 ?skill=)로
     해당 업무를 연다. 13종 시절 id 3개는 01에서 합쳐진 업무로 돌린다.
  2) 매뉴얼 안(iframe)에서는 01 자체 상단 바(「업무 매뉴얼 ↗」 링크)를 숨긴다 — 매뉴얼 탭과 겹친다.
  3) 높이 알림 보강  4) 로그인 · 구글 계정 안내(scripts/assets/login-guide.js)
  5) authuser 번호 → 이메일  6) 비어 있던 GA 속성 링크 채움
"""
import sys
from pathlib import Path

src = Path(sys.argv[1])
out = Path(__file__).resolve().parent.parent / "ops-center.html"
s = src.read_text(encoding="utf-8")

OLD_INIT = "renderList();const remembered=state.records.find(r=>r.id===state.active);if(remembered){current=remembered;renderDesk();renderList();}else selectSkill(skills[0]);"
NEW_INIT = ("renderList();"
            "const wanted=(function(){var A={'healthcare-ga-daily-input':'healthcare-daily-aggregation','monthly-member-sms-handover':'monthly-member-sms-copy','gdn-ad-monitoring-rotation':'competitor-gdn-signup-violation-monitoring'};"
            "var w=new URLSearchParams(location.search).get('skill')||decodeURIComponent((location.hash||'').replace(/^#\\/?/,'').split('/')[3]||'');"
            "w=A[w]||w;return skills.find(function(x){return x.id===w;});})();"
            "const remembered=state.records.find(r=>r.id===state.active);"
            "if(wanted)selectSkill(wanted);else if(remembered){current=remembered;renderDesk();renderList();}else selectSkill(skills[0]);")
assert s.count(OLD_INIT) == 1, "초기화 코드 위치가 바뀌었다 — 원본이 달라졌는지 확인"
s = s.replace(OLD_INIT, NEW_INIT, 1)

MARK = "<!-- ops-manual: in-frame -->"
# 3) 01 은 body 크기만 지켜보는데, body 가 화면 높이로 고정돼 있어 매뉴얼 iframe 이 최소 높이에 머문다(이중 스크롤).
#    실제로 자라는 main 을 지켜보며 문서 전체 높이를 부모(ops.js)에 알린다.
FRAME = (MARK + "<script>if(window.self!==window.top){document.documentElement.classList.add('in-frame');"
         "window.addEventListener('load',function(){var post=function(){parent.postMessage({type:'ops-model-height',height:document.documentElement.scrollHeight},'*');};"
         "new ResizeObserver(post).observe(document.querySelector('main')||document.body);post();});}</script>"
         "<style>.in-frame .appbar{display:none}</style>")
if MARK not in s:
    s = s.replace("</head>", FRAME + "</head>", 1)

# 5) authuser 번호(2)는 브라우저에 로그인한 계정 순서라 사람마다 다르다 — 이메일로 바꾼다(구글이 그 계정으로 연다).
s = s.replace("label: 'GA4 (dev@oceanbleu.co.kr, authuser=2)'", "label: 'GA4 (오션블루 구글 · dev@oceanbleu.co.kr)'")
s = s.replace("analytics/web/?authuser=2'", "analytics/web/?authuser=dev@oceanbleu.co.kr'")
s = s.replace("GA4(dev@ 계정, authuser=2)", "GA4(dev@oceanbleu.co.kr 계정 — 주소에 ?authuser=dev@oceanbleu.co.kr)")
s = s.replace("(구글 계정 `dev@oceanbleu.co.kr`, `?authuser=2`)", "(구글 계정 `dev@oceanbleu.co.kr` — 주소에 `?authuser=dev@oceanbleu.co.kr`, 번호는 사람마다 다르니 쓰지 않는다)")
assert "authuser=2" not in s, "authuser=2 가 남았다"

# 6) 원본에서 「링크 필요」로 비어 있던 GA 속성 주소를 채운다(growth-loop 수집에 쓰는 같은 속성 — 계정 dev@oceanbleu.co.kr).
GA = "https://analytics.google.com/analytics/web/?authuser=dev@oceanbleu.co.kr#/"
for a, b in [
    ("ga4_hc:            { label: 'GA4 › [SKT/KT/LGU+] app_passhealthcare_2.0', url: null, need: '속성 홈 주소 (analytics.google.com/…/p숫자/…)' }",
     "ga4_hc:            { label: 'GA4 › [SKT/KT/LGU+] app_passhealthcare_2.0', url: '" + GA + "a276347105p475743220/reports/intelligenthome' }"),
    ("ga4_hc_explore:    { label: 'GA4 › 탐색 「자유 양식」 보고서', url: null, need: '탐색 보고서 주소' }",
     "ga4_hc_explore:    { label: 'GA4 › 탐색 (헬스케어 속성 탐색 목록 — 「자유 양식」 선택)', url: '" + GA + "analysis/a276347105p475743220' }"),
    ("ga4_cloud:         { label: 'GA4 › PASS_Cloud', url: null, need: '속성 홈 주소' }",
     "ga4_cloud:         { label: 'GA4 › PASS_Cloud', url: '" + GA + "a276347105p535290657/reports/intelligenthome' }"),
]:
    if a in s:
        s = s.replace(a, b, 1)

# 7) Claude 결과 읽기 보강 — 답변에 ```json 이 없거나 줄바꿈·따옴표 때문에 JSON.parse 가 깨지는 일이 잦다.
#    ① 코드블록이 여럿이면 전부 시도 ② 자주 나는 흠(스마트 따옴표 · 끝 쉼표 · 문자열 안 줄바꿈)은 고쳐서 다시 시도
#    ③ 그래도 안 되면 답변의 표(마크다운 · 탭)를 읽는다 ④ 실패 화면에 「JSON만 다시 달라」 요청문을 복사 버튼으로 둔다
OLD_EXTRACT = """  K.extractJSON = function (text) {
    var t = String(text || '').trim();
    if (!t) throw new Error('붙여넣은 내용이 없습니다.');
    var fence = t.match(/```(?:json)?\\s*([\\s\\S]*?)```/i);
    if (fence) t = fence[1].trim();
    var s = t.search(/[\\[{]/);
    if (s < 0) throw new Error('JSON 블록을 찾지 못했습니다. Claude 답변의 ```json … ``` 부분을 통째로 붙여넣으세요.');
    var open = t[s], close = open === '[' ? ']' : '}', e = t.lastIndexOf(close);
    try { return JSON.parse(t.slice(s, e + 1)); }
    catch (err) { throw new Error('JSON 형식이 깨져 있습니다 (' + err.message + '). 답변을 빠짐없이 붙여넣었는지 확인하세요.'); }
  };
"""
NEW_EXTRACT = """  function jsonCandidates(text) {
    var out = [], t = String(text || ''), m, re = /```(?:json)?\\s*([\\s\\S]*?)```/gi;
    while ((m = re.exec(t))) out.push(m[1]);
    for (var i = 0; i < t.length; i++) {              /* 코드블록 밖에 그냥 쓴 경우 — 괄호 짝을 세어 뽑는다 */
      var o = t[i]; if (o !== '{' && o !== '[') continue;
      var close = o === '{' ? '}' : ']', depth = 0, inStr = false, esc = false;
      for (var j = i; j < t.length; j++) {
        var ch = t[j];
        if (inStr) { if (esc) esc = false; else if (ch === '\\\\') esc = true; else if (ch === '"') inStr = false; continue; }
        if (ch === '"') inStr = true;
        else if (ch === o) depth++;
        else if (ch === close && --depth === 0) { out.push(t.slice(i, j + 1)); i = j; break; }
      }
    }
    return out;
  }
  function repairJSON(s) {
    s = String(s).replace(/[\\u201c\\u201d\\u2033]/g, '"').replace(/[\\u2018\\u2019]/g, "'")   /* 스마트 따옴표 */
      .replace(/,\\s*([}\\]])/g, '$1');                                           /* 끝 쉼표 */
    var out = '', inStr = false, esc = false;                                   /* 문자열 안 생줄바꿈 → \\n */
    for (var i = 0; i < s.length; i++) {
      var c = s[i];
      if (inStr) {
        if (esc) { out += c; esc = false; continue; }
        if (c === '\\\\') { out += c; esc = true; continue; }
        if (c === '"') { inStr = false; out += c; continue; }
        if (c === '\\n') { out += '\\\\n'; continue; }
        if (c === '\\r') continue;
        if (c === '\\t') { out += '\\\\t'; continue; }
        out += c; continue;
      }
      if (c === '"') inStr = true;
      out += c;
    }
    return out;
  }
  K.extractJSON = function (text, want) {
    if (!String(text || '').trim()) throw new Error('붙여넣은 내용이 없습니다.');
    var cands = jsonCandidates(text), last = null, ok = function (v) { return v && (!want || want(v)); };
    for (var i = 0; i < cands.length; i++) {
      for (var k = 0; k < 2; k++) {
        try { var v = JSON.parse(k ? repairJSON(cands[i]) : cands[i]); if (ok(v)) return v; last = last || v; }
        catch (err) { last = last || null; }
      }
    }
    if (last) return last;
    if (!cands.length) throw new Error('JSON 블록을 찾지 못했습니다 — Claude 답변 끝의 ```json … ``` 을 통째로 붙여넣으세요. 답변에 아예 없으면 아래 문장으로 다시 요청하세요.');
    throw new Error('JSON 형식이 깨져 있습니다 — 답변을 중간에서 자르지 말고 블록 전체를 붙여넣으세요.');
  };
  /* 답변에 표만 있을 때 — 마크다운 표(| … |)나 탭으로 붙인 표를 회차 행으로 읽는다. */
  var TH = [['date', /발송\\s*일|날짜/], ['time', /시간/], ['target', /타겟|대상/], ['count', /건수|모수/],
            ['title', /타이틀|제목|상단/], ['body', /본문|문구|하단/], ['optout', /수신\\s*거부/],
            ['landing', /랜딩|url|링크/i], ['ctr', /ctr|클릭률/i], ['basis', /근거/]];
  K.rowsFromTable = function (text) {
    var lines = String(text || '').split('\\n').map(function (x) { return x.trim(); })
      .filter(function (x) { return (x.indexOf('|') >= 0 || x.indexOf('\\t') >= 0) && !/^\\|?[\\s|:-]+\\|?$/.test(x); });
    var split = function (x) { return x.replace(/^\\||\\|$/g, '').split(/\\s*\\|\\s*|\\t/).map(function (c) { return c.trim(); }); };
    if (lines.length < 2) throw new Error('표를 찾지 못했습니다.');
    var head = split(lines[0]), map = head.map(function (h) {
      var hit = TH.filter(function (t) { return t[1].test(h); })[0]; return hit ? hit[0] : null;
    });
    if (map.filter(Boolean).length < 3 || map.indexOf('date') < 0) throw new Error('표의 머리글에서 발송일·문구 칸을 찾지 못했습니다.');
    var rows = lines.slice(1).map(function (ln) {
      var c = split(ln), r = {};
      map.forEach(function (k, i) { if (k && c[i]) r[k] = c[i].replace(/<br\\s*\\/?>/gi, '\\n'); });
      return r;
    }).filter(function (r) { return r.date && (r.body || r.title); });
    if (!rows.length) throw new Error('표에서 회차를 읽지 못했습니다.');
    return { rows: rows, _fromTable: true };
  };
  /* 실패했을 때 띄우는 안내 — Claude 에 다시 요청할 문장을 그대로 복사한다. */
  K.RETRY_JSON = '방금 만든 발송계획을 실행 센터용 JSON 블록으로만 다시 줘. 설명 없이 ```json 코드블록 하나만, 회차 1행 = 1객체로.\\n' +
    '{"telco":"KT","service":"서비스명","month":"YYYY-MM","rows":[{"date":"YYYY-MM-DD","time":"","title":"","body":"","optout":"","target":"","count":"","landing":"","ctr":"","basis":""}]}\\n' +
    '줄바꿈은 \\\\n 으로 쓰고, 값 안에 따옴표는 넣지 마.';
  K.rescueBox = function () {
    var id = 'rt' + Math.random().toString(36).slice(2, 8);
    setTimeout(function () {
      var el = document.getElementById(id);
      if (el) el.addEventListener('click', function (e) { K.copy(K.RETRY_JSON, e.currentTarget); });
    }, 0);
    return '<div class="note"><b>JSON 없이 답변이 온 경우</b><div style="margin:6px 0">아래 문장을 복사해 같은 채팅에 그대로 보내면 JSON만 다시 받습니다. ' +
      '또는 답변의 <b>표</b>(발송일 · 문구 열이 있는)를 그대로 복사해 위 칸에 붙여넣어도 읽습니다.</div>' +
      '<button class="btn small" type="button" id="' + id + '">JSON 다시 요청 문장 복사</button></div>';
  };
"""
assert OLD_EXTRACT in s, "extractJSON 위치가 바뀌었다"
s = s.replace(OLD_EXTRACT, NEW_EXTRACT, 1)

OLD_READ = "      try { data = K.extractJSON($('[data-j]', b).value); } catch (e) { $('[data-r]', b).innerHTML = note('danger', esc(e.message)); return; }\n      var rows = data.rows || [], lim = K.num(api.v().limit), issues = [];"
NEW_READ = ("      var raw = $('[data-j]', b).value;\n"
            "      try { data = K.extractJSON(raw, function (v) { return v && Array.isArray(v.rows) && v.rows.length; }); }\n"
            "      catch (e) {\n"
            "        try { data = K.rowsFromTable(raw); K.toast('JSON 대신 표를 읽었습니다 — 값이 맞는지 보고 진행하세요.', 4500); }\n"
            "        catch (e2) { $('[data-r]', b).innerHTML = note('danger', esc(e.message)) + K.rescueBox(); return; }\n"
            "      }\n"
            "      var rows = data.rows || [], lim = K.num(api.v().limit), issues = [];\n"
            "      if (data._fromTable) issues.push('JSON 대신 표에서 읽었습니다 — 표에 없던 칸(수신거부 · 랜딩 URL · 건수 등)은 비어 있으니 엑셀을 받기 전에 확인하세요');")
assert OLD_READ in s, "pushPlan read() 위치가 바뀌었다"
s = s.replace(OLD_READ, NEW_READ, 1)

OLD_PROMPT = "'- 마지막에 실행 센터용 JSON 블록을 붙여줘 (회차 1행 = 1객체):\\n' +"
NEW_PROMPT = ("'- 답변 맨 끝에 실행 센터용 JSON 블록을 반드시 붙여줘 — 엑셀을 만들어 줬더라도 생략하지 말고, ```json 코드블록 하나로, 회차 1행 = 1객체. 값 안 줄바꿈은 \\\\n 으로:\\n' +")
assert OLD_PROMPT in s, "MODE B 프롬프트 위치가 바뀌었다"
s = s.replace(OLD_PROMPT, NEW_PROMPT, 1)

# 4) 로그인 · 구글 계정 안내 — scripts/assets/login-guide.js 를 본문 끝에 넣는다.
LG_MARK = "<!-- ops-manual: login-guide -->"
if LG_MARK not in s:
    lg = (Path(__file__).resolve().parent / "assets" / "login-guide.js").read_text(encoding="utf-8")
    i = s.rindex("</body>")
    s = s[:i] + LG_MARK + "<script>" + lg + "</script>" + s[i:]

out.write_text(s, encoding="utf-8")
print(f"{out.name} 저장 ({len(s):,}자)")
