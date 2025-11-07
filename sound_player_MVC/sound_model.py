import os

class SoundModel:
    def __init__(self):
        # Folder where all your .mp3 sounds are stored
        self.sound_folder = os.path.join(os.path.dirname(__file__), "..", "sound_system")

    def get_sound_path(self, bracelet_id: str):
        """
        Returns the full path to the student's sound file.
        """
        if bracelet_id == "NoAnswer":
            filename = "NoAnswer_audio.mp3"
        else:
            filename = f"{bracelet_id}_audio.mp3"

        sound_path = os.path.join(self.sound_folder, filename)
        if os.path.exists(sound_path):
            return sound_path
        else:
            print(f"⚠️ Sound file not found for bracelet_id: {bracelet_id}")
            return None
