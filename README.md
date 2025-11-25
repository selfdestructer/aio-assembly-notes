# AIO Launcher AssemblyAI Meeting Notes

This project automates the transcription and translation of voice recordings from AIO Launcher using the AssemblyAI API.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install assemblyai requests
    ```

2.  **Environment Variables:**
    Copy `.env.example` to `.env` and add your AssemblyAI API key.
    ```bash
    cp .env.example .env
    ```

3.  **Usage:**
    The script is intended to be triggered by AIO Launcher or run manually on a recorded file.
    ```bash
    python transcribe.py path/to/audio/file.mp3
    ```
