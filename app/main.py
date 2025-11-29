import pygame
import time
import math
import random
from utils import blit_text_center, scale_image, blit_rotate_center
from leaderboard import add_single_player_record, add_multiplayer_record, get_top_records
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
HUD_FONT = pygame.font.SysFont("consolas", 16, bold=True)
COUNTDOWN_FONT = pygame.font.SysFont("arial", 180, bold=True)

# AI Path
PATH = [(170, 200), (182, 115), (67, 153), (69, 532), (351, 803), (441, 701), (478, 565), 
        (624, 563), (687, 790), (819, 719), (804, 444), (685, 408), (490, 389), 
        (517, 312), (777, 278), (798, 101), (615, 80), (349, 94), (299, 421), 
        (199, 391), (205, 193), (170, 200)]

# Game Settings
class GameSettings:
    def __init__(self):
        self.laps_to_win = 1
        self.map_rotation = "manual"  # "manual", "per_lap"
        self.race_mode = "continuous"  # "continuous", "sprint"
        self.show_hud = True  # Show/hide HUD boxes
        self.powerups_enabled = True  # Enable/disable powerups
        self.editing_laps = False
        self.laps_input = "1"
        self.ai_difficulty = "medium"  # "easy", "medium", "hard", "extreme"
    
    def start_editing_laps(self):
        self.editing_laps = True
        self.laps_input = str(self.laps_to_win)
    
    def stop_editing_laps(self):
        self.editing_laps = False
        try:
            # Don't allow empty or zero
            if self.laps_input == "" or self.laps_input == "0":
                self.laps_input = str(self.laps_to_win)
                return
            
            value = int(self.laps_input)
            if 1 <= value <= 99:
                self.laps_to_win = value
            else:
                self.laps_input = str(self.laps_to_win)
        except:
            self.laps_input = str(self.laps_to_win)
    
    def add_digit(self, digit):
        # Don't allow leading zeros
        if self.laps_input == "" and digit == "0":
            return
        
        if len(self.laps_input) < 2:
            if self.laps_input == "0":
                self.laps_input = digit
            else:
                self.laps_input += digit
    
    def backspace(self):
        if len(self.laps_input) > 0:
            self.laps_input = self.laps_input[:-1]
        # Allow empty input so user can type fresh number
    
    def cycle_rotation(self):
        rotations = ["manual", "per_lap"]
        current_index = rotations.index(self.map_rotation)
        self.map_rotation = rotations[(current_index + 1) % len(rotations)]
    
    def cycle_race_mode(self):
        modes = ["continuous", "sprint"]
        current_index = modes.index(self.race_mode)
        self.race_mode = modes[(current_index + 1) % len(modes)]
    
    def get_rotation_text(self):
        if self.map_rotation == "manual":
            return "Manual Selection"
        else:
            return "Random Per Lap"
    
    def get_race_mode_text(self):
        if self.race_mode == "continuous":
            return "Continuous"
        else:
            return "Sprint"
    
    def toggle_hud(self):
        self.show_hud = not self.show_hud
    
    def get_hud_text(self):
        return "Visible" if self.show_hud else "Hidden"
    
    def toggle_powerups(self):
        self.powerups_enabled = not self.powerups_enabled
    
    def get_powerups_text(self):
        return "Enabled" if self.powerups_enabled else "Disabled"

game_settings = GameSettings()

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

# Load city circuit map assets
try:
    CITY_GRASS = pygame.image.load('imgs/city-grass.png')
    CITY_TRACK = pygame.image.load('imgs/city-track.png')
    CITY_BORDER = pygame.image.load('imgs/city-border.png')
    CITY_BORDER_MASK = pygame.mask.from_surface(CITY_BORDER)
    CITY_TRACK_MASK = pygame.mask.from_surface(CITY_TRACK)
    CITY_FINISH = pygame.image.load('imgs/city-finish.png')
    CITY_FINISH_MASK = pygame.mask.from_surface(CITY_FINISH)
    CITY_FINISH_POS = (510, 60)
    CITY_PATH = [  (104, 91), (102, 279), (224, 297),
             (229, 563), (111, 603), (125, 775),
             (790, 779), (794, 613), (656, 575),
             (662, 321), (794, 278), (798, 119),
             (499, 101)]
    city_available = True
except:
    city_available = False

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
        "ai_start": (170, 200),
        "checkpoint": (490, 389)  # Halfway point on the track
    }
}

if city_available:
    MAPS["city"] = {
        "name": "City Circuit",
        "grass": CITY_GRASS,
        "track": CITY_TRACK,
        "border": CITY_BORDER,
        "border_mask": CITY_BORDER_MASK,
        "track_mask": CITY_TRACK_MASK,
        "finish": CITY_FINISH,
        "finish_mask": CITY_FINISH_MASK,
        "finish_pos": CITY_FINISH_POS,
        "path": CITY_PATH,
        "player_start": (430, 105),
        "ai_start": (430, 75),
        "start_angle": 90,
        "checkpoint": (662, 575)  # Halfway point on city track
    }

class GameInfo:
    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0
        self.laps = 0
        self.best_time = None
        self.current_lap_start = 0
        self.last_lap_time = -10  # Initialize to -10 to allow first lap immediately
        self.frozen_time = None  # For freezing timer when race ends
        self.passed_halfway = False  # Track if player passed halfway point to prevent wrong-way finish
        self.wrong_way_warning = 0  # Timestamp for showing wrong way warning

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
        self.frozen_time = None
        self.passed_halfway = False  # Reset checkpoint for new race
    
    def freeze_time(self):
        """Freeze the timer at current time"""
        if self.started and self.frozen_time is None:
            self.frozen_time = time.time() - self.level_start_time

    def get_level_time(self):
        if not self.started:
            return 0
        if hasattr(self, 'frozen_time') and self.frozen_time is not None:
            return round(self.frozen_time, 2)
        return round(time.time() - self.level_start_time, 2)
    
    def get_lap_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.current_lap_start, 2)
    
    def complete_lap(self):
        current_time = time.time()
        # Prevent multiple lap counts within 2 seconds (cooldown)
        if current_time - self.last_lap_time < 2.0:
            return 0
        
        lap_time = self.get_lap_time()
        if self.best_time is None or lap_time < self.best_time:
            self.best_time = lap_time
        self.laps += 1
        self.current_lap_start = current_time
        self.last_lap_time = current_time
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

    def __init__(self, max_vel, rotation_vel, player_num=1):
        super().__init__(max_vel, rotation_vel)
        self.active_power = None
        self.power_end_time = 0
        self.vulnerable = False
        self.ammo = 0
        self.player_num = player_num
        self.stunned_until = 0
        
        # Set different colors for different players
        if player_num == 2:
            self.img = BLUE_CAR
    
    def is_stunned(self):
        return time.time() < self.stunned_until
    
    def stun(self, duration=2.0):
        self.stunned_until = time.time() + duration
        self.vel = 0

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
        target_x, target_y = target
        # Use distance check instead of rect collision (more reliable)
        dist = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
        if dist < 20:
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
            self.current_point = 0  # Loop back to start of path

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
    max_attempts = 5000
    
    if track_mask is None:
        track_mask = TRACK_MASK
    if border_mask is None:
        border_mask = TRACK_BORDER_MASK
    
    while len(powerups) < count and attempts < max_attempts:
        pu_type = random.choice([PU_BOOST, PU_VULN, PU_WEAPON])
        x = random.randint(margin, WIDTH - margin)
        y = random.randint(margin, HEIGHT - margin)
        
        try:
            # Check if position is on the track
            # get_at returns an integer (0 or 1) for masks
            on_track = track_mask.get_at((x, y)) > 0
        except IndexError:
            on_track = False
        
        try:
            # Check if position is on border
            on_border = border_mask.get_at((x, y)) > 0
        except IndexError:
            on_border = False

        # Only spawn if on track AND not on border
        if on_track and not on_border:
            powerups.append({
                "type": pu_type, 
                "pos": (x, y), 
                "angle": random.uniform(0, 360), 
                "rot_speed": random.uniform(-90, 90), 
                "pulse_offset": random.uniform(0, math.pi * 2)
            })
        attempts += 1

    # If we couldn't find enough valid positions, don't add random ones
    # This ensures powerups are ONLY on valid track areas
    return powerups

