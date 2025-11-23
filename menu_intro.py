import os
import arcade
from dataclasses import dataclass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
MENU_DIR = os.path.join(ASSETS_DIR, 'menu')
SOUNDS_DIR = os.path.join(BASE_DIR, 'sounds')

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Game Menu Intro"

FADE_DELAY = 3.0

FADE_IN_TIME = 2.0
AFTER_BG_DELAY = 2.0
BUTTON_STAGGER = 0.35
BUTTON_ANIM_TIME = 1.8

BUTTON_GAP_Y = 90
BUTTON_BASE_Y = 260
BUTTON_RISE_OFFSET = 40

MUSIC_FILE = os.path.join(SOUNDS_DIR, 'intro_game.mp3')
MUSIC_VOLUME = 0.0
MUSIC_TARGET_VOLUME = 1

BACKGROUND_IMG = os.path.join(MENU_DIR, 'iffar_menu.png')
BLACK_SCREEN_IMG = os.path.join(ASSETS_DIR, 'black_screen.png')

PLAY_IMG = os.path.join(MENU_DIR, 'play_button.png')
QUIT_IMG = os.path.join(MENU_DIR, 'quit_button.png')


@dataclass
class TimedAnim:
    start_time: float
    duration: float

    def progress(self, t: float) -> float:
        if t <= self.start_time:
            return 0.0
        if t >= self.start_time + self.duration:
            return 1.0
        return (t - self.start_time) / self.duration


def ease_out_cubic(x: float) -> float:
    return 1 - (1 - x) ** 3


class ButtonVisual:
    def __init__(self, texture: arcade.Texture, x: float, final_y: float, anim: TimedAnim):
        # Create sprite with given texture
        self.sprite = arcade.Sprite(texture)
        self.sprite.center_x = x
        self.final_y = final_y
        self.anim = anim

        self.sprite.center_y = self.final_y - BUTTON_RISE_OFFSET
        self.sprite.alpha = 0

        self.sprite.color = (240, 240, 240)

    def update(self, t: float) -> None:
        p = self.anim.progress(t)
        e = ease_out_cubic(p)

        # Rise up and fade in
        self.sprite.center_y = self.final_y - (1.0 - e) * BUTTON_RISE_OFFSET
        self.sprite.alpha = int(max(0, min(255, 255 * e)))


class MenuIntroView(arcade.View):
    def __init__(self):
        super().__init__()
        self.time = 0.0
        self.buttons: list[ButtonVisual] = []
        self.music_player = None
        self.music_sound = None

        self.bg_tex = arcade.load_texture(BACKGROUND_IMG)
        self.black_tex = arcade.load_texture(BLACK_SCREEN_IMG)
        self.play_tex = arcade.load_texture(PLAY_IMG)

        self.quit_tex = arcade.load_texture(QUIT_IMG)

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

        self.bg_list = arcade.SpriteList()
        self.ui_list = arcade.SpriteList()

        # Background
        self.bg_sprite = arcade.Sprite(self.bg_tex)
        self.bg_sprite.center_x = SCREEN_WIDTH / 2
        self.bg_sprite.center_y = SCREEN_HEIGHT / 2
        self.bg_list.append(self.bg_sprite)

        # Black overlay
        self.black_sprite = arcade.Sprite(self.black_tex)
        self.black_sprite.center_x = SCREEN_WIDTH / 2
        self.black_sprite.center_y = SCREEN_HEIGHT / 2
        self.black_sprite.alpha = 255
        self.ui_list.append(self.black_sprite)

        start_buttons = FADE_IN_TIME + AFTER_BG_DELAY
        cx = SCREEN_WIDTH / 2

        play_y = BUTTON_BASE_Y + BUTTON_GAP_Y / 2
        quit_y = BUTTON_BASE_Y - BUTTON_GAP_Y / 2

        play_anim = TimedAnim(start_time=start_buttons + 0 * BUTTON_STAGGER, duration=BUTTON_ANIM_TIME)
        quit_anim = TimedAnim(start_time=start_buttons + 1 * BUTTON_STAGGER, duration=BUTTON_ANIM_TIME)

        self.buttons = [
            ButtonVisual(self.play_tex, cx, play_y, play_anim),
            ButtonVisual(self.quit_tex, cx, quit_y, quit_anim),
        ]

        for btn in self.buttons:
            self.ui_list.append(btn.sprite)

        # Music
        if os.path.exists(MUSIC_FILE):
            try:
                self.music_sound = arcade.load_sound(MUSIC_FILE, streaming=True)
                self.music_player = self.music_sound.play(volume=MUSIC_VOLUME, loop=False)
            except Exception as e:
                print("Erro ao tocar música:", e)


    def on_update(self, delta_time: float):
        self.time += delta_time

        # Fade logic
        if self.time < FADE_DELAY:
            fade_p = 0
        else:
            fade_p = min((self.time - FADE_DELAY) / FADE_IN_TIME, 1)

        fade_eased = ease_out_cubic(fade_p)

        # Fade da tela preta
        self.black_sprite.alpha = int(255 * (1 - fade_eased))

        # Fade da música
        if self.music_player is not None:
            try:
                self.music_player.volume = MUSIC_VOLUME + (MUSIC_TARGET_VOLUME - MUSIC_VOLUME) * fade_eased
            except:
                pass

        # Update dos botões
        for btn in self.buttons:
            btn.update(self.time)


    def on_draw(self):
        self.clear()
        self.bg_list.draw()
        self.ui_list.draw()

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.buttons:
            if btn.sprite.alpha >= 250 and abs(btn.sprite.center_y - btn.final_y) < 0.5:
                if btn.sprite.left <= x <= btn.sprite.right and btn.sprite.bottom <= y <= btn.sprite.top:
                    btn.sprite.color = (255, 255, 255)
                else:
                    btn.sprite.color = (240, 240, 240)


    def on_mouse_press(self, x, y, button, modifiers):
        labels = ["play", "quit"]
        for i, btn in enumerate(self.buttons):
            if (btn.sprite.left <= x <= btn.sprite.right and
                btn.sprite.bottom <= y <= btn.sprite.top and
                btn.sprite.alpha > 250):

                print(f"Botão '{labels[i]}' clicado")
                if labels[i] == "quit":
                    arcade.close_window()

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)
    view = MenuIntroView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
