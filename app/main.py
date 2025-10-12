import pygame
import time
import math
import random
from utils import blit_text_center, scale_image, blit_rotate_center
pygame.font.init()

GRASS = scale_image(pygame.image.load('imgs/terrain-1.png'), 2.3) 
TRACK = scale_image(pygame.image.load('imgs/track.png'), 1)
TRACK_BORDER = scale_image(pygame.image.load('imgs/track-border.png'), 1)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
# mask for the track surface (road area). We use this to ensure power-ups spawn on the road
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

# Create window using track size, then set caption via pygame.display
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game!")

FPS = 60
PATH = [(182, 115), (67, 153), (69, 532), (351, 803), (441, 701), (478, 565), (624, 563), (687, 790), (819, 719), (804, 444), (685, 408), (490, 389), (517, 312), (777, 278), (798, 101), (615, 80), (349, 94), (299, 421), (199, 391), (205, 193)]

MAIN_FONT = pygame.font.SysFont("poppins", 44)
SMALL_FONT = pygame.font.SysFont("poppins", 20)

# Power-up types/colors
PU_BOOST = "boost"
PU_VULN = "vulnerability"
PU_WEAPON = "weapon"
PU_COLORS = {PU_BOOST: (255, 215, 0), PU_VULN: (200, 0, 200), PU_WEAPON: (0, 200, 0)}
POWERUP_DURATION = 5.0  # seconds

class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0
    
    def game_finished(self):
        return self.level > self.LEVELS
    
    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)

class AbstractCar:

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.original_max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        # keep previous position to revert when passing into walls while vulnerable
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
       
        # store previous position before moving
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
        self.ammo = 0  # weapon ammo

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
            # give 1 ammo; weapon does not auto-expire but ammo can be limited
            self.ammo += 1
            # small ephemeral UI indicator
            self.active_power = PU_WEAPON
            self.power_end_time = now + POWERUP_DURATION

    def update_power_state(self):
        if self.active_power and time.time() > self.power_end_time:
            # reset effects
            if self.active_power == PU_BOOST:
                self.max_vel = self.original_max_vel
            if self.active_power == PU_VULN:
                self.vulnerable = False
            # for weapon we don't remove ammo, just clear indicator
            self.active_power = None

class  ComputerCar(AbstractCar):
    IMG = BLUE_CAR
    START_POS = (170, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel
        self.acceleration = 0.4


    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (0,0,255), point, 5)

    def draw(self, win):
        super().draw(win)
        #self.draw_points(win)
    
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
        if self.current_point >= len(self.path):
            return
        
        self.calculate_angle()
        self.update_path_point()
        super().move()

# New: projectile class for weapons
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
        pygame.draw.circle(win, (255, 50, 50), (int(self.x), int(self.y)), self.RADIUS)

    def rect(self):
        return pygame.Rect(self.x - self.RADIUS, self.y - self.RADIUS, self.RADIUS*2, self.RADIUS*2)

def spawn_powerups(count=3):
    # spawn pickups only on the track surface (not on grass/outside nor on the border)
    powerups = []
    margin = 50
    attempts = 0
    max_attempts = 2000
    while len(powerups) < count and attempts < max_attempts:
        pu_type = random.choice([PU_BOOST, PU_VULN, PU_WEAPON])
        x = random.randint(margin, WIDTH - margin)
        y = random.randint(margin, HEIGHT - margin)
        # Ensure coordinates are on the track mask and not on the track border
        try:
            on_track = TRACK_MASK.get_at((x, y))
        except IndexError:
            on_track = 0
        try:
            on_border = TRACK_BORDER_MASK.get_at((x, y))
        except IndexError:
            on_border = 0

        if on_track and not on_border:
            # animation state: angle (deg) and phase offset for pulsing
            powerups.append({"type": pu_type, "pos": (x, y), "angle": random.uniform(0, 360), "rot_speed": random.uniform(-90, 90), "pulse_offset": random.uniform(0, math.pi * 2)})

        attempts += 1

    # If we couldn't find enough valid locations after many attempts, fall back to best-effort random positions
    while len(powerups) < count:
        pu_type = random.choice([PU_BOOST, PU_VULN, PU_WEAPON])
        x = random.randint(margin, WIDTH - margin)
        y = random.randint(margin, HEIGHT - margin)
        powerups.append({"type": pu_type, "pos": (x, y), "angle": random.uniform(0, 360), "rot_speed": random.uniform(-90, 90), "pulse_offset": random.uniform(0, math.pi * 2)})

    return powerups

