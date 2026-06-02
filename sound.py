# sound.py

import pygame
import math
import array

class SoundFX:
    def __init__(self):
        self.active = False
        try:
            # Инициализация микшера Pygame, если он не готов
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1)
            self.active = True
        except Exception:
            self.active = False

    def play_click(self):
        if not self.active: return
        self._play_tone(600, 0.05, 0.06)

    def play_error(self):
        if not self.active: return
        self._play_tone(150, 0.25, 0.12)

    def play_success(self):
        if not self.active: return
        # Двойной аккорд победы
        self._play_tone(523, 0.08, 0.05)
        self._play_tone(659, 0.12, 0.05)

    def play_notify(self):
        if not self.active: return
        self._play_tone(440, 0.12, 0.06)

    def _play_tone(self, frequency, duration, volume=0.05):
        try:
            sample_rate = 22050
            num_samples = int(sample_rate * duration)
            buf = array.array('h', [0] * num_samples)
            for i in range(num_samples):
                t = i / sample_rate
                # Прямоугольная (Square) волна для 8-битного звучания
                val = volume * 32767 * (1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0)
                buf[i] = int(val)
            sound = pygame.mixer.Sound(buffer=buf)
            sound.play()
        except Exception:
            pass