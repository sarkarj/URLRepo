# URLRepo 📚✨

**URLRepo** is a minimal yet powerful Flask web app that allows users to submit and analyze HTTPS URLs. Using Google's Gemini API, the app fetches article content, summarizes it, extracts critical keywords, and stores the metadata for later reference.

---

## 🚀 Features

- 🧠 **AI Summarization**: Uses Gemini 2.0 Flash to summarize content and extract keywords.
- 📎 **De-duplication**: Prevents storing the same URL multiple times.
- ⚡ **Rate Limiting**: Guards against abuse using Flask-Limiter.
- 💾 **SQLite Storage**: Lightweight, file-based database with auto-init.
- 🧹 **Bookmark Management**: Delete stored URLs via the interface.
- 📜 **Logging**: Centralized error logging for easy debugging.
- 📦 **Dockerized**: Production-ready with Docker Compose support.
- 🔐 **Secure Config**: Secrets loaded via `.env` using `python-decouple`.

---

## 🛠️ Setup

### Prerequisites

- Python 3.9+
- Docker + Docker Compose (optional but recommended)

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/urlrepo.git
cd urlrepo
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Add Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Run Locally

```bash
python app.py
```

Visit [http://localhost:8085](http://localhost:8085)

---

## 🐳 Run via Docker

```bash
docker-compose up -d --build
```

To access: `http://<your-host-ip>:8085`

---

## ✨ Tech Stack

- Flask (Jinja2, Flash, Request Handling)
- SQLite
- Google Gemini API
- `newspaper3k` for content extraction
- `requests`, `python-decouple`, `flask-limiter`
- Docker, Docker Compose

---

## 📁 Project Structure

```
├── app.py
├── database.db
├── templates/
├── static/
├── requirements.txt
├── .env
├── Dockerfile
└── docker-compose.yml
```

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing

Issues and PRs are welcome. Please open an issue to discuss your ideas or suggestions before submitting changes.

---

## 📬 Contact

Built with 💡 by [Your Name] — for support, open an issue or ping on GitHub.
