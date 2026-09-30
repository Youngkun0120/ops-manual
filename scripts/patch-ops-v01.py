#!/usr/bin/env python3
"""전임자 최종판 「01_운영실행센터_Claude확장형.html」(2026-09-28)을 상세 업무 처리(ops-center.html)로 쓴다.

    python3 scripts/patch-ops-v01.py <01_운영실행센터_Claude확장형.html 경로>

원본은 그대로 두고 두 군데만 고쳐서 ops-center.html 로 저장한다(멱등).
  1) 업무 바로 열기 — 매뉴얼의 「이 업무 실행하기」가 넘기는 주소(#/유형/서비스/통신사/<업무 id> 또는 ?skill=)로
     해당 업무를 연다. 13종 시절 id 3개는 01에서 합쳐진 업무로 돌린다.
  2) 매뉴얼 안(iframe)에서는 01 자체 상단 바(「업무 매뉴얼 ↗」 링크)를 숨긴다 — 매뉴얼 탭과 겹친다.
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

out.write_text(s, encoding="utf-8")
print(f"{out.name} 저장 ({len(s):,}자)")
