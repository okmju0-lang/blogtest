#!/usr/bin/env python3
"""
AI 슬롭 자동 검사 스크립트

Writer AGENT.md에 정의된 금지 패턴을 자동으로 스캔하여
최종본의 AI 슬롭 수준을 평가한다.

사용법:
    python scripts/slop_checker.py <markdown_file>
    python scripts/slop_checker.py output/drafts/post_20260326_1/draft_final.md
    python scripts/slop_checker.py output/posts/post_20260326_1/post.md
    python scripts/slop_checker.py --all-posts          # 발행된 전체 포스트 검사
    python scripts/slop_checker.py --all-drafts         # 전체 draft_final 검사

종료 코드:
    0: 슬롭 없음 (PASS)
    1: 경고 수준 (WARNING) - minor 이슈만 존재
    2: 실패 (FAIL) - critical 이슈 존재
"""

import re
import sys
import os
import io
from pathlib import Path
from dataclasses import dataclass, field

# Windows cp949 인코딩 이슈 방지
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─── 금지 패턴 정의 ───────────────────────────────────────────

@dataclass
class SlopPattern:
    """슬롭 패턴 정의"""
    name: str
    patterns: list
    severity: str  # "critical" | "warning"
    category: str
    description: str
    max_allowed: int = 0  # 허용 횟수 (0 = 완전 금지)


SLOP_RULES: list[SlopPattern] = [
    # ── 1. 상투적 도입부 (critical) ──
    SlopPattern(
        name="cliched_intro",
        patterns=[
            r"^최근\s",
            r"^오늘날\s",
            r"이[/가]\s*화두",
            r"빠르게\s*확산되고\s*있습니다",
            r"의\s*중요성이\s*커지고\s*있습니다",
            r"주목받고\s*있습니다",
            r"급부상하고\s*있습니다",
        ],
        severity="critical",
        category="도입부",
        description="AI가 100% 쓰는 상투적 도입부",
    ),

    # ── 2. 요약식 마무리 (critical) ──
    SlopPattern(
        name="summary_closing",
        patterns=[
            r"에\s*대해\s*(알아|살펴)(보았|봤)습니다",
            r"를\s*정리해\s*보겠습니다",
            r"를\s*알아보겠습니다",
            r"에\s*대해\s*살펴보겠습니다",
            r"를\s*살펴보았습니다",
        ],
        severity="critical",
        category="마무리",
        description="학생 보고서 같은 요약식 마무리",
    ),

    # ── 3. 기계적 나열 (critical) ──
    SlopPattern(
        name="mechanical_list",
        patterns=[
            r"첫째[,.].*둘째[,.].*셋째",
        ],
        severity="critical",
        category="구조",
        description="기계적 첫째/둘째/셋째 나열",
    ),

    # ── 4. 근거 없는 형용사 (critical) ──
    SlopPattern(
        name="ungrounded_adjective",
        patterns=[
            r"놀라운",
            r"획기적인",
            r"엄청난",
            r"혁신적인",
            r"게임\s*체인저",
            r"판도를\s*바꿀",
            r"전례\s*없는",
        ],
        severity="critical",
        category="형용사",
        description="근거 없이 신뢰를 떨어뜨리는 형용사",
    ),

    # ── 5. 과도한 메타 언급 (warning) ──
    SlopPattern(
        name="meta_commentary",
        patterns=[
            r"이\s*글에서는",
            r"본\s*포스트에서",
            r"아래에서\s*자세히",
            r"이번\s*글에서",
            r"본\s*글에서",
        ],
        severity="warning",
        category="메타 언급",
        description="글 자체를 언급하는 메타 코멘터리",
        max_allowed=1,
    ),

    # ── 6. 소극적 결론 (warning) ──
    SlopPattern(
        name="passive_conclusion",
        patterns=[
            r"할\s*수\s*있을\s*것입니다",
            r"이\s*될\s*것으로\s*기대됩니다",
            r"것으로\s*보입니다",
            r"것으로\s*예상됩니다",
            r"기대해\s*볼\s*만합니다",
        ],
        severity="warning",
        category="어조",
        description="소극적이고 회피적인 결론",
        max_allowed=1,
    ),

    # ── 7. 빈 강조 반복 (warning) ──
    SlopPattern(
        name="empty_emphasis",
        patterns=[
            r"중요한\s*것은",
            r"핵심은",
            r"결국",
        ],
        severity="warning",
        category="강조",
        description="매 문단마다 반복되는 빈 강조 표현",
        max_allowed=2,
    ),

    # ── 8. 반복 병렬 구조 (warning) ──
    SlopPattern(
        name="repetitive_parallel",
        patterns=[
            r"뿐만\s*아니라.*도",
            r"는\s*물론.*까지",
        ],
        severity="warning",
        category="구조",
        description="A뿐만 아니라 B도 — 반복 병렬 구조",
        max_allowed=2,
    ),
]


