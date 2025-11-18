# 🏎️ Ultimate Racing Championship

A professional 2D racing game built with Python and Pygame featuring multiple tracks, power-ups, AI opponents, and competitive gameplay.

## ✨ Features

### 🎮 Gameplay
- **Multiple Racing Tracks**: Classic Circuit and Speedway Oval
- **AI Opponent**: Intelligent computer-controlled racer
- **Power-Up System**:
  - ⚡ **Boost**: Temporary speed increase
  - 🛡️ **Vulnerability**: Risk/reward power-up
  - 🎯 **Weapon**: Fire projectiles at opponents
- **Lap System**: Track your best lap times
- **Particle Effects**: Visual feedback for collisions, pickups, and victories

### 🎨 Professional UI
- Modern menu system with smooth animations
- Real-time HUD displaying:
  - Current lap number
  - Lap time and best time
  - Speed indicator
  - Active power-ups and ammo count
- Countdown timer before race start
- Victory/defeat modals with options to restart or continue

### 🎯 Controls
- **W / ↑**: Accelerate
- **S / ↓**: Brake/Reverse
- **A / ←**: Turn Left
- **D / →**: Turn Right
- **SPACE**: Fire Weapon (when ammo available)
- **ESC**: Return to Menu

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Pygame library

### Setup
1. Clone or download this repository
2. Install dependencies:
```bash
pip install pygame
```

3. Run the game:
```bash
python app/main.py
```

## 🗺️ Maps

### Classic Circuit
The original challenging track with tight corners and technical sections.

### Speedway Oval
A high-speed oval track perfect for intense racing action.

### Adding New Maps
To create additional maps, use the map generator:
```bash
python app/map_generator.py
```

Then add the map configuration to `MAPS` dictionary in `main.py`.

## 🎯 Game Mechanics

### Power-Ups
Power-ups spawn randomly on the track and provide temporary advantages:
- **Boost** (Gold): Increases maximum speed by 80% for 5 seconds
- **Vulnerability** (Purple): Makes you vulnerable but allows passing through barriers
- **Weapon** (Green): Grants ammunition to fire projectiles

### Weapons
- Fire projectiles with SPACE when you have ammo
- Hit the AI opponent to stun them for 3 seconds
- Strategic weapon use can turn the tide of a race

### Winning
- Cross the finish line before your opponent
- Complete multiple laps to improve your best time
- Master each track's unique layout

## 🛠️ Technical Details

### Architecture
- **Object-Oriented Design**: Separate classes for cars, projectiles, particles, and game state
- **Collision Detection**: Pixel-perfect mask-based collision system
- **State Management**: Clean state machine for menu, gameplay, and modals
- **Particle System**: Dynamic visual effects for enhanced feedback

### File Structure
```
racing_game/
├── app/
│   ├── main.py          # Main game logic
│   ├── utils.py         # Helper functions
│   └── map_generator.py # Tool for creating new maps
├── imgs/                # Game assets
│   ├── fer.png          # Player car
│   ├── redbull.png      # AI car
│   ├── track*.png       # Track images
│   ├── powerup*.png     # Power-up sprites
│   └── speedway*.png    # Speedway map assets
└── README.md
```

## 🎨 Customization

### Adjusting Difficulty
Modify these constants in `main.py`:
- `FPS`: Game speed (default: 60)
- `SPAWN_INTERVAL`: Power-up spawn frequency (default: 12 seconds)
- `POWERUP_DURATION`: How long power-ups last (default: 5 seconds)
- Car `max_vel` and `rotation_vel` in initialization

### Visual Customization
- Fonts can be changed in the font initialization section
- Colors are defined in constants at the top of the file
- Particle effects can be adjusted in the `Particle` class

## 🐛 Troubleshooting

**Game won't start:**
- Ensure all image files are in the `imgs/` directory
- Check that Pygame is properly installed

**Performance issues:**
- Reduce `FPS` constant
- Decrease particle count in collision handlers

**Map not loading:**
- Run `map_generator.py` to regenerate map assets
- Verify image files exist in `imgs/` directory

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork this project and add your own features:
- New tracks and map designs
- Additional power-ups
- Multiplayer support
- Sound effects and music
- More AI difficulty levels

## 🎮 Enjoy the Race!

Have fun racing and may the best driver win! 🏁
