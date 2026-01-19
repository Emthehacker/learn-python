"""
PDF to Audiobook Converter with Natural Voices
Supports multiple TTS engines for better voice quality
"""

import re
import PyPDF2
from pathlib import Path

def remove_emojis(text):
    """Remove emojis and special characters from text"""
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", 
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

def clean_text(text):
    """Clean and normalize text for better speech output"""
    text = remove_emojis(text)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove page numbers (common pattern: isolated numbers)
    text = re.sub(r'\n\d+\n', '\n', text)
    return text.strip()

def extract_pdf_text(pdf_path):
    """Extract text from PDF file"""
    print(f"Reading PDF: {pdf_path}")
    
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        pages_count = len(reader.pages)
        print(f"Total pages: {pages_count}")
        
        full_text = ""
        for page_no in range(pages_count):
            page = reader.pages[page_no]
            text = page.extract_text()
            full_text += text + "\n"
            
            if (page_no + 1) % 10 == 0:
                print(f"Processed {page_no + 1}/{pages_count} pages...")
    
    return clean_text(full_text)


# Option 1: Using gTTS (Google Text-to-Speech) - Most natural sounding
def create_audiobook_gtts(text, output_file="audiobook.mp3"):
    """
    Create audiobook using Google Text-to-Speech (gTTS)
    Install: pip install gtts
    Pros: Very natural voice, multiple languages
    Cons: Requires internet connection
    """
    try:
        from gtts import gTTS
        
        print("Generating audiobook with Google TTS...")
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_file)
        print(f"✓ Audiobook saved to: {output_file}")
        
    except ImportError:
        print("Please install gTTS: pip install gtts")
    except Exception as e:
        print(f"Error: {e}")


# Option 2: Using pyttsx3 with improved settings
def create_audiobook_pyttsx3(text, output_file="audiobook.mp3"):
    """
    Create audiobook using pyttsx3
    Install: pip install pyttsx3
    Pros: Works offline, fast
    Cons: Less natural sounding than cloud services
    """
    try:
        import pyttsx3
        
        speaker = pyttsx3.init()
        
        # Improve voice quality with settings
        voices = speaker.getProperty('voices')
        
        # Try to use a better voice (usually index 1 is female, sounds more natural)
        if len(voices) > 1:
            speaker.setProperty('voice', voices[1].id)
        
        # Adjust speech rate (default is 200, lower is slower/clearer)
        speaker.setProperty('rate', 175)
        
        # Adjust volume (0.0 to 1.0)
        speaker.setProperty('volume', 0.9)
        
        print("Generating audiobook with pyttsx3...")
        speaker.save_to_file(text, output_file)
        speaker.runAndWait()
        speaker.stop()
        print(f"✓ Audiobook saved to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")


# Option 3: Using edge-tts (Microsoft Edge TTS) - Best free option
def create_audiobook_edge_tts(text, output_file="audiobook.mp3"):
    """
    Create audiobook using Microsoft Edge TTS
    Install: pip install edge-tts
    Pros: Excellent natural voices, offline capable, free
    Cons: Requires async code
    """
    try:
        import edge_tts
        import asyncio
        
        async def generate():
            print("Generating audiobook with Microsoft Edge TTS...")
            # Popular natural voices:
            # en-US-AriaNeural (female, warm)
            # en-US-GuyNeural (male, clear)
            # en-GB-SoniaNeural (British female)
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
            await communicate.save(output_file)
            print(f"✓ Audiobook saved to: {output_file}")
        
        asyncio.run(generate())
        
    except ImportError:
        print("Please install edge-tts: pip install edge-tts")
    except Exception as e:
        print(f"Error: {e}")


# Main execution
if __name__ == "__main__":
    # Configuration
    PDF_FILE = "hold me tight.pdf"
    OUTPUT_FILE = "audiobook.mp3"
    
    # Check if PDF exists
    if not Path(PDF_FILE).exists():
        print(f"Error: PDF file '{PDF_FILE}' not found!")
        exit(1)
    
    # Extract text from PDF
    text = extract_pdf_text(PDF_FILE)
    print(f"\nExtracted {len(text)} characters")
    
    # Preview first 200 characters
    print(f"\nPreview:\n{text[:200]}...\n")
    
    # Choose your preferred method (uncomment one):
    
    # Best quality (requires internet):
    # create_audiobook_gtts(text, OUTPUT_FILE)
    
    # Best free offline option (recommended):
    create_audiobook_edge_tts(text, OUTPUT_FILE)
    
    # Basic offline option:
    # create_audiobook_pyttsx3(text, OUTPUT_FILE)
    
    print("\nDone! 🎧")
