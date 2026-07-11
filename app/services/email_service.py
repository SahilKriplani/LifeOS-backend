import logging

import requests

from app.config import settings

logger = logging.getLogger("lifeos.email")

RESEND_ENDPOINT = "https://api.resend.com/emails"


def _otp_email_html(code: str) -> str:
    minutes = max(1, settings.OTP_TTL_SECONDS // 60)
    return f"""\
<div style="font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#0a0f0d;padding:40px 0;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center">
      <table role="presentation" width="440" cellpadding="0" cellspacing="0"
             style="background:#0f1715;border:1px solid #1f2a27;border-radius:16px;padding:40px;">
        <tr><td style="color:#e7f0ed;font-size:20px;font-weight:700;padding-bottom:8px;">LifeOS</td></tr>
        <tr><td style="color:#9fb2ad;font-size:14px;padding-bottom:28px;">
          Use this code to sign in. It expires in {minutes} minutes.
        </td></tr>
        <tr><td align="center" style="padding-bottom:28px;">
          <div style="display:inline-block;background:#0a0f0d;border:1px solid #14b8a6;border-radius:12px;
                      padding:16px 28px;font-size:34px;letter-spacing:12px;font-weight:700;color:#14b8a6;">
            {code}
          </div>
        </td></tr>
        <tr><td style="color:#6b7d78;font-size:12px;line-height:18px;">
          If you didn't request this, you can safely ignore this email — nobody can sign in without the code.
        </td></tr>
      </table>
      <div style="color:#4b5a56;font-size:11px;padding-top:16px;">© LifeOS</div>
    </td></tr>
  </table>
</div>"""


def send_otp_email(to_email: str, code: str) -> None:
    """
    Deliver the OTP via Resend. If RESEND_API_KEY isn't configured we log the
    code to the server console (dev mode) so the flow is fully testable without
    any provider. Raises RuntimeError if a configured send actually fails.
    """
    if not settings.RESEND_API_KEY:
        logger.warning("[DEV OTP] code for %s is %s", to_email, code)
        print(f"\n=== [DEV] LifeOS OTP for {to_email}: {code} ===\n")
        return

    try:
        resp = requests.post(
            RESEND_ENDPOINT,
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.RESEND_FROM,
                "to": [to_email],
                "subject": "Your LifeOS sign-in code",
                "html": _otp_email_html(code),
            },
            timeout=10,
        )
    except requests.RequestException as exc:
        logger.error("Resend request failed: %s", exc)
        raise RuntimeError("Failed to send the code. Please try again.") from exc

    if resp.status_code >= 300:
        logger.error("Resend returned %s: %s", resp.status_code, resp.text)
        raise RuntimeError("Failed to send the code. Please try again.")
