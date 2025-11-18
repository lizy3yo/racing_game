import pygame
import time
import math
import random
from utils import blit_text_center, scale_image, blit_rotate_center
pygame.font.init()

# Game Constants
FPS = 60
COUNTDOWN_SECONDS = 3
SPAWN_INTERVAL = 12
POWERUP_DURATION = 5.0

# Power-up types
PU_BOOST = "boost"
PU_VULN = "vulnerability"
PU_WEAPON = "weapon"
PU_COLORS = {PU_BOOST: (255, 215, 0), PU_VULN: (200, 0, 200), PU_WEAPON: (0, 200, 0)}

# Load assets
GRASS = scale_image(pygame.image.load('imgs/terrain-1.png'), 2.3) 
TRACK = scale_image(pygame.image.load('imgs/track.png'), 1)
TRACK_BORDER = scale_image(pygame.image.load('imgs/track-border.png'), 1)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
TRACK_MASK = pygame.mask.from_surface(TRACK)

FINISH = pygame.image.load('imgs/finish.png')
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (140, 250)

FERARRI = scale_image(pygame.image.load('imgs/fer.png'), 0.12)
BLUE_CAR = scale_image(pygame.image.load('imgs/redbull.png'), 0.08)

POWERUP_BOOST_IMG = scale_image(pygame.image.load('imgs/powerup_boost.png'), 0.3)
POWERUP_VULN_IMG = scale_image(pygame.image.load('imgs/powerup_vuln.png'), 0.3)
POWERUP_WEAPON_IMG = scale_image(pygame.image.load('imgs/powerup_weapon.png'), 0.3)
PROJECTILE_IMG = scale_image(pygame.image.load('imgs/projectile.png'), 1.0)

# Window setup
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🏎️ Ultimate Racing Championship")

# Fonts - Professional styling
TITLE_FONT = pygame.font.SysFont("arial", 72, bold=True)
MAIN_FONT = pygame.font.SysFont("arial", 36, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 24)
TINY_FONT = pygame.font.SysFont("arial", 18)
HUD_FONT = pygame.font.SysFont("consolas", 22, bold=True)
COUNTDOWN_FONT = pygame.font.SysFont("arial", 180, bold=True)

# AI Path
PATH = [(182, 115), (67, 153), (69, 532), (351, 803), (441, 701), (478, 565), 
        (624, 563), (687, 790), (819, 719), (804, 444), (685, 408), (490, 389), 
        (517, 312), (777, 278), (798, 101), (615, 80), (349, 94), (299, 421), 
        (199, 391), (205, 193)]

# Helper function to update window title
def update_window_title(state, current_map=None, lap=None):
    """Update window title based on game state"""
    if state == 'menu':
        pygame.display.set_caption("🏎️ Ultimate Racing Championship - Main Menu")
    elif state == 'map_select':
        pygame.display.set_caption("🏎️ Ultimate Racing Championship - Select Track")
    elif state == 'countdown':
        pygame.display.set_caption("🏎️ Ultimate Racing Championship - Get Ready!")
    elif state == 'playing':
        map_name = current_map["name"] if current_map else "Racing"
        lap_text = f" | Lap {lap}" if lap else ""
        pygame.display.set_caption(f"🏎️ Ultimate Racing Championship - {map_name}{lap_text}")
    elif state == 'modal':
        pygame.display.set_caption("🏎️ Ultimate Racing Championship - Race Complete!")
    else:
        pygame.display.set_caption("🏎️ Ultimate Racing Championship")

# Load speedway map assets
try:
    SPEEDWAY_GRASS = pygame.image.load('imgs/speedway-grass.png')
    SPEEDWAY_TRACK = pygame.image.load('imgs/speedway-track.png')
    SPEEDWAY_BORDER = pygame.image.load('imgs/speedway-border.png')
    SPEEDWAY_BORDER_MASK = pygame.mask.from_surface(SPEEDWAY_BORDER)
    SPEEDWAY_TRACK_MASK = pygame.mask.from_surface(SPEEDWAY_TRACK)
    SPEEDWAY_FINISH = pygame.image.load('imgs/speedway-finish.png')
    SPEEDWAY_FINISH_MASK = pygame.mask.from_surface(SPEEDWAY_FINISH)
    SPEEDWAY_FINISH_POS = (410, 130)
    SPEEDWAY_PATH = [(750, 450), (735, 527), (692, 596), (626, 652), (542, 687), (450, 700), 
                     (357, 687), (273, 652), (207, 596), (164, 527), (150, 450), (164, 372), 
                     (207, 303), (273, 247), (357, 212), (449, 200), (542, 212), (626, 247), 
                     (692, 303), (735, 372)]
    speedway_available = True