# ─── 문장 반복 검사 ───────────────────────────────────────────

@dataclass
class RepetitionIssue:
    """문장 반복 이슈"""
    issue_type: str
    location: str
    detail: str
    severity: str


def check_ending_repetition(lines: list[str]) -> list[RepetitionIssue]:
    """~합니다 등 동일 어미가 3회 이상 연속 반복되는지 검사"""
    issues = []
    ending_patterns = [
        (r"합니다[.\s]*$", "~합니다"),
        (r"입니다[.\s]*$", "~입니다"),
        (r"됩니다[.\s]*$", "~됩니다"),
        (r"있습니다[.\s]*$", "~있습니다"),
    ]

    # 본문 문장만 추출 (헤딩, 빈줄, 이미지, 인용, 테이블, frontmatter 제외)
    sentences = []
    in_frontmatter = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if not stripped:
            continue
        if stripped.startswith(("#", "!", ">", "|", "-", "```", "[")):
            continue
        sentences.append((i + 1, stripped))

    for pattern, label in ending_patterns:
        consecutive = 0
        start_line = 0
        last_line = 0
        for line_num, sent in sentences:
            if re.search(pattern, sent):
                if consecutive == 0:
                    start_line = line_num
                consecutive += 1
                last_line = line_num
            else:
                # 연속 구간 종료 — 3회 이상이면 최종 결과 1건만 기록
                if consecutive >= 3:
                    issues.append(RepetitionIssue(
                        issue_type="ending_repetition",
                        location=f"L{start_line}~L{last_line}",
                        detail=f"'{label}' 어미가 {consecutive}회 연속 반복",
                        severity="warning",
                    ))
                consecutive = 0
        # 마지막 구간 처리
        if consecutive >= 3:
            issues.append(RepetitionIssue(
                issue_type="ending_repetition",
                location=f"L{start_line}~L{last_line}",
                detail=f"'{label}' 어미가 {consecutive}회 연속 반복",
                severity="warning",
            ))
    return issues


def check_first_sentence(lines: list[str]) -> list[RepetitionIssue]:
    """첫 문장이 '최근~', '오늘날~' 등으로 시작하는지 검사"""
    issues = []
    in_frontmatter = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "---":
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        # 첫 본문 문장 발견
        bad_starts = [
            (r"^최근\s", "'최근~'으로 시작"),
            (r"^오늘날\s", "'오늘날~'로 시작"),
            (r"화두", "'화두' 포함"),
        ]
        for pat, desc in bad_starts:
            if re.search(pat, stripped):
                issues.append(RepetitionIssue(
                    issue_type="bad_first_sentence",
                    location=f"L{i+1}",
                    detail=f"첫 문장이 {desc} — AI 전형적 도입부",
                    severity="critical",
                ))
        break
    return issues


# ─── 메인 검사 로직 ───────────────────────────────────────────

@dataclass
class SlopMatch:
    """패턴 매치 결과"""
    rule_name: str
    severity: str
    category: str
    description: str
    line_num: int
    matched_text: str


