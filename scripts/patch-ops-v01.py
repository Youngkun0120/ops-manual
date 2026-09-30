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

# 4) 로그인 · 구글 계정 안내 — scripts/assets/login-guide.js 를 본문 끝에 넣는다.
LG_MARK = "<!-- ops-manual: login-guide -->"
if LG_MARK not in s:
    lg = (Path(__file__).resolve().parent / "assets" / "login-guide.js").read_text(encoding="utf-8")
    i = s.rindex("</body>")
    s = s[:i] + LG_MARK + "<script>" + lg + "</script>" + s[i:]

out.write_text(s, encoding="utf-8")
print(f"{out.name} 저장 ({len(s):,}자)")
