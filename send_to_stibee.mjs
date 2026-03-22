import { readFileSync } from 'fs';
import { resolve } from 'path';

// --- .env 로드 ---
function loadEnv() {
  try {
    const lines = readFileSync(resolve('.env'), 'utf-8').split('\n');
    for (const line of lines) {
      const match = line.match(/^\s*([^#=\s]+)\s*=\s*(.+)\s*$/);
      if (match) process.env[match[1]] = match[2].trim();
    }
  } catch {}
}
loadEnv();

// --- 설정 ---
const API_KEY = process.env.STIBEE_API_KEY;
if (!API_KEY) { console.error('❌ .env에 STIBEE_API_KEY가 없습니다.'); process.exit(1); }
const BASE_URL = 'https://api.stibee.com/v2';
const LIST_ID = 479501;           // 주소록 숫자 ID (GET /v1/lists로 확인)
const FROM_NAME = 'test';
const FROM_EMAIL = 'okmju0-gmail.com@send.stibee.com';
const POST_PATH = resolve('output/posts/post_20260319_1/post.md');

// --- Markdown → HTML 변환 ---
function markdownToHtml(md) {
  // frontmatter 제거
  const body = md.replace(/^---[\s\S]*?---\n/, '');

  let html = body
    // 이미지 (이메일 내 로컬 이미지 불가 → 제거)
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '')
    // h1
    .replace(/^# (.+)$/gm, '<h1 style="font-size:26px;font-weight:bold;color:#1a1a1a;margin:32px 0 16px;">$1</h1>')
    // h2
    .replace(/^## (.+)$/gm, '<h2 style="font-size:20px;font-weight:bold;color:#1a1a1a;border-bottom:2px solid #e5e7eb;padding-bottom:8px;margin:28px 0 12px;">$1</h2>')
    // h3
    .replace(/^### (.+)$/gm, '<h3 style="font-size:17px;font-weight:bold;color:#333;margin:20px 0 8px;">$1</h3>')
    // hr
    .replace(/^---$/gm, '<hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">')
    // bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 리스트 항목
    .replace(/^- (.+)$/gm, '<li style="margin:4px 0;">$1</li>')
    // li 묶기 (연속 li를 ul로)
    .replace(/(<li[^>]*>.*<\/li>\n?)+/g, (m) => `<ul style="padding-left:20px;margin:8px 0;">${m}</ul>`)
    // 빈 줄 → 단락 구분
    .replace(/\n{2,}/g, '\n\n')
    // 일반 줄바꿈이 있는 텍스트를 p로 감싸기
    .split('\n\n')
    .map(block => {
      block = block.trim();
      if (!block) return '';
      if (block.startsWith('<h') || block.startsWith('<hr') || block.startsWith('<ul')) return block;
      return `<p style="font-size:16px;line-height:1.8;color:#333;margin:0 0 16px;">${block.replace(/\n/g, '<br>')}</p>`;
    })
    .join('\n');

  return html;
}

// --- 이메일 HTML 템플릿 ---
function buildEmailHtml(title, bodyHtml) {
  return `<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:'Apple SD Gothic Neo',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="640" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <!-- 헤더 -->
          <tr>
            <td style="background:#111827;padding:24px 40px;">
              <p style="margin:0;color:#9ca3af;font-size:13px;letter-spacing:0.05em;">AX LAB NEWSLETTER</p>
            </td>
          </tr>
          <!-- 본문 -->
          <tr>
            <td style="padding:40px;">
              ${bodyHtml}
            </td>
          </tr>
          <!-- 푸터 -->
          <tr>
            <td style="background:#f9fafb;padding:24px 40px;border-top:1px solid #e5e7eb;">
              <p style="margin:0;font-size:12px;color:#9ca3af;text-align:center;">
                AX Lab 뉴스레터 · 수신을 원하지 않으시면 <a href="{{{unsubscribe}}}" style="color:#6b7280;">수신거부</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;
}

// --- Stibee v2 API 호출 ---
async function apiRequest(path, method = 'GET', body = null) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: {
      'AccessToken': API_KEY,
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(`[${res.status}] ${data.message || JSON.stringify(data)}`);
  }
  return data;
}

async function createEmail(subject, htmlContent) {
  // v2 POST /emails — 이메일 초안 생성
  const data = await apiRequest('/emails', 'POST', {
    listId: LIST_ID,
    type: 1,                         // 1 = 일반 뉴스레터
    subject: subject,
    fromName: FROM_NAME,
    fromEmail: FROM_EMAIL,
    contents: htmlContent,
  });
  // v2 응답: { ok: true, value: { id: ... } } 또는 { id: ... } 직접 반환
  const id = data?.value?.id ?? data?.id;
  if (!id) throw new Error(`이메일 ID를 찾을 수 없습니다: ${JSON.stringify(data)}`);
  return id;
}

async function sendEmail(emailId) {
  // v2 POST /emails/{id}/send — 즉시 발송
  return await apiRequest(`/emails/${emailId}/send`, 'POST', {});
}

// --- 메인 ---
async function main() {
  console.log('📄 포스트 파일 읽는 중...');
  const raw = readFileSync(POST_PATH, 'utf-8');

  // title 추출
  const titleMatch = raw.match(/^title:\s*["']?(.+?)["']?\s*$/m);
  const title = titleMatch ? titleMatch[1] : '블로그 뉴스레터';
  console.log(`📌 제목: ${title}`);

  // HTML 변환
  const bodyHtml = markdownToHtml(raw);
  const emailHtml = buildEmailHtml(title, bodyHtml);

  console.log('📡 스티비 이메일 초안 생성 중... (v2 API)');
  const emailId = await createEmail(title, emailHtml);
  console.log(`✅ 이메일 초안 생성 완료 (ID: ${emailId})`);

  console.log('🚀 발송 중...');
  await sendEmail(emailId);
  console.log('✅ 발송 완료!');
}

main().catch(err => {
  console.error('❌ 오류:', err.message);
  process.exit(1);
});
