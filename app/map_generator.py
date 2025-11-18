import pygame
import math

def create_speedway_map():
    """Create a speedway/oval track map"""
    width, height = 900, 900
    
    # Create surfaces
    grass = pygame.Surface((width, height))
    grass.fill((34, 139, 34))  # Forest green
    
    # Add grass texture
    import random
    for _ in range(2000):
        x = random.randint(0, width)
        y = random.randint(0, height)
        shade = random.randint(0, 20)
        color = (max(0, 34 - shade), max(0, 139 - shade), max(0, 34 - shade))
        pygame.draw.circle(grass, color, (x, y), random.randint(1, 3))
    
    # Create track (gray road)
    track = pygame.Surface((width, height), pygame.SRCALPHA)
    track.fill((0, 0, 0, 0))
    
    # Oval track shape
    center_x, center_y = width // 2, height // 2
    outer_width, outer_height = 700, 600
    inner_width, inner_height = 500, 400
    
    # Draw outer oval (road)
    pygame.draw.ellipse(track, (80, 80, 80), 
                       (center_x - outer_width//2, center_y - outer_height//2, 
                        outer_width, outer_height))
    
    # Draw inner oval (cut out center)
    pygame.draw.ellipse(track, (0, 0, 0, 0), 
                       (center_x - inner_width//2, center_y - inner_height//2, 
                        inner_width, inner_height))
    
    # Create track border (red/white barriers)
    border = pygame.Surface((width, height), pygame.SRCALPHA)
    border.fill((0, 0, 0, 0))
    
    # Outer border
    pygame.draw.ellipse(border, (200, 0, 0), 
                       (center_x - outer_width//2 - 10, center_y - outer_height//2 - 10, 
                        outer_width + 20, outer_height + 20), 15)
    
    # Inner border
    pygame.draw.ellipse(border, (200, 0, 0), 
                       (center_x - inner_width//2 - 10, center_y - inner_height//2 - 10, 
                        inner_width + 20, inner_height + 20), 15)
    
    # Add checkered pattern to borders
    for angle in range(0, 360, 20):
        rad = math.radians(angle)
        # Outer checkered
        x1 = center_x + math.cos(rad) * (outer_width//2)
        y1 = center_y + math.sin(rad) * (outer_height//2)
        if angle % 40 == 0:
            pygame.draw.circle(border, (255, 255, 255), (int(x1), int(y1)), 8)
        
        # Inner checkered
        x2 = center_x + math.cos(rad) * (inner_width//2)
        y2 = center_y + math.sin(rad) * (inner_height//2)
        if angle % 40 == 0:
            pygame.draw.circle(border, (255, 255, 255), (int(x2), int(y2)), 8)
    
    # Create finish line
    finish = pygame.Surface((80, 15), pygame.SRCALPHA)
    finish.fill((0, 0, 0, 0))
    
    # Checkered finish
    for i in range(8):
        for j in range(2):
            color = (255, 255, 255) if (i + j) % 2 == 0 else (0, 0, 0)
            pygame.draw.rect(finish, color, (i * 10, j * 7.5, 10, 7.5))
    
    finish_pos = (center_x - 40, center_y - outer_height//2 - 20)
    
    # Save images
    pygame.image.save(grass, 'imgs/speedway-grass.png')
    pygame.image.save(track, 'imgs/speedway-track.png')
    pygame.image.save(border, 'imgs/speedway-border.png')
    pygame.image.save(finish, 'imgs/speedway-finish.png')
    
    # Generate AI path points around the oval
    path = []
    num_points = 20
    mid_width = (outer_width + inner_width) // 4
    mid_height = (outer_height + inner_height) // 4
    
    for i in range(num_points):
        angle = (i / num_points) * 2 * math.pi
        x = center_x + math.cos(angle) * mid_width
        y = center_y + math.sin(angle) * mid_height
        path.append((int(x), int(y)))
    
    print(f"Speedway map created!")
    print(f"Finish position: {finish_pos}")
    print(f"Path points: {path}")
    print(f"Player start: ({center_x - 30}, {center_y - outer_height//2 + 50})")
    print(f"AI start: ({center_x + 30}, {center_y - outer_height//2 + 50})")
    
    return {
        "finish_pos": finish_pos,
        "path": path,
        "player_start": (center_x - 30, center_y - outer_height//2 + 50),
        "ai_start": (center_x + 30, center_y - outer_height//2 + 50)
    }

if __name__ == "__main__":
    pygame.init()
    data = create_speedway_map()
    pygame.quit()
    print("\nMap generation complete!")
