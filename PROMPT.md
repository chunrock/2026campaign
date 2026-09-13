# 하네스 재현 마스터 프롬프트 (Self-Contained)

아래 코드블록 **하나만** LLM(Claude Code)에 붙여넣으면, 저장소를 클론하거나 참조하지 않아도 **동일한 하네스 환경**이 그대로 구성됩니다.
저장소 주소·개인 정보는 들어있지 않으며, 프롬프트 자체에 모든 설정이 담겨 있습니다.

> 사용법: 아래 블록 전체를 복사 → Claude Code 프롬프트에 붙여넣기 → "먼저 계획을 보여주고 승인하면 실행" 흐름으로 진행됩니다.

````text
너는 지금부터 내 개발 머신에 "Claude Code 하네스"를 처음부터 구성한다.
아래 명세를 그대로 재현하되, 되돌리기 어려운 변경(파일 덮어쓰기, 플러그인 설치, 셸 설정 수정)은
먼저 무엇을 만들고 바꿀지 계획으로 정리해 보여주고, 내가 승인한 뒤에만 실행한다.
기존 파일이 있으면 덮어쓰기 전에 .bak 백업을 만든다.
API 키·토큰·.pem 같은 비밀정보는 이 명세에 없다. 필요하면 나에게 물어보고 로컬에만 저장한다.

================================================================
[1] ~/.claude/settings.json  — 아래 내용으로 생성
================================================================
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "ANTHROPIC_MODEL": "claude-opus-4-8[1m]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-opus-4-8",
    "CLAUDE_CODE_EFFORT_LEVEL": "high"
  },
  "permissions": {
    "allow": ["Bash(*)","Edit(*)","Write(*)","Read(*)","Glob(*)","Grep(*)","Agent(*)","Skill(*)"]
  },
  "model": "opus[1m]",
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'TODAY=$(date +%Y-%m-%d); HIST_DIR=\"history\"; if [ -d \"$HIST_DIR\" ]; then TODAY_FILES=$(ls $HIST_DIR/${TODAY}_*.md 2>/dev/null); if [ -z \"$TODAY_FILES\" ]; then echo \"[히스토리 훅] 오늘($TODAY) 작업 히스토리 파일이 없습니다. history/${TODAY}_{주제-슬러그}.md 파일을 생성해주세요.\"; else for f in $TODAY_FILES; do echo \"[히스토리 훅] 기존 파일: $f 상태를 갱신해주세요.\"; done; fi; fi'"
          }
        ]
      }
    ]
  },
  "effortLevel": "high",
  "skipDangerousModePermissionPrompt": true,
  "teammateMode": "tmux"
}

================================================================
[2] ~/.claude/CLAUDE.md  — 아래 내용으로 생성 (전역 작업 규칙)
================================================================
# 전역 작업 규칙

## 실행 방식
- 모든 작업은 반드시 plan 모드로 시작 (실행 전 계획 먼저 제시)
- 모든 작업은 팀 에이전트 구성으로 실행
- tmux split pane으로 각 에이전트 분리해서 병렬 실행
- 작업 분리 기준: 분석/작성/검증 역할별로 pane 나누기
- 히스토리 문서 작성(필수): 프로젝트 루트 `history/` 폴더에 `YYYY-MM-DD_{주제-슬러그}.md`로 저장.
  주요 단계가 끝날 때마다 갱신하고, 작업 종료 시 최종 상태(완료/미완/차후작업)를 명시한다.
  포함: 작업 목표·수행 내용·산출물 경로(파일/커밋)·이슈 및 해결·다음 단계.
  세션이 바뀌어도 이 문서만 보면 이어서 작업할 수 있게 쓴다.

## 스킬
- 모든 작업 시작 전 `using-superpowers` 스킬 항상 적용

