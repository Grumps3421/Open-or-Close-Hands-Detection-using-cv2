import threading
from .sound_model import SoundModel
from .sound_view import SoundView

class SoundController:
    def __init__(self):
        self.model = SoundModel()
        self.view = SoundView()

    def play_student_sound(self, bracelet_id: str):
        """
        Plays the correct audio for a student or 'NoAnswer'.
        """
        sound_path = self.model.get_sound_path(bracelet_id)
        if not sound_path:
            print(f"⚠️ No sound found for {bracelet_id}")
            return

        def play():
            self.view.play_sound(sound_path)
            if bracelet_id == "NoAnswer":
                print("🔊 NoAnswer played successfully")
            else:
                print(f"🔊 {bracelet_id} played successfully")

        # Non-blocking playback
        threading.Thread(target=play, daemon=True).start()