def draw (win, images, player_car, computer_car, game_info, powerups, projectiles):
    for img, pos in images:
        win.blit(img, pos)

    # draw powerups
    # animated powerups
    # use a consistent per-frame delta to update animations for smoothness
    dt = 1.0 / FPS
    for pu in powerups:
        img = None
        if pu["type"] == PU_BOOST:
            img = POWERUP_BOOST_IMG
        elif pu["type"] == PU_VULN:
            img = POWERUP_VULN_IMG
        elif pu["type"] == PU_WEAPON:
            img = POWERUP_WEAPON_IMG

        # update animation state
        pu_angle = pu.get("angle", 0) + pu.get("rot_speed", 0) * dt
        pu["angle"] = pu_angle % 360
        pulse_phase = pu.get("pulse_offset", 0) + dt * 2.0
        pu["pulse_offset"] = pulse_phase

        if img:
            # pulse scale between 0.85 and 1.15
            scale = 1.0 + 0.15 * math.sin(pulse_phase)
            rot_img = pygame.transform.rotozoom(img, pu["angle"], scale)
            rect = rot_img.get_rect(center=pu["pos"])
            win.blit(rot_img, rect.topleft)
        else:
            color = PU_COLORS.get(pu["type"], (255,255,255))
            pygame.draw.circle(win, color, pu["pos"], 12)
            pygame.draw.circle(win, (0,0,0), pu["pos"], 12, 2)

    # draw projectiles
    for p in projectiles:
        # if we have an image for projectile, draw it rotated
        if PROJECTILE_IMG:
            img = pygame.transform.rotate(PROJECTILE_IMG, p.angle)
            rect = img.get_rect(center=(int(p.x), int(p.y)))
            win.blit(img, rect.topleft)
        else:
            p.draw(win)

    level_text = MAIN_FONT.render(f"Level: {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    vel_text = MAIN_FONT.render(f"Speed: {round(player_car.vel, 1 )}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    # ammo / active power info
    ammo_text = SMALL_FONT.render(f"Ammo: {player_car.ammo}", 1, (255,255,255))
    win.blit(ammo_text, (WIDTH - 120, 10))
    if player_car.active_power:
        ap_text = SMALL_FONT.render(f"Power: {player_car.active_power}", 1, (255,255,255))
        win.blit(ap_text, (WIDTH - 220, 10))

    player_car.draw(win)
    computer_car.draw(win)


def draw_button(win, rect, text, font, base_color, hover_color):
    mx, my = pygame.mouse.get_pos()
    x, y, w, h = rect
    is_hover = x <= mx <= x + w and y <= my <= y + h
    color = hover_color if is_hover else base_color
    pygame.draw.rect(win, color, rect, border_radius=8)
    txt = font.render(text, True, (0, 0, 0))
    tw, th = txt.get_width(), txt.get_height()
    win.blit(txt, (x + (w - tw) // 2, y + (h - th) // 2))


def draw_main_menu(win):
    # draw background images first then apply translucent overlay
    for img, pos in images:
        win.blit(img, pos)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))

    title = MAIN_FONT.render("Car Racing Game", True, (255, 255, 255))
    win.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 4))

    btn_w, btn_h = 220, 70
    btn_x = (WIDTH - btn_w) // 2
    btn_y = HEIGHT // 2
    draw_button(win, (btn_x, btn_y, btn_w, btn_h), "Play", MAIN_FONT, (255, 200, 0), (255, 230, 120))