## 전역 기본 팀 구조 (전사 6팀)
| 팀 이름 | 역할 |
|---------|------|
| proposal-team | 제안서, RFP 분석, 국책과제 보고서, 산출물 작성 |
| dev-team | 코드 개발, API, 인프라, 테스트, CI/CD |
| bizdev-team | 시장조사, 경쟁분석, 사업화 전략, 영업지원 |
| design-team | 인포그래픽, 다이어그램, UI/UX, 발표자료 |
| ops-team | 일정관리, 내부 커뮤니케이션, 프로젝트 운영 |
| qa-team | 문서 검증, 코드 리뷰, 컴플라이언스 체크 |

## 프로젝트 개발 팀(커스터마이징 예시)
- project-dev: FE/BE 통합 개발 (team-lead, fe-developer, be-developer, tester) — cwd는 실제 프로젝트 경로로 수정
- project-frontend-dev: Frontend 전용 (Figma → React 변환)

================================================================
[3] ~/.claude/teams/<팀>/config.json  — 아래 8개 팀을 각각 생성
    그리고 각 팀의 각 member마다 ~/.claude/teams/<팀>/agents/<name>.md 를 생성한다.
    agents/<name>.md 형식(반드시 이 패턴을 따른다):
      ---
      name: <member name>
      agentType: <member agentType>
      description: <member description>
      skills: [<member skills>]
      ---
      # <Name> — <팀>
      ## 역할  (description을 풀어 1~2문장)
      ## 행동 지침  (skills를 어떻게 활용해 역할을 수행하는지 3~5개 단계)
      ## 산출물  (해당 역할이 만드는 결과물 목록)
