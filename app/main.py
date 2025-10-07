import pygame
import time
import math
from utils import scale_image, blit_rotate_center

GRASS = scale_image(pygame.image.load('imgs/terrain-1.png'), 2.3) 
TRACK = scale_image(pygame.image.load('imgs/track.png'), 1)

TRACK_BORDER = scale_image(pygame.image.load('imgs/track-border.png'), 1)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load('imgs/finish.png')
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (140, 250)

FERARRI = scale_image(pygame.image.load('imgs/fer.png'), 0.12)
BLUE_CAR = scale_image(pygame.image.load('imgs/redbull.png'), 0.08)

# Create window using track size, then set caption via pygame.display
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game!")

FPS = 60
PATH = [(182, 115), (67, 153), (69, 532), (351, 803), (441, 701), (478, 565), (624, 563), (687, 790), (819, 719), (804, 444), (685, 408), (490, 389), (517, 312), (777, 278), (798, 101), (615, 80), (349, 94), (299, 421), (199, 391), (205, 193)]
class AbstractCar:

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
    
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

class PlayerCar(AbstractCar):
    IMG = FERARRI
    START_POS = (205, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 0.5, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move() 

class  ComputerCar(AbstractCar):
    IMG = BLUE_CAR
    START_POS = (170, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

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

def draw (win, images, player_car, computer_car):
    for img, pos in images:
        win.blit(img, pos)
    
    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()

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

def handle_collision(player_car, computer_car):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    computer_finish_point_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_point_collide != None:
        player_car.reset()
        computer_car.reset()
        print("You Lose!")

    player_finish_point_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_point_collide != None:
        if player_finish_point_collide[1] == 0:
            player_car.bounce()
        else:
            player_car.reset()
            computer_car.reset()
            print("You Win!")

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0,0)), (TRACK, (0,0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0,0))]
player_car = PlayerCar(4, 4) 
computer_car = ComputerCar(4, 4, PATH)    

while run:
    clock.tick(FPS)

    pygame.display.update()

    draw(WIN, images, player_car, computer_car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        #if event.type == pygame.MOUSEBUTTONDOWN:
        #    pos = pygame.mouse.get_pos()
        #    computer_car.path.append(pos)

    move_player(player_car)
    computer_car.move()

    handle_collision(player_car, computer_car)


        

print(computer_car.path)
pygame.quit()
 