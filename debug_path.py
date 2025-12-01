import math

path = [(182, 109), (81, 99), (64, 441), (115, 594), (319, 808), 
        (431, 782), (468, 560), (605, 533), (667, 620), (683, 777), 
        (803, 784), (813, 417), (497, 393), (470, 297), (789, 268), 
        (800, 92), (337, 87), (307, 396), (213, 393), (199, 223)]

finish = (140, 250)
ai_start = (170, 200)

print('Distance from each path point to finish line:')
for i, (x, y) in enumerate(path):
    dist = math.sqrt((x-finish[0])**2 + (y-finish[1])**2)
    print(f'Point {i}: ({x:3}, {y:3}) - Distance to finish: {dist:6.1f}')

print(f'\nAI starts at: {ai_start}')
print(f'Finish line at: {finish}')

# Find closest point to AI start
min_dist = float('inf')
closest_idx = 0
for i, (x, y) in enumerate(path):
    dist = math.sqrt((x-ai_start[0])**2 + (y-ai_start[1])**2)
    if dist < min_dist:
        min_dist = dist
        closest_idx = i

print(f'\nClosest path point to AI start: Point {closest_idx} at {path[closest_idx]} (distance: {min_dist:.1f})')
