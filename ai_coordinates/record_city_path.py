import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Helper function
def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)

# Load the city track images (NO SCALING - match actual game)
try:
    city_grass = pygame.image.load('imgs/city-grass.png')
    city_track = pygame.image.load('imgs/city-track.png')
    city_border = pygame.image.load('imgs/city-border.png')
    city_finish = pygame.image.load('imgs/city-finish.png')
    car_img = scale_image(pygame.image.load('imgs/redbull.png'), 0.08)
except:
    print("Error: Could not load city track images!")
    sys.exit(1)

# Window setup
WIDTH, HEIGHT = city_track.get_width(), city_track.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🏎️ City Circuit - Path Recording Tool")

# Font
FONT = pygame.font.SysFont("arial", 16)
TITLE_FONT = pygame.font.SysFont("arial", 24, bold=True)

# Starting position and finish line
START_POS = (430, 75)
FINISH_POS = (510, 60)
START_ANGLE = 90

# Path recording
path_points = []
recording = False
test_mode = False

# Test car
class TestCar:
    def __init__(self):
        self.x, self.y = START_POS
        self.angle = START_ANGLE
        self.current_point = 0
        self.img = car_img
        
    def reset(self):
        self.x, self.y = START_POS
        self.angle = START_ANGLE
        self.current_point = 0
    
    def calculate_angle(self, target_x, target_y):
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
        
        rotation_vel = 3
        if difference_in_angle > 0:
            self.angle -= min(rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(rotation_vel, abs(difference_in_angle))
    
    def move_to_target(self, target_x, target_y):
        self.calculate_angle(target_x, target_y)
        
        # Move towards target
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * 3
        horizontal = math.sin(radians) * 3
        
        self.y -= vertical
        self.x -= horizontal
        
        # Check if reached target
        dist = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
        return dist < 20
    
    def update(self, path):
        if not path or self.current_point >= len(path):
            return False
        
        target_x, target_y = path[self.current_point]
        if self.move_to_target(target_x, target_y):
            self.current_point += 1
            if self.current_point >= len(path):
                return True  # Completed
        return False
    
    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

test_car = TestCar()

def draw_window():
    # Draw track layers
    WIN.blit(city_grass, (0, 0))
    WIN.blit(city_track, (0, 0))
    
    # Draw finish line
    WIN.blit(city_finish, FINISH_POS)
    
    WIN.blit(city_border, (0, 0))
    
    # Draw recorded path
    if len(path_points) > 1:
        pygame.draw.lines(WIN, (255, 0, 0), False, path_points, 3)
    
    # Draw path points
    for i, point in enumerate(path_points):
        pygame.draw.circle(WIN, (255, 215, 0), point, 5)
        if i % 5 == 0:  # Show index every 5 points
            label = FONT.render(str(i), True, (255, 255, 255))
            WIN.blit(label, (point[0] + 8, point[1] - 8))
    
    # Draw starting position marker
    pygame.draw.circle(WIN, (0, 255, 0), START_POS, 15, 3)
    start_label = FONT.render("START", True, (0, 255, 0))
    WIN.blit(start_label, (START_POS[0] - 20, START_POS[1] - 30))
    
    # Draw test car
    if test_mode and path_points:
        test_car.draw(WIN)
    
    # Draw cursor position
    mx, my = pygame.mouse.get_pos()
    cursor_text = FONT.render(f"Position: ({mx}, {my})", True, (255, 255, 255))
    WIN.blit(cursor_text, (10, 10))
    
    # Draw instructions
    instructions = [
        "INSTRUCTIONS:",
        "CLICK - Add waypoint",
        "SPACE - Toggle recording mode",
        "T - Test path (watch car follow)",
        "R - Reset test car",
        "BACKSPACE - Remove last point",
        "ENTER - Save path and exit",
        "ESC - Exit without saving",
        "",
        f"Recording: {'ON' if recording else 'OFF'}",
        f"Test Mode: {'ON' if test_mode else 'OFF'}",
        f"Points: {len(path_points)}",
        f"Car at point: {test_car.current_point}/{len(path_points)}" if test_mode else ""
    ]
    
    y_offset = 40
    for line in instructions:
        if not line:
            y_offset += 10
            continue
        color = (0, 255, 0) if "Recording: ON" in line or "Test Mode: ON" in line else (255, 255, 255)
        text = FONT.render(line, True, color)
        WIN.blit(text, (10, y_offset))
        y_offset += 22
    
    pygame.display.update()

def save_path():
    if len(path_points) < 3:
        print("Need at least 3 points to save a path!")
        return False
    
    print("\n" + "="*60)
    print("CITY CIRCUIT PATH - Copy this into your main.py:")
    print("="*60)
    print("CITY_PATH = [", end="")
    
    for i, point in enumerate(path_points):
        if i % 3 == 0:
            print("\n             ", end="")
        print(f"{point}", end="")
        if i < len(path_points) - 1:
            print(", ", end="")
    
    print("]")
    print("="*60)
    print(f"\nTotal waypoints: {len(path_points)}")
    print("Path saved! Replace CITY_PATH in main.py with the above.")
    return True

# Main loop
run = True
clock = pygame.time.Clock()

print("="*60)
print("City Circuit Path Recording Tool")
print("="*60)
print("Click on the track to add waypoints for the AI to follow.")
print("Start at the AI starting position (430, 75) - marked with green circle")
print("Follow the track and create a complete lap.")
print("Press T to test the path and watch the car follow it!")
print("="*60)

while run:
    clock.tick(60)
    
    # Update test car if in test mode
    if test_mode and path_points:
        completed = test_car.update(path_points)
        if completed:
            print("Test completed! Car reached all waypoints.")
            test_mode = False
            test_car.reset()
    
    draw_window()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("Exiting without saving...")
                run = False
                
            elif event.key == pygame.K_RETURN:
                if save_path():
                    run = False
                    
            elif event.key == pygame.K_SPACE:
                recording = not recording
                print(f"Recording mode: {'ON' if recording else 'OFF'}")
                
            elif event.key == pygame.K_t:
                if path_points:
                    test_mode = not test_mode
                    if test_mode:
                        test_car.reset()
                        print("Test mode ON - Watch the car follow your path!")
                    else:
                        print("Test mode OFF")
                else:
                    print("Add some waypoints first!")
                    
            elif event.key == pygame.K_r:
                test_car.reset()
                print("Test car reset to starting position")
                
            elif event.key == pygame.K_BACKSPACE:
                if path_points:
                    removed = path_points.pop()
                    print(f"Removed point: {removed} (Total: {len(path_points)})")
                    test_car.reset()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not test_mode:  # Left click (not in test mode)
                pos = pygame.mouse.get_pos()
                path_points.append(pos)
                print(f"Added point {len(path_points)}: {pos}")

pygame.quit()
print("\nPath recording tool closed.")
