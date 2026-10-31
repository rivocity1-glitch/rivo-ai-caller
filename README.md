# Rivo AI Caller

Local-first Windows desktop prototype for RivoCity vendor outreach.

## Saved development checkpoint — 31 October 2026

The desktop prototype launches and the local AI prompt test has been confirmed working with `qwen2.5:3b` through Ollama.

Implemented and tested:
- PySide6 desktop dashboard.
- Microphone device discovery and live input-level testing.
- Green-to-yellow-to-red microphone level progress bar.
- Local Ollama connectivity check and prompt/response test.
- AI generation in a background QThread so the UI does not freeze during inference.
- Error reporting in the diagnostics panel for failed AI requests.

**Last confirmed working state:** App opens, Ollama reports connected, and the sample RivoCity prompt returns a response in the diagnostics panel.

**Not implemented yet:** speech-to-text, text-to-speech, live conversation handling, Android/SIM call integration, and phone calls. The prototype does not place calls.

### Resume from here

Next milestone: implement local speech-to-text first, then evaluate Marathi/Hindi/English text-to-speech and connect both to the conversation engine. Before adding the acoustic SIM-call bridge, test microphone and speaker routing independently.

## Target hardware

- Windows 10 (22H2 recommended)
- AMD Ryzen 5 2600
- NVIDIA GTX 1650 4 GB
- 16 GB RAM
- Android phone with active SIM (AI runs on the PC)

## Prerequisites

1. Install Python 3.11 (64-bit).
2. Install Git for Windows.
3. Install Ollama for Windows.
4. In a terminal, download the initial model:

```powershell
ollama pull qwen2.5:3b
```

## Setup

Open PowerShell in the cloned repository:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

If PowerShell blocks activation, run this once for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## First test

1. Open Rivo AI Caller.
2. Select the microphone device.
3. Click **Start microphone test** and speak.
4. Confirm the input meter moves.
5. Click **Test Ollama** to check the local model connection.

Ollama normally serves its local API at `http://127.0.0.1:11434`.

## Safety and calling policy

- The app does not auto-dial or bulk-call.
- Identify the caller as Rivo's AI assistant.
- Only contact vendors using an appropriate consent-based and legally compliant process.
- Do not upload vendor contact lists, call recordings, or transcripts to public repositories.
- Do not commit real credentials or private customer/vendor data.

## Planned milestones

1. Local desktop + hardware diagnostics (current).
2. Local speech recognition and language detection.
3. Marathi/Hindi/English voice output evaluation.
4. Turn-taking, interruption handling, and echo control.
5. Acoustic bridge with manually initiated SIM calls.
6. Call summaries and consent/opt-out records.
7. Optional Supabase integration with RivoCity Admin.
