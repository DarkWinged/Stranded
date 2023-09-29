import pygame.mixer

class SoundManager:
    def __init__(self, music_file_path, music_volume=0.5):
        pygame.mixer.init()
        self.music_channel = pygame.mixer.Channel(0)
        self.music_volume = music_volume
        self.load_music(music_file_path)
        self.sound_enabled = True

    def load_music(self, music_file_path):
        pygame.mixer.music.load(music_file_path)
        pygame.mixer.music.set_volume(self.music_volume)

    def play_music(self, loop_count=-1):
        if self.sound_enabled:
            pygame.mixer.music.play(loop_count)

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.unpause_music()
        else:
            self.pause_music()

    def volume_up(self):
        self.music_volume += 0.1
        if self.music_volume > 1.0:
            self.music_volume = 1.0
        pygame.mixer.music.set_volume(self.music_volume)

    def volume_down(self):
        self.music_volume -= 0.1
        if self.music_volume < 0.0:
            self.music_volume = 0.0
        pygame.mixer.music.set_volume(self.music_volume)
