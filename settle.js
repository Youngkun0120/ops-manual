/* =========================================================================
   정산 업무 탭 — 월 정산 워크벤치(settlement-workbench.html)를 iframe 으로 띄운다.
   워크벤치는 자체 머리말·좌측 메뉴를 가진 앱이라 화면 높이에 맞춰 통째로 넣는다.
   입력값은 워크벤치가 브라우저(localStorage)에 저장한다 — 보는 사람 기기에만 남는다.
   ========================================================================= */
(function () {
  var SRC = 'settlement-workbench.html';

  window.renderSettle = function () {
    return '<iframe id="settleFrame" class="settle-frame" src="' + SRC + '" title="월 정산 워크벤치"></iframe>' +
      '<div class="settle-foot">' +
        '<span>입력한 값은 이 브라우저에만 저장됩니다. 다른 기기와 공유되지 않으니 ' +
        '워크벤치의 <b>백업</b> 버튼으로 JSON을 내려받아 보관하세요. ' +
        '넓게 쓰려면 <a class="ops-link" href="' + SRC + '" target="_blank" rel="noopener">새 창으로 열기 ↗</a></span>' +
      '</div>';
  };
})();
