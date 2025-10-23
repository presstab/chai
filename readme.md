# Project: Chai (Chat + AI)

This repository contains the source code for the "Chai" command-line AI chat application, developed as part of the DBT230 course.

## Author

**Name:** [TODO: Add Your Name Here]

## Lab 1: Flat-File Persistence

This lab focuses on building the foundational persistence layer using a simple flat-file (JSON) system. The goal is to establish a performance baseline for file I/O operations, which will serve as a benchmark for subsequent labs involving more advanced database technologies.

## Run

Run the app with uv (it will create an environment and install dependencies as needed):

```bash
uv run main.py
```

Tip: set up your `.env` first (see section below) so the AI responses are enabled.

## AI Provider Configuration (.env)

Chai uses an OpenAI-compatible API for AI responses. Configure your credentials and provider via a local `.env` file at the project root.

Quick setup:

1. Copy the example env file to create your local config
   - macOS/Linux: `cp .env.example .env`
   - Windows (PowerShell): `Copy-Item .env.example .env`
2. Open `.env` and replace `OPENAI_KEY` with your real API key.
3. Optional: set `BASE_URL` to target a different OpenAI-compatible provider (e.g., `https://api.openai.com/v1`, `https://api.groq.com/openai/v1`, or a local server).
4. Optional: set `MODEL` (e.g., `gpt-4o-mini`, `gpt-4o`, `llama3.1:8b`). If unset, the app uses `OPENAI_MODEL` then a sensible default.

Notes:
- The app loads `.env` automatically on startup.
- If `OPENAI_KEY` is missing, the app will run but will print a helpful message instead of contacting the provider.
- Conversation history is stored under `data/` using flat files.
