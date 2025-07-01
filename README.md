
This project is a conversational bot powered by **Gemini (Google Generative AI)** and integrated with **Google Calendar API** to help users:
- Chat about a real estate project
- Schedule events directly into Google Calendar

---

## 🛠️ Tech Stack

- LangGraph + LangChain
- Google Calendar API
- Gemini (Generative AI from Google)
- Python 3.9+
- uv (ultra-fast virtual environment tool)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Install `uv`

If you don't have `uv` installed:

```bash
pip install uv
```

### 3. Create Virtual Environment and Install Dependencies

```bash
uv venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate        # Windows

uv pip install -r requirements.txt
```

Or manually install:

```bash
uv pip install langgraph langchain python-dotenv google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client langchain_google_genai
```

---

## 🔑 Configuration

### 1. Get Gemini API Key

- Visit [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
- Copy your Gemini API key

### 2. Set Up Google Calendar API

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Enable **Google Calendar API** in your project
- Go to **Credentials** > Create **OAuth Client ID**
- Download the `client_secret.json` file
- Place it in your project root

### 3. Create `.env` File

Create a `.env` file in your root directory:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 4. Authenticate with Google

First time you run the app, it will generate a `token.json` file after OAuth login in the browser.

---

## ▶️ Run the App

```bash
python main.py
```

Type messages to interact with the bot.

Type `exit` or `quit` to end.

---

## 💡 Sample Interactions

- "Tell me about the 3BHK apartment"
- "Schedule a meeting for tomorrow at 2 PM"
- "Can you add a calendar event on Friday?"

---

## 📂 Folder Structure

```
.
├── client_secret.json
├── .env
├── main.py
├── requirements.txt
├── README.md
├── token.json (after first run)
```

---

## ❗ Notes

- Make sure `.env` and `client_secret.json` are **not committed** to version control.
- Only schedule when **both date and time** are provided.
- Booking tool avoids multiple calendar insertions.

---