except:
    speedway_available = False

# Map configurations
MAPS = {
    "classic": {
        "name": "Classic Circuit",
        "grass": GRASS,
        "track": TRACK,
        "border": TRACK_BORDER,
        "border_mask": TRACK_BORDER_MASK,
        "track_mask": TRACK_MASK,
        "finish": FINISH,
        "finish_mask": FINISH_MASK,
        "finish_pos": FINISH_POSITION,
        "path": PATH,
        "player_start": (205, 200),
        "ai_start": (170, 200)
    }
}

if speedway_available:
    MAPS["speedway"] = {
        "name": "Speedway Oval",
        "grass": SPEEDWAY_GRASS,
        "track": SPEEDWAY_TRACK,
        "border": SPEEDWAY_BORDER,
        "border_mask": SPEEDWAY_BORDER_MASK,
        "track_mask": SPEEDWAY_TRACK_MASK,
        "finish": SPEEDWAY_FINISH,
        "finish_mask": SPEEDWAY_FINISH_MASK,
        "finish_pos": SPEEDWAY_FINISH_POS,
        "path": SPEEDWAY_PATH,
        "player_start": (420, 200),
        "ai_start": (480, 200)
    }

class GameInfo:
    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0
        self.laps = 0
        self.best_time = None
        self.current_lap_start = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0
        self.laps = 0
        self.current_lap_start = 0
    
    def start_level(self):
        self.started = True
        self.level_start_time = time.time()
        self.current_lap_start = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time, 2)
    
    def get_lap_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.current_lap_start, 2)
    
    def complete_lap(self):
        lap_time = self.get_lap_time()
        if self.best_time is None or lap_time < self.best_time:
            self.best_time = lap_time
        self.laps += 1
        self.current_lap_start = time.time()
        return lap_time

class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.original_max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.prev_x, self.prev_y = self.x, self.y
        self.acceleration = 0.2
    
    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()
    
    def move(self):
        radias = math.radians(self.angle)
        vertical = math.cos(radias) * self.vel
        horizontal = math.sin(radias) * self.vel
        self.prev_x, self.prev_y = self.x, self.y
        self.x -= horizontal
        self.y -= vertical
    
    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi
    
    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0
        self.max_vel = self.original_max_vel
        self.prev_x, self.prev_y = self.x, self.y

class PlayerCar(AbstractCar):
    IMG = FERARRI
    START_POS = (205, 200)

    def __init__(self, max_vel, rotation_vel):
        super().__init__(max_vel, rotation_vel)
        self.active_power = None
        self.power_end_time = 0
        self.vulnerable = False
        self.ammo = 0

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 0.5, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

    def apply_powerup(self, pu_type):
        now = time.time()
        if pu_type == PU_BOOST:
            self.max_vel = self.original_max_vel * 1.8
            self.active_power = PU_BOOST
            self.power_end_time = now + POWERUP_DURATION
        elif pu_type == PU_VULN:
            self.vulnerable = True
            self.active_power = PU_VULN
            self.power_end_time = now + POWERUP_DURATION
        elif pu_type == PU_WEAPON:
            self.ammo += 1
            self.active_power = PU_WEAPON
            self.power_end_time = now + POWERUP_DURATION

    def update_power_state(self):
        if self.active_power and time.time() > self.power_end_time:
            if self.active_power == PU_BOOST:
                self.max_vel = self.original_max_vel
            if self.active_power == PU_VULN:
                self.vulnerable = False
            self.active_power = None

class ComputerCar(AbstractCar):
    IMG = BLUE_CAR
    START_POS = (170, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel
        self.acceleration = 0.4
        self.stunned_until = 0

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi
        
        difference_in_angle = self.angle - math.degrees(desired_radian_angle)   
        if difference_in_angle >= 180:
            difference_in_angle -= 360
        
        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))
    
    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        now = time.time()
        if self.stunned_until:
            if now < self.stunned_until:
                return
            else:
                self.stunned_until = 0
                self.vel = self.max_vel

        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