def draw_text_with_shadow(win, text, font, x, y, color=(255, 255, 255), shadow_color=(0, 0, 0), offset=2):
    shadow = font.render(text, True, shadow_color)
    main = font.render(text, True, color)
    win.blit(shadow, (x + offset, y + offset))
    win.blit(main, (x, y))

def draw_hud(win, player_car, game_info, current_map, player_car2=None, game_info2=None, ai_game_info=None):
    # Draw wrong way warnings (always show, even if HUD is hidden)
    current_time = time.time()
    
    # Player 1 wrong way warning
    if hasattr(game_info, 'wrong_way_warning') and current_time - game_info.wrong_way_warning < 2.0:
        warning_alpha = int(255 * (1 - (current_time - game_info.wrong_way_warning) / 2.0))
        warning_text = "⚠️ WRONG WAY! ⚠️"
        warning_surface = MAIN_FONT.render(warning_text, True, (255, 50, 50))
        warning_x = (WIDTH - warning_surface.get_width()) // 2
        warning_y = HEIGHT // 3
        
        # Pulsing effect
        scale = 1.0 + 0.1 * math.sin(current_time * 10)
        scaled_warning = pygame.transform.rotozoom(warning_surface, 0, scale)
        win.blit(scaled_warning, (warning_x, warning_y))
    
    # Player 2 wrong way warning
    if player_car2 and game_info2 and hasattr(game_info2, 'wrong_way_warning') and current_time - game_info2.wrong_way_warning < 2.0:
        warning_alpha = int(255 * (1 - (current_time - game_info2.wrong_way_warning) / 2.0))
        warning_text = "⚠️ P2 WRONG WAY! ⚠️"
        warning_surface = SMALL_FONT.render(warning_text, True, (255, 100, 150))
        warning_x = (WIDTH - warning_surface.get_width()) // 2
        warning_y = HEIGHT // 3 + 60
        
        # Pulsing effect
        scale = 1.0 + 0.1 * math.sin(current_time * 10)
        scaled_warning = pygame.transform.rotozoom(warning_surface, 0, scale)
        win.blit(scaled_warning, (warning_x, warning_y))
    
    # Check if HUD should be shown
    if not game_settings.show_hud:
        return
    
    # Modern HUD with panels - more transparent
    panel_color = (20, 20, 30, 120)
    accent_color = (255, 215, 0)
    accent_color2 = (100, 150, 255)
    accent_color_ai = (255, 100, 100)
    
    # Bottom-left panel - Player 1 info (combined with ammo)
    panel_height = 140 if player_car.active_power else 115
    panel_rect = pygame.Rect(10, HEIGHT - panel_height - 10, 220, panel_height)
    s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    s.fill(panel_color)
    pygame.draw.rect(s, accent_color, s.get_rect(), 2, border_radius=8)
    win.blit(s, panel_rect.topleft)
    
    p1_label = "P1 " if player_car2 else ""
    y_start = HEIGHT - panel_height - 5
    draw_text_with_shadow(win, f"{p1_label}LAP: {game_info.laps}/{game_settings.laps_to_win}", HUD_FONT, 18, y_start, (255, 255, 255))
    draw_text_with_shadow(win, f"TIME: {game_info.get_lap_time():.2f}s", HUD_FONT, 18, y_start + 20, (100, 255, 100))
    if game_info.best_time:
        draw_text_with_shadow(win, f"BEST: {game_info.best_time:.2f}s", HUD_FONT, 18, y_start + 40, (255, 200, 0))
    draw_text_with_shadow(win, f"AMMO: {player_car.ammo}", HUD_FONT, 18, y_start + 60, (255, 100, 100))
    
    # Show active power if any
    if player_car.active_power:
        remaining = max(0, player_car.power_end_time - time.time())
        power_name = player_car.active_power.upper()
        power_color = (255, 215, 0) if player_car.active_power == PU_BOOST else (200, 0, 200) if player_car.active_power == PU_VULN else (0, 255, 0)
        draw_text_with_shadow(win, f"PWR: {power_name[:4]} {remaining:.1f}s", HUD_FONT, 18, y_start + 80, power_color)
    
    # Player 2 HUD (if multiplayer)
    if player_car2 and game_info2:
        # Bottom-right panel - Player 2 info (combined with ammo) - moved more to the left
        panel_height2 = 140 if player_car2.active_power else 115
        p2_x_offset = WIDTH - 420  # Moved even more to the left
        panel_rect3 = pygame.Rect(p2_x_offset, HEIGHT - panel_height2 - 10, 220, panel_height2)
        s3 = pygame.Surface((panel_rect3.width, panel_rect3.height), pygame.SRCALPHA)
        s3.fill(panel_color)
        pygame.draw.rect(s3, accent_color2, s3.get_rect(), 2, border_radius=8)
        win.blit(s3, panel_rect3.topleft)
        
        y_start2 = HEIGHT - panel_height2 - 5
        p2_text_x = p2_x_offset + 8
        draw_text_with_shadow(win, f"P2 LAP: {game_info2.laps}/{game_settings.laps_to_win}", HUD_FONT, p2_text_x, y_start2, (255, 255, 255))
        draw_text_with_shadow(win, f"TIME: {game_info2.get_lap_time():.2f}s", HUD_FONT, p2_text_x, y_start2 + 20, (100, 255, 100))
        if game_info2.best_time:
            draw_text_with_shadow(win, f"BEST: {game_info2.best_time:.2f}s", HUD_FONT, p2_text_x, y_start2 + 40, (255, 200, 0))
        draw_text_with_shadow(win, f"AMMO: {player_car2.ammo}", HUD_FONT, p2_text_x, y_start2 + 60, (255, 100, 100))
        
        # Show active power if any
        if player_car2.active_power:
            remaining = max(0, player_car2.power_end_time - time.time())
            power_name = player_car2.active_power.upper()
            power_color = (255, 215, 0) if player_car2.active_power == PU_BOOST else (200, 0, 200) if player_car2.active_power == PU_VULN else (0, 255, 0)
            draw_text_with_shadow(win, f"PWR: {power_name[:4]} {remaining:.1f}s", HUD_FONT, p2_text_x, y_start2 + 80, power_color)
    
    # AI HUD (if single player mode)
    elif ai_game_info:
        # Bottom-right panel - AI info
        ai_panel_height = 80
        ai_x_offset = WIDTH - 420
        ai_panel_rect = pygame.Rect(ai_x_offset, HEIGHT - ai_panel_height - 10, 220, ai_panel_height)
        s_ai = pygame.Surface((ai_panel_rect.width, ai_panel_rect.height), pygame.SRCALPHA)
        s_ai.fill(panel_color)
        pygame.draw.rect(s_ai, accent_color_ai, s_ai.get_rect(), 2, border_radius=8)
        win.blit(s_ai, ai_panel_rect.topleft)
        
        ai_y_start = HEIGHT - ai_panel_height - 5
        ai_text_x = ai_x_offset + 8
        draw_text_with_shadow(win, f"AI LAP: {ai_game_info.laps}/{game_settings.laps_to_win}", HUD_FONT, ai_text_x, ai_y_start, (255, 255, 255))
        draw_text_with_shadow(win, f"TIME: {ai_game_info.get_lap_time():.2f}s", HUD_FONT, ai_text_x, ai_y_start + 20, (255, 150, 150))
        if ai_game_info.best_time:
            draw_text_with_shadow(win, f"BEST: {ai_game_info.best_time:.2f}s", HUD_FONT, ai_text_x, ai_y_start + 40, (255, 200, 100))

