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

# ------------------------------------------------------------------------------------- #

# New assets & timing for character/dialog entrance
DANIEL_IMG = os.path.join(ASSETS_DIR, "daniel.png")
DIALOG_BOX_IMG = os.path.join(ASSETS_DIR, "dialog_box", "dialog_box4.png")
SKIP_BUTTON_IMG = os.path.join(ASSETS_DIR, "skip_button.png")
VOICELINE_SOUND = os.path.join(SOUNDS_DIR, "voiceline.mp3")

DANIEL_ENTRANCE_DELAY = 1.5        # seconds after black screen fully disappears
ENTRANCE_DURATION = 1.2            # duration of slide-in animations
DANIEL_FINAL_MARGIN = 2           # px from right edge
DIALOG_BOTTOM_MARGIN = -460           # px above bottom edge (reduced so box sits lower)

# Wait after dialog fully appeared before enabling text & skip button
DIALOG_POST_APPEAR_DELAY = 2.0  # seconds

# Typewriter / dialog configuration (you can tweak these)
LETTER_INTERVAL_MS = 50                     # milliseconds per letter (variable you can adjust)

# Dialog title properties
DIALOG_TITLE = "Daniel Temp"
DIALOG_TITLE_X = 160                        # adjust X of title text (pixels)
DIALOG_TITLE_Y = 320                        # adjust Y of title text (pixels)
DIALOG_TITLE_FONT_SIZE = 28                 # font size for title

# Dialog body properties - Texto

DIALOG_TEXT_X = 100                         # adjust X of dialog text (pixels)
DIALOG_TEXT_Y = 250                          # adjust Y of dialog text (pixels)
DIALOG_TEXT_FONT_SIZE = 18                  # font size for dialog body

SKIP_BUTTON_X = 1150
SKIP_BUTTON_Y = 120

# Texts shown each time the player clicks Skip (create as many as you need)
SKIP_TEXTS = [
    "Bem-vindo ao Instituto Federal Farroupilha.",
    "Seu projeto foi avaliada e aprovada. Não haverá segunda chance nem fase de adaptação.",
    "A missão terá início assim que a noite apagar o último resquício de luz.\nA partir desse momento, você estará por conta própria.",
    "O protocolo, apesar do que alguns dizem, não é complexo.",
    "O campus oculta objetos que desapareceram durante o dia.",
    "Deslocados, abandonados, ou simplesmente atraídos para lugares onde não deveriam estar.",
    "Sua tarefa é localizar todos eles. Não deixe que a escuridão o distraia.",
    "A operação será encerrada apenas quando todos os itens forem recuperados.\nNão importa o que veja, o que escute ou o que julgue sentir atrás de você.",
    "Não interrompa o processo. Não compartilhe informações.",
    "Os alvos identificados para esta sessão são: Item1, Item2, Item3, Item4 e Item5.\nCada objeto carrega vestígios do que aconteceu antes que você chegasse.",
    "Bom, eu vou indo. Conto com você"
]


