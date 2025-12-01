# cutscene.py
# ------------
# APENAS cut-scene. Quando acabar, fecha a janela.
# NÃO importa Phase1View, NÃO redireciona para lugar nenhum.

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
BLACKSCREEN_HOLD = 7.0
FADE_SOUNDS_TIME = 2.0
FADE_OUT_TIME = 2.0

# ---------- diálogo / Daniel ----------
DANIEL_IMG = os.path.join(ASSETS_DIR, "daniel.png")
DIALOG_BOX_IMG = os.path.join(ASSETS_DIR, "dialog_box", "dialog_box4.png")
SKIP_BUTTON_IMG = os.path.join(ASSETS_DIR, "skip_button.png")
VOICELINE_SOUND = os.path.join(SOUNDS_DIR, "voiceline.mp3")

DANIEL_ENTRANCE_DELAY = 1.5
ENTRANCE_DURATION = 1.2
DANIEL_FINAL_MARGIN = 2
DIALOG_BOTTOM_MARGIN = -460
DIALOG_POST_APPEAR_DELAY = 2.0
LETTER_INTERVAL_MS = 50

DIALOG_TITLE = "Daniel Temp"
DIALOG_TITLE_X = 160
DIALOG_TITLE_Y = 320
DIALOG_TITLE_FONT_SIZE = 28
DIALOG_TEXT_X = 100
DIALOG_TEXT_Y = 250
DIALOG_TEXT_FONT_SIZE = 18

SKIP_BUTTON_X = 1150
SKIP_BUTTON_Y = 120

DANIEL_BACK_IMG = os.path.join(ASSETS_DIR, "daniel_back.png")
CAR_START_SOUND = os.path.join(SOUNDS_DIR, "car_start.mp3")

FINAL_BLACK_FADE_TIME = 2.0
FINAL_BLACK_HOLD = 3.0
CAR_SOUND_DELAY = 2.0

SKIP_TEXTS = [
    "Bem-vindo ao Instituto Federal Farroupilha.",
    "Seu projeto foi avaliada e aprovada. Não haverá segunda chance nem fase de adaptação.",
    "A missão terá início assim que a noite apagar o último resquício de luz",
    "O protocolo, apesar do que alguns dizem, não é complexo.",
    "O campus oculta objetos que desapareceram durante o dia.",
    "Deslocados, abandonados, ou simplesmente atraídos para lugares onde não deveriam estar.",
    "Sua tarefa é localizar todos eles. Não deixe que a escuridão o distraia.",
    "A operação será encerrada apenas quando todos os itens forem recuperados.\nNão importa o que veja, o que escute ou o que julgue sentir atrás de você.",
    "Não interrompa o processo. Não compartilhe informações.",
    "Os alvos identificados para esta sessão são: Guarda-chuva, Fones de ouvido, Mochila, Tesoura e A̷̢̹̰̅r̴͈̥̟̪̂̈̋̄m̸̢͙͔̀̊͜a̵̢̨̧̛̻̝͐̉",
    "Cada objeto carrega vestígios do que aconteceu antes que você chegasse.",
    "Bom, eu vou indo. Conto com você."
]