def draw(win, images, player_car, computer_car, game_info, powerups, projectiles, particles, current_map, player_car2=None, game_info2=None, ai_game_info=None):
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
    # Draw stun indicator for player 1
    if player_car.is_stunned():
        stun_text = SMALL_FONT.render("STUNNED!", True, (255, 50, 50))
        win.blit(stun_text, (int(player_car.x - 30), int(player_car.y - 40)))
    
    if player_car2:
        player_car2.draw(win)
        # Draw stun indicator for player 2
        if player_car2.is_stunned():
            stun_text = SMALL_FONT.render("STUNNED!", True, (255, 50, 50))
            win.blit(stun_text, (int(player_car2.x - 30), int(player_car2.y - 40)))
    else:
        computer_car.draw(win)
    
    # Draw HUD
    draw_hud(win, player_car, game_info, current_map, player_car2, game_info2, ai_game_info)

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
    start_y = HEIGHT // 2 - 90
    
    buttons = [
        ("SINGLE PLAYER", start_y),
        ("MULTIPLAYER", start_y + btn_h + spacing),
        ("LEADERBOARD", start_y + (btn_h + spacing) * 2),
        ("OPTIONS", start_y + (btn_h + spacing) * 3),
        ("QUIT", start_y + (btn_h + spacing) * 4)
    ]
    
    hover_states = []
    for text, y in buttons:
        hover = draw_button(win, (btn_x, y, btn_w, btn_h), text, MAIN_FONT, 
                          (50, 50, 80), (80, 80, 120), (255, 255, 255))
        hover_states.append(hover)
    
    return hover_states