def draw_modal(win, message):
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    win.blit(overlay, (0, 0))

    box_w, box_h = 500, 240
    box_x = (WIDTH - box_w) // 2
    box_y = (HEIGHT - box_h) // 2
    pygame.draw.rect(win, (240, 240, 240), (box_x, box_y, box_w, box_h), border_radius=10)
    pygame.draw.rect(win, (0, 0, 0), (box_x, box_y, box_w, box_h), 2, border_radius=10)

    msg = MAIN_FONT.render(message, True, (20, 20, 20))
    win.blit(msg, (box_x + (box_w - msg.get_width()) // 2, box_y + 30))

    # buttons: Restart and Quit
    btn_w, btn_h = 160, 56
    spacing = 30
    total_w = btn_w * 2 + spacing
    start_x = box_x + (box_w - total_w) // 2
    btn_y = box_y + box_h - btn_h - 30

    draw_button(win, (start_x, btn_y, btn_w, btn_h), "Restart", SMALL_FONT, (100, 220, 120), (140, 255, 170))
    draw_button(win, (start_x + btn_w + spacing, btn_y, btn_w, btn_h), "Quit", SMALL_FONT, (220, 100, 100), (255, 140, 140))

def move_player(player_car):
    keys = pygame.key.get_pressed()
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

def handle_collision(player_car, computer_car, powerups, projectiles):
    # car vs border
    if player_car.collide(TRACK_BORDER_MASK) != None:
        # When boosted or vulnerable, disable bounce behaviour but also prevent
        # crossing the border. Instead of hard-reverting (which can stick the
        # player), push the car out along the vector from the overlap point to
        # the car center so it can slide along the wall. If not boosted/
        # vulnerable, perform normal bounce.
        if player_car.active_power == PU_BOOST or player_car.vulnerable:
            poi = player_car.collide(TRACK_BORDER_MASK)
            if poi:
                # compute offset of car top-left relative to mask
                offset_x, offset_y = int(player_car.x), int(player_car.y)
                # overlap point in car-local coordinates
                overlap_x = poi[0] - offset_x
                overlap_y = poi[1] - offset_y

                img_w, img_h = player_car.img.get_width(), player_car.img.get_height()
                center_x, center_y = img_w / 2.0, img_h / 2.0

                # vector from overlap -> car center (push direction)
                vx = center_x - overlap_x
                vy = center_y - overlap_y

                # fallback to movement direction if vector is zero
                if vx == 0 and vy == 0:
                    rad = math.radians(player_car.angle)
                    vx = -math.sin(rad)
                    vy = -math.cos(rad)

                # normalize
                mag = math.hypot(vx, vy)
                if mag != 0:
                    vx /= mag
                    vy /= mag

                # try nudging the car out stepwise until no overlap (safety cap)
                pushed = False
                for step in range(6):
                    push_amount = 1 + step  # increase push slightly each attempt
                    player_car.x += vx * push_amount
                    player_car.y += vy * push_amount
                    if player_car.collide(TRACK_BORDER_MASK) is None:
                        pushed = True
                        break

                if not pushed:
                    # last resort: revert to previous safe position
                    player_car.x, player_car.y = player_car.prev_x, player_car.prev_y

                # reduce forward velocity so player doesn't blast through next frame
                player_car.vel *= 0.5
        else:
            player_car.bounce()

    # finish line
    computer_finish_point_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_point_collide != None:
        # computer reached finish -> player loses
        return "lose"

    player_finish_point_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_point_collide != None:
        if player_finish_point_collide[1] == 0:
            player_car.bounce()
        else:
            # player reached finish -> player wins
            return "win"

    # player picks up powerups
    px, py = int(player_car.x), int(player_car.y)
    to_remove = []
    for i, pu in enumerate(powerups):
        pux, puy = pu["pos"]
        if math.hypot(pux - px, puy - py) < 30:
            player_car.apply_powerup(pu["type"])
            to_remove.append(i)
    # remove picked powerups
    for i in sorted(to_remove, reverse=True):
        powerups.pop(i)

    # update projectiles and check collisions
    for p in list(projectiles):
        p.move()
        # kill if hit border or offscreen
        if p.x < 0 or p.x > WIDTH or p.y < 0 or p.y > HEIGHT:
            projectiles.remove(p)
            continue
        # projectile hits computer car
        if p.owner == "player":
            # simple rect collision then mask overlap for better accuracy
            if p.rect().colliderect(pygame.Rect(computer_car.x, computer_car.y, computer_car.img.get_width(), computer_car.img.get_height())):
                car_mask = pygame.mask.from_surface(computer_car.img)
                offset = (int(computer_car.x - p.x + p.RADIUS), int(computer_car.y - p.y + p.RADIUS))
                # approximate: if rect collision already, register hit
                computer_car.reset()
                projectiles.remove(p)
                print("Computer hit by projectile!")
                continue
        elif p.owner == "computer":
            if p.rect().colliderect(pygame.Rect(player_car.x, player_car.y, player_car.img.get_width(), player_car.img.get_height())):
                # if player vulnerable, stronger effect
                if player_car.vulnerable:
                    player_car.reset()
                else:
                    player_car.bounce()
                projectiles.remove(p)
                continue
    return None

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0,0)), (TRACK, (0,0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0,0))]


