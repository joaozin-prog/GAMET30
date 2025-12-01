import arcade
import os
from phase1 import Phase1View

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

DANIEL_BACK_IMG = os.path.join(ASSETS_DIR, "daniel_back.png")
CAR_START_SOUND = os.path.join(SOUNDS_DIR, "car_start.mp3")

FINAL_BLACK_FADE_TIME = 2.0
FINAL_BLACK_HOLD = 3.0
DANIEL_LEAVE_DELAY = 4.0
CAR_SOUND_DELAY = 2.0


# Texts shown each time the player clicks Skip (create as many as you need)
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


class CutsceneView(arcade.View):

    STATE_FADE_TO_BLACK = 0
    STATE_HOLD = 1
    STATE_FADE_FROM_BLACK = 2

    STATE_FADE_OUT_TO_PHASE1 = 10

    STATE_WAIT_FOR_DANIEL = 3
    STATE_DANIEL_ENTRANCE = 4
    STATE_PRESENT_COMPLETE = 5

    STATE_WHITE_FADE_IN_AFTER_DIALOG = 6
    STATE_WHITE_FADE_OUT = 7
    STATE_SHOW_DANIEL_BACK = 8
    STATE_FINAL_BLACK = 9
    STATE_COMPLETE = 10

    STATE_DANIEL_LEAVING = 11
    STATE_FADE_TO_BLACK_2 = 12
    STATE_FADE_FROM_BLACK_2 = 13
    STATE_DANIEL_BACK_SCENE = 14

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
        self._ending_started = False
        # When ending starts, hide dialog text so it doesn't linger
        self._hide_dialog_text = False
        # Ensure car sound plays only once
        self._car_sound_played = False
        # Daniel offscreen target for leaving animation
        self._daniel_offscreen_x = None

        self.menu_music_player = None
        self.cricket_player = None
        self.wind_player = None
        self.theme_player = None

        self.sfx_played = False

    def setup(self, menu_music_player):
        self.menu_music_player = menu_music_player
    
    def _start_end_sequence(self):
        # Immediately hide dialog text, disable interaction and remove UI sprites.
        self.time = 0
        self._hide_dialog_text = True
        self._dialog_interactable = False
        self._visible_text = ""
        self._full_text = ""
        self._type_pos = 0
        self._typing = False

        # Clear skip button and dialog sprites/lists so nothing lingers visually
        try:
            self.skip_list = arcade.SpriteList()
            self.skip_sprite = None
        except Exception:
            pass
        try:
            self.dialog_list = arcade.SpriteList()
            self.dialog_sprite = None
        except Exception:
            pass

        # Lower theme/music if present
        try:
            if self.theme_player:
                self.theme_player.volume = 0
        except Exception:
            pass

        # Prepare for Daniel leaving animation and final sequence
        self.state = self.STATE_DANIEL_LEAVING
        self._ending_started = True
        # prepare an offscreen target far to the right to ensure full disappearance
        if self.daniel_sprite:
            try:
                self._daniel_offscreen_x = SCREEN_WIDTH + (self.daniel_sprite.width / 2) + 500
            except Exception:
                self._daniel_offscreen_x = SCREEN_WIDTH + 1000

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
            self.black_sprite.alpha = int(255 * p)

            if self.menu_music_player:
                try:
                    self.menu_music_player.volume = 1 - p
                except:
                    pass

            if p >= 1:
                self.state = self.STATE_HOLD
                self.time = 0

        # -----------------------------------
        # ESTADO 2 — blackscreen hold
        # -----------------------------------
        elif self.state == self.STATE_HOLD:
            if not self.sfx_played:
                try:
                    arcade.Sound(FOOTSTEPS_SOUND).play(volume=1.0)
                except:
                    pass

                self.cricket_player = arcade.Sound(
                    CRICKET_SOUND, streaming=True
                ).play(volume=0, loop=True)
                self.wind_player = arcade.Sound(
                    WIND_SOUND, streaming=True
                ).play(volume=0, loop=True)
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

        # -----------------------------------
        # ESTADO 3 — Fade de volta do preto
        # -----------------------------------
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

        # -----------------------------------
        # ESTADO 4 — Aguardar X segundos
        # -----------------------------------
        elif self.state == self.STATE_WAIT_FOR_DANIEL:
            if self.time >= DANIEL_ENTRANCE_DELAY:

                try:
                    self.daniel_sprite = arcade.Sprite(DANIEL_IMG)
                    final_y = int(SCREEN_HEIGHT * 0.35)
                    start_x = SCREEN_WIDTH + (self.daniel_sprite.width/2) + 50
                    target_x = SCREEN_WIDTH - (self.daniel_sprite.width/2) - DANIEL_FINAL_MARGIN
                    self.daniel_sprite.center_x = start_x
                    self.daniel_sprite.center_y = final_y
                    self.daniel_list.append(self.daniel_sprite)
                    self._daniel_start_x = start_x
                    self._daniel_target_x = target_x
                except:
                    pass

                try:
                    self.dialog_sprite = arcade.Sprite(DIALOG_BOX_IMG)
                    dialog_target_y = (self.dialog_sprite.height/2) + DIALOG_BOTTOM_MARGIN
                    dialog_start_y = -(self.dialog_sprite.height/2) - 50
                    self.dialog_sprite.center_x = SCREEN_WIDTH//2
                    self.dialog_sprite.center_y = dialog_start_y
                    self.dialog_list.append(self.dialog_sprite)
                    self._dialog_start_y = dialog_start_y
                    self._dialog_target_y = dialog_target_y
                except:
                    pass

                self.state = self.STATE_DANIEL_ENTRANCE
                self.time = 0

        # -----------------------------------
        # ESTADO 5 — Daniel entra + caixa sobe
        # -----------------------------------
        elif self.state == self.STATE_DANIEL_ENTRANCE:
            t = min(self.time / ENTRANCE_DURATION, 1)
            eased = ease_out_cubic(t)

            if self.daniel_sprite:
                nx = self._daniel_start_x + (self._daniel_target_x - self._daniel_start_x)*eased
                self.daniel_sprite.center_x = nx

            if self.dialog_sprite:
                ny = self._dialog_start_y + (self._dialog_target_y - self._dialog_start_y)*eased
                self.dialog_sprite.center_y = ny

            if t >= 1:
                self.state = self.STATE_PRESENT_COMPLETE
                self.time = 0

        # -----------------------------------
        # ESTADO 6 — DIALOGO ATIVO
        # -----------------------------------
        if self.state == self.STATE_PRESENT_COMPLETE and not self._dialog_interactable:
            self._post_dialog_timer += dt
            if self._post_dialog_timer >= DIALOG_POST_APPEAR_DELAY:
                try:
                    self.skip_sprite = arcade.Sprite(SKIP_BUTTON_IMG)
                    self.skip_sprite.center_x = SKIP_BUTTON_X
                    self.skip_sprite.center_y = SKIP_BUTTON_Y
                    self.skip_list.append(self.skip_sprite)
                except:
                    pass

                self._current_text_index = 0
                self._start_typing(SKIP_TEXTS[0])
                self._dialog_interactable = True

        # -----------------------------------
        # SISTEMA DE TYPEWRITER
        # -----------------------------------
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

        # ============================================================
        #              🔥 INÍCIO DO FIM DO DIALOGO 🔥
        # ============================================================
        # Quando TODAS voicelines acabaram — iniciar final
        if self._dialog_interactable and not self._typing:
            if self._current_text_index == len(SKIP_TEXTS)-1 and not self._ending_started:
                self._ending_started = True
                self.state = self.STATE_DANIEL_LEAVING
                self.time = 0

        # -----------------------------------
        # ESTADO 7 — Daniel sai (Slide p/ direita)
        # -----------------------------------
        if self.state == self.STATE_DANIEL_LEAVING:
            t = min(self.time / 1.5, 1)
            eased = ease_out_cubic(t)

            if self.daniel_sprite:
                # Use current center_x as start so the animation is smooth regardless of previous targets
                try:
                    start_x = self.daniel_sprite.center_x
                    offscreen_x = self._daniel_offscreen_x or (SCREEN_WIDTH + (self.daniel_sprite.width / 2) + 500)
                    self.daniel_sprite.center_x = start_x + (offscreen_x - start_x) * eased
                except Exception:
                    self.daniel_sprite.center_x = (self._daniel_target_x or SCREEN_WIDTH) + 1000 * eased

            if t >= 1:
                # Reset timer and ensure black starts from fully transparent
                self.state = self.STATE_FADE_TO_BLACK_2
                self.time = 0
                try:
                    self.black_sprite.alpha = 0
                except Exception:
                    pass

        # -----------------------------------
        # ESTADO 8 — Tela preta aparece novamente
        # -----------------------------------
        if self.state == self.STATE_FADE_TO_BLACK_2:
            p = min(self.time/2.0, 1)
            self.black_sprite.alpha = int(255*p)

            if p >= 1:
                self.state = self.STATE_FADE_FROM_BLACK_2
                self.time = 0

        # -----------------------------------
        # ESTADO 9 — Remove cenário e tira blackscreen
        # -----------------------------------
        if self.state == self.STATE_FADE_FROM_BLACK_2:
            p = min(self.time/3.0, 1)
            self.black_sprite.alpha = int(255*(1-p))

            # Remover BG, Daniel, caixa
            if self.time == 0:
                # Immediately clear visual lists and UI references so nothing lingers
                self.bg_list = arcade.SpriteList()
                self.daniel_list = arcade.SpriteList()
                self.dialog_list = arcade.SpriteList()
                self.skip_list = arcade.SpriteList()
                # Also clear individual sprite references and visible text so
                # dialog text doesn't remain after the dialog box disappears.
                try:
                    self.dialog_sprite = None
                except Exception:
                    pass
                try:
                    self.skip_sprite = None
                except Exception:
                    pass
                try:
                    self.daniel_sprite = None
                except Exception:
                    pass
                # Remove any visible text immediately
                try:
                    self._visible_text = ""
                except Exception:
                    pass

            if p >= 1:
                self.state = self.STATE_DANIEL_BACK_SCENE
                self.time = 0

                # spawn Daniel de costas
                try:
                    self._daniel_back_sprite = arcade.Sprite(
                        os.path.join(ASSETS_DIR, "daniel_back.png")
                    )
                    self._daniel_back_sprite.center_x = SCREEN_WIDTH//2
                    self._daniel_back_sprite.center_y = SCREEN_HEIGHT*0.5
                    self.daniel_list.append(self._daniel_back_sprite)
                except:
                    pass

                # som de passos
                try:
                    arcade.Sound(FOOTSTEPS_SOUND).play(volume=1.0)
                except:
                    pass

        # -----------------------------------
        # ESTADO 10 — Cena final com daniel costas
        # -----------------------------------
        if self.state == self.STATE_DANIEL_BACK_SCENE:
            # After Daniel (back) has been visible for 3 seconds,
            # start the final black fade so it appears shortly before the car sound.
            if self.time >= 3:
                # Ensure the black sprite starts transparent before fading in
                try:
                    self.black_sprite.alpha = 0
                except Exception:
                    pass
                self.state = self.STATE_FINAL_BLACK
                self.time = 0

        # -----------------------------------
        # ESTADO 11 — Fade preto + som do carro
        # -----------------------------------
        if self.state == self.STATE_FINAL_BLACK:
            p = min(self.time / FINAL_BLACK_FADE_TIME, 1)
            try:
                self.black_sprite.alpha = int(255 * p)
            except Exception:
                pass

            if p >= 1 and not self._car_sound_played:
                try:
                    arcade.Sound(CAR_START_SOUND).play(volume=1.0)
                except Exception:
                    try:
                        arcade.Sound(os.path.join(SOUNDS_DIR, "car_sound.mp3")).play(volume=1.0)
                    except:
                        pass
                self._car_sound_played = True

            if p >= 1 and self.time >= (FINAL_BLACK_FADE_TIME + FINAL_BLACK_HOLD):
                self.state = self.STATE_FADE_OUT_TO_PHASE1
                self.time = 0
                return
            
        # ----------------------------------------
        # ESTADO FINAL — Fade preto + som do carro
        # ----------------------------------------

        if self.state == self.STATE_FINAL_BLACK:

            # fade in para o preto
            p = min(self.time / FINAL_BLACK_FADE_TIME, 1)
            try:
                self.black_sprite.alpha = int(255 * p)
            except Exception:
                pass

            # toca o som do carro apenas uma vez, quando o fade termina
            if p >= 1 and not self._car_sound_played:
                try:
                    arcade.Sound(CAR_START_SOUND).play(volume=1.0)
                except Exception:
                    try:
                        arcade.Sound(os.path.join(SOUNDS_DIR, "car_sound.mp3")).play(volume=1.0)
                    except:
                        pass
                self._car_sound_played = True

            # quando fade + hold tiverem terminado → mudar de cena
            if p >= 1 and self.time >= (FINAL_BLACK_FADE_TIME + FINAL_BLACK_HOLD):

                # marca como concluído
                self.state = self.STATE_COMPLETE

                # remove blackscreen da cena antes de mudar de view
                try:
                    self.black_sprite.alpha = 0
                    self.black_list = arcade.SpriteList()
                except Exception:
                    pass

                # troca para fase 1
                #try:
                    self.window.show_view(Phase1View(start_area='entrada_info'))
                #except Exception as e:
                    #print("Erro ao iniciar Phase1View")

                return
            
        # -----------------------------------
        # ESTADO 15 — Fade para preto e troca para phase1
        # -----------------------------------
        # No final da cutscene, no estado STATE_FADE_OUT_TO_PHASE1
        if self.state == self.STATE_FADE_OUT_TO_PHASE1:
            p = min(self.time / 1.5, 1)
            self.black_sprite.alpha = int(255 * p)
        
            if p >= 1:
                print("[CUTSCENE] Transição concluída. Redirecionando para Phase1View...")
                try:
                    # Redirecionar para Phase1View
                    self.window.show_view(Phase1View(start_area='entrada_info'))
                except Exception as e:
                    print(f"[CUTSCENE] Erro ao redirecionar para Phase1View: {e}")
                return



    def on_draw(self):
        self.clear()

        # Draw background once we are revealing it and afterwards
        if self.state >= self.STATE_FADE_FROM_BLACK:
            self.bg_list.draw()

        # draw Daniel and dialog if present (black overlay will be drawn last)
        if len(self.daniel_list) > 0:
            self.daniel_list.draw()
        if len(self.dialog_list) > 0:
            self.dialog_list.draw()

        if (not getattr(self, "_hide_dialog_text", False)) and self.dialog_sprite is not None:
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

        if len(self.skip_list) > 0:
            self.skip_list.draw()

        self.black_list.draw()

    def _start_typing(self, full_text: str):
        self._full_text = full_text
        self._visible_text = ""
        self._type_pos = 0
        self._type_accum = 0.0
        self._typing = True

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
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
        except Exception:
            pass