def draw_help_screen(win, images):
    for img, pos in images:
        win.blit(img, pos)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    win.blit(overlay, (0, 0))

    # Title
    title = MAIN_FONT.render("GAME GUIDE", True, (255, 215, 0))
    win.blit(title, ((WIDTH - title.get_width()) // 2, 30))

    # Content area
    content_x = 80
    content_y = 100
    line_height = 28
    section_spacing = 15
    
    # Controls Section - Two columns for P1 and P2
    section_title = SMALL_FONT.render("🎮 CONTROLS", True, (255, 215, 0))
    win.blit(section_title, (content_x, content_y))
    content_y += 35
    
    # Player 1 Controls (Left Column)
    col1_x = content_x + 20
    col2_x = WIDTH // 2 + 40
    p1_y = content_y
    
    p1_title = TINY_FONT.render("Player 1 (WASD):", True, (100, 200, 255))
    win.blit(p1_title, (col1_x, p1_y))
    p1_y += line_height
    
    p1_controls = [
        "  W - Accelerate",
        "  S - Brake/Reverse",
        "  A - Turn Left",
        "  D - Turn Right",
        "  SPACE - Fire Weapon"
    ]
    for ctrl in p1_controls:
        txt = TINY_FONT.render(ctrl, True, (255, 255, 255))
        win.blit(txt, (col1_x, p1_y))
        p1_y += line_height
    
    # Player 2 Controls (Right Column)
    p2_y = content_y
    
    p2_title = TINY_FONT.render("Player 2 (Arrow Keys):", True, (255, 150, 150))
    win.blit(p2_title, (col2_x, p2_y))
    p2_y += line_height
    
    p2_controls = [
        "  ↑ - Accelerate",
        "  ↓ - Brake/Reverse",
        "  ← - Turn Left",
        "  → - Turn Right",
        "  [ - Fire Weapon"
    ]
    for ctrl in p2_controls:
        txt = TINY_FONT.render(ctrl, True, (255, 255, 255))
        win.blit(txt, (col2_x, p2_y))
        p2_y += line_height
    
    # Move content_y to after both columns
    content_y = max(p1_y, p2_y) + 5
    
    # General Controls
    general = TINY_FONT.render("ESC - Return to Menu    G - Toggle HUD", True, (200, 200, 200))
    win.blit(general, (col1_x, content_y))
    content_y += line_height
    
    content_y += section_spacing
    
    # Power-ups Section
    section_title = SMALL_FONT.render("⚡ POWER-UPS", True, (255, 215, 0))
    win.blit(section_title, (content_x, content_y))
    content_y += 35
    
    powerups_info = [
        ("🟡 BOOST", "- Speed +80% for 5 seconds", (255, 215, 0)),
        ("🟣 VULNERABILITY", "- Pass through walls (risky!)", (200, 0, 200)),
        ("🟢 WEAPON", "- +1 ammo to stun opponents", (0, 255, 0))
    ]
    for name, desc, color in powerups_info:
        name_txt = TINY_FONT.render(name, True, color)
        desc_txt = TINY_FONT.render(desc, True, (255, 255, 255))
        win.blit(name_txt, (content_x + 20, content_y))
        win.blit(desc_txt, (content_x + 200, content_y))
        content_y += line_height
    
    # Note about disabling powerups
    note_txt = TINY_FONT.render("* Can be disabled in OPTIONS menu", True, (150, 150, 150))
    win.blit(note_txt, (content_x + 20, content_y))
    content_y += line_height
    
    content_y += section_spacing
    
    # Mechanics Section (Column 1)
    mechanics_y = content_y
    section_title = SMALL_FONT.render("🎯 GAME MECHANICS", True, (255, 215, 0))
    win.blit(section_title, (content_x, mechanics_y))
    mechanics_y += 35
    
    mechanics = [
        "• Hit walls = BOUNCE BACK (unless",
        "  boosted/vulnerable)",
        "• Weapon hits = STUN opponent",
        "  for 2-3 seconds",
        "• Collect power-ups by driving",
        "  through them",
        "• Cross finish line to complete laps",
        "• Beat your best lap time!"
    ]
    for mech in mechanics:
        txt = TINY_FONT.render(mech, True, (255, 255, 255))
        win.blit(txt, (content_x + 20, mechanics_y))
        mechanics_y += line_height
    
    # Pro Tips Section (Column 2)
    tips_y = content_y
    section_title = SMALL_FONT.render("💡 PRO TIPS", True, (255, 215, 0))
    win.blit(section_title, (col2_x, tips_y))
    tips_y += 35
    
    tips = [
        "• Brake before corners,",
        "  accelerate out",
        "• Use boost on straightaways",
        "  for max speed",
        "• Save weapons for strategic",
        "  moments",
        "• Watch your speed - too fast",
        "  = less control"
    ]
    for tip in tips:
        txt = TINY_FONT.render(tip, True, (200, 255, 200))
        win.blit(txt, (col2_x, tips_y))
        tips_y += line_height
    
    # Update content_y to after both sections
    content_y = max(mechanics_y, tips_y) + section_spacing
    
    # Back button
    btn_w, btn_h = 200, 60
    btn_x = (WIDTH - btn_w) // 2
    btn_y = HEIGHT - 80
    back_hover = draw_button(win, (btn_x, btn_y, btn_w, btn_h), "BACK", SMALL_FONT,
                            (100, 50, 50), (150, 80, 80), (255, 255, 255))
    
    return back_hover

def draw_options_menu(win, images, settings):
    for img, pos in images:
        win.blit(img, pos)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    win.blit(overlay, (0, 0))

    # Title
    title = MAIN_FONT.render("OPTIONS", True, (255, 215, 0))
    win.blit(title, ((WIDTH - title.get_width()) // 2, 50))

    # Options panel
    panel_w, panel_h = 600, 490
    panel_x = (WIDTH - panel_w) // 2
    panel_y = 150
    
    pygame.draw.rect(win, (40, 40, 60), (panel_x, panel_y, panel_w, panel_h), border_radius=15)
    pygame.draw.rect(win, (255, 215, 0), (panel_x, panel_y, panel_w, panel_h), 4, border_radius=15)

    # Option 1: Laps to Win (Text Input)
    opt_y = panel_y + 60
    label1 = SMALL_FONT.render("Laps to Win:", True, (255, 255, 255))
    win.blit(label1, (panel_x + 50, opt_y))
    
    btn_w, btn_h = 200, 50
    btn_x = panel_x + panel_w - btn_w - 50
    
    # Show input field or current value
    if settings.editing_laps:
        display_text = (settings.laps_input if settings.laps_input else "") + "_"
        btn_color = (120, 160, 120)
        hover_color = (140, 180, 140)
    else:
        display_text = str(settings.laps_to_win)
        btn_color = (80, 120, 80)
        hover_color = (120, 160, 120)
    
    laps_hover = draw_button(win, (btn_x, opt_y - 10, btn_w, btn_h), 
                            display_text, SMALL_FONT,
                            btn_color, hover_color, (255, 255, 255))
    
    # Show hint text
    if settings.editing_laps:
        hint = TINY_FONT.render("Type number, press ENTER", True, (200, 200, 200))
        win.blit(hint, (btn_x, opt_y + 45))
    
    # Option 2: Race Mode
    opt_y += 90
    label2 = SMALL_FONT.render("Race Mode:", True, (255, 255, 255))
    win.blit(label2, (panel_x + 50, opt_y))
    
    race_mode_hover = draw_button(win, (btn_x, opt_y - 10, btn_w, btn_h), 
                                settings.get_race_mode_text(), SMALL_FONT,
                                (100, 80, 120), (140, 120, 160), (255, 255, 255))
    
    # Race mode description
    if settings.race_mode == "continuous":
        mode_desc = "Race continues until all laps complete"
    else:
        mode_desc = "Reset positions after each lap winner"
    mode_desc_render = TINY_FONT.render(mode_desc, True, (200, 200, 200))
    win.blit(mode_desc_render, (panel_x + 50, opt_y + 45))
    
    # Option 3: Map Rotation (disabled in Continuous mode)
    opt_y += 90
    
    # Disable map rotation in continuous mode
    rotation_disabled = settings.race_mode == "continuous"
    
    if rotation_disabled:
        label3 = SMALL_FONT.render("Map Rotation:", True, (100, 100, 100))  # Gray text
    else:
        label3 = SMALL_FONT.render("Map Rotation:", True, (255, 255, 255))
    win.blit(label3, (panel_x + 50, opt_y))
    
    if rotation_disabled:
        # Show disabled button
        rotation_hover = draw_button(win, (btn_x, opt_y - 10, btn_w, btn_h), 
                                    "Disabled", TINY_FONT,
                                    (50, 50, 60), (50, 50, 60), (100, 100, 100))
        # Show why it's disabled
        disabled_text = TINY_FONT.render("Only available in Sprint mode", True, (150, 150, 150))
        win.blit(disabled_text, (panel_x + 50, opt_y + 45))
    else:
        rotation_hover = draw_button(win, (btn_x, opt_y - 10, btn_w, btn_h), 
                                    settings.get_rotation_text(), TINY_FONT,
                                    (80, 80, 120), (120, 120, 160), (255, 255, 255))
    
    # Option 4: Powerups
    opt_y += 90
    label4 = SMALL_FONT.render("Powerups:", True, (255, 255, 255))
    win.blit(label4, (panel_x + 50, opt_y))
    
    powerups_hover = draw_button(win, (btn_x, opt_y - 10, btn_w, btn_h), 
                                settings.get_powerups_text(), SMALL_FONT,
                                (100, 80, 100), (140, 120, 140), (255, 255, 255))
    
    powerups_desc = TINY_FONT.render("Enable or disable all powerups", True, (200, 200, 200))
    win.blit(powerups_desc, (panel_x + 50, opt_y + 45))
    
    # Option 5: Show HUD
    opt_y += 90
    label5 = SMALL_FONT.render("Show HUD:", True, (255, 255, 255))
    win.blit(label5, (panel_x + 50, opt_y))
    
    # Show hint text above button
    hud_desc = TINY_FONT.render("Press G during race to toggle", True, (200, 200, 200))
    win.blit(hud_desc, (panel_x + 50, opt_y + 25))
    
    hud_hover = draw_button(win, (btn_x, opt_y - 10, btn_w, btn_h), 
                           settings.get_hud_text(), SMALL_FONT,
                           (80, 100, 80), (120, 140, 120), (255, 255, 255))

    # Help button (above Back button)
    back_btn_w, back_btn_h = 200, 60
    back_btn_x = (WIDTH - back_btn_w) // 2
    help_btn_y = HEIGHT - 180
    help_hover = draw_button(win, (back_btn_x, help_btn_y, back_btn_w, back_btn_h), 
                            "HELP", SMALL_FONT,
                            (80, 120, 80), (120, 180, 120), (255, 255, 255))
    
    # Back button
    back_btn_y = HEIGHT - 100
    back_hover = draw_button(win, (back_btn_x, back_btn_y, back_btn_w, back_btn_h), 
                            "BACK", SMALL_FONT,
                            (100, 50, 50), (150, 80, 80), (255, 255, 255))
    
    return laps_hover, race_mode_hover, rotation_hover, powerups_hover, hud_hover, help_hover, back_hover

def draw_difficulty_selection(win, images):
    for img, pos in images:
        win.blit(img, pos)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))

    title = TITLE_FONT.render("SELECT DIFFICULTY", True, (255, 255, 255))
    win.blit(title, ((WIDTH - title.get_width()) // 2, 50))

    # Difficulty cards
    card_w, card_h = 400, 120
    spacing = 20
    start_y = 220
    
    difficulties = [
        ("EASY", "AI Speed: Slow", (100, 255, 100)),
        ("MEDIUM", "AI Speed: Normal", (255, 215, 0)),
        ("HARD", "AI Speed: Fast", (255, 150, 50)),
        ("EXTREME", "AI Speed: Very Fast", (255, 50, 50))
    ]
    
    hover_states = []
    for i, (name, desc, color) in enumerate(difficulties):
        x = (WIDTH - card_w) // 2
        y = start_y + i * (card_h + spacing)
        
        # Card background
        card_rect = (x, y, card_w, card_h)
        mx, my = pygame.mouse.get_pos()
        is_hover = x <= mx <= x + card_w and y <= my <= y + card_h
        
        bg_color = (80, 80, 120) if is_hover else (50, 50, 80)
        pygame.draw.rect(win, bg_color, card_rect, border_radius=15)
        pygame.draw.rect(win, color, card_rect, 4, border_radius=15)
        
        # Difficulty name
        name_txt = MAIN_FONT.render(name, True, color)
        win.blit(name_txt, (x + 20, y + 25))
        
        # Description
        desc_txt = SMALL_FONT.render(desc, True, (200, 200, 200))
        win.blit(desc_txt, (x + 20, y + 70))
        
        hover_states.append((is_hover, name.lower()))
    
    # Back button
    btn_w, btn_h = 200, 60
    btn_x = (WIDTH - btn_w) // 2
    btn_y = HEIGHT - 100
    back_hover = draw_button(win, (btn_x, btn_y, btn_w, btn_h), "BACK", SMALL_FONT,
                            (100, 50, 50), (150, 80, 80), (255, 255, 255))
    
    return hover_states, back_hover

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
        
        # Map preview - composite of all layers (grass + track + border)
        preview_surface = pygame.Surface((map_data["track"].get_width(), map_data["track"].get_height()))
        preview_surface.blit(map_data["grass"], (0, 0))
        preview_surface.blit(map_data["track"], (0, 0))
        preview_surface.blit(map_data["border"], (0, 0))
        
        preview = pygame.transform.scale(preview_surface, (150, 120))
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

def draw_name_entry(win, images, current_name, prompt="ENTER YOUR NAME"):
    """Draw name entry screen for leaderboard"""
    for img, pos in images:
        win.blit(img, pos)
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))
    
    box_w, box_h = 600, 300
    box_x = (WIDTH - box_w) // 2
    box_y = (HEIGHT - box_h) // 2
    
    pygame.draw.rect(win, (40, 40, 60), (box_x, box_y, box_w, box_h), border_radius=15)
    pygame.draw.rect(win, (255, 215, 0), (box_x, box_y, box_w, box_h), 4, border_radius=15)
    
    # Prompt
    prompt_txt = MAIN_FONT.render(prompt, True, (255, 215, 0))
    win.blit(prompt_txt, (box_x + (box_w - prompt_txt.get_width()) // 2, box_y + 40))
    
    # Name input box
    input_w, input_h = 400, 60
    input_x = box_x + (box_w - input_w) // 2
    input_y = box_y + 120
    
    pygame.draw.rect(win, (60, 60, 80), (input_x, input_y, input_w, input_h), border_radius=10)
    pygame.draw.rect(win, (255, 215, 0), (input_x, input_y, input_w, input_h), 3, border_radius=10)
    
    # Display name with cursor
    display_name = current_name + "_"
    name_txt = MAIN_FONT.render(display_name, True, (255, 255, 255))
    win.blit(name_txt, (input_x + 20, input_y + 15))
    
    # Instructions
    inst_txt = TINY_FONT.render("Press ENTER to continue (max 10 characters)", True, (200, 200, 200))
    win.blit(inst_txt, (box_x + (box_w - inst_txt.get_width()) // 2, box_y + 220))

def draw_leaderboard(win, images, mode="single_player", difficulty="easy"):
    """Draw leaderboard screen"""
    for img, pos in images:
        win.blit(img, pos)
    
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))
    
    title_text = "SINGLE PLAYER RECORDS" if mode == "single_player" else "MULTIPLAYER RECORDS"
    title = TITLE_FONT.render(title_text, True, (255, 215, 0))
    win.blit(title, ((WIDTH - title.get_width()) // 2, 30))
    
    # Difficulty tabs for single player
    difficulty_tabs = []
    if mode == "single_player":
        tab_y = 110
        tab_w = 150
        tab_h = 40
        tab_spacing = 10
        difficulties = ["easy", "medium", "hard", "extreme"]
        total_w = tab_w * 4 + tab_spacing * 3
        start_x = (WIDTH - total_w) // 2
        
        for i, diff in enumerate(difficulties):
            tab_x = start_x + i * (tab_w + tab_spacing)
            is_active = diff == difficulty
            
            # Tab colors
            if is_active:
                tab_color = (100, 150, 100) if diff == "easy" else (150, 150, 100) if diff == "medium" else (150, 100, 50) if diff == "hard" else (150, 50, 50)
                border_color = (150, 255, 150) if diff == "easy" else (255, 255, 150) if diff == "medium" else (255, 150, 100) if diff == "hard" else (255, 100, 100)
            else:
                tab_color = (40, 40, 60)
                border_color = (100, 100, 120)
            
            # Draw tab
            tab_rect = (tab_x, tab_y, tab_w, tab_h)
            pygame.draw.rect(win, tab_color, tab_rect, border_radius=8)
            pygame.draw.rect(win, border_color, tab_rect, 2, border_radius=8)
            
            # Tab text
            tab_txt = TINY_FONT.render(diff.upper(), True, (255, 255, 255))
            win.blit(tab_txt, (tab_x + (tab_w - tab_txt.get_width()) // 2, tab_y + 12))
            
            # Check hover
            mx, my = pygame.mouse.get_pos()
            is_hover = tab_x <= mx <= tab_x + tab_w and tab_y <= my <= tab_y + tab_h
            difficulty_tabs.append((is_hover, diff))
    
    # Get records (filtered by difficulty for single player)
    if mode == "single_player":
        records = get_top_records(mode, 10, difficulty)
    else:
        records = get_top_records(mode, 10)
    
    # Display records
    start_y = 170 if mode == "single_player" else 150
    line_height = 45
    
    if not records:
        no_records = MAIN_FONT.render("No records yet!", True, (200, 200, 200))
        win.blit(no_records, ((WIDTH - no_records.get_width()) // 2, HEIGHT // 2))
    else:
        for i, record in enumerate(records):
            y = start_y + i * line_height
            rank_color = (255, 215, 0) if i == 0 else (192, 192, 192) if i == 1 else (205, 127, 50) if i == 2 else (255, 255, 255)
            
            # Rank
            rank_txt = SMALL_FONT.render(f"#{i+1}", True, rank_color)
            win.blit(rank_txt, (100, y))
            
            if mode == "single_player":
                # Name
                name_txt = SMALL_FONT.render(record["name"], True, (255, 255, 255))
                win.blit(name_txt, (180, y))
                
                # Time
                time_txt = SMALL_FONT.render(f"{record['time']:.2f}s", True, (100, 255, 100))
                win.blit(time_txt, (350, y))
                
                # Map & Difficulty
                info_txt = TINY_FONT.render(f"{record['map']} - {record['difficulty'].upper()}", True, (200, 200, 200))
                win.blit(info_txt, (500, y + 5))
            else:
                # Winner name only
                name_txt = SMALL_FONT.render(record['winner'], True, (255, 255, 255))
                win.blit(name_txt, (180, y))
                
                # Time
                time_txt = SMALL_FONT.render(f"{record['time']:.2f}s", True, (100, 255, 100))
                win.blit(time_txt, (400, y))
                
                # Map
                map_txt = TINY_FONT.render(record['map'], True, (200, 200, 200))
                win.blit(map_txt, (550, y + 5))
    
    # Buttons
    btn_w, btn_h = 200, 60
    btn_spacing = 20
    total_w = btn_w * 2 + btn_spacing
    start_x = (WIDTH - total_w) // 2
    btn_y = HEIGHT - 100
    
    # Toggle mode button
    toggle_text = "MULTIPLAYER" if mode == "single_player" else "SINGLE PLAYER"
    toggle_hover = draw_button(win, (start_x, btn_y, btn_w, btn_h), toggle_text, TINY_FONT,
                               (80, 80, 120), (120, 120, 160), (255, 255, 255))
    
    # Back button
    back_hover = draw_button(win, (start_x + btn_w + btn_spacing, btn_y, btn_w, btn_h), "BACK", SMALL_FONT,
                            (100, 50, 50), (150, 80, 80), (255, 255, 255))
    
    return toggle_hover, back_hover, difficulty_tabs

def draw_modal(win, message, winner_time=None, loser_time=None, winner_name=None, loser_name=None):
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

    # Display winner time only
    if winner_time is not None:
        time_y = box_y + 120
        
        # Winner time (centered)
        winner_label = winner_name if winner_name else "Winner"
        time_text = f"{winner_label} Time: {winner_time:.2f}s"
        time_txt = SMALL_FONT.render(time_text, True, (100, 255, 100))
        win.blit(time_txt, (box_x + (box_w - time_txt.get_width()) // 2, time_y))

    # Buttons - only RESTART and MENU
    btn_w, btn_h = 160, 60
    spacing = 30
    total_w = btn_w * 2 + spacing
    start_x = box_x + (box_w - total_w) // 2
    btn_y = box_y + box_h - btn_h - 40
    
    restart_hover = draw_button(win, (start_x, btn_y, btn_w, btn_h), "RESTART", SMALL_FONT,
                               (100, 220, 120), (140, 255, 170), (0, 0, 0))
    quit_hover = draw_button(win, (start_x + btn_w + spacing, btn_y, btn_w, btn_h), "MENU", SMALL_FONT,
                            (220, 100, 100), (255, 140, 140), (0, 0, 0))
    return restart_hover, quit_hover

def move_player(player_car, player_car2=None):
    keys = pygame.key.get_pressed()
    
    # Player 1 controls (WASD) - only if not stunned
    if not player_car.is_stunned():
        moved = False
        if keys[pygame.K_a]:
            player_car.rotate(left=True)
        if keys[pygame.K_d]:
            player_car.rotate(right=True)
        if keys[pygame.K_w]:
            moved = True
            player_car.move_forward()
        if keys[pygame.K_s]:
            moved = True
            player_car.move_backward()
        
        if not moved:
            player_car.reduce_speed()
    else:
        # Stunned - can't move
        player_car.reduce_speed()
    
    # Player 2 controls (Arrow keys) - only if not stunned
    if player_car2:
        if not player_car2.is_stunned():
            moved2 = False
            if keys[pygame.K_LEFT]:
                player_car2.rotate(left=True)
            if keys[pygame.K_RIGHT]:
                player_car2.rotate(right=True)
            if keys[pygame.K_UP]:
                moved2 = True
                player_car2.move_forward()
            if keys[pygame.K_DOWN]:
                moved2 = True
                player_car2.move_backward()
            
            if not moved2:
                player_car2.reduce_speed()
        else:
            # Stunned - can't move
            player_car2.reduce_speed()

def handle_collision(player_car, computer_car, powerups, projectiles, particles, current_map, game_info, player_car2=None, game_info2=None):
    border_mask = current_map["border_mask"]
    finish_mask = current_map["finish_mask"]
    finish_pos = current_map["finish_pos"]
    
    # Car vs border - Player 1
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

    # Car vs border - Player 2
    if player_car2 and player_car2.collide(border_mask) != None:
        poi = player_car2.collide(border_mask)
        if poi:
            img_w, img_h = player_car2.img.get_width(), player_car2.img.get_height()
            
            # Spark particles on collision
            for _ in range(5):
                particles.append(Particle(
                    player_car2.x + img_w//2, 
                    player_car2.y + img_h//2,
                    (255, 200, 0),
                    random.uniform(-3, 3),
                    random.uniform(-3, 3),
                    0.5
                ))
            
            # Push through if boost or vulnerable, otherwise bounce
            if player_car2.active_power == PU_BOOST or player_car2.vulnerable:
                offset_x, offset_y = int(player_car2.x), int(player_car2.y)
                overlap_x = poi[0] - offset_x
                overlap_y = poi[1] - offset_y

                center_x, center_y = img_w / 2.0, img_h / 2.0

                vx = center_x - overlap_x
                vy = center_y - overlap_y

                if vx == 0 and vy == 0:
                    rad = math.radians(player_car2.angle)
                    vx = -math.sin(rad)
                    vy = -math.cos(rad)

                mag = math.hypot(vx, vy)
                if mag != 0:
                    vx /= mag
                    vy /= mag

                pushed = False
                for step in range(6):
                    push_amount = 1 + step
                    player_car2.x += vx * push_amount
                    player_car2.y += vy * push_amount
                    if player_car2.collide(border_mask) is None:
                        pushed = True
                        break

                if not pushed:
                    player_car2.x, player_car2.y = player_car2.prev_x, player_car2.prev_y

                player_car2.vel *= 0.5
            else:
                player_car2.bounce()

    # Checkpoint detection - Player 1
    checkpoint_pos = current_map.get("checkpoint", (0, 0))
    checkpoint_radius = 80
    player_dist_to_checkpoint = math.hypot(player_car.x - checkpoint_pos[0], player_car.y - checkpoint_pos[1])
    if player_dist_to_checkpoint < checkpoint_radius:
        game_info.passed_halfway = True
    
    # Checkpoint detection - Player 2
    if player_car2:
        player2_dist_to_checkpoint = math.hypot(player_car2.x - checkpoint_pos[0], player_car2.y - checkpoint_pos[1])
        if player2_dist_to_checkpoint < checkpoint_radius:
            game_info2.passed_halfway = True
    
    # Checkpoint detection - AI
    if not player_car2 and ai_game_info:
        ai_dist_to_checkpoint = math.hypot(computer_car.x - checkpoint_pos[0], computer_car.y - checkpoint_pos[1])
        if ai_dist_to_checkpoint < checkpoint_radius:
            ai_game_info.passed_halfway = True

    # Finish line - AI in single player mode
    if not player_car2:
        computer_finish_point_collide = computer_car.collide(finish_mask, *finish_pos)
        if computer_finish_point_collide != None and ai_game_info.passed_halfway:
            # AI completed a lap
            lap_time = ai_game_info.complete_lap()
            if lap_time == 0:  # Cooldown active, don't process
                pass
            else:
                # Reset checkpoint flag for next lap
                ai_game_info.passed_halfway = False
                
                # Check if AI completed required laps
                if ai_game_info.laps >= game_settings.laps_to_win:
                    return "lose"  # AI finished all laps first
                # Sprint mode: Check for map rotation per lap (only if not finished)
                elif game_settings.race_mode == "sprint" and game_settings.map_rotation == "per_lap":
                    return "change_map"
                # Continuous mode: Check for map rotation per lap (only if not finished)
                elif game_settings.race_mode == "continuous" and game_settings.map_rotation == "per_lap":
                    return "change_map"

    player_finish_point_collide = player_car.collide(finish_mask, *finish_pos)
    if player_finish_point_collide != None:
        if not game_info.passed_halfway:
            # Show wrong way warning
            game_info.wrong_way_warning = time.time()
        else:
            lap_time = game_info.complete_lap()
            if lap_time == 0:  # Cooldown active, don't process
                pass
            else:
                # Reset checkpoint flag for next lap
                game_info.passed_halfway = False
                
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
                
                # Sprint Mode handling
                if game_settings.race_mode == "sprint":
                    if player_car2:
                        # Multiplayer sprint: Player 1 won this lap
                        if game_info.laps >= game_settings.laps_to_win:
                            return "p1_win"  # Player 1 won the most laps
                        else:
                            return "p1_lap_win"  # Player 1 won this lap, reset positions
                    else:
                        # Single-player sprint: Check who won this lap
                        if game_info.laps >= game_settings.laps_to_win:
                            return "win"  # Player won all laps
                        # Check for map rotation per lap (only if not finished)
                        elif game_settings.map_rotation == "per_lap":
                            return "change_map"
                
                # Continuous Mode: Check if all laps completed
                elif game_info.laps >= game_settings.laps_to_win:
                    if player_car2:
                        return "p1_win"  # Player 1 finished all laps first
                    else:
                        return "win"  # Player beat AI
                # Check for map rotation per lap (only if not finished)
                elif game_settings.map_rotation == "per_lap":
                    return "change_map"
    
    # Player 2 finish line
    if player_car2:
        player2_finish_point_collide = player_car2.collide(finish_mask, *finish_pos)
        if player2_finish_point_collide != None:
            if not game_info2.passed_halfway:
                # Show wrong way warning
                game_info2.wrong_way_warning = time.time()
            else:
                lap_time = game_info2.complete_lap()
                if lap_time == 0:  # Cooldown active, don't process
                    pass
                else:
                    # Reset checkpoint flag for next lap
                    game_info2.passed_halfway = False
                    
                    # Celebration particles
                    for _ in range(20):
                        particles.append(Particle(
                            finish_pos[0] + 50,
                            finish_pos[1] + 50,
                            random.choice([(100, 150, 255), (255, 100, 255), (100, 255, 255)]),
                            random.uniform(-5, 5),
                            random.uniform(-5, 5),
                            1.5
                        ))
                    
                    # Sprint Mode: Reset positions after each lap
                    if game_settings.race_mode == "sprint":
                        # Player 2 won this lap
                        if game_info2.laps >= game_settings.laps_to_win:
                            return "p2_win"  # Player 2 won the most laps
                        else:
                            return "p2_lap_win"  # Player 2 won this lap, reset positions
                    
                    # Continuous Mode: Check if all laps completed
                    elif game_info2.laps >= game_settings.laps_to_win:
                        return "p2_win"  # Player 2 finished all laps first
                    # Check for map rotation per lap (only if not finished)
                    elif game_settings.map_rotation == "per_lap":
                        return "change_map"

    # Player 1 picks up powerups
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
    
    # Player 2 picks up powerups
    if player_car2:
        p2x, p2y = int(player_car2.x), int(player_car2.y)
        for i, pu in enumerate(powerups):
            if i in to_remove:
                continue
            pux, puy = pu["pos"]
            if math.hypot(pux - p2x, puy - p2y) < 30:
                player_car2.apply_powerup(pu["type"])
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
        
        # Projectile hits AI
        if p.owner in ["player", "player2"] and not player_car2:
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
        
        # Projectile hits player 2 (from player 1)
        if p.owner == "player" and player_car2:
            if p.rect().colliderect(pygame.Rect(player_car2.x, player_car2.y, 
                                                player_car2.img.get_width(), 
                                                player_car2.img.get_height())):
                # Stun player 2 for 2 seconds
                player_car2.stun(2.0)
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
        
        # Projectile hits player 1 (from player 2)
        if p.owner == "player2" and player_car2:
            if p.rect().colliderect(pygame.Rect(player_car.x, player_car.y, 
                                                player_car.img.get_width(), 
                                                player_car.img.get_height())):
                # Stun player 1 for 2 seconds
                player_car.stun(2.0)
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

def reset_game_state(current_map_key, multiplayer=False):
    global player_car, player_car2, computer_car, powerups, projectiles, particles, game_info, game_info2, ai_game_info, last_spawn
    
    current_map = MAPS[current_map_key]
    PlayerCar.START_POS = current_map["player_start"]
    ComputerCar.START_POS = current_map["ai_start"]
    
    player_car = PlayerCar(4, 4, player_num=1)
    
    # Set initial angle if specified in map
    if "start_angle" in current_map:
        player_car.angle = current_map["start_angle"]
    
    if multiplayer:
        # Player 2 starts at AI position
        player_car2 = PlayerCar(4, 4, player_num=2)
        player_car2.x, player_car2.y = current_map["ai_start"]
        player_car2.START_POS = current_map["ai_start"]
        if "start_angle" in current_map:
            player_car2.angle = current_map["start_angle"]
        game_info2 = GameInfo()
        computer_car = None
    else:
        player_car2 = None
        game_info2 = None
        
        # Set AI speed based on difficulty
        # Player max speed is 4, rotation is 4
        difficulty_speeds = {
            "easy": (2.5, 2.5),    # Slow but not too slow
            "medium": (3.2, 3.5),  # Moderate challenge
            "hard": (4.0, 4.0),    # Same as player
            "extreme": (5.0, 5.5)  # Faster than player
        }
        
        ai_speed, ai_rotation = difficulty_speeds.get(game_settings.ai_difficulty, (2.5, 3))
        
        # Adjust for city circuit (slightly slower)
        if current_map_key == "city":
            ai_speed *= 0.8
        
        computer_car = ComputerCar(ai_speed, ai_rotation, current_map["path"])
        computer_car.x, computer_car.y = current_map["ai_start"]
        computer_car.START_POS = current_map["ai_start"]
        if "start_angle" in current_map:
            computer_car.angle = current_map["start_angle"]
        ai_game_info = GameInfo()  # Track AI laps
    
    game_info = GameInfo()
    # Only spawn powerups if enabled
    if game_settings.powerups_enabled:
        powerups = spawn_powerups(4, current_map["track_mask"], current_map["border_mask"])
    else:
        powerups = []
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
is_multiplayer = False
player_car2 = None
game_info2 = None
ai_game_info = None
reset_game_state(current_map_key, is_multiplayer)
images = get_map_images(current_map_key)

state = 'menu'
modal_result = None
countdown_start = 0
countdown_number = 0
selected_difficulty = None
player_name = ""
player2_name = ""
name_entry_stage = 1  # 1 for first player, 2 for second player
leaderboard_mode = "single_player"
leaderboard_difficulty = "easy"  # For single player difficulty filter
update_window_title('menu')

# Add help state to window title updater
def update_window_title_extended(state, current_map=None, lap=None):
    if state == 'help':
        pygame.display.set_caption("🏎️ Ultimate Racing Championship - Game Guide")
    else:
        update_window_title(state, current_map, lap)

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
                if hover_states[0]:  # Single Player
                    state = 'difficulty_select'
                    pygame.display.set_caption("🏎️ Ultimate Racing Championship - Select Difficulty")
                elif hover_states[1]:  # Multiplayer
                    is_multiplayer = True
                    state = 'map_select'
                    update_window_title('map_select')
                elif hover_states[2]:  # Leaderboard
                    state = 'leaderboard'
                    leaderboard_mode = 'single_player'
                    leaderboard_difficulty = 'easy'
                    pygame.display.set_caption("🏎️ Ultimate Racing Championship - Leaderboard")
                elif hover_states[3]:  # Options
                    state = 'options'
                    update_window_title('options')
                elif hover_states[4]:  # Quit
                    run = False
                    break
        
        pygame.display.update()
        continue

    # Help state
    if state == 'help':
        back_hover = draw_help_screen(WIN, images)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_hover:
                    state = 'options'
                    update_window_title('options')
        
        pygame.display.update()
        continue

    # Options state
    if state == 'options':
        laps_hover, race_mode_hover, rotation_hover, powerups_hover, hud_hover, help_hover, back_hover = draw_options_menu(WIN, images, game_settings)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            # Handle keyboard input for lap number
            if event.type == pygame.KEYDOWN and game_settings.editing_laps:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    game_settings.stop_editing_laps()
                elif event.key == pygame.K_BACKSPACE:
                    game_settings.backspace()
                elif event.key == pygame.K_ESCAPE:
                    game_settings.editing_laps = False
                    game_settings.laps_input = str(game_settings.laps_to_win)
                elif event.unicode.isdigit():
                    game_settings.add_digit(event.unicode)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if laps_hover:
                    if not game_settings.editing_laps:
                        game_settings.start_editing_laps()
                    else:
                        game_settings.stop_editing_laps()
                elif race_mode_hover:
                    game_settings.cycle_race_mode()
                elif rotation_hover and game_settings.race_mode != "continuous":
                    # Only allow clicking if not in continuous mode
                    game_settings.cycle_rotation()
                elif powerups_hover:
                    game_settings.toggle_powerups()
                elif hud_hover:
                    game_settings.toggle_hud()
                elif help_hover:
                    state = 'help'
                    pygame.display.set_caption("🏎️ Ultimate Racing Championship - Game Guide")
                elif back_hover:
                    if game_settings.editing_laps:
                        game_settings.stop_editing_laps()
                    state = 'menu'
                    update_window_title('menu')
        
        pygame.display.update()
        continue

    # Difficulty selection state
    if state == 'difficulty_select':
        hover_states, back_hover = draw_difficulty_selection(WIN, images)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_hover:
                    state = 'menu'
                    update_window_title('menu')
                else:
                    for is_hover, difficulty in hover_states:
                        if is_hover:
                            game_settings.ai_difficulty = difficulty
                            is_multiplayer = False
                            state = 'map_select'
                            update_window_title('map_select')
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
                    # Go back to appropriate screen
                    if is_multiplayer:
                        state = 'menu'
                        update_window_title('menu')
                    else:
                        state = 'difficulty_select'
                        pygame.display.set_caption("🏎️ Ultimate Racing Championship - Select Difficulty")
                else:
                    for is_hover, map_key in hover_states:
                        if is_hover:
                            current_map_key = map_key
                            reset_game_state(current_map_key, is_multiplayer)
                            images = get_map_images(current_map_key)
                            countdown_start = time.time()
                            countdown_number = COUNTDOWN_SECONDS
                            state = 'countdown'
                            update_window_title('countdown')
                            break
        
        pygame.display.update()
        continue

    # Leaderboard state
    if state == 'leaderboard':
        toggle_hover, back_hover, difficulty_tabs = draw_leaderboard(WIN, images, leaderboard_mode, leaderboard_difficulty)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if toggle_hover:
                    leaderboard_mode = "multiplayer" if leaderboard_mode == "single_player" else "single_player"
                elif back_hover:
                    state = 'menu'
                    update_window_title('menu')
                else:
                    # Check difficulty tab clicks
                    for is_hover, diff in difficulty_tabs:
                        if is_hover:
                            leaderboard_difficulty = diff
                            break
        
        pygame.display.update()
        continue
    
    # Name entry state
    if state == 'name_entry':
        # Determine prompt based on stage and mode
        if is_multiplayer:
            if name_entry_stage == 1:
                if modal_result == "p1_win":
                    prompt = "PLAYER 1 (WINNER) - ENTER NAME"
                else:
                    prompt = "PLAYER 2 (WINNER) - ENTER NAME"
                current_name = player_name
            else:
                if modal_result == "p1_win":
                    prompt = "PLAYER 2 - ENTER NAME"
                else:
                    prompt = "PLAYER 1 - ENTER NAME"
                current_name = player2_name
        else:
            prompt = "ENTER YOUR NAME"
            current_name = player_name
        
        draw_name_entry(WIN, images, current_name, prompt)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Check if name is entered
                    if is_multiplayer and name_entry_stage == 1:
                        current_name_check = player_name
                    elif is_multiplayer and name_entry_stage == 2:
                        current_name_check = player2_name
                    else:
                        current_name_check = player_name
                    
                    if current_name_check:
                        if is_multiplayer and name_entry_stage == 1:
                            # Move to second player name entry
                            name_entry_stage = 2
                        else:
                            # Save to leaderboard
                            if modal_result in ("win", "p1_win"):
                                winner_time = game_info.get_level_time()
                                if is_multiplayer:
                                    add_multiplayer_record(player_name, player2_name, winner_time, MAPS[current_map_key]["name"], game_settings.laps_to_win)
                                else:
                                    add_single_player_record(player_name, winner_time, MAPS[current_map_key]["name"], game_settings.ai_difficulty, game_settings.laps_to_win)
                            elif modal_result == "p2_win":
                                winner_time = game_info2.get_level_time()
                                add_multiplayer_record(player2_name, player_name, winner_time, MAPS[current_map_key]["name"], game_settings.laps_to_win)
                            
                            player_name = ""
                            player2_name = ""
                            name_entry_stage = 1
                            state = 'menu'
                            update_window_title('menu')
                elif event.key == pygame.K_BACKSPACE:
                    if is_multiplayer and name_entry_stage == 1:
                        player_name = player_name[:-1]
                    elif is_multiplayer and name_entry_stage == 2:
                        player2_name = player2_name[:-1]
                    else:
                        player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    player_name = ""
                    player2_name = ""
                    name_entry_stage = 1
                    state = 'menu'
                    update_window_title('menu')
                elif event.unicode.isalnum() or event.unicode == " ":
                    if is_multiplayer and name_entry_stage == 1:
                        if len(player_name) < 10:
                            player_name += event.unicode.upper()
                    elif is_multiplayer and name_entry_stage == 2:
                        if len(player2_name) < 10:
                            player2_name += event.unicode.upper()
                    else:
                        if len(player_name) < 10:
                            player_name += event.unicode.upper()
        
        pygame.display.update()
        continue

    # Countdown state
    if state == 'countdown':
        draw(WIN, images, player_car, computer_car, game_info, powerups, projectiles, particles, MAPS[current_map_key], player_car2, game_info2, ai_game_info)
        
        elapsed = time.time() - countdown_start
        sec = COUNTDOWN_SECONDS - int(elapsed)
        if sec <= 0:
            state = 'playing'
            game_info.start_level()
            if game_info2:
                game_info2.start_level()
            elif ai_game_info:
                ai_game_info.start_level()
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
        if player_car2:
            player_car2.update_power_state()

        # Periodic powerup spawn (only if enabled)
        if game_settings.powerups_enabled and time.time() - last_spawn > SPAWN_INTERVAL:
            powerups.extend(spawn_powerups(1, MAPS[current_map_key]["track_mask"], 
                                          MAPS[current_map_key]["border_mask"]))
            last_spawn = time.time()

        # Update particles
        particles = [p for p in particles if p.update(dt)]

        draw(WIN, images, player_car, computer_car, game_info, powerups, projectiles, particles, MAPS[current_map_key], player_car2, game_info2, ai_game_info)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                # Player 1 shoot (Space)
                if event.key == pygame.K_SPACE and player_car.ammo > 0:
                    rad = math.radians(player_car.angle)
                    front_x = player_car.x - math.sin(rad) * (player_car.img.get_height()//2)
                    front_y = player_car.y - math.cos(rad) * (player_car.img.get_height()//2)
                    proj = Projectile(front_x, front_y, player_car.angle, owner="player")
                    projectiles.append(proj)
                    player_car.ammo -= 1
                # Player 2 shoot ([)
                elif event.key == pygame.K_LEFTBRACKET and player_car2 and player_car2.ammo > 0:
                    rad = math.radians(player_car2.angle)
                    front_x = player_car2.x - math.sin(rad) * (player_car2.img.get_height()//2)
                    front_y = player_car2.y - math.cos(rad) * (player_car2.img.get_height()//2)
                    proj = Projectile(front_x, front_y, player_car2.angle, owner="player2")
                    projectiles.append(proj)
                    player_car2.ammo -= 1
                elif event.key == pygame.K_g:
                    game_settings.toggle_hud()
                elif event.key == pygame.K_ESCAPE:
                    state = 'menu'
                    update_window_title('menu')

        move_player(player_car, player_car2)
        if computer_car:
            computer_car.move()

        result = handle_collision(player_car, computer_car, powerups, projectiles, particles, 
                                 MAPS[current_map_key], game_info, player_car2, game_info2)
        
        if result in ("p1_lap_win", "p2_lap_win"):
            # Sprint Mode: Player won this lap, reset positions
            player_car.x, player_car.y = MAPS[current_map_key]["player_start"]
            player_car.angle = MAPS[current_map_key].get("start_angle", 0)
            player_car.vel = 0
            
            if player_car2:
                player_car2.x, player_car2.y = MAPS[current_map_key]["ai_start"]
                player_car2.angle = MAPS[current_map_key].get("start_angle", 0)
                player_car2.vel = 0
            
            # Brief countdown before next lap
            countdown_start = time.time()
            countdown_number = 2  # 2 second countdown
            state = 'countdown'
            update_window_title('countdown')
        
        elif result == "change_map":
            # Random map rotation per lap
            available_maps = list(MAPS.keys())
            current_map_key = random.choice(available_maps)
            reset_game_state(current_map_key, is_multiplayer)
            images = get_map_images(current_map_key)
            countdown_start = time.time()
            countdown_number = COUNTDOWN_SECONDS
            state = 'countdown'
            update_window_title('countdown')
        
        elif result in ("win", "lose", "p1_win", "p2_win"):
            # Freeze all timers when race ends
            game_info.freeze_time()
            if game_info2:
                game_info2.freeze_time()
            if ai_game_info:
                ai_game_info.freeze_time()
            
            modal_result = result
            state = 'modal'
            update_window_title('modal')
        
        pygame.display.update()
        continue

    # Modal state
    if state == 'modal':
        winner_time = None
        winner_name = None
        
        if modal_result == 'p1_win':
            msg = "🏆 PLAYER 1 WINS! 🏆"
            winner_time = game_info.get_level_time()
            winner_name = "Player 1"
        elif modal_result == 'p2_win':
            msg = "🏆 PLAYER 2 WINS! 🏆"
            winner_time = game_info2.get_level_time()
            winner_name = "Player 2"
        elif modal_result == 'win':
            msg = "🏆 YOU WIN! 🏆"
            winner_time = game_info.get_level_time()
            winner_name = "Your"
        else:
            msg = "💥 YOU LOSE! 💥"
            winner_time = ai_game_info.get_level_time() if ai_game_info else None
            winner_name = "AI"
        
        draw(WIN, images, player_car, computer_car, game_info, powerups, projectiles, particles, MAPS[current_map_key], player_car2, game_info2, ai_game_info)
        
        restart_hover, quit_hover = draw_modal(WIN, msg, winner_time, None, winner_name, None)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_hover:
                    reset_game_state(current_map_key, is_multiplayer)
                    images = get_map_images(current_map_key)
                    countdown_start = time.time()
                    countdown_number = COUNTDOWN_SECONDS
                    state = 'countdown'
                    update_window_title('countdown')
                elif quit_hover:
                    # If player won, go to name entry for leaderboard
                    if modal_result in ("win", "p1_win", "p2_win"):
                        state = 'name_entry'
                        player_name = ""
                        player2_name = ""
                        name_entry_stage = 1
                        pygame.display.set_caption("🏎️ Ultimate Racing Championship - Enter Name")
                    else:
                        state = 'menu'
                        update_window_title('menu')

        pygame.display.update()
        continue

pygame.quit()
