import pyttsx3
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    found = False
    print("--- Searching for Hindi/India Voices ---")
    for voice in voices:
        if "Hindi" in voice.name or "India" in voice.name or "Kalpana" in voice.name or "Hemant" in voice.name:
            print(f"FOUND: ID={voice.id} | Name={voice.name}")
            found = True
            
    if not found:
        print("No specific Hindi/India voices found. Listing all:")
        for voice in voices:
            print(f"Name={voice.name}")
except Exception as e:
    print(f"Error: {e}")
