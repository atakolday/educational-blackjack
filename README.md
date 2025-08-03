# Blackjack with Card Counting and Statistical Strategy

A sophisticated blackjack game implementation in Python that includes card counting (Hi-Lo system) and statistical strategy calculation based on the current count and remaining deck composition.

## Features

### Core Game Engine
- **Multi-deck support** (typically 6-8 decks like casino blackjack)
- **Complete blackjack rules** including hit, stand, double, split, and surrender
- **Realistic casino rules** (dealer hits soft 17, blackjack pays 3:2, etc.)
- **Proper card tracking** for accurate probability calculations

### Card Counting System
- **Hi-Lo counting system** implementation
- **Running count** and **true count** calculation
- **Card removal tracking** for precise probability analysis
- **Deck penetration** monitoring

### Statistical Strategy Calculator (Coming Soon)
- **Dynamic probability calculations** based on remaining deck composition
- **Expected value (EV) analysis** for all possible actions
- **Optimal strategy recommendations** that adapt to the current count
- **Comparison with basic strategy** to show count-based advantages

### Graphical Interface (Coming Soon)
- **Modern GUI** with card visualization
- **Real-time count display**
- **Strategy recommendation panel**
- **Statistics and performance tracking**

## Project Structure

```
blackjack/
├── main.py                 # Entry point with console interface
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── game/              # Core game engine
│   │   ├── card.py        # Card class with counting properties
│   │   ├── hand.py        # Hand management and blackjack logic
│   │   ├── deck.py        # Multi-deck with card tracking
│   │   └── game.py        # Main game engine and flow
│   ├── counting/          # Card counting system (Phase 2)
│   ├── strategy/          # Statistical strategy (Phase 3)
│   └── gui/               # Graphical interface (Phase 4)
└── tests/                 # Unit tests
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd blackjack
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game:**

   **Console Interface:**
   ```bash
   python3 main.py
   ```

   **Graphical Interface:**
   ```bash
   python3 gui_main.py
   ```
   
   **Note:** The GUI requires tkinter. If you get a "No module named '_tkinter'" error, install it with:
   ```bash
   # On macOS with Homebrew:
   brew install python-tk
   
   # On Ubuntu/Debian:
   sudo apt-get install python3-tk
   
   # On Windows:
   # tkinter is usually included with Python installation
   ```

## Building a Standalone App

To create a standalone macOS app that you can double-click to run:

### Option 1: Simple Build (Recommended)
```bash
python build_app_simple.py
```

### Option 2: Full Build with DMG
```bash
python build_app.py
```

After building, you'll find your app at:
- **Simple build**: `dist/Blackjack` (executable file)
- **Full build**: `dist/Blackjack.app` (macOS app bundle)

### Features of the Standalone App:
- ✅ **No Python required** - runs independently
- ✅ **Custom icon** - uses your game icon
- ✅ **Native macOS app** - appears in Dock, Applications folder
- ✅ **All assets included** - no missing files
- ✅ **Professional appearance** - looks like a real app

### Installing the App:
1. **Test**: Double-click the app to make sure it works
2. **Install**: Drag `Blackjack.app` to your Applications folder
3. **Launch**: Use Spotlight (Cmd+Space) and type "Blackjack"
4. **Dock**: The app will appear in your Dock when running

## How to Play

### Console Interface
The current version includes a fully functional console interface:

### Graphical Interface
The GUI provides a modern, user-friendly interface with:

- **Start Screen** with bankroll selection and game rules
- **Professional card design** with realistic proportions and styling
- **Real-time card display** with suit symbols and colors
- **Live count tracking** showing running count, true count, and count status
- **Strategy recommendations** displaying optimal actions and expected values
- **Interactive betting** with quick bet buttons and bankroll management
- **Game action buttons** (hit, stand, double, split, surrender) that update based on game state
- **Insurance handling** when dealer shows an Ace
- **Game statistics** including win rate and games played
- **Responsive layout** that adapts to different window sizes
- **Menu navigation** with back-to-menu functionality

The GUI automatically updates all displays in real-time as the game progresses, providing immediate feedback on count changes and strategy recommendations.

1. **Place a bet:** `bet 50`
2. **Take actions during play:**
   - `hit` - Take another card
   - `stand` - Keep current hand
   - `double` - Double down (if available)
   - `split` - Split the hand (if available)
   - `surrender` - Surrender the hand (if available)
3. **Start new hand:** `new`
4. **Quit:** `quit`

### Card Counting
The game automatically tracks the Hi-Lo count:
- **+1:** 2, 3, 4, 5, 6
- **0:** 7, 8, 9
- **-1:** 10, J, Q, K, A

The running count and true count are displayed during gameplay.

## Development Phases

### ✅ Phase 1: Core Game Engine (Complete)
- [x] Card and Deck classes with counting properties
- [x] Hand management with blackjack logic
- [x] Complete game engine with all rules
- [x] Console interface for testing

### ✅ Phase 2: Card Counting System (Complete)
- [x] Hi-Lo counting implementation
- [x] Running count and true count calculation
- [x] Probability engine for remaining cards
- [x] Count-based strategy analysis

### ✅ Phase 3: Statistical Strategy Calculator (Complete)
- [x] Dynamic probability calculations
- [x] Expected value analysis
- [x] Optimal strategy recommendations
- [x] Strategy comparison tools

### ✅ Phase 4: Graphical Interface (Complete)
- [x] Modern GUI design
- [x] Card visualization
- [x] Real-time strategy display
- [x] Statistics dashboard

### 📋 Phase 5: Advanced Features
- [ ] Simulation mode for strategy validation
- [ ] Learning mode with explanations
- [ ] Performance tracking and analysis
- [ ] Customizable rules and settings

## Technical Details

### Card Counting System
The game implements the Hi-Lo counting system, which is one of the most popular and effective card counting methods:

- **Low cards (2-6):** +1 to count
- **Neutral cards (7-9):** 0 to count  
- **High cards (10-A):** -1 to count

The **true count** is calculated as: `running_count / decks_remaining`

### Probability Calculations
The system tracks exact card composition of the remaining deck, enabling precise probability calculations for:
- Drawing specific ranks
- Busting probabilities
- Dealer outcome probabilities
- Expected values for all actions

### Strategy Optimization
Unlike basic strategy (which assumes infinite deck), this system calculates optimal play based on the actual remaining deck composition, providing a significant advantage when the count is favorable.

## Contributing

This is an educational project demonstrating advanced blackjack strategy concepts. Contributions are welcome, especially for:
- Bug fixes and improvements
- Additional card counting systems
- Enhanced probability calculations
- GUI development
- Testing and validation

## Disclaimer

This software is for educational purposes only. Card counting may be frowned upon or prohibited in some casinos. Always check local regulations and casino policies before attempting to use card counting techniques.

## License

This project is open source and available under the MIT License. 