class Projectile:
    RADIUS = 5
    SPEED = 8

    def __init__(self, x, y, angle, owner="player"):
        self.x = x
        self.y = y
        self.angle = angle
        self.owner = owner
        self.dead = False

    def move(self):
        rad = math.radians(self.angle)
        self.x -= math.sin(rad) * self.SPEED
        self.y -= math.cos(rad) * self.SPEED

    def draw(self, win):
        # Draw rocket shape
        rad = math.radians(self.angle)
        
        # Rocket body (elongated)
        length = 15
        width = 6
        
        # Calculate rocket points
        front_x = self.x - math.sin(rad) * length / 2
        front_y = self.y - math.cos(rad) * length / 2
        back_x = self.x + math.sin(rad) * length / 2
        back_y = self.y + math.cos(rad) * length / 2
        
        # Perpendicular for width
        perp_x = math.cos(rad) * width / 2
        perp_y = -math.sin(rad) * width / 2
        
        # Rocket body points (diamond/arrow shape)
        points = [
            (front_x, front_y),  # Tip
            (back_x + perp_x, back_y + perp_y),  # Right side
            (back_x, back_y),  # Back center
            (back_x - perp_x, back_y - perp_y),  # Left side
        ]
        
        # Draw rocket body
        pygame.draw.polygon(win, (255, 80, 80), points)
        pygame.draw.polygon(win, (200, 0, 0), points, 2)
        
        # Draw flame trail at back
        flame_points = [
            (back_x - perp_x * 0.5, back_y - perp_y * 0.5),
            (back_x + math.sin(rad) * 8, back_y + math.cos(rad) * 8),
            (back_x + perp_x * 0.5, back_y + perp_y * 0.5),
        ]
        pygame.draw.polygon(win, (255, 200, 0), flame_points)

    def rect(self):
        return pygame.Rect(self.x - self.RADIUS, self.y - self.RADIUS, self.RADIUS*2, self.RADIUS*2)

