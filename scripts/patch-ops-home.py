#!/usr/bin/env python3
"""실행 센터(ops-center.html)에 「메인으로 가기」 버튼을 넣는다.

스킬 상세로 들어가 실행 버튼을 누른 뒤 처음 화면(①②③ 고르기)으로 한 번에 돌아온다.
 · 상세 화면 맨 위 · 맨 아래에 버튼, 스크롤을 내리면 오른쪽 아래에 떠 있는 버튼
 · 매뉴얼 안(iframe)에서는 부모 화면도 맨 위로 올린다
여러 번 돌려도 한 번만 들어간다.
"""
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'ops-center.html'
MARK = '/* 메인으로 가기 */'

CSS_OLD = '</style>'
CSS_NEW = MARK + '''
.home-bar{display:flex;align-items:center;gap:10px;margin:18px 0 0}
.home-bar .sp{flex:1}
.home-btn{
  appearance:none;display:inline-flex;align-items:center;gap:6px;cursor:pointer;
  border:1px solid var(--border-strong);background:var(--surface);color:var(--ink-muted);
  font:inherit;font-size:12.5px;font-weight:600;padding:7px 13px;border-radius:999px;
}
.home-btn:hover{border-color:var(--accent);color:var(--accent-ink);background:var(--accent-soft)}
.home-fab{
  position:fixed;right:18px;bottom:18px;z-index:40;display:none;
  box-shadow:0 6px 20px -8px rgba(20,30,40,.45);background:var(--surface)
}
.home-fab.on{display:inline-flex}
@media print{.home-bar,.home-fab{display:none!important}}
</style>'''

# 상세 화면 맨 위 — 되돌아가기 줄
TOP_OLD = """    host.innerHTML =
      '<div class="sec-h"><span class="dep">4</span><h2>스킬 사용법 설명</h2></div>' +"""
TOP_NEW = """    host.innerHTML =
      '<div class="home-bar"><button type="button" class="home-btn" data-home="1">← 메인으로 가기</button>' +
        '<span class="sp"></span><span class="small faint">' + esc(s.name) + '</span></div>' +
      '<div class="sec-h"><span class="dep">4</span><h2>스킬 사용법 설명</h2></div>' +"""

# 상세 화면 맨 아래 — 실행 버튼을 누른 뒤 바로 돌아갈 수 있게
BOTTOM_OLD = """        '<div id="runs"></div><div id="tool"></div>' +
      '</div></div>';"""
BOTTOM_NEW = """        '<div id="runs"></div><div id="tool"></div>' +
      '</div></div>' +
      '<div class="home-bar"><button type="button" class="home-btn" data-home="1">← 메인으로 가기</button>' +
        '<span class="sp"></span><span class="small faint">다른 업무를 고르려면 누르세요</span></div>';"""

# 메인으로 돌아가기 · 떠 있는 버튼
RENDER_OLD = """  function render() { writeHash(); renderPicker(); renderList(); renderDetail(); sendHeight(); }"""
RENDER_NEW = """  function render() { writeHash(); renderPicker(); renderList(); renderDetail(); sendHeight(); toggleFab(); }

  /* ---------- 메인으로 가기 ---------- */
  function goHome() {
    sel.type = null; sel.service = null; sel.telco = null; sel.skill = null;
    render();
    window.scrollTo(0, 0);
    try { if (window.self !== window.top) parent.postMessage({ type: 'ops-scroll-top' }, '*'); } catch (e) {}
    var p = $('#picker'); if (p && p.scrollIntoView) p.scrollIntoView({ block: 'start' });
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-home]');
    if (b) { e.preventDefault(); goHome(); }
  });

  var fab = document.createElement('button');
  fab.type = 'button'; fab.className = 'home-btn home-fab'; fab.textContent = '← 메인으로 가기';
  fab.setAttribute('data-home', '1');
  document.body.appendChild(fab);
  function toggleFab() {
    var deep = !!sel.skill;
    fab.classList.toggle('on', deep && (window.scrollY > 240 || window.self !== window.top));
  }
  window.addEventListener('scroll', toggleFab);"""

# 매뉴얼 안(iframe)에서 머리말을 통째로 숨기면 ①②③ 고르기 줄까지 사라진다.
# 설명 문구만 숨기고 고르기 줄은 남긴다.
EMBED_OLD = 'body.embedded .top{display:none}'
EMBED_NEW = ('body.embedded .top .crumb,body.embedded .top h1,body.embedded .top .lede{display:none}'
             'body.embedded .top{padding-top:0;margin-top:0}'
             'body.embedded .top .picker{margin-top:0}')

REPL = [(CSS_OLD, CSS_NEW), (EMBED_OLD, EMBED_NEW), (TOP_OLD, TOP_NEW), (BOTTOM_OLD, BOTTOM_NEW), (RENDER_OLD, RENDER_NEW)]


def main():
    s = HTML.read_text(encoding='utf-8')
    if MARK in s:
        print('이미 적용돼 있음 — 건너뜀')
        return
    for old, new in REPL:
        assert old in s, f'기준 문구를 못 찾음: {old[:60]!r}'
        s = s.replace(old, new, 1)   # 첫 번째 것에만 넣는다(</style> 는 여러 개)
    HTML.write_text(s, encoding='utf-8')
    print('메인으로 가기 버튼 적용 완료')


if __name__ == '__main__':
    main()
