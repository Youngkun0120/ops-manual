#!/usr/bin/env python3
"""index.html 에 세 번째 탭(정산 업무)을 넣는다.

정산 워크벤치(settlement-workbench.html)는 자체 화면을 가진 앱이라 iframe 으로 띄운다.
patch-ops.py 를 먼저 돌린 뒤에 돌린다. 여러 번 돌려도 한 번만 들어간다.
"""
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'index.html'
MARK = '/* settle patch */'

CSS = MARK + '''
.settle-frame{display:block;width:100%;height:calc(100vh - 140px);min-height:620px;border:1px solid var(--border);border-radius:14px;background:var(--surface)}
.settle-foot{margin-top:10px;font-size:12px;color:var(--ink-faint)}
body.settle-mode .sidebar{display:none}
body.settle-mode .content{padding-top:10px}
'''

TAB_OLD = """      <button data-tab="ops" onclick="location.hash='#/ops/-/-/-'">상세 업무 처리</button>"""
TAB_NEW = TAB_OLD + """
      <button data-tab="settle" onclick="location.hash='#/settle'">정산 업무</button>"""

ROUTE_OLD = """  /* ops.js patch — 상세 업무 처리 탭 */
  var isOps = id.split('/')[0]==='ops';
  document.body.classList.toggle('ops-mode', isOps);
  document.querySelectorAll('#tabbar button').forEach(function(b){
    b.classList.toggle('on', b.getAttribute('data-tab')===(isOps?'ops':'manual'));
  });"""
ROUTE_NEW = """  /* ops.js patch — 상세 업무 처리 탭 · settle patch — 정산 업무 탭 */
  var head = id.split('/')[0];
  var isOps = head==='ops', isSettle = head==='settle';
  document.body.classList.toggle('ops-mode', isOps);
  document.body.classList.toggle('settle-mode', isSettle);
  var cur = isOps ? 'ops' : (isSettle ? 'settle' : 'manual');
  document.querySelectorAll('#tabbar button').forEach(function(b){
    b.classList.toggle('on', b.getAttribute('data-tab')===cur);
  });
  if(isSettle){
    document.getElementById('pageBody').innerHTML = renderSettle();
    document.getElementById('content').scrollTop = 0;
    window.scrollTo(0,0);
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('scrim').classList.remove('open');
    return;
  }"""

HASH_OLD = """  if(h.split('/')[0]==='ops') return h;   /* ops.js patch */"""
HASH_NEW = """  if(h.split('/')[0]==='ops') return h;   /* ops.js patch */
  if(h.split('/')[0]==='settle') return h;   /* settle patch */"""


def main():
    s = HTML.read_text(encoding='utf-8')
    if MARK in s:
        print('이미 적용돼 있음 — 건너뜀')
        return
    for old in (TAB_OLD, ROUTE_OLD, HASH_OLD, 'body.ops-mode .sidebar{display:none}',
                '<script src="ops.js"></script>'):
        assert old in s, f'기준 문구를 못 찾음: {old[:40]}'

    s = s.replace('body.ops-mode .sidebar{display:none}', CSS + 'body.ops-mode .sidebar{display:none}', 1)
    s = s.replace(TAB_OLD, TAB_NEW, 1)
    s = s.replace(ROUTE_OLD, ROUTE_NEW, 1)
    s = s.replace(HASH_OLD, HASH_NEW, 1)
    s = s.replace('<script src="ops.js"></script>', '<script src="ops.js"></script>\n<script src="settle.js"></script>', 1)

    HTML.write_text(s, encoding='utf-8')
    print('정산 업무 탭 적용 완료')


if __name__ == '__main__':
    main()