class Particle:
    def __init__(self, x, y, color, vel_x, vel_y, lifetime=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.lifetime = lifetime
        self.age = 0
        self.size = random.randint(2, 5)

    def update(self, dt):
        self.x += self.vel_x * dt * 60
        self.y += self.vel_y * dt * 60
        self.age += dt
        return self.age < self.lifetime

    def draw(self, win):
        alpha = int(255 * (1 - self.age / self.lifetime))
        size = max(1, int(self.size * (1 - self.age / self.lifetime)))
        color = (*self.color[:3], alpha) if len(self.color) == 4 else self.color
        pygame.draw.circle(win, color, (int(self.x), int(self.y)), size)

def spawn_powerups(count=3, track_mask=None, border_mask=None):
    powerups = []
    margin = 50
    attempts = 0
    max_attempts = 2000
    
    if track_mask is None:
        track_mask = TRACK_MASK
    if border_mask is None:
        border_mask = TRACK_BORDER_MASK
    
    while len(powerups) < count and attempts < max_attempts:
        pu_type = random.choice([PU_BOOST, PU_VULN, PU_WEAPON])
        x = random.randint(margin, WIDTH - margin)
        y = random.randint(margin, HEIGHT - margin)
        
        try:
            on_track = track_mask.get_at((x, y))
        except IndexError:
            on_track = 0
        try:
            on_border = border_mask.get_at((x, y))
        except IndexError:
            on_border = 0

        if on_track and not on_border:
            powerups.append({
                "type": pu_type, 
                "pos": (x, y), 
                "angle": random.uniform(0, 360), 
                "rot_speed": random.uniform(-90, 90), 
                "pulse_offset": random.uniform(0, math.pi * 2)
            })
        attempts += 1

    while len(powerups) < count:
        pu_type = random.choice([PU_BOOST, PU_VULN, PU_WEAPON])
        x = random.randint(margin, WIDTH - margin)
        y = random.randint(margin, HEIGHT - margin)
        powerups.append({
            "type": pu_type, 
            "pos": (x, y), 
            "angle": random.uniform(0, 360), 
            "rot_speed": random.uniform(-90, 90), 
            "pulse_offset": random.uniform(0, math.pi * 2)
        })

    return powerups

def draw_text_with_shadow(win, text, font, x, y, color=(255, 255, 255), shadow_color=(0, 0, 0), offset=2):
    shadow = font.render(text, True, shadow_color)
    main = font.render(text, True, color)
    win.blit(shadow, (x + offset, y + offset))
    win.blit(main, (x, y))

def draw_hud(win, player_car, game_info, current_map):
    # Modern HUD with panels
    panel_color = (20, 20, 30, 200)
    accent_color = (255, 215, 0)
    
    # Bottom-left panel - Game info
    panel_rect = pygame.Rect(10, HEIGHT - 150, 280, 140)
    s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    s.fill(panel_color)
    pygame.draw.rect(s, accent_color, s.get_rect(), 2, border_radius=8)
    win.blit(s, panel_rect.topleft)
    
    draw_text_with_shadow(win, f"LAP: {game_info.laps}", HUD_FONT, 20, HEIGHT - 140, (255, 255, 255))
    draw_text_with_shadow(win, f"TIME: {game_info.get_lap_time():.2f}s", HUD_FONT, 20, HEIGHT - 110, (100, 255, 100))
    if game_info.best_time:
        draw_text_with_shadow(win, f"BEST: {game_info.best_time:.2f}s", HUD_FONT, 20, HEIGHT - 80, (255, 200, 0))
    draw_text_with_shadow(win, f"SPEED: {round(player_car.vel, 1)}px/s", HUD_FONT, 20, HEIGHT - 50, (150, 200, 255))
    
    # Top-right panel - Power-ups & Ammo
    panel_rect2 = pygame.Rect(WIDTH - 290, 10, 280, 100)
    s2 = pygame.Surface((panel_rect2.width, panel_rect2.height), pygame.SRCALPHA)
    s2.fill(panel_color)
    pygame.draw.rect(s2, accent_color, s2.get_rect(), 2, border_radius=8)
    win.blit(s2, panel_rect2.topleft)
    
    draw_text_with_shadow(win, f"AMMO: {player_car.ammo}", HUD_FONT, WIDTH - 280, 20, (255, 100, 100))
    
    if player_car.active_power:
        remaining = max(0, player_car.power_end_time - time.time())
        power_name = player_car.active_power.upper()
        power_color = (255, 215, 0) if player_car.active_power == PU_BOOST else (200, 0, 200) if player_car.active_power == PU_VULN else (0, 255, 0)
        draw_text_with_shadow(win, f"POWER: {power_name}", HUD_FONT, WIDTH - 280, 50, power_color)
        draw_text_with_shadow(win, f"{remaining:.1f}s", HUD_FONT, WIDTH - 280, 75, (255, 255, 255))

def draw(win, images, player_car, computer_car, game_info, powerups, projectiles, particles, current_map):
    for img, pos in images:
        win.blit(img, pos)

    # Draw particles
    for p in particles:
        p.draw(win)

    # Draw powerups with animation
    dt = 1.0 / FPS
    for pu in powerups:
        img = None
        if pu["type"] == PU_BOOST:
            img = POWERUP_BOOST_IMG
        elif pu["type"] == PU_VULN:
            img = POWERUP_VULN_IMG
        elif pu["type"] == PU_WEAPON:
            img = POWERUP_WEAPON_IMG

        pu["angle"] = (pu.get("angle", 0) + pu.get("rot_speed", 0) * dt) % 360
        pu["pulse_offset"] = pu.get("pulse_offset", 0) + dt * 2.0

        if img:
            scale = 1.0 + 0.15 * math.sin(pu["pulse_offset"])
            rot_img = pygame.transform.rotozoom(img, pu["angle"], scale)
            rect = rot_img.get_rect(center=pu["pos"])
            win.blit(rot_img, rect.topleft)
        else:
            color = PU_COLORS.get(pu["type"], (255,255,255))
            pygame.draw.circle(win, color, pu["pos"], 12)
            pygame.draw.circle(win, (0,0,0), pu["pos"], 12, 2)

    # Draw projectiles
    for p in projectiles:
        if PROJECTILE_IMG:
            img = pygame.transform.rotate(PROJECTILE_IMG, p.angle)
            rect = img.get_rect(center=(int(p.x), int(p.y)))
            win.blit(img, rect.topleft)
        else:
            p.draw(win)

    player_car.draw(win)
    computer_car.draw(win)
    
    # Draw HUD
    draw_hud(win, player_car, game_info, current_map)

def draw_button(win, rect, text, font, base_color, hover_color, text_color=(0, 0, 0)):
    mx, my = pygame.mouse.get_pos()
    x, y, w, h = rect
    is_hover = x <= mx <= x + w and y <= my <= y + h
    color = hover_color if is_hover else base_color
    
    # Draw button with shadow
    shadow_rect = (x + 3, y + 3, w, h)
    pygame.draw.rect(win, (0, 0, 0, 100), shadow_rect, border_radius=10)
    pygame.draw.rect(win, color, rect, border_radius=10)
    pygame.draw.rect(win, (255, 255, 255), rect, 3, border_radius=10)
    
    txt = font.render(text, True, text_color)
    tw, th = txt.get_width(), txt.get_height()
    win.blit(txt, (x + (w - tw) // 2, y + (h - th) // 2))
    
    return is_hover

def draw_main_menu(win, images):
    for img, pos in images:
        win.blit(img, pos)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))

    # Title with glow effect
    title_text = "ULTIMATE RACING"
    subtitle_text = "CHAMPIONSHIP"
    
    for offset in range(5, 0, -1):
        glow_color = (255, 215, 0, 50 * (6 - offset))
        glow = TITLE_FONT.render(title_text, True, glow_color)
        win.blit(glow, ((WIDTH - glow.get_width()) // 2 - offset, HEIGHT // 6 - offset))
        win.blit(glow, ((WIDTH - glow.get_width()) // 2 + offset, HEIGHT // 6 + offset))
    
    title = TITLE_FONT.render(title_text, True, (255, 255, 255))
    win.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 6))
    
    subtitle = MAIN_FONT.render(subtitle_text, True, (255, 215, 0))
    win.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, HEIGHT // 6 + 80))

    # Menu buttons
    btn_w, btn_h = 300, 70
    btn_x = (WIDTH - btn_w) // 2
    spacing = 20
    
    buttons = [
        ("PLAY", HEIGHT // 2 - 20),
        ("SELECT MAP", HEIGHT // 2 + btn_h + spacing - 20),
        ("QUIT", HEIGHT // 2 + (btn_h + spacing) * 2 - 20)
    ]
    
    hover_states = []
    for text, y in buttons:
        hover = draw_button(win, (btn_x, y, btn_w, btn_h), text, MAIN_FONT, 
                          (50, 50, 80), (80, 80, 120), (255, 255, 255))
        hover_states.append(hover)
    
    return hover_states

def draw_map_selection(win, images, maps_list):
    for img, pos in images:
        win.blit(img, pos)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))

    title = TITLE_FONT.render("SELECT TRACK", True, (255, 255, 255))
    win.blit(title, ((WIDTH - title.get_width()) // 2, 50))

    # Map cards
    card_w, card_h = 350, 200
    spacing = 40
    start_y = 200
    
    hover_states = []
    for i, (map_key, map_data) in enumerate(maps_list):
        x = (WIDTH - card_w) // 2
        y = start_y + i * (card_h + spacing)
        
        # Card background
        card_rect = (x, y, card_w, card_h)
        mx, my = pygame.mouse.get_pos()
        is_hover = x <= mx <= x + card_w and y <= my <= y + card_h
        
        color = (80, 80, 120) if is_hover else (50, 50, 80)
        pygame.draw.rect(win, color, card_rect, border_radius=15)
        pygame.draw.rect(win, (255, 215, 0), card_rect, 4, border_radius=15)
        
        # Map name
        name = MAIN_FONT.render(map_data["name"], True, (255, 255, 255))
        win.blit(name, (x + 20, y + 20))
        
        # Map preview (small track image)
        preview = pygame.transform.scale(map_data["track"], (150, 120))
        win.blit(preview, (x + 20, y + 60))
        
        hover_states.append((is_hover, map_key))
    
    # Back button
    btn_w, btn_h = 200, 60
    btn_x = (WIDTH - btn_w) // 2
    btn_y = HEIGHT - 100
    back_hover = draw_button(win, (btn_x, btn_y, btn_w, btn_h), "BACK", SMALL_FONT,
                            (100, 50, 50), (150, 80, 80), (255, 255, 255))
    
    return hover_states, back_hover

def draw_countdown(win, number):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    win.blit(overlay, (0, 0))

    # Animated countdown
    scale = 1.0 + 0.2 * math.sin(time.time() * 10)
    color_intensity = int(200 + 55 * math.sin(time.time() * 8))
    
    txt = COUNTDOWN_FONT.render(str(number), True, (255, color_intensity, 0))
    scaled = pygame.transform.rotozoom(txt, 0, scale)
    win.blit(scaled, ((WIDTH - scaled.get_width()) // 2, (HEIGHT - scaled.get_height()) // 2))

def draw_modal(win, message, show_next=False):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))

    box_w, box_h = 600, 300
    box_x = (WIDTH - box_w) // 2
    box_y = (HEIGHT - box_h) // 2
    
    pygame.draw.rect(win, (40, 40, 60), (box_x, box_y, box_w, box_h), border_radius=15)
    pygame.draw.rect(win, (255, 215, 0), (box_x, box_y, box_w, box_h), 4, border_radius=15)

    msg = MAIN_FONT.render(message, True, (255, 255, 255))
    win.blit(msg, (box_x + (box_w - msg.get_width()) // 2, box_y + 40))

    # Buttons
    btn_w, btn_h = 160, 60
    spacing = 30
    
    if show_next:
        total_w = btn_w * 3 + spacing * 2
        start_x = box_x + (box_w - total_w) // 2
        btn_y = box_y + box_h - btn_h - 40
        
        restart_hover = draw_button(win, (start_x, btn_y, btn_w, btn_h), "RESTART", SMALL_FONT,
                                   (100, 220, 120), (140, 255, 170), (0, 0, 0))
        next_hover = draw_button(win, (start_x + btn_w + spacing, btn_y, btn_w, btn_h), "NEXT", SMALL_FONT,
                                (100, 150, 255), (140, 190, 255), (0, 0, 0))
        quit_hover = draw_button(win, (start_x + (btn_w + spacing) * 2, btn_y, btn_w, btn_h), "MENU", SMALL_FONT,
                                (220, 100, 100), (255, 140, 140), (0, 0, 0))
        return restart_hover, next_hover, quit_hover
    else:
        total_w = btn_w * 2 + spacing
        start_x = box_x + (box_w - total_w) // 2
        btn_y = box_y + box_h - btn_h - 40
        
        restart_hover = draw_button(win, (start_x, btn_y, btn_w, btn_h), "RESTART", SMALL_FONT,
                                   (100, 220, 120), (140, 255, 170), (0, 0, 0))
        quit_hover = draw_button(win, (start_x + btn_w + spacing, btn_y, btn_w, btn_h), "MENU", SMALL_FONT,
                                (220, 100, 100), (255, 140, 140), (0, 0, 0))
        return restart_hover, False, quit_hover

def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        player_car.rotate(left=True)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        player_car.rotate(right=True)
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        moved = True
        player_car.move_backward()
    
    if not moved:
        player_car.reduce_speed()

def handle_collision(player_car, computer_car, powerups, projectiles, particles, current_map, game_info):
    border_mask = current_map["border_mask"]
    finish_mask = current_map["finish_mask"]
    finish_pos = current_map["finish_pos"]
    
    # Car vs border
    if player_car.collide(border_mask) != None:
        poi = player_car.collide(border_mask)
        if poi:
            img_w, img_h = player_car.img.get_width(), player_car.img.get_height()
            
            # Spark particles on collision
            for _ in range(5):
                particles.append(Particle(
                    player_car.x + img_w//2, 
                    player_car.y + img_h//2,
                    (255, 200, 0),
                    random.uniform(-3, 3),
                    random.uniform(-3, 3),
                    0.5
                ))
            
            # Push through if boost or vulnerable, otherwise bounce
            if player_car.active_power == PU_BOOST or player_car.vulnerable:
                offset_x, offset_y = int(player_car.x), int(player_car.y)
                overlap_x = poi[0] - offset_x
                overlap_y = poi[1] - offset_y

                center_x, center_y = img_w / 2.0, img_h / 2.0

                vx = center_x - overlap_x
                vy = center_y - overlap_y

                if vx == 0 and vy == 0:
                    rad = math.radians(player_car.angle)
                    vx = -math.sin(rad)
                    vy = -math.cos(rad)

                mag = math.hypot(vx, vy)
                if mag != 0:
                    vx /= mag
                    vy /= mag

                pushed = False
                for step in range(6):
                    push_amount = 1 + step
                    player_car.x += vx * push_amount
                    player_car.y += vy * push_amount
                    if player_car.collide(border_mask) is None:
                        pushed = True
                        break

                if not pushed:
                    player_car.x, player_car.y = player_car.prev_x, player_car.prev_y

                player_car.vel *= 0.5
            else:
                player_car.bounce()

    # Finish line
    computer_finish_point_collide = computer_car.collide(finish_mask, *finish_pos)
    if computer_finish_point_collide != None:
        return "lose"

    player_finish_point_collide = player_car.collide(finish_mask, *finish_pos)
    if player_finish_point_collide != None:
        if player_finish_point_collide[1] == 0:
            player_car.bounce()
        else:
            lap_time = game_info.complete_lap()
            # Celebration particles
            for _ in range(20):
                particles.append(Particle(
                    finish_pos[0] + 50,
                    finish_pos[1] + 50,
                    random.choice([(255, 215, 0), (255, 100, 100), (100, 255, 100)]),
                    random.uniform(-5, 5),
                    random.uniform(-5, 5),
                    1.5
                ))
            return "win"

    # Player picks up powerups
    px, py = int(player_car.x), int(player_car.y)
    to_remove = []
    for i, pu in enumerate(powerups):
        pux, puy = pu["pos"]
        if math.hypot(pux - px, puy - py) < 30:
            player_car.apply_powerup(pu["type"])
            to_remove.append(i)
            # Pickup particles
            for _ in range(10):
                particles.append(Particle(
                    pux, puy,
                    PU_COLORS.get(pu["type"], (255, 255, 255)),
                    random.uniform(-4, 4),
                    random.uniform(-4, 4),
                    0.8
                ))
    
    for i in sorted(to_remove, reverse=True):
        powerups.pop(i)

    # Update projectiles
    for p in list(projectiles):
        p.move()
        if p.x < 0 or p.x > WIDTH or p.y < 0 or p.y > HEIGHT:
            projectiles.remove(p)
            continue
        
        if p.owner == "player":
            if p.rect().colliderect(pygame.Rect(computer_car.x, computer_car.y, 
                                                computer_car.img.get_width(), 
                                                computer_car.img.get_height())):
                hit_x, hit_y = computer_car.x, computer_car.y
                computer_car.reset()
                computer_car.x, computer_car.y = hit_x, hit_y
                computer_car.prev_x, computer_car.prev_y = hit_x, hit_y
                computer_car.stunned_until = time.time() + 3.0
                projectiles.remove(p)
                # Explosion particles
                for _ in range(15):
                    particles.append(Particle(
                        p.x, p.y,
                        (255, 100, 0),
                        random.uniform(-6, 6),
                        random.uniform(-6, 6),
                        1.0
                    ))
                continue
    
    return None

def reset_game_state(current_map_key):
    global player_car, computer_car, powerups, projectiles, particles, game_info, last_spawn
    
    current_map = MAPS[current_map_key]
    PlayerCar.START_POS = current_map["player_start"]
    ComputerCar.START_POS = current_map["ai_start"]
    
    player_car = PlayerCar(4, 4)
    computer_car = ComputerCar(4, 4, current_map["path"])
    game_info = GameInfo()
    powerups = spawn_powerups(4, current_map["track_mask"], current_map["border_mask"])
    projectiles = []
    particles = []
    last_spawn = time.time()

def get_map_images(map_key):
    m = MAPS[map_key]
    return [(m["grass"], (0,0)), (m["track"], (0,0)), (m["finish"], m["finish_pos"]), (m["border"], (0,0))]

# Main game loop
run = True
clock = pygame.time.Clock()

# Initialize with classic map
current_map_key = "classic"
reset_game_state(current_map_key)
images = get_map_images(current_map_key)

state = 'menu'
modal_result = None
countdown_start = 0
countdown_number = 0
update_window_title('menu')

while run:
    clock.tick(FPS)
    dt = 1.0 / FPS

    # Menu state
    if state == 'menu':
        hover_states = draw_main_menu(WIN, images)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hover_states[0]:  # Play
                    reset_game_state(current_map_key)
                    images = get_map_images(current_map_key)
                    countdown_start = time.time()
                    countdown_number = COUNTDOWN_SECONDS
                    state = 'countdown'
                    update_window_title('countdown')
                elif hover_states[1]:  # Select Map
                    state = 'map_select'
                    update_window_title('map_select')
                elif hover_states[2]:  # Quit
                    run = False
                    break
        
        pygame.display.update()
        continue

    # Map selection state
    if state == 'map_select':
        maps_list = list(MAPS.items())
        hover_states, back_hover = draw_map_selection(WIN, images, maps_list)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_hover:
                    state = 'menu'
                    update_window_title('menu')
                else:
                    for is_hover, map_key in hover_states:
                        if is_hover:
                            current_map_key = map_key
                            reset_game_state(current_map_key)
                            images = get_map_images(current_map_key)
                            state = 'menu'
                            update_window_title('menu')
                            break
        
        pygame.display.update()
        continue

    # Countdown state
    if state == 'countdown':
        draw(WIN, images, player_car, computer_car, game_info, powerups, projectiles, particles, MAPS[current_map_key])
        
        elapsed = time.time() - countdown_start
        sec = COUNTDOWN_SECONDS - int(elapsed)
        if sec <= 0:
            state = 'playing'
            game_info.start_level()
            update_window_title('playing', MAPS[current_map_key], game_info.laps)
        else:
            draw_countdown(WIN, sec)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        continue

    # Playing state
    if state == 'playing':
        player_car.update_power_state()

        # Periodic powerup spawn
        if time.time() - last_spawn > SPAWN_INTERVAL:
            powerups.extend(spawn_powerups(1, MAPS[current_map_key]["track_mask"], 
                                          MAPS[current_map_key]["border_mask"]))
            last_spawn = time.time()

        # Update particles
        particles = [p for p in particles if p.update(dt)]

        draw(WIN, images, player_car, computer_car, game_info, powerups, projectiles, particles, MAPS[current_map_key])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player_car.ammo > 0:
                    rad = math.radians(player_car.angle)
                    front_x = player_car.x - math.sin(rad) * (player_car.img.get_height()//2)
                    front_y = player_car.y - math.cos(rad) * (player_car.img.get_height()//2)
                    proj = Projectile(front_x, front_y, player_car.angle, owner="player")
                    projectiles.append(proj)
                    player_car.ammo -= 1
                elif event.key == pygame.K_ESCAPE:
                    state = 'menu'
                    update_window_title('menu')

        move_player(player_car)
        computer_car.move()

        result = handle_collision(player_car, computer_car, powerups, projectiles, particles, 
                                 MAPS[current_map_key], game_info)
        if result in ("win", "lose"):
            modal_result = result
            state = 'modal'
            update_window_title('modal')
        
        pygame.display.update()
        continue

    # Modal state
    if state == 'modal':
        msg = "🏆 YOU WIN! 🏆" if modal_result == 'win' else "💥 YOU LOSE! 💥"
        draw(WIN, images, player_car, computer_car, game_info, powerups, projectiles, particles, MAPS[current_map_key])
        
        show_next = modal_result == 'win'
        buttons = draw_modal(WIN, msg, show_next)
        restart_hover, next_hover, quit_hover = buttons

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_hover:
                    reset_game_state(current_map_key)
                    images = get_map_images(current_map_key)
                    countdown_start = time.time()
                    countdown_number = COUNTDOWN_SECONDS
                    state = 'countdown'
                    update_window_title('countdown')
                elif next_hover and show_next:
                    # Continue to next lap
                    countdown_start = time.time()
                    countdown_number = COUNTDOWN_SECONDS
                    state = 'countdown'
                    update_window_title('countdown')
                elif quit_hover:
                    state = 'menu'
                    update_window_title('menu')

        pygame.display.update()
        continue

pygame.quit()
