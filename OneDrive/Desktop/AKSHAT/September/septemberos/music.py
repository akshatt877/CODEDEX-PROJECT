import pygame
import threading

def play_lofi_music():
    def _play():
        try:
            pygame.mixer.init()
            # Placeholder: Replace 'lofi.mp3' with your own cozy lo-fi track
            pygame.mixer.music.load('')
            pygame.mixer.music.play(-1)
        except Exception:
            pass  # Ignore errors if no music file is present
    threading.Thread(target=_play, daemon=True).start()
