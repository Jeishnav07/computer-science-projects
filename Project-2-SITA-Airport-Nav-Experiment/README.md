# Airport Navigation (2D) — Small demo

A minimal Pygame demonstration of A* pathfinding on a simple bird's-eye airport map.
This project illustrates:
- computing a shortest path (A* with Manhattan heuristic) from a fixed check-in location
- simulating simple GPS noise (Gaussian) and snapping to anchor points
- comparing how noise affects the chosen path with simple statistics

Why it's useful:
This small demo shows how sensor noise can change routing decisions and how anchors can improve robustness — useful when explaining algorithm behaviour in a personal statement.

Quick start
1. create and activate a virtual environment (optional but recommended)
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS / Linux:
   # source .venv/bin/activate

2. install dependencies
   pip install -r requirements.txt

3. run the demo
   python main.py

Controls (inside the app)
- Click a red target circle to select a destination
- ] / [ : increase / decrease noise sigma
- ; / l : increase / decrease anchor radius
- r : run a single noisy trial (shows noisy path)
- m : run 10 trials and show aggregate stats
- c : save the current stats to `output/noise_stats.csv`

Notes
- Keep the window open and press keys to run experiments.
- The code is intentionally small and well-commented for easy explanation.

Maintainer
- Your Name (you) — small school project / portfolio
