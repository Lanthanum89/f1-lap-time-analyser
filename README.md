# F1 Lap Time Analyser 🏎️

Comprehensive Formula 1 session analysis tool with both CLI and interactive web GUI using FastF1 data.

## Features

- 🏆 **Best Lap Analysis** - Find fastest laps per driver with detailed timing
- 📈 **Interactive Lap Comparisons** - Compare multiple drivers lap-by-lap
- 🎯 **Sector Analysis** - Break down performance by track sectors
- 🔧 **Telemetry Visualization** - Speed, throttle, brake, RPM analysis
- 📊 **Statistical Distribution** - Lap time distribution and consistency metrics
- 💾 **Smart Caching** - Fast subsequent loads with local data caching

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Installation

```bash
python -m pip install -r requirements.txt
```

## Usage

### 🚀 Easy Launcher (All Options)

Run the launcher script to choose your preferred interface:

```bash
python run.py
```

This gives you a menu to select:
1. **Real-Time Desktop GUI** - Best for live session monitoring
2. **Interactive Web GUI** - Best for detailed historical analysis  
3. **Command Line Interface** - Best for automation and scripting

### 🔴 Real-Time Desktop GUI (Recommended for Live Sessions)

Launch the Tkinter real-time application:

```bash
python tkinter_app.py
```

Features:
- **Real-time monitoring** - Automatically detects live F1 sessions
- **Live timing display** - Shows current positions and lap times during sessions
- **Auto-refresh** - Updates every 30 seconds when enabled
- **Offline content** - F1 calendar and statistics when no live sessions
- **Historical analysis** - Load any past session for detailed analysis
- **Desktop native** - No browser required, runs as standalone application

### 🖥️ Interactive Web GUI

Launch the Streamlit web interface:

```bash
streamlit run streamlit_app.py
```

This opens a browser with:
- - **Session Selection**: Choose any F1 session from 2018-2025
- Interactive plots and analysis tabs
- Real-time data loading with progress indicators
- Multiple visualization types (Plotly charts, statistical plots)

### ⌨️ Command Line Interface

Basic analysis (2023 Monza Qualifying top 5):

```bash
python lap_analyser.py --year 2023 --gp Monza --session Q --top 5
```

Plot a driver's fastest lap speed trace:

```bash
python lap_analyser.py --year 2023 --gp Monza --session Q --plot HAM
```

All CLI options:

```bash
python lap_analyser.py --help
```

## Examples

### GUI Features
- **Current F1 Calendar** with dates and circuits (2025 season)
- **Best Laps Tab**: Sortable table with lap times, compounds, teams
- **Lap Comparison**: Interactive line charts comparing multiple drivers
- **Sector Analysis**: Bar charts showing sector-by-sector performance
- **Telemetry**: Speed/throttle/brake traces overlaid by driver
- **Distribution**: Box plots showing lap time consistency

### CLI Examples

Compare multiple sessions:
```bash
python lap_analyser.py --year 2023 --gp "Great Britain" --session Q --top 10
python lap_analyser.py --year 2023 --gp Monaco --session R --plot VER --lap 45
```

## Data Sources

- **FastF1 API** - Official F1 timing and telemetry data
- **Cached locally** - Subsequent loads are much faster
- **Historical data** - Sessions from 2018 onwards available

## Notes

- First session load requires internet and may take 1-2 minutes
- Cache directory default: `~/.fastf1-cache` (customizable)
- Some older sessions may have limited telemetry data
- GUI automatically handles session info, weather, and results when available

## Troubleshooting

**Session won't load**: Check internet connection, verify GP name spelling
**No telemetry data**: Some practice sessions or older seasons may lack detailed data
**Cache issues**: Delete cache directory to force fresh download
**GUI not opening**: Ensure Streamlit installed, check browser popup blockers
