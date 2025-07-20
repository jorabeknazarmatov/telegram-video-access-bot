# 🎬 telegram-video-access-bot

**telegram-video-access-bot** — Telegram bot for distributing exclusive video content via secure access keys.  
Admins upload videos and generate unique keys. Users submit those keys to access the content instantly.

## 🚀 Features

- 👤 Role-based logic (admin vs user)
- 🎞 Admins can:
  - Upload videos via FSM flow
  - Assign title, description, categories, actors
  - Auto-generate secure access key
- 📥 Users can:
  - Submit access key (e.g., `GC_T_XXXX`)
  - Receive the corresponding video with details
- 📊 Admin control panel and key tracking
- ✅ Secure `.env` configuration
- 🧱 Modular architecture

## 🛠 Stack

- Python 3.10+
- [Aiogram 3](https://github.com/aiogram/aiogram)
- SQLite or PostgreSQL (via `db.py`)
- Render-ready deployment

## 🔧 Local Setup

```bash
git clone https://github.com/jorabeknazarmatov/telegram-video-access-bot.git
cd telegram-video-access-bot
```

Create a `.env` file:

```
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=admin1_id,admin2_id
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the bot locally:

```bash
python main.py
```

## ☁️ Deploy to Render

1. Go to [Render.com](https://render.com/)
2. Click **New Web Service**
3. Connect your GitHub repo
4. Set the start command:
   ```bash
   python main.py
   ```
5. Add environment variable:
   ```
   BOT_TOKEN=your_telegram_bot_token
   ```

6. Deploy and your bot will go live!

## 📁 Project Structure

```
video-key-bot/
│
├── handlers/          # Admin and user message handlers
├── keyboards/         # Inline and reply keyboards
├── middleware/        # Role-based middleware
├── db.py              # Database interaction
├── main.py            # Bot entry point
├── .env               # Your secrets (ignored from git)
└── requirements.txt   # Python dependencies
```

## 🧑‍💻 Author

Created by [@jorabeknazarmatov](https://github.com/jorabeknazarmatov) — PRs welcome!
