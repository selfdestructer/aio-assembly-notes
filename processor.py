import os
import assemblyai as aai
from dotenv import load_dotenv
from datetime import datetime
from context_manager import get_context, log_decision
from ghost_ship import get_ghost_ship_prompt

# Load environment variables
load_dotenv()

API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not API_KEY:
    # Fallback if called from server where env might be loaded differently
    API_KEY = os.environ.get("ASSEMBLYAI_API_KEY")

if API_KEY:
    aai.settings.api_key = API_KEY

def get_lemur_prompt(mode, context=None):
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
    elif mode == 'story':
        return f"""
        You are a Master Biographer and Storyteller. 
        
        **Context from the Book of Life:**
        {context}
        
        **Task:**
        Take the provided transcript (which is a raw entry from the user's life) and weave it into the non-linear narrative of their biography.
        
        **Output Format:**
        # 📖 The Living Book: New Entry
        **Chapter Title:** [Creative Title]
        **The Narrative:** [Write this as a compelling story scene in the third person or first person, matching the user's style. Do not just summarize; Dramatize.]
        **Thematic Link:** [Explain how this event connects to previous themes in the Context provided]
        """
    elif mode == 'decision':
        return """
        You are a Strategic Life Advisor. Analyze this transcript where the user is discussing a decision or an outcome.
        
        **Output Format:**
        # ⚖️ Decision Matrix
        **The Dilemma:** [What was at stake?]
        **The Choice:** [What did they do?]
        **The Outcome:** [What happened?]
        **Analysis:** [Was this consistent with their values? What can be learned?]
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

def process_audio(file_path, mode='quick', options=None):
    if options is None:
        options = {}
        
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    print(f"Transcribing {file_path} in {mode} mode...")
    
    transcriber = aai.Transcriber()
    
    # Configure based on mode
    config_args = {
        "speaker_labels": mode == 'meeting',
        "auto_chapters": mode == 'lecture' or mode == 'story',
        "entity_detection": True,
        "sentiment_analysis": True,
    }
    
    config = aai.TranscriptionConfig(**config_args)
    
    try:
        transcript = transcriber.transcribe(file_path, config)
        
        if transcript.status == aai.TranscriptionStatus.error:
            return f"Transcription failed: {transcript.error}"
            
        # --- Generate Outputs ---
        
        # Get Context for advanced modes
        context_data = get_context() if mode in ['story', 'decision'] else None
        
        # 1. LeMUR Analysis
        prompt = get_lemur_prompt(mode, context_data)
        lemur_result = transcript.lemur.task(prompt)
        ai_notes = lemur_result.response

        # 2. Special Logic: Ghost Ship (Alternate Timeline)
        ghost_ship_content = ""
        if mode == 'decision' and options.get('ghost_ship', False):
             print("Calculating Alternate Timeline (Ghost Ship)...")
             # In a real app, we'd fetch past decisions specifically related to this topic
             past_decisions_summary = str(context_data.get('decisions', []))
             ghost_prompt = get_ghost_ship_prompt(transcript.text, past_decisions_summary)
             ghost_result = transcript.lemur.task(ghost_prompt)
             ghost_ship_content = f"\n\n---\n{ghost_result.response}\n---\n"

        # --- Save to Markdown File ---
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Determine output directory based on mode
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if mode == 'story':
            output_dir = os.path.join(base_dir, "Life_OS", "02_Library")
        elif mode == 'decision':
            output_dir = os.path.join(base_dir, "Life_OS", "03_Decision_Matrix")
        else:
            output_dir = os.path.join(base_dir, "Life_OS", "01_Inbox")
            
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_file = os.path.join(output_dir, f"{base_name}_{mode}_{timestamp}.md")
        
        content = []
        content.append(f"# {mode.capitalize()} Report: {base_name}")
        content.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        content.append("## 🤖 AI Analysis")
        content.append(ai_notes)
        content.append(ghost_ship_content)
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