# ---------- estados ----------
class CutsceneView(arcade.View):
    STATE_FADE_TO_BLACK = 0
    STATE_HOLD = 1
    STATE_FADE_FROM_BLACK = 2
    STATE_WAIT_FOR_DANIEL = 3
    STATE_DANIEL_ENTRANCE = 4
    STATE_PRESENT_COMPLETE = 5
    STATE_DANIEL_LEAVING = 6
    STATE_FADE_TO_BLACK_2 = 7
    STATE_FADE_FROM_BLACK_2 = 8
    STATE_DANIEL_BACK_SCENE = 9
    STATE_FINAL_BLACK = 10
    STATE_FADE_OUT_TO_END = 11

    def __init__(self):
        super().__init__()
        self.time = 0
        self.state = self.STATE_FADE_TO_BLACK
        self._ending_started = False
        self._car_sound_played = False
        self._voiceline_sound = None
        self.menu_music_player = None
        self.theme_player = None
        self.cricket_player = None
        self.wind_player = None
        self.sfx_played = False

        # sprites básicos
        self.bg_sprite = arcade.Sprite(ENTRADA_INFO_IMG)
        self.bg_sprite.center_x = SCREEN_WIDTH // 2
        self.bg_sprite.center_y = SCREEN_HEIGHT // 2

        self.black_sprite = arcade.Sprite(BLACK_SCREEN_IMG)
        self.black_sprite.center_x = SCREEN_WIDTH // 2
        self.black_sprite.center_y = SCREEN_HEIGHT // 2
        self.black_sprite.alpha = 0

        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg_sprite)
        self.black_list = arcade.SpriteList()
        self.black_list.append(self.black_sprite)

        # Daniel / dialog
        self.daniel_sprite = None
        self.daniel_list = arcade.SpriteList()
        self.dialog_sprite = None
        self.dialog_list = arcade.SpriteList()
        self.skip_sprite = None
        self.skip_list = arcade.SpriteList()

        # typewriter
        self._letter_interval = LETTER_INTERVAL_MS / 1000.0
        self._current_text_index = 0
        self._full_text = ""
        self._visible_text = ""
        self._type_accum = 0.0
        self._type_pos = 0
        self._typing = False
        self._hide_dialog_text = False
        self._post_dialog_timer = 0.0
        self._dialog_interactable = False
        self._daniel_offscreen_x = None

    # ---------- setup ----------
    def setup(self, menu_music_player):
        self.menu_music_player = menu_music_player

    # ---------- ciclo ----------
    def on_update(self, dt):
        if self._voiceline_sound is None:
            try:
                self._voiceline_sound = arcade.Sound(VOICELINE_SOUND)
            except Exception:
                self._voiceline_sound = None

        def ease_out_cubic(t):
            return 1 - pow(1 - t, 3)

        self.time += dt

        # 0 → 1 (fade-in preto)
        if self.state == self.STATE_FADE_TO_BLACK:
            p = min(self.time / FADE_TIME, 1)
            self.black_sprite.alpha = int(255 * p)
            if self.menu_music_player:
                try:
                    self.menu_music_player.volume = 1 - p
                except:
                    pass
            if p >= 1:
                self.state = self.STATE_HOLD
                self.time = 0

        # 1 → 2 (hold + sons)
        elif self.state == self.STATE_HOLD:
            if not self.sfx_played:
                try:
                    arcade.Sound(FOOTSTEPS_SOUND).play(volume=1.0)
                except:
                    pass
                self.cricket_player = arcade.Sound(CRICKET_SOUND, streaming=True).play(volume=0, loop=True)
                self.wind_player = arcade.Sound(WIND_SOUND, streaming=True).play(volume=0, loop=True)
                self.sfx_played = True
            if self.time <= FADE_SOUNDS_TIME:
                k = self.time / FADE_SOUNDS_TIME
                if self.cricket_player:
                    self.cricket_player.volume = k
                if self.wind_player:
                    self.wind_player.volume = k
            if self.time >= BLACKSCREEN_HOLD:
                self.state = self.STATE_FADE_FROM_BLACK
                self.time = 0

        # 2 → 3 (revelação)
        elif self.state == self.STATE_FADE_FROM_BLACK:
            p = min(self.time / FADE_OUT_TIME, 1)
            self.black_sprite.alpha = int(255 * (1 - p))
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
                self.state = self.STATE_WAIT_FOR_DANIEL
                self.time = 0

        # 3 → 4 (espera)
        elif self.state == self.STATE_WAIT_FOR_DANIEL:
            if self.time >= DANIEL_ENTRANCE_DELAY:
                self._spawn_daniel_and_dialog()
                self.state = self.STATE_DANIEL_ENTRANCE
                self.time = 0

        # 4 → 5 (entradas animadas)
        elif self.state == self.STATE_DANIEL_ENTRANCE:
            t = min(self.time / ENTRANCE_DURATION, 1)
            eased = ease_out_cubic(t)
            if self.daniel_sprite:
                nx = self._daniel_start_x + (self._daniel_target_x - self._daniel_start_x) * eased
                self.daniel_sprite.center_x = nx
            if self.dialog_sprite:
                ny = self._dialog_start_y + (self._dialog_target_y - self._dialog_start_y) * eased
                self.dialog_sprite.center_y = ny
            if t >= 1:
                self.state = self.STATE_PRESENT_COMPLETE
                self.time = 0

        # 5 → diálogo ativo
        if self.state == self.STATE_PRESENT_COMPLETE and not self._dialog_interactable:
            self._post_dialog_timer += dt
            if self._post_dialog_timer >= DIALOG_POST_APPEAR_DELAY:
                self._spawn_skip_button()
                self._current_text_index = 0
                self._start_typing(SKIP_TEXTS[0])
                self._dialog_interactable = True

        # typewriter
        if self._typing:
            self._type_accum += dt
            while self._type_accum >= self._letter_interval and self._type_pos < len(self._full_text):
                self._type_accum -= self._letter_interval
                self._type_pos += 1
                self._visible_text = self._full_text[:self._type_pos]
                try:
                    if self._voiceline_sound:
                        self._voiceline_sound.play(volume=0.6)
                except:
                    pass
            if self._type_pos >= len(self._full_text):
                self._typing = False

        # fim das falas → inicia saída
        if self._dialog_interactable and not self._typing:
            if self._current_text_index == len(SKIP_TEXTS) - 1 and not self._ending_started:
                self._ending_started = True
                self.state = self.STATE_DANIEL_LEAVING
                self.time = 0

        # 6 → 7 (Daniel sai)
        if self.state == self.STATE_DANIEL_LEAVING:
            t = min(self.time / 1.5, 1)
            eased = ease_out_cubic(t)
            if self.daniel_sprite:
                start_x = self.daniel_sprite.center_x
                offscreen_x = self._daniel_offscreen_x or (SCREEN_WIDTH + (self.daniel_sprite.width / 2) + 500)
                self.daniel_sprite.center_x = start_x + (offscreen_x - start_x) * eased
            if t >= 1:
                self.state = self.STATE_FADE_TO_BLACK_2
                self.time = 0
                self.black_sprite.alpha = 0

        # 7 → 8 (fade para preto)
        if self.state == self.STATE_FADE_TO_BLACK_2:
            p = min(self.time / 2.0, 1)
            self.black_sprite.alpha = int(255 * p)
            if p >= 1:
                self.state = self.STATE_FADE_FROM_BLACK_2
                self.time = 0

        # 8 → 9 (remove tudo e revela Daniel de costas)
        if self.state == self.STATE_FADE_FROM_BLACK_2:
            p = min(self.time / 3.0, 1)
            self.black_sprite.alpha = int(255 * (1 - p))
            if self.time == 0:
                self.bg_list = arcade.SpriteList()
                self.daniel_list = arcade.SpriteList()
                self.dialog_list = arcade.SpriteList()
                self.skip_list = arcade.SpriteList()
                self.dialog_sprite = None
                self.skip_sprite = None
                self.daniel_sprite = None
                self._visible_text = ""
                # spawn Daniel de costas
                try:
                    self._daniel_back_sprite = arcade.Sprite(DANIEL_BACK_IMG)
                    self._daniel_back_sprite.center_x = SCREEN_WIDTH // 2
                    self._daniel_back_sprite.center_y = SCREEN_HEIGHT * 0.5
                    self.daniel_list.append(self._daniel_back_sprite)
                except:
                    pass
                try:
                    arcade.Sound(FOOTSTEPS_SOUND).play(volume=1.0)
                except:
                    pass
            if p >= 1:
                self.state = self.STATE_DANIEL_BACK_SCENE
                self.time = 0

        # 9 → 10 (aguarda 3 s)
        if self.state == self.STATE_DANIEL_BACK_SCENE:
            if self.time >= 3:
                self.state = self.STATE_FINAL_BLACK
                self.time = 0
                self.black_sprite.alpha = 0

        # 10 → 11 (fade preto + som carro)
        if self.state == self.STATE_FINAL_BLACK:
            p = min(self.time / FINAL_BLACK_FADE_TIME, 1)
            self.black_sprite.alpha = int(255 * p)
            if p >= 1 and not self._car_sound_played:
                try:
                    arcade.Sound(CAR_START_SOUND).play(volume=1.0)
                except:
                    pass
                self._car_sound_played = True
            if p >= 1 and self.time >= (FINAL_BLACK_FADE_TIME + FINAL_BLACK_HOLD):
                self.state = self.STATE_FADE_OUT_TO_END
                self.time = 0
                return

        # 11 → fecha a janela
        if self.state == self.STATE_FADE_OUT_TO_END:
            p = min(self.time / 1.5, 1)
            self.black_sprite.alpha = int(255 * p)
            if p >= 1:
                print("[CUTSCENE] Fim. Fechando janela.")
                arcade.close_window()
                return

    # ---------- desenho ----------
    def on_draw(self):
        self.clear()
        if self.state >= self.STATE_FADE_FROM_BLACK:
            self.bg_list.draw()
        self.daniel_list.draw()
        self.dialog_list.draw()
        if (not self._hide_dialog_text) and self.dialog_sprite is not None:
            try:
                arcade.draw_text(DIALOG_TITLE, DIALOG_TITLE_X, DIALOG_TITLE_Y,
                                 arcade.color.WHITE, DIALOG_TITLE_FONT_SIZE, anchor_x="left")
                arcade.draw_text(self._visible_text, DIALOG_TEXT_X, DIALOG_TEXT_Y,
                                 arcade.color.WHITE, DIALOG_TEXT_FONT_SIZE,
                                 multiline=True, width=SCREEN_WIDTH - (DIALOG_TEXT_X + 40), anchor_x="left")
            except:
                pass
        self.skip_list.draw()
        self.black_list.draw()

    # ---------- input ----------
    def on_mouse_press(self, x, y, button, modifiers):
        try:
            if self.skip_sprite and self.skip_sprite.collides_with_point((x, y)):
                if self._typing:
                    self._typing = False
                    self._visible_text = self._full_text
                    self._type_pos = len(self._full_text)
                    return
                next_index = self._current_text_index + 1
                if next_index < len(SKIP_TEXTS):
                    self._current_text_index = next_index
                    self._start_typing(SKIP_TEXTS[self._current_text_index])
                else:
                    self._start_end_sequence()
        except:
            pass

    # ---------- helpers ----------
    def _spawn_daniel_and_dialog(self):
        try:
            self.daniel_sprite = arcade.Sprite(DANIEL_IMG)
            final_y = int(SCREEN_HEIGHT * 0.35)
            start_x = SCREEN_WIDTH + (self.daniel_sprite.width / 2) + 50
            target_x = SCREEN_WIDTH - (self.daniel_sprite.width / 2) - DANIEL_FINAL_MARGIN
            self.daniel_sprite.center_x = start_x
            self.daniel_sprite.center_y = final_y
            self.daniel_list.append(self.daniel_sprite)
            self._daniel_start_x = start_x
            self._daniel_target_x = target_x
        except:
            pass
        try:
            self.dialog_sprite = arcade.Sprite(DIALOG_BOX_IMG)
            dialog_target_y = (self.dialog_sprite.height / 2) + DIALOG_BOTTOM_MARGIN
            dialog_start_y = -(self.dialog_sprite.height / 2) - 50
            self.dialog_sprite.center_x = SCREEN_WIDTH // 2
            self.dialog_sprite.center_y = dialog_start_y
            self.dialog_list.append(self.dialog_sprite)
            self._dialog_start_y = dialog_start_y
            self._dialog_target_y = dialog_target_y
        except:
            pass

    def _spawn_skip_button(self):
        try:
            self.skip_sprite = arcade.Sprite(SKIP_BUTTON_IMG)
            self.skip_sprite.center_x = SKIP_BUTTON_X
            self.skip_sprite.center_y = SKIP_BUTTON_Y
            self.skip_list.append(self.skip_sprite)
        except:
            pass

    def _start_typing(self, full_text: str):
        self._full_text = full_text
        self._visible_text = ""
        self._type_pos = 0
        self._type_accum = 0.0
        self._typing = True


# ---------- main só da cut-scene ----------
def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Project IFFar - Cutscene", resizable=False)
    view = CutsceneView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()