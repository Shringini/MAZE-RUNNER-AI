# Maze Runner with AI-Controlled Enemy

A dynamic maze game where the player must navigate through obstacles to reach the green exit while escaping an AI-controlled enemy. The enemy uses **Breadth-First Search (BFS)** pathfinding to calculate the shortest path and pursue the player in real-time.

---

##  Features

- **Real-Time BFS AI Pathfinding**: The enemy calculates the optimal path through the maze to pursue the player.
- **Smooth Movement & Collision Detection**: Responsive player controls with auto-alignment corner-nudging to prevent snagging on walls.
- **Dual Platform Support**:
  - **Web Version**: Runs natively in any browser with zero setup.
  - **Desktop Version**: Built with Python and Pygame.
- **Cross-Device Controls**: Support for Keyboard (WASD / Arrow Keys) and Mobile Touch D-Pad.
- **Game Metrics**: Live timer and victory/game-over screens with instant restart support.

---

## How to Run the Project

### Option 1: Web Version (Browser - Easiest)

You can run the web version locally without installing any dependencies:

1. Double-click **`index.html`** in your project folder to open it in your web browser.
2. Alternatively, serve it locally using Python:
   ```bash
   python -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser.

---

### Option 2: Desktop Python Version

To run the desktop Pygame version:

1. **Install Dependencies**:
   Ensure you have Python installed, then install Pygame:
   ```bash
   pip install pygame
   ```

2. **Run the Game**:
   Navigate to the project root and run:
   ```bash
   python game/main.py
   ```
   *or navigate to `game/MazeRunner` and run:*
   ```bash
   python main.py
   ```

---

##  Controls

| Action | Keyboard | Touch / Mobile |
| :--- | :--- | :--- |
| **Move Up** | `W` / `Up Arrow` | `▲` D-Pad Button |
| **Move Down** | `S` / `Down Arrow` | `▼` D-Pad Button |
| **Move Left** | `A` / `Left Arrow` | `◄` D-Pad Button |
| **Move Right** | `D` / `Right Arrow` | `►` D-Pad Button |
| **Restart Game** | `R` | `Restart` Button |

---

##  Project Structure

```text
MAZE-RUNNER-AI/
├── index.html        # Primary Web Application (HTML5 Canvas + JS)
├── netlify.toml      # Netlify Deployment Configuration
├── vercel.json       # Vercel Deployment Configuration
├── .nojekyll         # GitHub Pages Configuration
├── game/             # Python Pygame source code
│   └── MazeRunner/   # Main Pygame entry & modules
├── ai/               # AI pathfinding algorithms (BFS)
├── assets/           # Game assets and images
├── public/           # Static build exports
├── README.md         # Project documentation
└── requirements.txt  # Python package requirements
```

---

##  Deployment

The web version is ready to be hosted on **Netlify**, **Vercel**, or **GitHub Pages**:
- **Netlify**: Configured via `netlify.toml` for automatic static publishing.
- **GitHub Pages**: Go to **Repository Settings -> Pages** and select `main` branch to deploy.