@dataclass
class SlopReport:
    """검사 리포트"""
    file_path: str
    matches: list[SlopMatch] = field(default_factory=list)
    repetition_issues: list[RepetitionIssue] = field(default_factory=list)
    word_count: int = 0

    @property
    def critical_count(self) -> int:
        c1 = sum(1 for m in self.matches if m.severity == "critical")
        c2 = sum(1 for r in self.repetition_issues if r.severity == "critical")
        return c1 + c2

    @property
    def warning_count(self) -> int:
        w1 = sum(1 for m in self.matches if m.severity == "warning")
        w2 = sum(1 for r in self.repetition_issues if r.severity == "warning")
        return w1 + w2

    @property
    def status(self) -> str:
        if self.critical_count > 0:
            return "FAIL"
        elif self.warning_count > 0:
            return "WARNING"
        return "PASS"

    @property
    def exit_code(self) -> int:
        if self.critical_count > 0:
            return 2
        elif self.warning_count > 0:
            return 1
        return 0


def extract_body(text: str) -> str:
    """frontmatter를 제외한 본문만 추출"""
    lines = text.split("\n")
    in_fm = False
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
            else:
                body_start = i + 1
                break
    return "\n".join(lines[body_start:])


def check_file(filepath: str) -> SlopReport:
    """파일 하나를 검사하여 리포트 반환"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    body = extract_body(content)
    body_lines = body.split("\n")

    report = SlopReport(file_path=filepath)
    report.word_count = len(body.replace("\n", " ").split())

    # 패턴 매치 검사
    for rule in SLOP_RULES:
        rule_matches = []
        for i, line in enumerate(body_lines):
            stripped = line.strip()
            # 코드블록, 인용, 이미지, 테이블 헤더는 스킵
            if stripped.startswith(("```", "!", ">", "| ---")):
                continue
            for pat in rule.patterns:
                match = re.search(pat, stripped)
                if match:
                    rule_matches.append(SlopMatch(
                        rule_name=rule.name,
                        severity=rule.severity,
                        category=rule.category,
                        description=rule.description,
                        line_num=i + 1,
                        matched_text=match.group(),
                    ))

        # max_allowed 초과 시에만 이슈로 기록
        if len(rule_matches) > rule.max_allowed:
            # max_allowed가 0이면 전부 기록, 아니면 초과분만 기록
            if rule.max_allowed == 0:
                report.matches.extend(rule_matches)
            else:
                # 초과분만 기록하되, 전체 횟수를 설명에 포함
                for m in rule_matches[rule.max_allowed:]:
                    m.description += f" (총 {len(rule_matches)}회, 허용 {rule.max_allowed}회)"
                    report.matches.append(m)

    # 문장 반복 검사
    report.repetition_issues.extend(check_ending_repetition(body_lines))
    report.repetition_issues.extend(check_first_sentence(lines))

    return report


# ─── 출력 포맷 ────────────────────────────────────────────────

def format_report(report: SlopReport) -> str:
    """리포트를 터미널용 텍스트로 포맷"""
    status_icon = {"PASS": "\u2705", "WARNING": "\u26a0\ufe0f", "FAIL": "\u274c"}
    lines = []
    lines.append("")
    lines.append(f"{'='*60}")
    lines.append(f"  AI 슬롭 검사 결과: {status_icon.get(report.status, '?')} {report.status}")
    lines.append(f"  파일: {report.file_path}")
    lines.append(f"  단어 수: {report.word_count}")
    lines.append(f"{'='*60}")

    if report.critical_count > 0:
        lines.append(f"\n  \u274c CRITICAL ({report.critical_count}건)")
        lines.append(f"  {'─'*50}")
        for m in report.matches:
            if m.severity == "critical":
                lines.append(f"    L{m.line_num:>4} | [{m.category}] {m.description}")
                lines.append(f"         | 매치: \"{m.matched_text}\"")
        for r in report.repetition_issues:
            if r.severity == "critical":
                lines.append(f"    {r.location:>5} | [{r.issue_type}] {r.detail}")

    if report.warning_count > 0:
        lines.append(f"\n  \u26a0\ufe0f  WARNING ({report.warning_count}건)")
        lines.append(f"  {'─'*50}")
        for m in report.matches:
            if m.severity == "warning":
                lines.append(f"    L{m.line_num:>4} | [{m.category}] {m.description}")
                lines.append(f"         | 매치: \"{m.matched_text}\"")
        for r in report.repetition_issues:
            if r.severity == "warning":
                lines.append(f"    {r.location:>5} | [{r.issue_type}] {r.detail}")

    if report.critical_count == 0 and report.warning_count == 0:
        lines.append(f"\n  슬롭 패턴이 발견되지 않았습니다.")

    lines.append(f"\n{'='*60}")
    lines.append(f"  Critical: {report.critical_count}  |  Warning: {report.warning_count}")
    lines.append(f"{'='*60}")
    lines.append("")
    return "\n".join(lines)


def format_batch_summary(reports: list[SlopReport]) -> str:
    """여러 파일의 배치 검사 요약"""
    lines = []
    lines.append("")
    lines.append(f"{'='*60}")
    lines.append(f"  AI 슬롭 배치 검사 요약 ({len(reports)}개 파일)")
    lines.append(f"{'='*60}")

    pass_count = sum(1 for r in reports if r.status == "PASS")
    warn_count = sum(1 for r in reports if r.status == "WARNING")
    fail_count = sum(1 for r in reports if r.status == "FAIL")

    lines.append(f"\n  \u2705 PASS: {pass_count}  |  \u26a0\ufe0f  WARNING: {warn_count}  |  \u274c FAIL: {fail_count}")
    lines.append("")

    for r in sorted(reports, key=lambda x: (-x.critical_count, -x.warning_count)):
        status_icon = {"PASS": "\u2705", "WARNING": "\u26a0\ufe0f", "FAIL": "\u274c"}
        post_id = Path(r.file_path).parent.name
        if post_id == "images" or not post_id.startswith("post_"):
            post_id = Path(r.file_path).stem
        lines.append(f"  {status_icon.get(r.status, '?')} {post_id:30s} C:{r.critical_count} W:{r.warning_count}")

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


# ─── CLI ──────────────────────────────────────────────────────

def find_all_posts() -> list[str]:
    """output/posts/ 내 모든 post.md 파일 경로 반환"""
    posts_dir = Path(__file__).parent.parent / "output" / "posts"
    if not posts_dir.exists():
        return []
    results = []
    for post_dir in sorted(posts_dir.iterdir()):
        post_file = post_dir / "post.md"
        if post_file.exists():
            results.append(str(post_file))
    return results


def find_all_drafts() -> list[str]:
    """output/drafts/ 내 모든 draft_final.md 파일 경로 반환"""
    drafts_dir = Path(__file__).parent.parent / "output" / "drafts"
    if not drafts_dir.exists():
        return []
    results = []
    for draft_dir in sorted(drafts_dir.iterdir()):
        final = draft_dir / "draft_final.md"
        if final.exists():
            results.append(str(final))
    return results


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    arg = sys.argv[1]

    # 배치 모드
    if arg == "--all-posts":
        files = find_all_posts()
        if not files:
            print("발행된 포스트가 없습니다.")
            sys.exit(0)
        reports = [check_file(f) for f in files]
        for r in reports:
            print(format_report(r))
        print(format_batch_summary(reports))
        worst = max(r.exit_code for r in reports)
        sys.exit(worst)

    elif arg == "--all-drafts":
        files = find_all_drafts()
        if not files:
            print("draft_final.md 파일이 없습니다.")
            sys.exit(0)
        reports = [check_file(f) for f in files]
        for r in reports:
            print(format_report(r))
        print(format_batch_summary(reports))
        worst = max(r.exit_code for r in reports)
        sys.exit(worst)

    # 단일 파일 모드
    filepath = arg
    if not os.path.exists(filepath):
        print(f"파일을 찾을 수 없습니다: {filepath}")
        sys.exit(1)

    report = check_file(filepath)
    print(format_report(report))
    sys.exit(report.exit_code)


if __name__ == "__main__":
    main()
