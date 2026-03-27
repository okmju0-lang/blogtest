from __future__ import annotations

import argparse
import base64
import html
from pathlib import Path

from playwright.sync_api import sync_playwright


WIDTH = 2400
HEIGHT = 2440


def to_data_uri(image_path: Path) -> str:
    mime = "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def build_html(base_image_uri: str) -> str:
    title = "HS효성그룹 HR AI 교육은 '툴 교육'을 넘어 'PoC 상상'으로 이어졌습니다"
    description = (
        "사후 설문 94명 응답과 현장 자료를 보면, 교육이 끝난 뒤 질문의 방향이 "
        "'어떤 기능을 배웠나'에서 '우리 HR 업무에 어떻게 붙일 것인가'로 이동했습니다."
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width={WIDTH}, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --navy: #0f2742;
      --navy-strong: #112d4f;
      --emerald: #0f9b82;
      --emerald-strong: #0a7a67;
      --mint: #dff8f1;
      --sky: #ebf4ff;
      --line: rgba(17, 45, 79, 0.12);
      --text: #18304a;
      --muted: #5f7389;
      --shadow: 0 24px 80px rgba(15, 39, 66, 0.14);
      --card-shadow: 0 14px 40px rgba(15, 39, 66, 0.08);
    }}

    * {{
      box-sizing: border-box;
    }}

    html, body {{
      margin: 0;
      width: {WIDTH}px;
      height: {HEIGHT}px;
      overflow: hidden;
      font-family: "Pretendard", "Malgun Gothic", "Apple SD Gothic Neo", "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(255,255,255,0.75), transparent 28%),
        linear-gradient(180deg, #edf4fb 0%, #e7eef8 100%);
      color: var(--text);
    }}

    body {{
      padding: 72px;
    }}

    .canvas {{
      height: 100%;
      display: grid;
      grid-template-rows: 760px 1fr 320px;
      gap: 24px;
    }}

    .hero {{
      position: relative;
      overflow: hidden;
      border-radius: 44px;
      box-shadow: var(--shadow);
      background:
        linear-gradient(135deg, rgba(7, 28, 49, 0.84) 0%, rgba(12, 79, 83, 0.66) 48%, rgba(6, 111, 94, 0.58) 100%),
        url("{base_image_uri}") center/cover no-repeat;
      padding: 64px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .hero::after {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at 16% 22%, rgba(255,255,255,0.18), transparent 24%),
        radial-gradient(circle at 82% 12%, rgba(255,255,255,0.18), transparent 20%),
        linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
      pointer-events: none;
    }}

    .hero-copy, .hero-metrics {{
      position: relative;
      z-index: 1;
    }}

    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 12px 18px;
      border-radius: 999px;
      background: rgba(255,255,255,0.14);
      border: 1px solid rgba(255,255,255,0.18);
      color: #d7fff6;
      font-size: 28px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      backdrop-filter: blur(10px);
    }}

    .hero h1 {{
      margin: 28px 0 20px;
      max-width: 1120px;
      color: #ffffff;
      font-size: 88px;
      line-height: 1.08;
      letter-spacing: -0.04em;
    }}

    .hero p {{
      margin: 0;
      max-width: 1180px;
      color: rgba(255,255,255,0.9);
      font-size: 34px;
      line-height: 1.6;
    }}

    .hero-metrics {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
    }}

    .metric-card {{
      border-radius: 28px;
      padding: 28px 30px;
      background: rgba(255,255,255,0.9);
      border: 1px solid rgba(255,255,255,0.58);
      box-shadow: 0 20px 48px rgba(6, 30, 54, 0.18);
      backdrop-filter: blur(14px);
    }}

    .metric-label {{
      color: var(--muted);
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}

    .metric-value {{
      margin-top: 10px;
      color: var(--navy-strong);
      font-size: 62px;
      font-weight: 900;
      letter-spacing: -0.05em;
      line-height: 1;
    }}

    .metric-sub {{
      margin-top: 8px;
      color: #6c8197;
      font-size: 22px;
      line-height: 1.4;
    }}

    .content-grid {{
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 24px;
    }}

    .panel {{
      border-radius: 36px;
      background: rgba(255,255,255,0.92);
      border: 1px solid rgba(255,255,255,0.72);
      box-shadow: var(--card-shadow);
      padding: 38px 40px;
      overflow: hidden;
    }}

    .panel h2 {{
      margin: 0;
      color: var(--navy-strong);
      font-size: 46px;
      line-height: 1.15;
      letter-spacing: -0.04em;
    }}

    .panel-intro {{
      margin: 14px 0 0;
      color: var(--muted);
      font-size: 24px;
      line-height: 1.55;
    }}

    .score-pills {{
      margin-top: 28px;
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
    }}

    .pill {{
      padding: 14px 18px;
      border-radius: 999px;
      background: var(--sky);
      color: var(--navy-strong);
      font-size: 24px;
      font-weight: 700;
      line-height: 1.2;
    }}

    .pill strong {{
      font-size: 30px;
      font-weight: 900;
      margin-right: 6px;
    }}

    .bar-list {{
      margin-top: 28px;
      display: grid;
      gap: 22px;
    }}

    .bar-card {{
      padding: 22px 24px;
      border-radius: 24px;
      background: linear-gradient(180deg, #f9fbfe 0%, #f2f7fc 100%);
      border: 1px solid rgba(17, 45, 79, 0.07);
    }}

    .bar-top {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 24px;
    }}

    .bar-title {{
      color: var(--navy-strong);
      font-size: 28px;
      font-weight: 800;
      line-height: 1.3;
    }}

    .bar-value {{
      color: var(--emerald-strong);
      font-size: 34px;
      font-weight: 900;
      letter-spacing: -0.04em;
      white-space: nowrap;
    }}

    .bar-track {{
      margin-top: 14px;
      height: 16px;
      border-radius: 999px;
      background: #d9e6f2;
      overflow: hidden;
    }}

    .bar-fill {{
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, #16b39a 0%, #0f8f86 100%);
    }}

    .bar-note {{
      margin-top: 10px;
      color: #698095;
      font-size: 21px;
      line-height: 1.45;
    }}

    .journey-grid {{
      margin-top: 28px;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}

    .journey-card {{
      min-height: 176px;
      padding: 22px 24px;
      border-radius: 24px;
      background: linear-gradient(180deg, #edf8f5 0%, #ffffff 100%);
      border: 1px solid rgba(15, 155, 130, 0.18);
    }}

    .journey-step {{
      display: inline-block;
      margin-bottom: 14px;
      padding: 9px 14px;
      border-radius: 999px;
      background: rgba(15, 155, 130, 0.12);
      color: var(--emerald-strong);
      font-size: 20px;
      font-weight: 800;
    }}

    .journey-title {{
      color: var(--navy-strong);
      font-size: 30px;
      font-weight: 800;
      line-height: 1.2;
    }}

    .journey-desc {{
      margin-top: 10px;
      color: #668095;
      font-size: 22px;
      line-height: 1.5;
    }}

    .quote-box {{
      margin-top: 18px;
      padding: 24px 28px;
      border-radius: 26px;
      background: linear-gradient(135deg, #13375b 0%, #0f8f86 100%);
      color: #ffffff;
      box-shadow: 0 16px 36px rgba(15, 39, 66, 0.14);
    }}

    .quote-box strong {{
      display: block;
      margin-bottom: 10px;
      font-size: 24px;
      color: #c9fff3;
      letter-spacing: 0.02em;
    }}

    .quote-box p {{
      margin: 0;
      font-size: 27px;
      line-height: 1.5;
      letter-spacing: -0.03em;
    }}

    .challenge-list {{
      margin-top: 18px;
      display: grid;
      gap: 14px;
    }}

    .challenge-item {{
      display: grid;
      grid-template-columns: 76px 1fr auto;
      align-items: center;
      gap: 16px;
      padding: 20px 22px;
      border-radius: 22px;
      background: #ffffff;
      border: 1px solid rgba(17, 45, 79, 0.08);
      box-shadow: 0 10px 24px rgba(15, 39, 66, 0.05);
    }}

    .challenge-rank {{
      width: 54px;
      height: 54px;
      border-radius: 18px;
      display: grid;
      place-items: center;
      color: #ffffff;
      font-size: 24px;
      font-weight: 900;
      background: linear-gradient(135deg, #17b49b 0%, #0c8577 100%);
    }}

    .challenge-title {{
      color: var(--navy-strong);
      font-size: 28px;
      font-weight: 800;
      line-height: 1.3;
    }}

    .challenge-desc {{
      margin-top: 8px;
      color: #698095;
      font-size: 21px;
      line-height: 1.45;
    }}

    .challenge-count {{
      color: #ff7a4d;
      font-size: 44px;
      font-weight: 900;
      letter-spacing: -0.04em;
      white-space: nowrap;
    }}

    .footer-panel {{
      border-radius: 36px;
      background: linear-gradient(135deg, #ffffff 0%, #eef7f5 100%);
      border: 1px solid rgba(15, 155, 130, 0.14);
      box-shadow: var(--card-shadow);
      padding: 34px 38px;
      display: grid;
      grid-template-columns: 390px 1fr;
      gap: 24px;
      align-items: center;
    }}

    .footer-title {{
      color: var(--navy-strong);
      font-size: 44px;
      font-weight: 900;
      line-height: 1.12;
      letter-spacing: -0.04em;
    }}

    .footer-copy {{
      margin-top: 12px;
      color: #688095;
      font-size: 23px;
      line-height: 1.5;
    }}

    .action-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }}

    .action-card {{
      min-height: 184px;
      border-radius: 24px;
      background: #ffffff;
      border: 1px solid rgba(17, 45, 79, 0.08);
      padding: 22px 22px 20px;
      box-shadow: 0 12px 26px rgba(15, 39, 66, 0.05);
    }}

    .action-index {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 12px;
      background: rgba(15, 155, 130, 0.14);
      color: var(--emerald-strong);
      font-size: 20px;
      font-weight: 900;
    }}

    .action-title {{
      margin-top: 14px;
      color: var(--navy-strong);
      font-size: 28px;
      font-weight: 800;
      line-height: 1.25;
    }}

    .action-desc {{
      margin-top: 10px;
      color: #698095;
      font-size: 21px;
      line-height: 1.45;
    }}
  </style>
</head>
<body>
  <div class="canvas">
    <section class="hero">
      <div class="hero-copy">
        <div class="eyebrow">Magic Ecole HR AX Case Study</div>
        <h1>HS효성그룹 HR AI 교육은<br>'툴 교육'을 넘어 'PoC 상상'으로 이어졌습니다</h1>
        <p>{html.escape(description)}</p>
      </div>
      <div class="hero-metrics">
        <div class="metric-card">
          <div class="metric-label">사후 설문 응답</div>
          <div class="metric-value">94명</div>
          <div class="metric-sub">현장 반응과 후속 의향을 확인한 기준 표본</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">추가 과정 참여 희망</div>
          <div class="metric-value">69명</div>
          <div class="metric-sub">응답자의 73.4%가 다음 단계를 원했습니다</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">업무 적용 자신감</div>
          <div class="metric-value">63.8%</div>
          <div class="metric-sub">만족 이상 비율, 실전 전환의 마지막 숙제도 함께 드러났습니다</div>
        </div>
      </div>
    </section>

    <section class="content-grid">
      <div class="panel">
        <h2>숫자로 본 교육 효과</h2>
        <p class="panel-intro">만족도 자체도 높았지만, 더 중요한 신호는 실무 연관성과 팀 프로젝트 경험이 강하게 남았다는 점입니다.</p>
        <div class="score-pills">
          <div class="pill"><strong>4.22</strong>/ 5 교육 만족도</div>
          <div class="pill"><strong>4.19</strong>/ 5 강사·멘토 만족도</div>
          <div class="pill"><strong>4.30</strong>/ 5 본인 참여도</div>
        </div>
        <div class="bar-list">
          <div class="bar-card">
            <div class="bar-top">
              <div class="bar-title">실습 내용의 실무 연관성</div>
              <div class="bar-value">74.5%</div>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:74.5%"></div></div>
            <div class="bar-note">실습이 '업무와 연결된다'고 느낀 만족 이상 비율</div>
          </div>
          <div class="bar-card">
            <div class="bar-top">
              <div class="bar-title">멘토링의 실질적 도움</div>
              <div class="bar-value">70.2%</div>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:70.2%"></div></div>
            <div class="bar-note">막히는 지점을 해결하는 피드백 효과가 확인됐습니다</div>
          </div>
          <div class="bar-card">
            <div class="bar-top">
              <div class="bar-title">팀 프로젝트 활동</div>
              <div class="bar-value">84.0%</div>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:84%"></div></div>
            <div class="bar-note">함께 만드는 경험이 가장 강한 만족을 남겼습니다</div>
          </div>
          <div class="bar-card">
            <div class="bar-top">
              <div class="bar-title">내 업무에 적용할 자신감</div>
              <div class="bar-value">63.8%</div>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width:63.8%"></div></div>
            <div class="bar-note">다음 과제로 남은 이유가 함께 보이는 지점입니다</div>
          </div>
        </div>
      </div>

      <div class="panel">
        <h2>HR 적용 포인트와 현장 과제</h2>
        <p class="panel-intro">교육 자료 안에서 HR 시나리오가 구체적으로 보였고, 동시에 실제 PoC로 넘어갈 때 부딪히는 과제도 선명해졌습니다.</p>
        <div class="journey-grid">
          <div class="journey-card">
            <div class="journey-step">Step 1</div>
            <div class="journey-title">리터러시</div>
            <div class="journey-desc">AI를 '기능'이 아니라 일 방식의 변화로 받아들이는 출발점</div>
          </div>
          <div class="journey-card">
            <div class="journey-step">Step 2</div>
            <div class="journey-title">실습</div>
            <div class="journey-desc">프롬프트, 워크플로우, 바이브 코딩으로 손에 익히는 단계</div>
          </div>
          <div class="journey-card">
            <div class="journey-step">Step 3</div>
            <div class="journey-title">팀 프로젝트</div>
            <div class="journey-desc">협업으로 문제를 정의하고 적용 장면을 함께 설계하는 단계</div>
          </div>
          <div class="journey-card">
            <div class="journey-step">Step 4</div>
            <div class="journey-title">HR 시나리오</div>
            <div class="journey-desc">채용 CRM, 지원 현황, 학습과정, 경력경로 등 업무형 PoC 상상</div>
          </div>
        </div>
        <div class="quote-box">
          <strong>현장에서 남은 질문</strong>
          <p>"이제 가능성은 알겠다. 그럼 우리 HR 업무는 어떤 PoC부터 시작할 수 있을까?"</p>
        </div>
        <div class="challenge-list">
          <div class="challenge-item">
            <div class="challenge-rank">1</div>
            <div>
              <div class="challenge-title">업무 데이터와 실습 환경 연동의 어려움</div>
              <div class="challenge-desc">실제 HR 데이터가 연결되지 않으면 자신감이 빠르게 꺾입니다.</div>
            </div>
            <div class="challenge-count">45건</div>
          </div>
          <div class="challenge-item">
            <div class="challenge-rank">2</div>
            <div>
              <div class="challenge-title">코드를 이해하고 수정하는 데 더 많은 시간 필요</div>
              <div class="challenge-desc">AI가 초안을 만들더라도 마지막 연결과 검증 역량이 요구됩니다.</div>
            </div>
            <div class="challenge-count">35건</div>
          </div>
          <div class="challenge-item">
            <div class="challenge-rank">3</div>
            <div>
              <div class="challenge-title">직무 특화 예시와 도구가 더 필요</div>
              <div class="challenge-desc">HR 맥락이 구체화될수록 PoC 전환 속도가 빨라집니다.</div>
            </div>
            <div class="challenge-count">28건</div>
          </div>
        </div>
      </div>
    </section>

    <section class="footer-panel">
      <div>
        <div class="footer-title">PoC로 넘어가기 위한<br>실행 조건 3가지</div>
        <div class="footer-copy">만족도만으로 끝내지 않으려면, 교육 이후의 연결 장치가 설계돼야 합니다.</div>
      </div>
      <div class="action-grid">
        <div class="action-card">
          <div class="action-index">1</div>
          <div class="action-title">업무 데이터 연결</div>
          <div class="action-desc">실습 결과가 실제 HR 프로세스와 이어지는 작은 데이터 흐름을 먼저 만듭니다.</div>
        </div>
        <div class="action-card">
          <div class="action-index">2</div>
          <div class="action-title">직무형 시나리오 보강</div>
          <div class="action-desc">채용, 온보딩, 학습, 인재DB 등 HR 장면별 예시를 구체화합니다.</div>
        </div>
        <div class="action-card">
          <div class="action-index">3</div>
          <div class="action-title">후속 멘토링</div>
          <div class="action-desc">막히는 구간에서 바로 다음 액션을 설계할 수 있도록 짧고 촘촘하게 돕습니다.</div>
        </div>
      </div>
    </section>
  </div>
</body>
</html>
"""


def render(output_html: Path, output_image: Path, base_image: Path) -> None:
    html_text = build_html(to_data_uri(base_image))
    output_html.write_text(html_text, encoding="utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
        page.goto(output_html.resolve().as_uri(), wait_until="networkidle")
        page.screenshot(
            path=str(output_image),
            clip={"x": 0, "y": 0, "width": WIDTH, "height": HEIGHT},
            full_page=False,
        )
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a high-resolution HR infographic.")
    parser.add_argument("--base-image", required=True, help="Nano Banana 2 base image path")
    parser.add_argument("--output-html", required=True, help="Output HTML path")
    parser.add_argument("--output-image", required=True, help="Output PNG path")
    args = parser.parse_args()

    render(
        output_html=Path(args.output_html),
        output_image=Path(args.output_image),
        base_image=Path(args.base_image),
    )


if __name__ == "__main__":
    main()
