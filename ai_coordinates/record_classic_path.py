"""
Professional AI Path Recorder for Classic Circuit
Records optimal racing line coordinates for AI pathfinding
"""

import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Load the exact same assets as main.py
def scale_image(image, factor):
    size = round(image.get_width() * factor), round(image.get_height() * factor)
    return pygame.transform.scale(image, size)

def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)

# Load Classic Circuit assets (same as main.py)
GRASS = scale_image(pygame.image.load('imgs/terrain-1.png'), 2.3)
TRACK = scale_image(pygame.image.load('imgs/track.png'), 1)
TRACK_BORDER = scale_image(pygame.image.load('imgs/track-border.png'), 1)
FINISH = pygame.image.load('imgs/finish.png')
FINISH_POSITION = (140, 250)
CAR_IMG = scale_image(pygame.image.load('imgs/redbull.png'), 0.08)

# Window setup (exact same dimensions as main.py)
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🏎️ Classic Circuit - AI Path Recorder")

# Fonts
FONT = pygame.font.SysFont("arial", 20, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 16)
TINY_FONT = pygame.font.SysFont("arial", 14)

# Path recording
path_points = []
recording = False
test_mode = False

# Starting position (near finish line)
START_POS = (180, 270)
START_ANGLE = 0

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Test car class
class TestCar:
    def __init__(self):
        self.x, self.y = START_POS
        self.angle = START_ANGLE
        self.current_point = 0
        self.img = CAR_IMG
        
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

def draw_instructions(win):
    """Draw professional instructions overlay"""
    # Semi-transparent panel
    panel = pygame.Surface((WIDTH, 140), pygame.SRCALPHA)
    panel.fill((20, 20, 30, 200))
    win.blit(panel, (0, 0))
    
    # Title
    title = FONT.render("CLASSIC CIRCUIT - AI PATH RECORDER", True, YELLOW)
    win.blit(title, (10, 10))
    
    # Instructions
    instructions = [
        "LEFT CLICK: Add waypoint to path",
        "RIGHT CLICK: Remove last waypoint",
        "SPACE: Toggle recording mode",
        "T: Test path (watch car follow)",
        "R: Reset test car",
        "S: Save path to file",
        "C: Clear all waypoints",
        "ESC: Exit"
    ]
    
    y = 40
    for instruction in instructions:
        text = SMALL_FONT.render(instruction, True, WHITE)
        win.blit(text, (10, y))
        y += 18

def draw_status(win, recording, point_count, test_mode, test_car):
    """Draw status bar at bottom"""
    # Status panel
    panel = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
    panel.fill((20, 20, 30, 200))
    win.blit(panel, (0, HEIGHT - 60))
    
    # Recording status
    status_text = "RECORDING" if recording else "PAUSED"
    status_color = GREEN if recording else RED
    status = FONT.render(f"Status: {status_text}", True, status_color)
    win.blit(status, (10, HEIGHT - 50))
    
    # Point count
    count_text = FONT.render(f"Waypoints: {point_count}", True, YELLOW)
    win.blit(count_text, (200, HEIGHT - 50))
    
    # Test mode status
    if test_mode:
        test_text = FONT.render(f"TEST MODE - Point: {test_car.current_point}/{point_count}", True, GREEN)
        win.blit(test_text, (400, HEIGHT - 50))
    
    # Hint
    hint = TINY_FONT.render("Follow the racing line around the track", True, (200, 200, 200))
    win.blit(hint, (10, HEIGHT - 25))

def draw_path(win, points):
    """Draw the recorded path with professional visualization"""
    if len(points) < 2:
        return
    
    # Draw connecting lines
    for i in range(len(points) - 1):
        pygame.draw.line(win, BLUE, points[i], points[i + 1], 3)
    
    # Draw waypoint markers
    for i, point in enumerate(points):
        # Outer circle
        pygame.draw.circle(win, YELLOW, point, 8)
        # Inner circle
        pygame.draw.circle(win, RED, point, 4)
        
        # Draw waypoint number for first, last, and every 5th point
        if i == 0 or i == len(points) - 1 or i % 5 == 0:
            num_text = TINY_FONT.render(str(i), True, WHITE)
            win.blit(num_text, (point[0] + 10, point[1] - 10))

