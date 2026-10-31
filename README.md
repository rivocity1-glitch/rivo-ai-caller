# Rivo AI Caller

Local-first Windows desktop prototype for RivoCity vendor outreach.

## Current milestone

This first scaffold provides:
- A PySide6 desktop dashboard.
- Microphone device discovery and live input-level testing.
- Local Ollama connectivity and model test.
- A configuration path designed for later speech recognition, TTS, conversation management, and acoustic SIM-call bridging.

**It does not place phone calls yet.** Calls remain manually initiated on the Android phone. The acoustic bridge will be added only after microphone/speaker testing is stable.

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