class CutsceneView(arcade.View):

    STATE_FADE_TO_BLACK = 0
    STATE_HOLD = 1
    STATE_FADE_FROM_BLACK = 2

    STATE_WAIT_FOR_DANIEL = 3
    STATE_DANIEL_ENTRANCE = 4
    STATE_PRESENT_COMPLETE = 5

    def __init__(self):
        super().__init__()
        self.time = 0
        self.state = self.STATE_FADE_TO_BLACK

        self.bg_sprite = arcade.Sprite(ENTRADA_INFO_IMG)
        self.bg_sprite.center_x = SCREEN_WIDTH // 2
        self.bg_sprite.center_y = SCREEN_HEIGHT // 2

        self.bg_list = arcade.SpriteList()
        self.bg_list.append(self.bg_sprite)

        self.black_sprite = arcade.Sprite(BLACK_SCREEN_IMG)
        self.black_sprite.center_x = SCREEN_WIDTH // 2
        self.black_sprite.center_y = SCREEN_HEIGHT // 2
        self.black_sprite.alpha = 0

        # Use a SpriteList for the black sprite as well
        self.black_list = arcade.SpriteList()
        self.black_list.append(self.black_sprite)

        # Daniel / dialog placeholders + lists (created when entrance starts)
        self.daniel_sprite = None
        self.daniel_list = arcade.SpriteList()
        self.dialog_sprite = None
        self.dialog_list = arcade.SpriteList()

        # Skip button sprite/list
        self.skip_sprite = None
        self.skip_list = arcade.SpriteList()

        # Typewriter / dialog runtime state
        self._letter_interval = LETTER_INTERVAL_MS / 1000.0   # seconds
        self._current_text_index = 0
        self._full_text = ""
        self._visible_text = ""
        self._type_accum = 0.0
        self._type_pos = 0
        self._typing = False
        self._voiceline_sound = None

        # Post-appearance timer and flag: wait before enabling dialog interaction
        self._post_dialog_timer = 0.0
        self._dialog_interactable = False

        # Entrance geometry (filled when sprites are created)
        self._daniel_start_x = None
        self._daniel_target_x = None
        self._daniel_start_y = None
        self._daniel_target_y = None
        self._dialog_start_y = None
        self._dialog_target_y = None

        self.menu_music_player = None
        self.cricket_player = None
        self.wind_player = None
        self.theme_player = None

        self.sfx_played = False

    def setup(self, menu_music_player):
        self.menu_music_player = menu_music_player

    def on_update(self, dt):
        # load voiceline lazily so missing file doesn't break everything
        if self._voiceline_sound is None:
            try:
                self._voiceline_sound = arcade.Sound(VOICELINE_SOUND)
            except Exception:
                self._voiceline_sound = None

        # simple cubic ease-out
        def ease_out_cubic(t):
            return 1 - pow(1 - t, 3)

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

        elif self.state == self.STATE_HOLD:
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
                # Black screen fully gone: start waiting before Daniel entrance
                self.state = self.STATE_WAIT_FOR_DANIEL
                self.time = 0

        elif self.state == self.STATE_WAIT_FOR_DANIEL:
            # wait DANIEL_ENTRANCE_DELAY seconds, then create sprites off-screen and start entrance
            if self.time >= DANIEL_ENTRANCE_DELAY:
                # Create Daniel sprite
                try:
                    self.daniel_sprite = arcade.Sprite(DANIEL_IMG)
                    # final Y around lower-right quadrant
                    final_y = int(SCREEN_HEIGHT * 0.35)
                    # initial X off-screen right
                    start_x = SCREEN_WIDTH + (self.daniel_sprite.width / 2) + 50
                    target_x = SCREEN_WIDTH - (self.daniel_sprite.width / 2) - DANIEL_FINAL_MARGIN
                    self.daniel_sprite.center_x = start_x
                    self.daniel_sprite.center_y = final_y
                    self.daniel_list.append(self.daniel_sprite)
                    # store geometry
                    self._daniel_start_x = start_x
                    self._daniel_target_x = target_x
                    self._daniel_start_y = final_y
                    self._daniel_target_y = final_y
                except Exception:
                    # If sprite loading fails, skip entrance but continue
                    self.daniel_sprite = None

                # Create dialogue box sprite (slide from bottom to bottom)
                try:
                    self.dialog_sprite = arcade.Sprite(DIALOG_BOX_IMG)
                    dialog_target_y = (self.dialog_sprite.height / 2) + DIALOG_BOTTOM_MARGIN
                    dialog_start_y = - (self.dialog_sprite.height / 2) - 50
                    self.dialog_sprite.center_x = SCREEN_WIDTH // 2
                    self.dialog_sprite.center_y = dialog_start_y
                    self.dialog_list.append(self.dialog_sprite)
                    self._dialog_start_y = dialog_start_y
                    self._dialog_target_y = dialog_target_y
                except Exception:
                    self.dialog_sprite = None

                # start entrance animation
                self.state = self.STATE_DANIEL_ENTRANCE
                self.time = 0

        elif self.state == self.STATE_DANIEL_ENTRANCE:
            t = min(self.time / ENTRANCE_DURATION, 1.0)
            eased = ease_out_cubic(t)

            # Update Daniel X position
            if self.daniel_sprite and self._daniel_start_x is not None:
                new_x = self._daniel_start_x + (self._daniel_target_x - self._daniel_start_x) * eased
                self.daniel_sprite.center_x = new_x

            # Update dialog Y position
            if self.dialog_sprite and self._dialog_start_y is not None:
                new_y = self._dialog_start_y + (self._dialog_target_y - self._dialog_start_y) * eased
                self.dialog_sprite.center_y = new_y

            if t >= 1.0:
                self.state = self.STATE_PRESENT_COMPLETE
                self.time = 0
                # Do NOT start typing or create skip button yet.
                # We'll wait DIALOG_POST_APPEAR_DELAY seconds before enabling dialog interaction.

        # Typewriter update (works while in PRESENT_COMPLETE or other states if needed)
        if self._typing:
            self._type_accum += dt
            # reveal letters at the configured interval
            while self._type_accum >= self._letter_interval and self._type_pos < len(self._full_text):
                self._type_accum -= self._letter_interval
                # advance one letter
                self._type_pos += 1
                self._visible_text = self._full_text[: self._type_pos]
                # play voiceline per-letter (if available)
                try:
                    if self._voiceline_sound:
                        # short play for each letter; use low volume
                        self._voiceline_sound.play(volume=0.6)
                except Exception:
                    pass
            # finished typing
            if self._type_pos >= len(self._full_text):
                self._typing = False
                self._type_accum = 0.0

        # After the dialog/character are presented, wait a bit then enable interaction:
        if self.state == self.STATE_PRESENT_COMPLETE and not self._dialog_interactable:
            self._post_dialog_timer += dt
            if self._post_dialog_timer >= DIALOG_POST_APPEAR_DELAY:
                # create skip button now (so it appears after the delay)
                try:
                    self.skip_sprite = arcade.Sprite(SKIP_BUTTON_IMG)
                    self.skip_sprite.center_x = SKIP_BUTTON_X
                    self.skip_sprite.center_y = SKIP_BUTTON_Y
                    self.skip_list.append(self.skip_sprite)
                except Exception:
                    self.skip_sprite = None

                # start typing first text automatically when interactable
                if len(SKIP_TEXTS) > 0:
                    self._current_text_index = 0
                    self._start_typing(SKIP_TEXTS[self._current_text_index])

                self._dialog_interactable = True

    def on_draw(self):
        self.clear()

        # Draw background once we are revealing it and afterwards
        if self.state >= self.STATE_FADE_FROM_BLACK:
            self.bg_list.draw()

        # draw black overlay via its SpriteList
        self.black_list.draw()

        # draw Daniel and dialog if present
        if len(self.daniel_list) > 0:
            self.daniel_list.draw()
        if len(self.dialog_list) > 0:
            self.dialog_list.draw()

        # Draw dialog title & body text (typewriter visible text)
        if self.dialog_sprite is not None:
            try:
                arcade.draw_text(
                    DIALOG_TITLE,
                    DIALOG_TITLE_X,
                    DIALOG_TITLE_Y,
                    arcade.color.WHITE,
                    DIALOG_TITLE_FONT_SIZE,
                    anchor_x="left",
                )
                arcade.draw_text(
                    self._visible_text,
                    DIALOG_TEXT_X,
                    DIALOG_TEXT_Y,
                    arcade.color.WHITE,
                    DIALOG_TEXT_FONT_SIZE,
                    multiline=True,
                    width=SCREEN_WIDTH - (DIALOG_TEXT_X + 40),
                    anchor_x="left",
                )
            except Exception:
                pass

        # draw skip button if present
        if len(self.skip_list) > 0:
            self.skip_list.draw()

    # helper to start typing a text
    def _start_typing(self, full_text: str):
        self._full_text = full_text
        self._visible_text = ""
        self._type_pos = 0
        self._type_accum = 0.0
        self._typing = True

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        # If skip sprite exists, check click
        try:
            if self.skip_sprite and self.skip_sprite.collides_with_point((x, y)):
                # If typing in progress, finish current text immediately
                if self._typing:
                    self._typing = False
                    self._visible_text = self._full_text
                    self._type_pos = len(self._full_text)
                    return
                # If current text fully shown, advance to next text (if any)
                next_index = self._current_text_index + 1
                if next_index < len(SKIP_TEXTS):
                    self._current_text_index = next_index
                    self._start_typing(SKIP_TEXTS[self._current_text_index])
                else:
                    # no more texts: do nothing or you can implement closing dialog / continue
                    pass
        except Exception:
            pass
