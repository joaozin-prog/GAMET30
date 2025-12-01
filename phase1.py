import arcade
import json
import os

# --- Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")
PHASE1 = os.path.join(ASSETS, "phase1")
ARROWS_DIR = os.path.join(ASSETS, "arrows")
SOUNDS = os.path.join(BASE_DIR, "sounds")

MAP_JSON = os.path.join(BASE_DIR, "map.json")

FOOTSTEPS_SOUND = os.path.join(SOUNDS, "footsteps.mp3")
BLACK_IMG = os.path.join(ASSETS, "black_screen.png")

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

FADE_TIME = 1.0  # Fade-out e Fade-in


class Phase1View(arcade.View):
    def __init__(self, start_area="entrada_info"):
        super().__init__()

        # Carrega o mapa
        with open(MAP_JSON, "r") as f:
            self.map_data = json.load(f)

        # Área atual
        self.current_area = start_area
        self.current_texture = arcade.load_texture(self.map_data[self.current_area]["image"])

        # Lista de setas
        self.arrow_sprites = arcade.SpriteList()

        # Fade controller
        self.fade_alpha = 0
        self.is_fading = False
        self.fade_direction = 1  # 1 = fade-out, -1 = fade-in
        self.fade_timer = 0

        # Next area
        self.next_area = None

        # Black overlay
        self.black_sprite = arcade.Sprite(BLACK_IMG)
        self.black_sprite.center_x = SCREEN_WIDTH // 2
        self.black_sprite.center_y = SCREEN_HEIGHT // 2
        self.black_sprite.alpha = 0

        # Sons
        self.footsteps = arcade.Sound(FOOTSTEPS_SOUND)

        # Carrega setas iniciais
        self.load_arrows()

    # -----------------------------
    # CARREGAR SETAS DO JSON
    # -----------------------------
    def load_arrows(self):
        self.arrow_sprites = arcade.SpriteList()

        arrows_info = self.map_data[self.current_area].get("arrows", {})

        for direction, info in arrows_info.items():
            img = os.path.join(ARROWS_DIR, f"arrow_{direction}.png")
            sprite = arcade.Sprite(img, scale=0.4)
            sprite.center_x = info["x"]
            sprite.center_y = info["y"]

            # Guarda o destino dentro da própria sprite
            sprite.target = info.get("target")
            sprite.trigger = info.get("trigger")  # caso seja evento/jumpscare

            self.arrow_sprites.append(sprite)

    # -----------------------------
    # INÍCIO
    # -----------------------------
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        print("Phase1 carregada com sucesso!")

        self.is_fading = True
        self.fade_direction = -1
        self.fade_timer = 0
        self.fade_alpha = 255

    # -----------------------------
    # DESENHO
    # -----------------------------
    def on_draw(self):
        self.clear()

        # Imagem base
        arcade.draw_lrwh_rectangle_textured(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.current_texture
        )

        # Setas
        self.arrow_sprites.draw()

        # Fade overlay
        self.black_sprite.alpha = self.fade_alpha
        self.black_sprite.draw()

    # -----------------------------
    # LÓGICA DO FADE DURANTE UPDATE
    # -----------------------------
    def on_update(self, dt):
        print(f"[FADE] alpha: {self.fade_alpha}, fading: {self.is_fading}, direction: {self.fade_direction}")
        
        if self.is_fading:
            self.fade_timer += dt
            progress = min(self.fade_timer / FADE_TIME, 1.0)

            if self.fade_direction == 1:
                # fade-out (0 → 255)
                self.fade_alpha = int(progress * 255)

                if progress >= 1:
                    # troca a imagem agora
                    self.swap_area()
                    # agora vamos fazer fade-in
                    self.fade_direction = -1
                    self.fade_timer = 0

            else:
                # fade-in (255 → 0)
                self.fade_alpha = int(255 * (1 - progress))

                if progress >= 1:
                    # fim
                    self.fade_alpha = 0
                    self.is_fading = False

    # -----------------------------
    # CLIQUE DO MOUSE
    # -----------------------------
    def on_mouse_press(self, x, y, button, modifiers):
        if self.is_fading:
            return  # não permitir interação durante fade

        for arrow in self.arrow_sprites:
            if arrow.collides_with_point((x, y)):
                # Som de passos
                self.footsteps.play()

                # Define próxima área
                if hasattr(arrow, "trigger") and arrow.trigger:
                    self.next_area = arrow.trigger  # jumpscare ou evento
                else:
                    self.next_area = arrow.target

                # Inicia o fade-out
                self.is_fading = True
                self.fade_direction = 1
                self.fade_timer = 0
                return

    # -----------------------------
    # TROCA A IMAGEM (NO MEIO DO FADE)
    # -----------------------------
    def swap_area(self):
        area_name = self._resolve_area_name(self.next_area)

        self.current_area = area_name
        self.current_texture = arcade.load_texture(self.map_data[area_name]["image"])

        # Recarregar setas
        self.load_arrows()

    # -----------------------------
    # RESOLVE nome da área baseado no caminho
    # Ex: "assets/phase1/hall_de_noite.jpeg" → "hall_de_noite"
    # -----------------------------
    def _resolve_area_name(self, path):
        for key, value in self.map_data.items():
            if "image" in value and value["image"] == path:
                return key
        return self.current_area  # fallback
