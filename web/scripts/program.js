// "01 종합건진 프로그램" 카드 그리드를 web/data/program.js(엑셀에서 생성)로 렌더링한다.
(function () {
  function rowHtml(row) {
    var label = row.label ? row.label + " " : "";
    var normal = row.normal != null
      ? '<span class="strike">정상 ' + row.normal + '만원</span>'
      : "";
    return '<div class="p-row">' + label + "<b>" + row.price + "만원</b>" + normal + "</div>";
  }

  function programHtml(program) {
    return (
      '<div class="program-card"><div class="p-name">' + program.name + "</div>" +
      program.rows.map(rowHtml).join("") +
      "</div>"
    );
  }

  function render() {
    var grid = document.getElementById("programGrid");
    if (!grid || !window.PROGRAM_ITEMS) return;
    grid.innerHTML = window.PROGRAM_ITEMS.map(programHtml).join("");
  }

  document.addEventListener("DOMContentLoaded", render);
})();
