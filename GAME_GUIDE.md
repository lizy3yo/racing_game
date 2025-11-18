# 🏁 Ultimate Racing Championship - Player Guide

## 🎯 Objective
Race against an AI opponent, complete laps faster than your rival, and master multiple racing circuits!

## 🎮 Getting Started

### Main Menu
When you launch the game, you'll see three options:
1. **PLAY** - Start racing on the currently selected track
2. **SELECT MAP** - Choose between available racing circuits
3. **QUIT** - Exit the game

### Selecting a Track
- Click "SELECT MAP" to view available circuits
- Each track has unique characteristics:
  - **Classic Circuit**: Technical track with tight corners and challenging sections
  - **Speedway Oval**: High-speed oval perfect for intense racing
- Click on a track card to select it
- Click "BACK" to return to the main menu

### Starting a Race
1. Click "PLAY" from the main menu
2. Watch the countdown: 3... 2... 1...
3. Race begins! Try to cross the finish line before your opponent

## 🎮 Controls

### Basic Controls
| Key | Action |
|-----|--------|
| W or ↑ | Accelerate forward |
| S or ↓ | Brake / Reverse |
| A or ← | Turn left |
| D or → | Turn right |
| SPACE | Fire weapon (when you have ammo) |
| ESC | Return to menu |

### Pro Tips
- **Smooth Steering**: Tap the turn keys gently for better control
- **Brake Before Corners**: Slow down before tight turns to maintain control
- **Accelerate Out**: Hit the gas as you exit corners for maximum speed
- **Wall Riding**: Avoid hitting walls - they slow you down significantly

## ⚡ Power-Ups

Power-ups appear as rotating, pulsing icons on the track. Drive through them to collect!

### 🟡 Boost (Gold)
- **Effect**: Increases your maximum speed by 80%
- **Duration**: 5 seconds
- **Strategy**: Use on straightaways for maximum advantage
- **Visual**: Gold/yellow icon
- **Tip**: Great for overtaking or building a lead

### 🟣 Vulnerability (Purple)
- **Effect**: Allows you to pass through barriers without bouncing
- **Duration**: 5 seconds
- **Risk**: You're more susceptible to weapon hits
- **Strategy**: Take risky shortcuts or recover from bad positions
- **Visual**: Purple/magenta icon
- **Tip**: High risk, high reward - use wisely!

### 🟢 Weapon (Green)
- **Effect**: Grants 1 ammunition for your projectile weapon
- **Duration**: Ammo persists until used
- **Strategy**: Save for strategic moments
- **Visual**: Green icon
- **Tip**: Hit the AI to stun them for 3 seconds!

## 🎯 Weapons System

### Using Weapons
1. Collect a weapon power-up (green icon)
2. Your ammo count appears in the top-right HUD
3. Press SPACE to fire a projectile forward
4. Hit the AI opponent to stun them

### Weapon Strategy
- **Lead Your Shots**: Aim where the opponent will be, not where they are
- **Close Range**: Weapons are most effective at close range
- **Save for Overtakes**: Use weapons when the AI is ahead to slow them down
- **Stun Duration**: AI is stunned for 3 seconds - use this time to gain a lead!

## 📊 HUD (Heads-Up Display)

### Top-Left Panel
- **LAP**: Current lap number
- **TIME**: Current lap time
- **BEST**: Your best lap time (appears after first lap)
- **SPEED**: Current speed in pixels per second

### Top-Right Panel
- **AMMO**: Number of projectiles available
- **POWER**: Currently active power-up
- **Timer**: Remaining duration of active power-up

## 🏆 Winning & Losing

### Victory Conditions
- Cross the finish line before the AI opponent
- Complete laps to set new best times
- Master each track's unique layout

### After a Race
When the race ends, you'll see a modal with options:
- **RESTART**: Race again on the same track
- **NEXT**: Continue to the next lap (if you won)
- **MENU**: Return to the main menu

## 🎓 Advanced Techniques

### Racing Line
- Take the inside line on corners for shorter distance
- Apex late on tight corners for better exit speed
- Use the full width of the track

### Power-Up Management
- **Boost**: Save for straightaways or when you need to catch up
- **Vulnerability**: Use when you're behind and need to take risks
- **Weapon**: Most effective when AI is ahead of you

### Defensive Driving
- Block the inside line to prevent AI overtakes
- Use weapons to maintain your lead
- Stay on the racing line to maximize speed

### Offensive Driving
- Look for power-ups to gain advantages
- Use boost on straights to overtake
- Fire weapons to create opportunities

## 🎨 Visual Feedback

### Particle Effects
The game uses particles to provide visual feedback:
- **Yellow Sparks**: Wall collision
- **Colored Bursts**: Power-up collection (matches power-up color)
- **Orange Explosion**: Weapon hit
- **Rainbow Confetti**: Lap completion

### HUD Indicators
- **Gold Border**: Active boost
- **Purple Border**: Vulnerability active
- **Green Border**: Weapon power-up collected
- **White Text**: Normal information
- **Colored Text**: Special states (speed, power-ups)

## ⚙️ Customization

Want to adjust the game to your liking? Edit `app/config.py`:
- Change game speed (FPS)
- Adjust difficulty (car speeds)
- Modify power-up duration
- Enable/disable particle effects
- And much more!

## 🐛 Common Issues

### Car feels too fast/slow
- Edit `PLAYER_MAX_SPEED` in `config.py`
- Default is 4, try 3 for slower or 5 for faster

### AI too difficult/easy
- Adjust `AI_MAX_SPEED` in `config.py`
- Lower values make AI easier to beat

### Performance issues
- Lower `FPS` in `config.py` (try 30)
- Set `ENABLE_PARTICLES = False` in `config.py`
- Close other applications

### Controls feel sluggish
- Increase `PLAYER_ROTATION_SPEED` in `config.py`
- Default is 4, try 5 or 6 for quicker turning

## 🏁 Race Strategy Guide

### Track-Specific Tips

#### Classic Circuit
- **Tight Corners**: Brake early, accelerate late
- **Long Straight**: Perfect for boost power-ups
- **Technical Sections**: Precision over speed
- **Best Line**: Hug the inside of corners

#### Speedway Oval
- **High Speed**: Maintain momentum at all costs
- **Banking**: Use the track's natural curve
- **Overtaking**: Use boost on straights
- **Defensive**: Block the inside line

### Lap Strategy
1. **First Lap**: Learn the track, collect power-ups
2. **Middle Laps**: Push for best time, use power-ups strategically
3. **Final Lap**: All-out attack, use any remaining weapons

## 🎯 Achievements to Try

Challenge yourself with these goals:
- ✅ Complete a lap without hitting walls
- ✅ Win using only boost power-ups
- ✅ Hit the AI with 3 weapons in one race
- ✅ Set a lap time under 30 seconds (Classic Circuit)
- ✅ Win on both tracks
- ✅ Complete 10 consecutive laps
- ✅ Win without using any power-ups (Hard Mode!)

## 🤝 Need Help?

- Check the README.md for technical information
- Review this guide for gameplay tips
- Experiment with config.py settings
- Practice makes perfect - keep racing!

---

**Good luck, racer! May you cross the finish line first! 🏆**