def save_path(points):
    """Save path to Python file with professional formatting"""
    if len(points) < 3:
        print("❌ Error: Need at least 3 waypoints to save path")
        return False
    
    try:
        with open('classic_path_output.py', 'w') as f:
            f.write('"""\\n')
            f.write('AI Path for Classic Circuit\\n')
            f.write(f'Generated with {len(points)} waypoints\\n')
            f.write('Optimized racing line for AI navigation\\n')
            f.write('"""\\n\\n')
            f.write('# Classic Circuit AI Path\\n')
            f.write('CLASSIC_PATH = [')
            
            # Format points nicely (5 per line)
            for i, point in enumerate(points):
                if i % 5 == 0:
                    f.write('\n    ')
                f.write(f'({point[0]}, {point[1]})')
                if i < len(points) - 1:
                    f.write(', ')
            
            f.write('\n]\n')
        
        print(f"✅ Path saved successfully!")
        print(f"📊 Total waypoints: {len(points)}")
        print(f"📁 File: classic_path_output.py")
        print(f"📋 Copy the CLASSIC_PATH list to main.py")
        return True
    except Exception as e:
        print(f"❌ Error saving path: {e}")
        return False

def main():
    """Main recording loop"""
    global recording, path_points, test_mode, test_car
    
    clock = pygame.time.Clock()
    running = True
    
    print("=" * 60)
    print("🏎️  CLASSIC CIRCUIT - AI PATH RECORDER")
    print("=" * 60)
    print("📍 Click along the optimal racing line")
    print("🎯 Start near the finish line and complete a full lap")
    print("🧪 Press 'T' to test the path with a car")
    print("💾 Press 'S' to save when finished")
    print("=" * 60)
    
    while running:
        clock.tick(60)
        
        # Update test car if in test mode
        if test_mode and path_points:
            completed = test_car.update(path_points)
            if completed:
                print("✅ Test completed! Car reached all waypoints.")
                test_mode = False
                test_car.reset()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_SPACE:
                    recording = not recording
                    status = "RECORDING" if recording else "PAUSED"
                    print(f"🔄 Status: {status}")
                
                elif event.key == pygame.K_t:
                    if path_points:
                        test_mode = not test_mode
                        if test_mode:
                            test_car.reset()
                            print("🧪 Test mode ON - Watch the car follow your path!")
                        else:
                            print("⏸️  Test mode OFF")
                    else:
                        print("⚠️  Add some waypoints first!")
                
                elif event.key == pygame.K_r:
                    test_car.reset()
                    print("🔄 Test car reset to starting position")
                
                elif event.key == pygame.K_s:
                    if save_path(path_points):
                        print("✅ Ready to copy to main.py!")
                
                elif event.key == pygame.K_c:
                    path_points.clear()
                    test_car.reset()
                    print("🗑️  Path cleared")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not test_mode:  # Left click (not in test mode)
                    pos = pygame.mouse.get_pos()
                    path_points.append(pos)
                    print(f"📍 Waypoint {len(path_points)}: {pos}")
                
                elif event.button == 3:  # Right click
                    if path_points:
                        removed = path_points.pop()
                        test_car.reset()
                        print(f"⬅️  Removed waypoint: {removed}")
        
        # Draw everything
        WIN.blit(GRASS, (0, 0))
        WIN.blit(TRACK, (0, 0))
        WIN.blit(FINISH, FINISH_POSITION)
        WIN.blit(TRACK_BORDER, (0, 0))
        
        # Draw path
        draw_path(WIN, path_points)
        
        # Draw starting position marker
        pygame.draw.circle(WIN, GREEN, START_POS, 15, 3)
        start_label = SMALL_FONT.render("START", True, GREEN)
        WIN.blit(start_label, (START_POS[0] - 20, START_POS[1] - 30))
        
        # Draw test car
        if test_mode and path_points:
            test_car.draw(WIN)
        
        # Draw UI
        draw_instructions(WIN)
        draw_status(WIN, recording, len(path_points), test_mode, test_car)
        
        # Draw cursor position
        mx, my = pygame.mouse.get_pos()
        cursor_text = TINY_FONT.render(f"({mx}, {my})", True, YELLOW)
        WIN.blit(cursor_text, (mx + 15, my - 10))
        
        pygame.display.flip()
    
    pygame.quit()
    print("\n" + "=" * 60)
    print("👋 Path recorder closed")
    print("=" * 60)

if __name__ == "__main__":
    main()
