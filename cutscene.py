import arcade
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
SOUNDS_DIR = os.path.join(BASE_DIR, 'sounds')

BLACK_SCREEN_IMG = os.path.join(ASSETS_DIR, "black_screen.png")
ENTRADA_INFO_IMG = os.path.join(ASSETS_DIR, "phase1", "entrada_info.jpeg")

FOOTSTEPS_SOUND = os.path.join(SOUNDS_DIR, 'footsteps_daniel.mp3')
CRICKET_SOUND = os.path.join(SOUNDS_DIR, 'cricket.mp3')
WIND_SOUND = os.path.join(SOUNDS_DIR, 'SoftWind.mp3')
THEME_SOUND = os.path.join(SOUNDS_DIR, 'theme.mp3')

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

FADE_TIME = 2.0
BLACKSCREEN_HOLD = 15.0
FADE_SOUNDS_TIME = 2.0
FADE_OUT_TIME = 2.0


class CutsceneView(arcade.View):

    STATE_FADE_TO_BLACK = 0
    STATE_HOLD = 1
    STATE_FADE_FROM_BLACK = 2

    def __init__(self):
        super().__init__()
        self.time = 0
        self.state = self.STATE_FADE_TO_BLACK

        # SPRITES (muito importante!)
        self.bg_sprite = arcade.Sprite(ENTRADA_INFO_IMG)
        self.bg_sprite.center_x = SCREEN_WIDTH // 2
        self.bg_sprite.center_y = SCREEN_HEIGHT // 2

        self.black_sprite = arcade.Sprite(BLACK_SCREEN_IMG)
        self.black_sprite.center_x = SCREEN_WIDTH // 2
        self.black_sprite.center_y = SCREEN_HEIGHT // 2
        self.black_sprite.alpha = 0

        # Som (players)
        self.menu_music_player = None
        self.cricket_player = None
        self.wind_player = None
        self.theme_player = None

        self.sfx_played = False

    def setup(self, menu_music_player):
        # Referência para a música do menu
        self.menu_music_player = menu_music_player

    def on_update(self, dt):
        self.time += dt

        # -----------------------------------
        # ESTADO 1 — Fade para preto
        # -----------------------------------
        if self.state == self.STATE_FADE_TO_BLACK:
            p = min(self.time / FADE_TIME, 1)

            # Fade visual
            self.black_sprite.alpha = int(255 * p)

            # Fade de música do menu
            if self.menu_music_player:
                try:
                    self.menu_music_player.volume = 1 - p
                except:
                    pass

            if p >= 1:
                self.state = self.STATE_HOLD
                self.time = 0

        # -----------------------------------
        # ESTADO 2 — Tela preta (sons)
        # -----------------------------------
        elif self.state == self.STATE_HOLD:

            # 1x sons de passos no começo
            if not self.sfx_played:
                try:
                    arcade.Sound(FOOTSTEPS_SOUND).play(volume=1.0)
                except:
                    pass

                # Sons ambientais LOOP
                self.cricket_player = arcade.Sound(CRICKET_SOUND, streaming=True).play(volume=0, loop=True)
                self.wind_player = arcade.Sound(WIND_SOUND, streaming=True).play(volume=0, loop=True)

                self.sfx_played = True

            # Fade-in sons ambientais
            if self.time <= FADE_SOUNDS_TIME:
                k = self.time / FADE_SOUNDS_TIME
                if self.cricket_player:
                    self.cricket_player.volume = k
                if self.wind_player:
                    self.wind_player.volume = k

            # Após tempo na escuridão -> reveal
            if self.time >= BLACKSCREEN_HOLD:
                self.state = self.STATE_FADE_FROM_BLACK
                self.time = 0

        # -----------------------------------
        # ESTADO 3 — Revealação (fade out da tela preta)
        # -----------------------------------
        elif self.state == self.STATE_FADE_FROM_BLACK:
            p = min(self.time / FADE_OUT_TIME, 1)

            # Alpha de 255 → 0
            self.black_sprite.alpha = int(255 * (1 - p))

            # Música da fase
            if self.theme_player is None:
                try:
                    snd = arcade.Sound(THEME_SOUND, streaming=True)
                    self.theme_player = snd.play(volume=0, loop=True)
                except:
                    pass
            else:
                try:
                    self.theme_player.volume = p
                except:
                    pass

            if p >= 1:
                print("Cutscene terminou — avance para a fase 1 aqui")
                # aqui você troca de view
                # ex:
                # from phase1 import Phase1View
                # self.window.show_view(Phase1View())
                pass

    def on_draw(self):
        self.clear()

        # Enquanto está no último estado, mostre o BG da fase
        if self.state == self.STATE_FADE_FROM_BLACK:
            self.bg_sprite.draw()

        self.black_sprite.draw()
