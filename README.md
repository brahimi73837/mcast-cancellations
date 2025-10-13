# MCAST Cancelled Lectures Notifier

Automatically checks the [MCAST IICT Cancelled Lectures](https://iict.mcast.edu.mt/cancelled-lectures/) page every morning and sends an email **only if** a lecture from a specified class (e.g. `SWD-6.3A`) appears among the cancellations.

Runs daily using **GitHub Actions** — no need to keep your computer on.

---

## 🧩 Features

- ✅ Automatically fetches the cancelled lectures page once per day  
- ✅ Detects your class name (with fuzzy matching for typos, e.g. `SWD-6.3A` vs `SWD–6.3A`)  
- ✅ Sends an email alert through Gmail SMTP  
- ✅ 100% free using GitHub Actions  
- ✅ No Selenium or browser required (uses `requests` + `BeautifulSoup`)

---

## ⚙️ How it Works

1. GitHub Actions triggers the workflow every day at **07:00 Malta time (05:00 UTC)**.  
2. The script downloads the HTML of the Cancelled Lectures page.  
3. It searches the page text for your class name using fuzzy matching.  
4. If found, an email is sent using your Gmail App Password.  
5. The run stops quietly if no match is found (no email).

---

## 📁 Repository Structure

```

mcast-cancellations/
├── check_cancellations.py   # Main Python script
├── requirements.txt         # Dependencies
├── .github/
│   └── workflows/
│       └── check.yml        # GitHub Actions workflow (runs daily)
└── README.md

````

---

## 🧰 Setup Instructions

### 1️⃣ Clone the repository locally (optional)

```bash
git clone https://github.com/<your-username>/mcast-cancellations.git
cd mcast-cancellations
````

### 2️⃣ Add GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret Name       | Example Value                                   | Description                               |
| ----------------- | ----------------------------------------------- | ----------------------------------------- |
| `EMAIL_USER`      | `you@gmail.com`                                 | Gmail address (must match App Password)   |
| `EMAIL_PASS`      | `xxxx xxxx xxxx xxxx`                           | Gmail App Password (16 chars)             |
| `TO_EMAIL`        | `you@gmail.com`                                 | Recipient address (can be same as sender) |
| `CLASS_NAME`      | `SWD-6.3A`                                      | Your class code                           |
| `FUZZY_THRESHOLD` | `0.8`                                           | Sensitivity for matching (optional)       |
| `TARGET_URL`      | `https://iict.mcast.edu.mt/cancelled-lectures/` | Website to monitor (optional)             |

> 📝 Tip: Type secrets manually — avoid invisible spaces that can cause encoding errors.

---

## 🧪 Manual Run

To test manually:

1. Go to your GitHub repo → **Actions** tab.
2. Select **Check MCAST cancelled lectures** → **Run workflow** → click **Run workflow**.
3. Check your email and the workflow logs.

---

## ⏰ Schedule

* The workflow runs daily at **05:00 UTC** (07:00 Malta during DST).
* When DST ends (around late October), update `.github/workflows/check.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'   # 06:00 UTC = 07:00 Malta after DST
```

---

## 🔐 Security

* Your Gmail credentials are **never committed** to the repo.
* They are stored securely in GitHub Secrets.
* Uses Gmail **App Passwords** (not your main password).

---

### ❤️ Credits

Developed by **Brahim** — built to make MCAST mornings easier ☕
