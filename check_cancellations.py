"""
check_cancellations.py
Requests-based checker for MCAST cancelled lectures page.
Sends an email (Gmail SMTP) only if a (fuzzy) match for CLASS_NAME is found
and we haven't already notified today.
"""

from datetime import date
import difflib
import logging
import os
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

# ---------- CONFIG via environment (GitHub Secrets) ----------
EMAIL_USER = os.environ.get("EMAIL_USER")         # Gmail address
EMAIL_PASS = os.environ.get("EMAIL_PASS")         # Gmail App Password
TO_EMAIL = os.environ.get("TO_EMAIL", EMAIL_USER)
CLASS_NAME = os.environ.get("CLASS_NAME", "SWD-6.3A")
FUZZY_THRESHOLD = float(os.environ.get("FUZZY_THRESHOLD", "0.8"))
TARGET_URL = os.environ.get("TARGET_URL", "https://iict.mcast.edu.mt/cancelled-lectures/")

# Storage for last notification (in GitHub Actions we use a temp file)
STATE_FILE = os.environ.get("STATE_FILE", "/tmp/mcast_last_notified.txt")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def fetch_html(url, timeout=15):
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; mcast-checker/1.0; +https://github.com/)"
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup
    return main.get_text(separator="\n", strip=True)


def fuzzy_search(text, target, threshold=0.8):
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    candidates = []
    for line in lines:
        parts = [p.strip() for p in line.replace("—", ",").split(",") if p.strip()]
        candidates.extend(parts)
        candidates.append(line)
    # deduplicate but keep order
    seen = set()
    dedup = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            dedup.append(c)
    matches = []
    for cand in dedup:
        ratio = difflib.SequenceMatcher(None, target.lower(), cand.lower()).ratio()
        if ratio >= threshold:
            matches.append((cand, ratio))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def read_last_notified(state_file):
    try:
        with open(state_file, "r") as f:
            line = f.read().strip()
            return line  # format YYYY-MM-DD
    except Exception:
        return None


def write_last_notified(state_file, iso_date):
    try:
        with open(state_file, "w") as f:
            f.write(iso_date)
    except Exception as e:
        logging.warning("Could not write state file: %s", e)


def send_email(subject, body, smtp_user, smtp_pass, to_addr):
    msg = MIMEText(body)
    msg["From"] = smtp_user
    msg["To"] = to_addr
    msg["Subject"] = subject

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as s:
        s.ehlo()
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.send_message(msg)


def main():
    if not EMAIL_USER or not EMAIL_PASS:
        logging.error("EMAIL_USER and EMAIL_PASS environment variables must be set.")
        return 2

    logging.info("Fetching %s ...", TARGET_URL)
    try:
        html = fetch_html(TARGET_URL)
    except Exception as e:
        logging.exception("Failed to fetch page: %s", e)
        return 3

    text = extract_text(html)
    matches = fuzzy_search(text, CLASS_NAME, threshold=FUZZY_THRESHOLD)

    today_iso = date.today().isoformat()
    last = read_last_notified(STATE_FILE)
    if matches:
        if last == today_iso:
            logging.info("Already notified today (%s) — skipping email.", today_iso)
            return 0
        # Build email body
        body_lines = [
            f"Possible cancellation(s) for '{CLASS_NAME}' detected at {TARGET_URL}",
            "",
            "Top matches (similarity score):",
        ]
        for cand, score in matches[:10]:
            body_lines.append(f"- [{score:.2f}] {cand}")
        body = "\n".join(body_lines)
        subject = f"[MCAST] Possible cancelled lecture for {CLASS_NAME}"
        logging.info("Matches found: sending email...")
        try:
            send_email(subject, body, EMAIL_USER, EMAIL_PASS, TO_EMAIL)
            write_last_notified(STATE_FILE, today_iso)
            logging.info("Notification sent and state updated.")
        except Exception as e:
            logging.exception("Failed to send email: %s", e)
            return 4
    else:
        logging.info("No matches found for %s today.", CLASS_NAME)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