# a small helper to reset game state
def reset_game_state():
    global player_car, computer_car, powerups, projectiles, last_spawn, game_info
    player_car = PlayerCar(4, 4)
    computer_car = ComputerCar(4, 4, PATH)
    game_info = GameInfo()
    powerups = spawn_powerups(4)
    projectiles = []
    last_spawn = time.time()


# initialize state
reset_game_state()
SPAWN_INTERVAL = 12  # seconds - spawn a new pickup periodically

# states: 'menu', 'playing', 'modal' (end)
state = 'menu'
modal_result = None

while run:
    clock.tick(FPS)

    # menu state: show Play button until clicked
    if state == 'menu':
        draw_main_menu(WIN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                btn_w, btn_h = 220, 70
                btn_x = (WIDTH - btn_w) // 2
                btn_y = HEIGHT // 2
                if btn_x <= mx <= btn_x + btn_w and btn_y <= my <= btn_y + btn_h:
                    state = 'playing'
                    game_info.start_level()
        pygame.display.update()
        continue

    # playing state: normal game loop
    if state == 'playing':
        # update player's power state timers
        player_car.update_power_state()

        # periodic spawn
        if time.time() - last_spawn > SPAWN_INTERVAL:
            powerups.extend(spawn_powerups(1))
            last_spawn = time.time()

        draw(WIN, images, player_car, computer_car, game_info, powerups, projectiles)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                # fire weapon if ammo
                if event.key == pygame.K_SPACE and player_car.ammo > 0:
                    rad = math.radians(player_car.angle)
                    front_x = player_car.x - math.sin(rad) * (player_car.img.get_height()//2)
                    front_y = player_car.y - math.cos(rad) * (player_car.img.get_height()//2)
                    proj = Projectile(front_x, front_y, player_car.angle, owner="player")
                    projectiles.append(proj)
                    player_car.ammo -= 1

        move_player(player_car)
        computer_car.move()

        result = handle_collision(player_car, computer_car, powerups, projectiles)
        if result in ("win", "lose"):
            modal_result = result
            # pause game and show modal
            state = 'modal'
        pygame.display.update()
        continue

    # modal state: show end-of-game dialog with Restart/Quit
    if state == 'modal':
        msg = "You Win!" if modal_result == 'win' else "You Lose!"
        draw(WIN, images, player_car, computer_car, game_info, powerups, projectiles)
        draw_modal(WIN, msg)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                # compute button positions from draw_modal
                box_w, box_h = 500, 240
                box_x = (WIDTH - box_w) // 2
                box_y = (HEIGHT - box_h) // 2
                btn_w, btn_h = 160, 56
                spacing = 30
                total_w = btn_w * 2 + spacing
                start_x = box_x + (box_w - total_w) // 2
                btn_y = box_y + box_h - btn_h - 30

                # Restart
                if start_x <= mx <= start_x + btn_w and btn_y <= my <= btn_y + btn_h:
                    reset_game_state()
                    state = 'playing'
                    game_info.start_level()
                # Quit
                if start_x + btn_w + spacing <= mx <= start_x + btn_w + spacing + btn_w and btn_y <= my <= btn_y + btn_h:
                    run = False
                    break

    pygame.display.update()
    continue

print(computer_car.path)
pygame.quit()
