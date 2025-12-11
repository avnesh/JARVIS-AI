from dotenv import load_dotenv
import os
import sys

# Python 3.13 removed aifc, which speech_recognition needs. Mock it.
if sys.version_info >= (3, 13):
    import types
    aifc = types.ModuleType('aifc')
    aifc.Error = Exception
    sys.modules['aifc'] = aifc
    
    # Shim audioop
    try:
        import audioop
    except ImportError:
        try:
            import audioop_lts as audioop
            sys.modules['audioop'] = audioop
        except ImportError:
            pass # Let it fail later or handled by pip install


# Load config from .env or env.txt
# Ensure we load from the GUI directory where main.py resides
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not load_dotenv(env_path):
    # If no .env is found in GUI/, try root or env.txt
    if os.path.exists("env.txt"):
        load_dotenv("env.txt")
    else:
        # Fallback to standard search if specific path fails
        load_dotenv()

from kivy import app, clock
from jarvis import Jarvis

class MykivyApp(app.App):
    def build(self):
        jarvis = Jarvis()
        jarvis.start_listening()
        
        self.update_event = clock.Clock.schedule_interval(jarvis.update_circle,1/60)
        self.btn_rotation_event = clock.Clock.schedule_interval(jarvis.circle.rotate_button,1/60)
        
        return jarvis
    
    
if __name__ == '__main__':
    MykivyApp = MykivyApp()
    MykivyApp.run()    