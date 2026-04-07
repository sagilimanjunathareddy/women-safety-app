# utils/siren_player.py
import pygame
import threading

def play_siren():
    def run():
        pygame.mixer.init()
        pygame.mixer.music.load("assets/siren.mp3")
        pygame.mixer.music.play()
    threading.Thread(target=run).start()
