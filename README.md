# 🎙️ Life OS (AI Audio Transcription)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![AssemblyAI](https://img.shields.io/badge/Powered%20by-AssemblyAI-purple?style=flat-square)](https://www.assemblyai.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**Turn your voice recordings into a Living Autobiography, Decision Matrix, and actionable intelligence.**

---

## 📖 Description

**Life OS** is a locally-hosted AI engine designed to run on your Android device (via Termux) or local machine. It bridges the gap between your daily voice notes and a structured, intelligible record of your life.

Unlike standard transcription tools, Life OS uses **context-aware AI** to:
*   Write your life story as a non-linear novel (**Story Mode**).
*   Analyze your life choices and simulate alternate timelines (**Decision Mode** & **Ghost Ship**).
*   Turn lectures into study guides (**Lecture Mode**).
*   Generate professional meeting minutes (**Meeting Mode**).

It leverages **AssemblyAI's Universal-1** model for high-accuracy transcription and **LeMUR** (LLM) for deep understanding.

### ✨ Key Features
*   **📖 Story Mode**: Automatically weaves new diary entries into a cohesive, thematic biography.
*   **👻 Ghost Ship Simulator**: A predictive engine that calculates "unlived lives" based on your decisions.
*   **🧠 Context Memory**: Remembers your core values, friends, and past events to provide personalized analysis.
*   **📱 Mobile-First**: Optimized for Android + AIO Launcher workflow.
*   **🔒 Private Storage**: All data is saved as open Markdown files on your device.

---

## 🛠️ Installation

### Prerequisites
*   **Android User**: [Termux](https://termux.dev/en/) installed.
*   **Python**: Version 3.8 or higher.
*   **AssemblyAI API Key**: Get one for free at [assemblyai.com](https://www.assemblyai.com/).

### Step-by-Step Setup

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/selfdestructer/aio-assembly-notes.git
    cd aio-assembly-notes
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key**:
    Create a `.env` file in the root directory:
    ```bash
    cp .env.example .env
    nano .env
    ```
    Paste your key: `ASSEMBLYAI_API_KEY=your_key_here`

4.  **Configure Recording Path**:
    Edit `server.py` to point to your audio folder:
    ```python
    # In server.py
    RECORDINGS_DIR = "/sdcard/Music/Recordings" # Update this path!
    ```

---

## 🚀 Usage

### 1. Start the Server
Run the Flask application:
```bash
python server.py
```

### 2. Open the Dashboard
Open your browser (or AIO Launcher widget) to:
`http://localhost:5000`

### 3. Choose a Mode
*   **Story Mode**: For diary entries. Updates your "Book of Life".
*   **Decision Logic**: For major choices. Toggling **Ghost Ship** will simulate what happens if you choose differently.
*   **Meeting**: For work calls. Generates action items.
*   **Lecture**: For classes. Generates quizzes and notes.

### 4. View Your Life
Outputs are automatically organized into the `Life_OS` folder:
*   `Life_OS/01_Inbox`: Standard transcripts.
*   `Life_OS/02_Library`: Your generated biography chapters.
*   `Life_OS/03_Decision_Matrix`: Analysis of your choices.

---

## 🏗️ Architecture

Life OS uses a **Hybrid Edge-Cloud** architecture:
1.  **Edge (Your Phone)**: Handles the UI, file storage (`Life_OS/`), and Context Logic (`context_manager.py`).
2.  **Cloud (AssemblyAI)**: Handles the heavy lifting—Speech Recognition and LLM reasoning.

This ensures your "Book of Life" (the text files) remains physically in your possession, while you still get SOTA AI performance.

---

## 🤝 Contributing

We welcome contributions! Whether it's a new "AI Persona" for a different mode or a better way to visualize the timeline.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Acknowledgments

*   **AssemblyAI**: For the powerful Speech AI models.
*   **AIO Launcher**: For the inspiration to build a streamlined mobile workflow.