----------------------------------------------------------------
proposal-team/config.json:
{
  "name": "proposal-team",
  "description": "제안서 작성 팀. RFP 분석, 국책과제 보고서, 제안서 산출물 작성을 담당한다.",
  "members": [
    {"name":"analyst","agentId":"analyst@proposal-team","agentType":"researcher","description":"RFP 분석, 요구사항 추출, 평가기준 매핑","skills":["document-skills:pdf","document-skills:xlsx"]},
    {"name":"writer","agentId":"writer@proposal-team","agentType":"writer","description":"제안서/보고서 본문 작성","skills":["document-skills:docx","document-skills:pptx","document-skills:doc-coauthoring"]},
    {"name":"reviewer","agentId":"reviewer@proposal-team","agentType":"reviewer","description":"금지어 체크, RFP 정합성 검증, 최종 교정","skills":["superpowers:requesting-code-review"]}
  ]
}
----------------------------------------------------------------
dev-team/config.json:
{
  "name": "dev-team",
  "description": "코드 개발 팀. 플랫폼 개발, API 설계/구현, 인프라 구축, 테스트, CI/CD를 담당한다.",
  "members": [
    {"name":"architect","agentId":"architect@dev-team","agentType":"architect","description":"설계, 기술 의사결정, 코드 구조 설계","skills":["superpowers:writing-plans","document-skills:mcp-builder"]},
    {"name":"fe-developer","agentId":"fe-developer@dev-team","agentType":"developer","description":"프론트엔드 구현 (React, TanStack, Zustand, shadcn/ui)","skills":["document-skills:frontend-design","figma:implement-design"]},
    {"name":"be-developer","agentId":"be-developer@dev-team","agentType":"developer","description":"백엔드 구현 (Spring Boot, JPA, QueryDSL, API)","skills":["superpowers:test-driven-development","document-skills:claude-api"]},
    {"name":"tester","agentId":"tester@dev-team","agentType":"tester","description":"테스트 작성/실행, E2E 테스트, 버그 추적","skills":["document-skills:webapp-testing","superpowers:systematic-debugging"]}
  ]
}
----------------------------------------------------------------
bizdev-team/config.json:
{
  "name": "bizdev-team",
  "description": "사업화/영업 지원 팀. 시장조사, 경쟁분석, 사업화 전략, 기술이전 계획, 사업계획서, 영업 제안 지원을 담당한다.",
  "members": [
    {"name":"researcher","agentId":"researcher@bizdev-team","agentType":"researcher","description":"시장조사, 경쟁분석, 트렌드 리서치","skills":["document-skills:xlsx","document-skills:pdf"]},
    {"name":"strategist","agentId":"strategist@bizdev-team","agentType":"strategist","description":"사업화 전략, 수익모델 설계, 기술이전 계획","skills":["document-skills:doc-coauthoring","document-skills:pptx"]},
    {"name":"presenter","agentId":"presenter@bizdev-team","agentType":"writer","description":"사업계획서, IR자료, 영업제안서 작성","skills":["document-skills:docx","document-skills:pptx"]}
  ]
}
----------------------------------------------------------------
design-team/config.json:
{
  "name": "design-team",
  "description": "디자인 팀. 인포그래픽, 다이어그램, UI/UX 설계, 발표자료, 시각자료 제작을 담당한다.",
  "members": [
    {"name":"ui-designer","agentId":"ui-designer@design-team","agentType":"designer","description":"UI/UX 설계, Figma 연동, 디자인 시스템 관리","skills":["figma:implement-design","figma:create-design-system-rules","document-skills:frontend-design"]},
    {"name":"graphic-designer","agentId":"graphic-designer@design-team","agentType":"designer","description":"인포그래픽, 포스터, 시각자료 제작","skills":["document-skills:canvas-design","document-skills:algorithmic-art"]},
    {"name":"slide-maker","agentId":"slide-maker@design-team","agentType":"writer","description":"발표자료, 슬라이드, 브랜드 적용 문서 제작","skills":["document-skills:pptx","document-skills:theme-factory","document-skills:brand-guidelines"]}
  ]
}
----------------------------------------------------------------
ops-team/config.json:
{
  "name": "ops-team",
  "description": "프로젝트 운영 팀. 일정관리, 내부 커뮤니케이션, 회의록, 상태 리포트, 체크리스트, 과제 행정 지원을 담당한다.",
  "members": [
    {"name":"pm","agentId":"pm@ops-team","agentType":"manager","description":"일정관리, 진행 추적, 리소스 조율, 마일스톤 관리","skills":["document-skills:xlsx"]},
    {"name":"communicator","agentId":"communicator@ops-team","agentType":"writer","description":"회의록, 상태보고, 내부 커뮤니케이션 문서 작성","skills":["document-skills:internal-comms","document-skills:docx"]}
  ]
}
----------------------------------------------------------------
qa-team/config.json:
{
  "name": "qa-team",
  "description": "품질 관리 팀. 문서 검증(금지어/키워드/RFP 정합성), 코드 리뷰, 보안 점검, 컴플라이언스, 테스트 자동화를 담당한다.",
  "members": [
    {"name":"doc-reviewer","agentId":"doc-reviewer@qa-team","agentType":"reviewer","description":"문서 검증, 금지어/키워드 체크, 컴플라이언스 검증","skills":["document-skills:pdf","document-skills:docx"]},
    {"name":"code-reviewer","agentId":"code-reviewer@qa-team","agentType":"reviewer","description":"코드 리뷰, 보안 점검, 품질 메트릭 분석","skills":["superpowers:requesting-code-review","superpowers:receiving-code-review"]},
    {"name":"test-engineer","agentId":"test-engineer@qa-team","agentType":"tester","description":"테스트 자동화, 회귀 테스트, E2E 검증","skills":["document-skills:webapp-testing","superpowers:systematic-debugging"]}
  ]
}
----------------------------------------------------------------
project-dev/config.json  (cwd는 나에게 실제 프로젝트 경로를 물어본 뒤 채운다. 아래는 기본 예시):
{
  "name": "project-dev",
  "description": "프로젝트 FE/BE 통합 개발 팀.",
  "members": [
    {"name":"team-lead","agentId":"team-lead@project-dev","agentType":"team-lead","cwd":"~/my-project","description":"전체 조율, 인프라/배포, Docker 관리"},
    {"name":"fe-developer","agentId":"fe-developer@project-dev","agentType":"developer","cwd":"~/my-project/frontend","description":"프론트엔드 구현"},
    {"name":"be-developer","agentId":"be-developer@project-dev","agentType":"developer","cwd":"~/my-project/backend","description":"백엔드 API 구현"},
    {"name":"tester","agentId":"tester@project-dev","agentType":"tester","cwd":"~/my-project","description":"E2E 테스트, API 검증, 디버깅"}
  ]
}
----------------------------------------------------------------
project-frontend-dev/config.json:
{
  "name": "project-frontend-dev",
  "description": "프로젝트 Frontend 전용 팀: Figma → React 변환, 코드 리뷰, 문서화",
  "leadAgentId": "team-lead@project-frontend-dev",
  "members": [
    {"agentId":"team-lead@project-frontend-dev","name":"team-lead","agentType":"team-lead","cwd":"~/my-project/frontend","subscriptions":[]}
  ]
}

