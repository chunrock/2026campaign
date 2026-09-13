"""
web/index.html의 현재 화면(포스터 4페이지)을 그대로 정적 PDF 파일로 구워
web/assets/2026-gunjin-campaign.pdf에 저장한다. "PDF로 저장" 버튼은 이제
window.print()가 아니라 이 파일을 직접 다운로드하므로, 포스터 디자인이나
내용이 바뀌면(재추출·엑셀 동기화 등) 이 스크립트를 다시 실행해 PDF도 갱신해야
한다. 실행 전 미리보기 서버가 떠 있어야 한다: python devserver.py 8810 web

사용법: python scripts/generate_poster_pdf.py
"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "web" / "assets" / "2026-gunjin-campaign.pdf"
TMP_PATH = OUT_PATH.with_suffix(".raw.pdf")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8810/", wait_until="load")

        # lazy-poster.js가 표지 이후 나머지 3페이지를 순차 로딩하므로,
        # 4개 poster-object 전부 실제 data가 채워질 때까지 기다린다.
        page.wait_for_function(
            """() => Array.from(document.querySelectorAll('.poster-object'))
                  .every(o => o.getAttribute('data'))"""
        )
        page.wait_for_timeout(1500)

        page.emulate_media(media="print")
        page.pdf(
            path=str(TMP_PATH),
            format="A4",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            prefer_css_page_size=True,
        )
        browser.close()

    # Chrome의 print-to-pdf 출력은 중복 스트림이 많아 용량이 커서(약 24MB),
    # pymupdf로 무손실 최적화(중복 객체 제거+재압축)해 약 1/3로 줄인다.
    import pymupdf

    doc = pymupdf.open(str(TMP_PATH))
    doc.save(str(OUT_PATH), garbage=4, deflate=True, clean=True)
    doc.close()
    TMP_PATH.unlink()

    print(f"생성 완료: {OUT_PATH} ({OUT_PATH.stat().st_size / 1024 / 1024:.1f}MB, {pymupdf.open(str(OUT_PATH)).page_count}페이지)")


if __name__ == "__main__":
    main()
