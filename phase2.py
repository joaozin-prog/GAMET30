# phase1.py
# ----------
# Jogo completo, sem dependências de cutscene.
# Executar este arquivo inicia diretamente a fase 1.

import arcade
import json
import os

# ---------- caminhos obrigatórios ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
MENU_DIR = os.path.join(ASSETS_DIR, 'menu')
SOUNDS_DIR = os.path.join(BASE_DIR, 'sounds')

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Project IFFar"

MAP_JSON = os.path.join(BASE_DIR, "map.json")
FOOTSTEPS_SOUND = os.path.join(SOUNDS_DIR, "footsteps.mp3")
BLACK_IMG = os.path.join(ASSETS_DIR, "black_screen.png")
ARROWS_DIR = os.path.join(ASSETS_DIR, "arrows")

FADE_TIME = 1.0


class Phase1View(arcade.View):
    def __init__(self, start_area="entrada_info"):
        super().__init__()
        with open(MAP_JSON, "r") as f:
            self.map_data = json.load(f)

        self.current_area = start_area
        self.current_texture = arcade.load_texture(self.map_data[self.current_area]["image"])
        self.arrow_sprites = arcade.SpriteList()

        self.fade_alpha = 0
        self.is_fading = False
        self.fade_direction = 1
        self.fade_timer = 0
        self.next_area = None

        self.black_sprite = arcade.Sprite(BLACK_IMG)
        self.black_sprite.center_x = SCREEN_WIDTH // 2
        self.black_sprite.center_y = SCREEN_HEIGHT // 2
        self.black_sprite.alpha = 0

        self.footsteps = arcade.Sound(FOOTSTEPS_SOUND)
        self.load_arrows()

    # ---------- setas ----------
    def load_arrows(self):
        self.arrow_sprites = arcade.SpriteList()
        arrows_info = self.map_data[self.current_area].get("arrows", {})
        for direction, info in arrows_info.items():
            img = os.path.join(ARROWS_DIR, f"arrow_{direction}.png")
            spr = arcade.Sprite(img, scale=0.4)
            spr.center_x = info["x"]
            spr.center_y = info["y"]
            spr.target = info.get("target")
            spr.trigger = info.get("trigger")
            self.arrow_sprites.append(spr)

    # ---------- ciclo ----------
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        print("Phase1 carregada com sucesso!")
        self.is_fading = True
        self.fade_direction = -1
        self.fade_timer = 0
        self.fade_alpha = 255

    def on_update(self, dt):
        if self.is_fading:
            self.fade_timer += dt
            progress = min(self.fade_timer / FADE_TIME, 1.0)
            if self.fade_direction == 1:
                self.fade_alpha = int(progress * 255)
                if progress >= 1:
                    self.swap_area()
                    self.fade_direction = -1
                    self.fade_timer = 0
            else:
                self.fade_alpha = int(255 * (1 - progress))
                if progress >= 1:
                    self.fade_alpha = 0
                    self.is_fading = False

    def on_draw(self):
        self.clear()

        self.current_texture.draw_sized(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        )

        self.arrow_sprites.draw()
        self.black_sprite.alpha = self.fade_alpha
        self.black_sprite.draw()


    def on_mouse_press(self, x, y, button, modifiers):
        if self.is_fading:
            return
        for arr in self.arrow_sprites:
            if arr.collides_with_point((x, y)):
                self.footsteps.play()
                self.next_area = arr.trigger if hasattr(arr, "trigger") and arr.trigger else arr.target
                self.is_fading = True
                self.fade_direction = 1
                self.fade_timer = 0
                return

    # ---------- troca de sala ----------
    def swap_area(self):
        area_name = self._resolve_area_name(self.next_area)
        self.current_area = area_name
        self.current_texture = arcade.load_texture(self.map_data[area_name]["image"])
        self.load_arrows()

    def _resolve_area_name(self, path):
        for key, value in self.map_data.items():
            if "image" in value and value["image"] == path:
                return key
        return self.current_area


# ---------- main só da fase 1 ----------
def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)
    view = Phase1View()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()