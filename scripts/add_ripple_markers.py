#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""web/assets/source/examitems-page.svg의 6개 강조 마커에 동심원(ripple)
애니메이션을 켠다.

포스터 원본(Artboard3)을 그대로 추출하면 마커 6곳(뇌·심혈관·폐·갑상선·소화기·
비뇨기)마다 정적인 빨강 원이 이미 4개씩 있다(각자 <g transform=...>로 한 겹씩
감싸진 채 형제로 연달아 있음 — Affinity의 도형별 개별 group 내보내기 방식).
투명도 패턴은 항상 0.45×3 + 0.8×1이며, 순서대로 ripple 바깥→안쪽 3겹 + 중심
점 하나다. 이 스크립트는 그 4개를 문서 순서 그대로
class="body-point-ripple r1"/"r2"/"r3"/"body-point-dot"로 바꾸고(기존
style 속성은 제거 — 클래스가 fill을 대신 정의함), 파일 맨 위에
web/styles/body-points.css를 <?xml-stylesheet?>로 추가해 애니메이션
(@keyframes body-point-ripple)을 켠다.

**`scripts/sync_exam_items.py`로 포스터를 다시 추출한 뒤에는 이 스크립트도
다시 실행해야 한다** — 원본 소스에는 클래스가 없어 재추출할 때마다 사라진다.
이미 변환된 파일(circle에 class가 있고 style이 없는 상태)에 다시 실행하면
매칭 실패로 assert가 터진다 — 그러면 이미 적용된 상태이니 다시 실행할 필요가
없다는 뜻이다.

사용법:
    python scripts/add_ripple_markers.py
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("serif", "http://www.serif.com/")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = ROOT / "web" / "assets" / "source" / "examitems-page.svg"

STYLESHEETS = [
    "../../styles/body-points.css",
    "../../styles/poster-fonts.css",
]


def q(tag):
    return f"{{{SVG_NS}}}{tag}"


def is_marker_circle(el):
    if el.tag != q("circle"):
        return False
    style = el.get("style") or ""
    return "rgb(230,0,0)" in style and el.get("r") == "13"


def wrapped_marker_circle(el):
    """마커 원 하나하나가 자기만의 <g transform=...>로 감싸져 있다
    (Affinity의 도형별 개별 group 내보내기 패턴) -- el이 그런 래퍼면
    안의 circle을 돌려준다."""
    if el.tag != q("g"):
        return None
    kids = list(el)
    if len(kids) == 1 and is_marker_circle(kids[0]):
        return kids[0]
    return None


def main():
    if not SVG_PATH.exists():
        sys.exit(f"파일을 찾을 수 없습니다: {SVG_PATH}")

    tree = ET.parse(SVG_PATH)
    root = tree.getroot()

    converted_groups = 0
    converted_circles = 0

    for parent in root.iter():
        children = list(parent)
        i = 0
        while i < len(children):
            c0 = wrapped_marker_circle(children[i])
            if c0 is not None:
                run = [c0]
                j = i + 1
                while j < len(children):
                    cj = wrapped_marker_circle(children[j])
                    if cj is not None and cj.get("cx") == c0.get("cx") and cj.get("cy") == c0.get("cy"):
                        run.append(cj)
                        j += 1
                    else:
                        break
                if len(run) == 4:
                    labels = ["body-point-ripple r1", "body-point-ripple r2", "body-point-ripple r3", "body-point-dot"]
                    for c, cls in zip(run, labels):
                        c.set("class", cls)
                        if "style" in c.attrib:
                            del c.attrib["style"]
                    converted_groups += 1
                    converted_circles += 4
                i = j
            else:
                i += 1

    if converted_groups == 0:
        sys.exit(
            "정적 마커 원(4개 묶음)을 찾지 못했습니다. 이미 변환됐거나(class가 이미 있음), "
            "포스터 구조가 바뀌었을 수 있습니다."
        )
    if converted_groups != 6:
        sys.exit(f"마커 6개가 아니라 {converted_groups}개가 매칭됐습니다 — 구조를 확인하세요.")

    print(f"변환됨: 마커 {converted_groups}개 ({converted_circles}개 원)")

    tree.write(SVG_PATH, encoding="unicode", xml_declaration=False)
    body = SVG_PATH.read_text(encoding="utf-8")
    if not body.startswith("<svg"):
        sys.exit("예상치 못한 파일 시작 — <svg>로 시작하지 않습니다.")

    prefix = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
    for href in STYLESHEETS:
        prefix += f'<?xml-stylesheet href="{href}" type="text/css"?>\n'
    SVG_PATH.write_text(prefix + body, encoding="utf-8")
    print(f"[{SVG_PATH.relative_to(ROOT)}] 갱신함. 미리보기 서버에서 화면을 새로고침해 확인하세요.")


if __name__ == "__main__":
    main()