================================================================
[4] 플러그인 마켓플레이스 등록 + 플러그인 설치
================================================================
아래 마켓플레이스를 먼저 등록한다:
- anthropic-agent-skills : github: anthropics/skills
- superpowers-marketplace : github: obra/superpowers-marketplace
- claude-plugins-official : (기본 공식 마켓플레이스)
- cli-anything : github: HKUDS/CLI-Anything
- claude-hud : github: jarrodwatts/claude-hud
- awesome-ai-studio : github: MJbae/awesome-novel-studio

그 다음 아래 플러그인을 설치한다 (형식: plugin@marketplace):
superpowers, agent-sdk-dev, claude-code-setup, claude-md-management, code-review,
code-simplifier, commit-commands, feature-dev, frontend-design, hookify,
learning-output-style, playground, plugin-dev, pr-review-toolkit, ralph-loop,
security-guidance, skill-creator, typescript-lsp  (이상 @claude-plugins-official)
document-skills, example-skills, brand-guidelines, canvas-design, claude-api,
doc-coauthoring, docx, internal-comms, mcp-builder, pdf, pptx, theme-factory,
web-artifacts-builder, webapp-testing, xlsx  (이상 @anthropic-agent-skills)
telegram, figma, playwright  (이상 @claude-plugins-official — 통신/디자인)
cli-anything@cli-anything, claude-hud@claude-hud, novel-studio@awesome-ai-studio

LSP 플러그인(pyright/gopls/rust-analyzer 등)은 필요할 때만 켜므로 지금은 설치하지 않아도 된다.
설치 후 상태표시줄(statusLine)로 claude-hud를 사용하도록 settings.json의 statusLine을 설정한다.

================================================================
[5] 셸/터미널 환경 (선택 — 있으면 좋음)
================================================================
- claude alias: `claude --dangerously-skip-permissions` 를 셸 rc(zshrc/bashrc, Windows는 PowerShell profile)에 추가
- starship 프롬프트, tmux(마우스/상태바), fzf, zoxide, bat 설치 권장
- teammateMode가 tmux이므로 tmux는 반드시 설치한다

================================================================
[6] 검증
================================================================
1. `claude` 실행이 되는지 확인
2. 팀 8개가 인식되는지 확인 (~/.claude/teams/ 아래 config.json 8개 + 각 agents/*.md)
3. 플러그인 목록이 정상 로드되는지 확인
4. Stop 훅이 history/ 문서를 요구하는지 확인
5. 결과를 요약해서 보고하고, 실패한 항목이 있으면 원인과 재시도 방안을 제시한다

먼저 [1]~[6]을 무엇을 만들고 설치·변경할지 계획으로 정리해서 보여줘. 승인 전에는 실제 변경하지 마.
````

---

## 참고
- 위 프롬프트는 **저장소 접근이 필요 없는 자기완결형**입니다. 그대로 붙여넣으면 동일한 하네스가 재현됩니다.
- 팀의 `cwd`(프로젝트 경로)와 비밀정보(토큰·API 키)는 각자 환경 값이므로, LLM이 실행 중 물어보게 되어 있습니다.
- 특정 부분만 원하면(예: 팀 구조만, CLAUDE.md 규칙만) 해당 섹션([2] 또는 [3])만 잘라서 붙여넣어도 됩니다.
