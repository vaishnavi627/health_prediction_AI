 # HealthPredict AI

An educational health-risk information application with a FastAPI backend,
Streamlit frontend, SQLite storage, and Groq-powered health remarks.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set `GROQ_API_KEY`.

## Run

Start the API from the project root:

```bash
uvicorn backend.main:app --reload
```

In another terminal, start the frontend:

```bash
streamlit run frontend/app.py
```

The API runs at `http://127.0.0.1:8000` and the Streamlit app opens in your
browser. This application provides educational information only and does not
diagnose medical conditions.