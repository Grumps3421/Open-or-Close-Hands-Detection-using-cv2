import pygame
import time

class SoundView:
    def __init__(self):
        pygame.mixer.init()

    def play_sound(self, sound_path: str):
        """
        Plays the given sound file using pygame.
        """
        try:
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()

            # Wait until the sound finishes
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
        except Exception as e:
            print(f"❌ Error playing sound: {e}")
