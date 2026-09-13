#!/usr/bin/env python3
"""data/종합건진프로그램.xlsx의 값을 web/data/program.js로 반영한다.

매칭 방법: 엑셀은 "프로그램명 | 구분 | 가격(만원) | 정상가(만원) | 비고" 행으로
구성되며, 같은 프로그램명을 가진 연속된 행들이 화면의 카드 한 장(.program-card)
안의 줄(.p-row)이 된다. 구분이 비어 있으면 줄 앞에 라벨을 붙이지 않고,
정상가가 비어 있으면 취소선 정상가를 표시하지 않는다(VIP건진처럼).

web/index.html의 "01 종합건진 프로그램" 카드는 이 데이터를 읽어 화면을
직접 그리는 web/scripts/program.js를 통해 렌더링된다(.program-grid를
비워두고 JS가 채움) — SVG처럼 좌표 동기화가 필요 없어 훨씬 단순하다.

사용법:
    python scripts/sync_program_items.py
"""
import json
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
XLSX_PATH = ROOT / "data" / "종합건진프로그램.xlsx"
JS_PATH = ROOT / "web" / "data" / "program.js"


def load_programs():
    wb = openpyxl.load_workbook(XLSX_PATH, data_only=True)
    ws = wb.active
    programs = []
    by_name = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        name, label, price, normal, note = row[0], row[1], row[2], row[3], row[4]
        if name is None or price is None:
            continue
        name = str(name).strip()
        entry = by_name.get(name)
        if entry is None:
            entry = {"name": name, "rows": []}
            by_name[name] = entry
            programs.append(entry)
        entry["rows"].append({
            "label": str(label).strip() if label is not None else None,
            "price": int(price),
            "normal": int(normal) if normal is not None else None,
        })
    return programs


def main():
    if not XLSX_PATH.exists():
        sys.exit(f"엑셀 파일을 찾을 수 없습니다: {XLSX_PATH}")
    programs = load_programs()
    print(f"엑셀에서 {len(programs)}개 프로그램({sum(len(p['rows']) for p in programs)}개 줄)을 읽었습니다.")

    JS_PATH.parent.mkdir(parents=True, exist_ok=True)
    old_text = JS_PATH.read_text(encoding="utf-8") if JS_PATH.exists() else None
    body = json.dumps(programs, ensure_ascii=False, indent=2)
    new_text = (
        "// 자동 생성 파일 — data/종합건진프로그램.xlsx를 고친 뒤\n"
        "// python scripts/sync_program_items.py 로 다시 만든다. 직접 편집하지 않는다.\n"
        f"window.PROGRAM_ITEMS = {body};\n"
    )

    if new_text != old_text:
        JS_PATH.write_text(new_text, encoding="utf-8")
        print(f"[{JS_PATH.relative_to(ROOT)}] 갱신함. 미리보기 서버에서 화면을 새로고침해 확인하세요.")
    else:
        print(f"[{JS_PATH.relative_to(ROOT)}] 변경 없음. 모든 값이 이미 최신 상태입니다.")


if __name__ == "__main__":
    main()
