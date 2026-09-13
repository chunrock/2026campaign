#!/usr/bin/env python3
"""검진팀 대시보드 미리보기 서버.

`python -m http.server`는 Cache-Control 헤더를 보내지 않아, 브라우저가
Last-Modified 기준으로 자체 판단해 예전 JS/CSS를 재사용하는 문제가 있었다
(파일을 고치고 ?v= 쿼리를 새로 바꿔도 탭에 따라 반영이 안 되는 원인).
모든 응답에 no-store를 강제해 이 문제를 서버 단에서 없앤다.

사용법: python devserver.py <port> <directory>
"""
import sys
import http.server


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8795
    directory = sys.argv[2] if len(sys.argv) > 2 else '.'
    handler = lambda *args, **kwargs: NoCacheHandler(*args, directory=directory, **kwargs)
    http.server.ThreadingHTTPServer(('', port), handler).serve_forever()
