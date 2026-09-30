#!/usr/bin/env python3
"""settlement-workbench.html 의 저장 위치를 브라우저 → 서버(Supabase)로 바꾼다.

화면·계산·양식 코드는 건드리지 않고 저장 계층만 갈아 끼운다.
 · 입력값·설정 JSON  → 테이블 stl_docs   (settle-sync.js 가 담당)
 · 기존 양식 · CTN  → 스토리지 stl-files (IndexedDB 는 사본으로 유지)
새 워크벤치 파일을 받으면 이 스크립트를 다시 돌린다. 여러 번 돌려도 한 번만 들어간다.
"""
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'settlement-workbench.html'
MARK = 'STL_SYNC'

REPL = []

# 1) 동기화 모듈 로드
REPL.append((
    "<script>\n/* ═════════ 업무 정의 ═════════ */",
    "<script src=\"settle-sync.js\"></script>\n<script>\n/* ═════════ 업무 정의 ═════════ */",
))

# 2) 저장소 — 서버 값을 먼저 보고, 저장하면 서버로 올린다
REPL.append((
    """const store = {
  get(k, d) { if (k in mem) return mem[k]; try { const v = localStorage.getItem(k); if (v) return (mem[k] = JSON.parse(v)); } catch (e) {} return d; },
  set(k, v) { mem[k] = v; try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
};""",
    """const store = {
  get(k, d) {
    if (k in mem) return mem[k];
    const sv = STL_SYNC.get(k);                       /* 서버에서 읽어 온 값 */
    if (sv !== undefined) return (mem[k] = sv);
    try { const v = localStorage.getItem(k); if (v) return (mem[k] = JSON.parse(v)); } catch (e) {}
    return d;
  },
  set(k, v) {
    mem[k] = v;
    try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {}   /* 오프라인 사본 */
    STL_SYNC.push(k, v);                                                /* 서버 저장 */
  },
  /* 서버에서 새로 온 값을 반영할 때 — 메모리 사본을 비운다 */
  forget(k) { delete mem[k]; }
};""",
))

# 3) 기존 양식 파일 — IndexedDB 저장 뒤 서버에도 올린다
REPL.append((
    """  try { navigator.storage && navigator.storage.persist && navigator.storage.persist(); } catch (e) {}
  tplWhere[id] = where; return where;
}""",
    """  try { navigator.storage && navigator.storage.persist && navigator.storage.persist(); } catch (e) {}
  tplWhere[id] = where;
  try {                                                /* 서버 업로드 + 목록 갱신 */
    await STL_SYNC.filePut('tpl/' + id + '.xlsx', rec.buf,
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    const meta = store.get('stl.tplmeta', {});
    meta[id] = { name: rec.name, savedAt: rec.savedAt, source: rec.source, size: rec.buf.byteLength };
    store.set('stl.tplmeta', meta);
    where = 'server';
  } catch (e) { console.warn('양식 서버 업로드 실패', e); }
  tplWhere[id] = where; return where;
}""",
))

REPL.append((
    """async function tplGet(id) {
  if (tplMem[id]) return tplMem[id];
  try { const v = await idbGet(await idb(), id); if (v && v.buf) { tplWhere[id] = 'idb'; return (tplMem[id] = v); } } catch (e) {}""",
    """async function tplGet(id) {
  if (tplMem[id]) return tplMem[id];
  try {                                                /* 서버에 있으면 서버 것이 정본 */
    const meta = (store.get('stl.tplmeta', {}) || {})[id];
    if (meta) {
      const f = await STL_SYNC.fileGet('tpl/' + id + '.xlsx');
      if (f && f.buf && f.buf.byteLength) {
        tplWhere[id] = 'server';
        return (tplMem[id] = { name: meta.name, savedAt: meta.savedAt, source: meta.source, buf: f.buf });
      }
    }
  } catch (e) { console.warn('양식 서버 조회 실패', e); }
  try { const v = await idbGet(await idb(), id); if (v && v.buf) { tplWhere[id] = 'idb'; return (tplMem[id] = v); } } catch (e) {}""",
))

REPL.append((
    """async function tplDel(id) {
  delete tplMem[id]; delete tplWhere[id];""",
    """async function tplDel(id) {
  delete tplMem[id]; delete tplWhere[id];
  try {                                                /* 서버에서도 지운다 */
    await STL_SYNC.fileDel('tpl/' + id + '.xlsx');
    const meta = store.get('stl.tplmeta', {}); delete meta[id]; store.set('stl.tplmeta', meta);
  } catch (e) {}""",
))

# 4) CTN 증빙 — 서버 우선
REPL.append((
    """async function ctnPut(ym, obj) {
  ctnMem[ym] = obj;""",
    """async function ctnPut(ym, obj) {
  ctnMem[ym] = obj;
  try { await STL_SYNC.jsonPut('ctn/' + ym + '.json', obj); } catch (e) { console.warn('CTN 서버 저장 실패', e); }""",
))

REPL.append((
    """async function ctnGet(ym) {
  if (ctnMem[ym]) return ctnMem[ym];""",
    """async function ctnGet(ym) {
  if (ctnMem[ym]) return ctnMem[ym];
  try { const v = await STL_SYNC.jsonGet('ctn/' + ym + '.json'); if (v) return (ctnMem[ym] = v); } catch (e) {}""",
))

# 5) 부팅 — 서버 값을 먼저 읽고 화면을 그린다
REPL.append((
    """if (state.view !== 'dash' && !T[state.view]) state.view = 'dash';
loadMonth(); renderAll();""",
    """if (state.view !== 'dash' && !T[state.view]) state.view = 'dash';

/* 서버 값을 먼저 읽고 화면을 그린다. 다른 사람이 저장하면 보고 있는 달만 새로 고친다. */
STL_SYNC.init({
  onRemote(keys) {
    const mine = keys.filter(k => k === 'stl.settings.v1' || k === monthKey(state.ym) || k === 'stl.tplmeta');
    if (!mine.length) return;
    if (document.activeElement && ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
    mine.forEach(store.forget);
    settings = store.get('stl.settings.v1', {});
    loadMonth(); renderAll();
    toast('다른 사람이 저장한 내용을 가져왔습니다.');
  }
}).then(okOnline => {
  loadMonth(); renderAll();
  if (!okOnline) toast('서버에 연결하지 못했습니다 — 이 브라우저에만 저장됩니다.');
});""",
))


def main():
    s = HTML.read_text(encoding='utf-8')
    if MARK in s:
        print('이미 적용돼 있음 — 건너뜀')
        return
    for old, new in REPL:
        assert s.count(old) == 1, f'기준 문구를 한 번만 찾지 못함: {old[:60]!r}'
        s = s.replace(old, new, 1)
    HTML.write_text(s, encoding='utf-8')
    print('서버 저장 적용 완료 — supabase/settlement.sql 을 먼저 실행해 둘 것')


if __name__ == '__main__':
    main()
