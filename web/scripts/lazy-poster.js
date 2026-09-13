// 첫 페이지(cover-page)를 최우선으로 로딩하고, 나머지 포스터 페이지(프로그램/
// 추가검사항목/VIP)는 이전 페이지의 <object> 로딩이 끝난 뒤 순서대로 하나씩
// 불러온다. 각 포스터 SVG가 쓰는 폰트도 그 시점에야(해당 <object>가 자기 문서를
// 파싱하면서) 요청되므로, 뒤 페이지의 폰트도 자연히 함께 늦게 로딩된다 — 첫 페이지가
// 4개 SVG(4MB대)·모든 폰트와 네트워크를 다투지 않고 먼저 뜬다.
(function(){
  var queue = Array.prototype.slice.call(document.querySelectorAll('.poster-object[data-src]'));
  var first = document.querySelector('.poster-object[data]');

  function loadNext(){
    var obj = queue.shift();
    if(!obj) return;
    obj.addEventListener('load', loadNext, {once:true});
    obj.data = obj.dataset.src;
  }

  if(first){
    first.addEventListener('load', loadNext, {once:true});
  }else{
    loadNext();
  }
})();
