import os
import assemblyai as aai
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not API_KEY:
    # Fallback if called from server where env might be loaded differently
    API_KEY = os.environ.get("ASSEMBLYAI_API_KEY")

if API_KEY:
    aai.settings.api_key = API_KEY

def get_lemur_prompt(mode):
    if mode == 'meeting':
        return """
        You are an expert executive assistant. Analyze the provided transcript and generate a comprehensive meeting report.
        
        Please provide the output in the following Markdown format:
        # Meeting Summary
        [Provide a concise executive summary of the meeting]
        # Key Takeaways
        [List the main points discussed]
        # Action Items
        [List specific tasks, who is responsible (if mentioned), and deadlines]
        # Decisions Made
        [List any concrete decisions or agreements reached]
        # Sentiment Analysis
        [Briefly describe the overall tone and sentiment of the meeting]
        """
    elif mode == 'lecture':
        return """
        You are a diligent student. Analyze this lecture transcript and create a study guide.
        
        Please provide the output in the following Markdown format:
        # Lecture Topic
        [Brief summary of the main topic]
        # Core Concepts
        [List and define the key concepts explained]
        # Detailed Notes
        [Summarize the lecture content chronologically]
        # Quiz Questions
        [Generate 3-5 questions to test understanding of this material]
        """
    else: # quick / default
        return """
        You are a helpful assistant. Summarize this recording briefly.
        
        Format:
        # Summary
        [Concise summary]
        # Main Points
        [Bullet points]
        """

def process_audio(file_path, mode='quick'):
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    print(f"Transcribing {file_path} in {mode} mode...")
    
    transcriber = aai.Transcriber()
    
    # Configure based on mode
    config_args = {
        "speaker_labels": mode == 'meeting',
        "auto_chapters": mode == 'lecture',
        "entity_detection": True,
        "sentiment_analysis": True,
    }
    
    config = aai.TranscriptionConfig(**config_args)
    
    try:
        transcript = transcriber.transcribe(file_path, config)
        
        if transcript.status == aai.TranscriptionStatus.error:
            return f"Transcription failed: {transcript.error}"
            
        # --- Generate Outputs ---
        
        # 1. LeMUR Analysis
        prompt = get_lemur_prompt(mode)
        lemur_result = transcript.lemur.task(prompt)
        ai_notes = lemur_result.response

        # 2. Translation (Optional - could be added to mode config)
        # translation = ... 

        # --- Save to Markdown File ---
        base_name = os.path.splitext(file_path)[0]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"{base_name}_{mode}_{timestamp}.md"
        
        content = []
        content.append(f"# {mode.capitalize()} Report: {os.path.basename(file_path)}")
        content.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        content.append("## 🤖 AI Analysis")
        content.append(ai_notes)
        content.append("\n")
        
        if transcript.chapters:
            content.append("## TAB Chapters")
            for chapter in transcript.chapters:
                start = int(chapter.start / 1000)
                content.append(f"- **{start}s**: {chapter.headline}")
            content.append("\n")

        content.append("## 📝 Transcript")
        for utterance in transcript.utterances:
            speaker_label = f"**Speaker {utterance.speaker}**" if config_args["speaker_labels"] else "**Speaker**"
            content.append(f"{speaker_label}: {utterance.text}\n")
            
        final_md = "\n".join(content)
        
        with open(output_file, "w") as f:
            f.write(final_md)
            
        return output_file

    except Exception as e:
        return f"An error occurred: {str(e)}"