"""
Game Configuration File
Modify these values to customize your racing experience
"""

# === GAME SETTINGS ===
FPS = 60                    # Frames per second (higher = smoother but more CPU intensive)
COUNTDOWN_SECONDS = 3       # Countdown before race starts
SPAWN_INTERVAL = 12         # Seconds between power-up spawns
POWERUP_DURATION = 5.0      # How long power-ups last (seconds)

# === DIFFICULTY SETTINGS ===
PLAYER_MAX_SPEED = 4        # Player car maximum speed
PLAYER_ROTATION_SPEED = 4   # How fast player can turn
AI_MAX_SPEED = 4            # AI car maximum speed
AI_ROTATION_SPEED = 4       # How fast AI can turn
AI_STUN_DURATION = 3.0      # How long AI is stunned when hit (seconds)

# === POWER-UP SETTINGS ===
BOOST_MULTIPLIER = 1.8      # Speed multiplier for boost power-up
WEAPON_AMMO_PER_PICKUP = 1  # Ammo granted per weapon pickup
PROJECTILE_SPEED = 8        # Speed of fired projectiles
POWERUP_SPAWN_COUNT = 4     # Initial number of power-ups on track

# === VISUAL SETTINGS ===
PARTICLE_COUNT_COLLISION = 5    # Particles spawned on wall collision
PARTICLE_COUNT_PICKUP = 10      # Particles spawned on power-up pickup
PARTICLE_COUNT_EXPLOSION = 15   # Particles spawned on projectile hit
PARTICLE_COUNT_FINISH = 20      # Particles spawned on lap completion

# === UI COLORS ===
HUD_PANEL_COLOR = (20, 20, 30, 200)     # HUD background color (RGBA)
HUD_ACCENT_COLOR = (255, 215, 0)        # HUD border/accent color
MENU_OVERLAY_ALPHA = 180                # Menu background transparency (0-255)

# === CONTROLS ===
# You can modify these in the code if you want different key bindings
# Current controls:
# - W/UP: Accelerate
# - S/DOWN: Brake
# - A/LEFT: Turn Left
# - D/RIGHT: Turn Right
# - SPACE: Fire Weapon
# - ESC: Pause/Menu

# === ADVANCED SETTINGS ===
ENABLE_PARTICLES = True     # Set to False to disable particle effects for better performance
DEBUG_MODE = False          # Set to True to show AI path points and collision boxes
