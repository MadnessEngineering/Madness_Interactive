# Snowball Snowman

A delightful game where players build snowmen while engaging in epic snowball battles!

## Game Overview

In Snowball Snowman, players navigate a winter wonderland where they can:
- Collect snow to make snowballs
- Build snowmen piece by piece
- Engage in snowball fights with other players/AI
- Protect their snowmen while trying to destroy others'

## Art Creation Guide

### Tools for Creating Game Art
1. **Kid-Friendly Art Tools:**
   - [Piskel](https://www.piskelapp.com/) - Free online sprite editor, great for pixel art
   - [Krita](https://krita.org/) - Free drawing program with simple tools
   - [Paint.NET](https://www.getpaint.net/) - Easy to use image editor
   - Regular paper and pencils/markers for drawing, then scanning or photographing

### Recommended Art Assets to Create
1. **Characters:**
   - Player character (front, back, side views)
   - Different colored outfits/hats for customization

2. **Snowmen Parts:**
   - Snow balls (different sizes)
   - Carrot noses
   - Coal/button eyes
   - Stick arms
   - Various hats and scarves

3. **Environment:**
   - Snow textures
   - Trees and bushes
   - Fences
   - Houses in background
   - Clouds and snowflakes

4. **UI Elements:**
   - Buttons (Play, Pause, etc.)
   - Health/Snow meter
   - Score display
   - Menu backgrounds

### Art Guidelines
- Keep designs simple and clear
- Use PNG format for transparency
- Make sprites at least 64x64 pixels for good visibility
- Use bright, contrasting colors
- Save all original art files in a separate folder

## Technical Details

### Requirements
- Python 3.8+
- Pygame
- Other dependencies will be listed in requirements.txt

### Project Structure
```
snowball_snowman/
├── src/
│   ├── game/
│   │   ├── __init__.py
│   │   ├── player.py
│   │   ├── snowman.py
│   │   └── world.py
│   ├── graphics/
│   │   ├── __init__.py
│   │   └── sprites.py
│   └── utils/
│       ├── __init__.py
│       └── physics.py
├── assets/
│   ├── images/
│   │   ├── characters/
│   │   ├── snowmen/
│   │   ├── environment/
│   │   └── ui/
│   ├── sounds/
│   └── music/
├── tests/
└── docs/
```

## Android APK Creation Plan

We'll use [Pygame-Android](https://pygame-android.readthedocs.io/) to package the game as an APK. This will involve:

1. **Setup Requirements:**
   - Python for Android (p4a)
   - Android SDK
   - Android NDK
   - Java JDK

2. **Packaging Steps:**
   - Optimize images and sounds for mobile
   - Add touch controls
   - Test on different screen sizes
   - Create app icons
   - Package with buildozer

3. **Testing:**
   - Test on Android emulator
   - Test on real devices
   - Optimize performance

## Development Status

🚧 Currently in initial development phase

## Getting Started

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python src/main.py
```

## Features Roadmap

- [ ] Basic world generation with snow
- [ ] Player movement and controls
- [ ] Snowball mechanics (collecting, throwing)
- [ ] Snowman building system
- [ ] Basic AI opponents
- [ ] Scoring system
- [ ] Sound effects and background music
- [ ] Menu system and UI
- [ ] Touch controls for mobile
- [ ] Android APK packaging

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
