# Snowball Snowman

A delightful game where players build snowmen while engaging in epic snowball battles!

## Game Overview

In Snowball Snowman, players navigate a winter wonderland where they can:
- Collect snow to make snowballs
- Build snowmen piece by piece
- Engage in snowball fights with other players/AI
- Protect their snowmen while trying to destroy others'

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
│   ├── sounds/
│   └── music/
├── tests/
└── docs/
```

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
