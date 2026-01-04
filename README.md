# Highway Traffic Simulation - Italian Highway Rules

This simulation demonstrates how traffic jams form on a 3-lane highway when drivers don't follow the Italian highway rule of using the rightmost free lane.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install required dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Optional: Video Generation Support

For MP4 video output, install **ffmpeg** (system dependency):

- **macOS:**
  ```bash
  brew install ffmpeg
  ```

- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt-get install ffmpeg
  ```

- **Linux (Fedora/RHEL):**
  ```bash
  sudo yum install ffmpeg
  ```

- **Windows:**
  ```bash
  choco install ffmpeg
  ```
  Or download from [ffmpeg.org](https://ffmpeg.org/download.html)

**Note:** If ffmpeg is not installed, the video generation will automatically fall back to GIF format using Pillow (included with matplotlib).

## Italian Highway Rules

1. **Passing Rule**: Cars can only pass on the left
2. **Lane Usage Rule**: Drivers must use the rightmost free lane when not overtaking
3. **Bad Practice**: Driving in the middle lane when the right lane is free

## How It Works

The simulation models:
- A 3-lane highway with multiple cars
- Each car has a position, speed, and lane
- Cars can only pass slower vehicles on the left
- Some cars follow "bad practice" (don't use rightmost free lane)
- Cars exit when they reach the end of the highway; new cars can spawn near
  the start when the active count drops below the configured `num_cars`
  using the `spawn_probability` parameter
- Traffic jams are detected when cars are blocked and can't pass

## Running the Simulation

### Basic Simulation

```bash
python highway_simulation.py
```

The simulation will:
1. Run multiple trials with different ratios of "bad practice" drivers
2. Calculate the probability of traffic jams for each ratio
3. Show how traffic jam probability increases with more bad practice drivers

### Generate Visualization

```bash
python visualize_results.py
```

Creates a graph showing traffic jam probability vs bad practice ratio.

### Generate Video Animation

```bash
python generate_video.py
```

Creates an animated video showing:
- Initial setup of cars on the 3-lane highway
- Real-time car movements and lane changes
- How traffic jams form when drivers don't follow rules
- Color-coded cars:
  - **Blue**: Normal drivers (follow rules)
  - **Purple**: Bad practice drivers (don't use rightmost lane)
  - **Orange**: Blocked cars (can't pass)
  - **Red**: Cars in traffic jam

**Note:** If ffmpeg is installed, MP4 format will be used. Otherwise, the script automatically creates a GIF instead.

## Results

The simulation demonstrates that as the percentage of drivers following bad practice increases, the probability of traffic jams also increases. This is because:
- Cars in the middle lane block faster traffic from passing
- Forces faster cars to use multiple lane changes
- Creates bottlenecks when slow cars occupy the leftmost lane
