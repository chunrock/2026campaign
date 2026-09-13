#!/usr/bin/env python3
"""data/추가검사항목.xlsx의 항목명·가격을 web/assets/source/examitems-page.svg에 반영한다.

매칭 방법: SVG 안 각 항목의 <text> 요소에 id="exam-{엑셀행번호}-label"
/ "-label2"(2줄인 항목만) / "-price"가 붙어 있다(엑셀 2행 = 1번, ... 31행 = 30번).
이 id는 원본 포스터(source/캠페인 포스터-outlined.svg)를 Affinity에서 만들 때부터
붙어 있던 것이라, 새 항목을 추가/삭제하면 이 스크립트가 아니라 SVG 쪽부터
다시 손봐야 한다(§AGENTS.md "원본 자료 취급" 참고).

2026-09-11부터 "02 추가검사 항목" 페이지는 포스터 4페이지 세트에서 추출한
examitems-page.svg를 쓴다(예전 body-info.svg는 더 이상 화면에 쓰이지 않음).
web/index.html은 이 SVG를 <object>로 외부 참조만 하므로 별도로 갱신할
인라인 사본이 없다 — 이 파일 하나만 고치면 끝이다.

사용법:
    python scripts/sync_exam_items.py
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX_PATH = ROOT / "data" / "추가검사항목.xlsx"
SVG_PATH = ROOT / "web" / "assets" / "source" / "examitems-page.svg"

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("serif", "http://www.serif.com/")
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def q(tag):
    return f"{{{SVG_NS}}}{tag}"


def load_rows():
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb.active
    rows = []
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=1):
        category, name, price, note = row[0], row[1], row[2], row[3]
        if name is None or price is None:
            continue
        rows.append({"n": i, "category": category, "name": str(name).strip(), "price": int(price)})
    return rows


def _resolve_text_targets(root):
    """id="exam-N-label"/"-price"가 <text>에 직접 붙어 있는 경우(예전 body-info.svg
    방식)와, <g>에 붙어 있고 그 안에 <text>가 하나뿐인 경우(source/캠페인 포스터
    원본 방식, examitems-page.svg가 이쪽) 둘 다 지원해 "id -> 실제로 값을 고쳐야
    할 <text> 요소"로 매핑한다."""
    by_id = {}
    for el in root.iter():
        eid = el.get("id")
        if not eid or not eid.startswith("exam-"):
            continue
        tag = el.tag.split("}")[-1]
        if tag == "text":
            by_id[eid] = el
        elif tag == "g":
            texts = [c for c in el if c.tag.split("}")[-1] == "text"]
            if len(texts) == 1:
                by_id[eid] = texts[0]
    return by_id


def _full_text(el):
    """el.text만으로는 부족하다 — 원본 포스터는 커닝 때문에 마지막 한두 글자를
    <tspan>으로 따로 잘라 넣은 항목이 있다(예: "· 뇌 C" + <tspan>T</tspan>).
    비교용으로는 텍스트 전체(자손의 text까지 포함)를 이어붙여야 한다."""
    return "".join(el.itertext())


def _set_flat_text(el, new_text):
    """새 텍스트를 <text>의 .text에 통째로 넣고, 커닝용으로 잘려 있던 <tspan>
    자손은 전부 제거한다. 안 지우면 옛 tspan이 엉뚱한 절대좌표(x=...)에 남아
    옛 글자 일부를 새 텍스트 위에 겹쳐 그리거나(우연히 안 보일 수도, 잘못된
    위치에 보일 수도 있음) 어긋난 채로 남는다."""
    for child in list(el):
        el.remove(child)
    el.text = new_text


def apply_updates(svg_text, rows, source_label):
    """svg_text 안의 id 달린 항목들을 rows 값으로 갱신한다.
    반환값: (수정된 svg_text, 변경 로그 목록)"""
    m = re.search(r"<svg[ >].*?</svg>", svg_text, re.S)
    if not m:
        raise RuntimeError(f"{source_label}: <svg>...</svg> 블록을 찾지 못했습니다.")
    svg_fragment = m.group(0)
    root = ET.fromstring(svg_fragment)

    by_id = _resolve_text_targets(root)
    logs = []

    for row in rows:
        n = row["n"]
        price_el = by_id.get(f"exam-{n}-price")
        label_el = by_id.get(f"exam-{n}-label")
        label2_el = by_id.get(f"exam-{n}-label2")

        if price_el is None or label_el is None:
            logs.append(f"  ! exam-{n}: id를 찾지 못해 건너뜀 (SVG에 항목이 추가/삭제됐을 수 있음)")
            continue

        new_price_text = f"{row['price']:,}원"
        if _full_text(price_el) != new_price_text:
            logs.append(f"  - exam-{n} 가격: {_full_text(price_el)!r} -> {new_price_text!r}")
            _set_flat_text(price_el, new_price_text)

        if label2_el is not None:
            # 2줄로 나뉜 항목(원본 디자인의 줄바꿈). 기존 두 줄을 이어붙인 값이
            # 엑셀 이름과 같으면(=이름 안 바뀜) 줄바꿈을 그대로 두고 손대지 않는다.
            current_combined = _full_text(label_el).lstrip("· ").rstrip() + _full_text(label2_el)
            current_combined = current_combined.replace("+", "").replace(" ", "")
            new_normalized = row["name"].replace("+", "").replace(" ", "")
            if current_combined != new_normalized:
                logs.append(
                    f"  - exam-{n} 항목명이 바뀌어 2줄 배치를 유지할 수 없습니다. "
                    f"1줄로 합쳐 넣었으니 필요하면 SVG에서 줄바꿈 위치를 손으로 조정하세요: {row['name']!r}"
                )
                _set_flat_text(label_el, f"· {row['name']}")
                _set_flat_text(label2_el, "")
        else:
            new_label_text = f"· {row['name']}"
            if _full_text(label_el) != new_label_text:
                logs.append(f"  - exam-{n} 항목명: {_full_text(label_el)!r} -> {new_label_text!r}")
                _set_flat_text(label_el, new_label_text)

    new_fragment = ET.tostring(root, encoding="unicode")
    return svg_text[: m.start()] + new_fragment + svg_text[m.end() :], logs


def main():
    if not XLSX_PATH.exists():
        sys.exit(f"엑셀 파일을 찾을 수 없습니다: {XLSX_PATH}")
    rows = load_rows()
    print(f"엑셀에서 {len(rows)}개 항목을 읽었습니다.")

    svg_text = SVG_PATH.read_text(encoding="utf-8")
    new_svg_text, logs = apply_updates(svg_text, rows, "body-info.svg")
    if logs:
        print(f"[{SVG_PATH.relative_to(ROOT)}]")
        print("\n".join(logs))
        SVG_PATH.write_text(new_svg_text, encoding="utf-8")
        print("완료. 미리보기 서버에서 화면을 새로고침해 확인하세요.")
    else:
        print(f"[{SVG_PATH.relative_to(ROOT)}] 변경 없음. 모든 값이 이미 최신 상태입니다.")


if __name__ == "__main__":
    main()
