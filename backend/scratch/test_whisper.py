import whisper
import traceback
from pathlib import Path

def test_whisper():
    print("Loading whisper model...")
    try:
        model = whisper.load_model("base")
        print("Model loaded successfully!")
        
        uploads = list(Path("uploads").glob("*"))
        if uploads:
            test_file = str(uploads[0])
            print(f"Transcribing test file: {test_file}")
            result = model.transcribe(test_file)
            print("Transcription success:", result.get("text")[:100])
        else:
            print("No uploaded files found in uploads/ directory.")
    except Exception as e:
        print("Error during whisper transcription:")
        traceback.print_exc()

test_whisper()
