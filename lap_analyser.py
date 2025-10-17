import argparse
import fastf1
from fastf1 import plotting
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import os


def setup_cache(cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)


def load_session(year, gp, session):
    """Load a session using fastf1 and return the Session object."""
    try:
        sess = fastf1.get_session(year, gp, session)
        sess.load()  # download telemetry and laps
        return sess
    except Exception as e:
        raise RuntimeError(f"Failed to load session: {e}")


def best_laps_dataframe(session):
    """Return a DataFrame with each driver's best lap time and lap number."""
    laps = session.laps
    if laps is None or laps.empty:
        raise RuntimeError("No lap data available in session")

    # Filter to valid laps
    valid = laps[laps['IsAccurate'] | laps['IsPersonalBest'] | (laps['LapTime'].notnull())]
    # Group by driver and take minimum lap time
    best = valid.loc[valid.groupby('Driver')['LapTime'].idxmin()].copy()
    best = best[['Driver', 'Team', 'LapTime', 'LapNumber', 'Compound']]
    best = best.sort_values('LapTime')
    best['LapTime_s'] = best['LapTime'].dt.total_seconds()
    return best


def print_top_laps(df, n=10):
    df = df.head(n)
    print(df[['Driver', 'Team', 'LapNumber', 'Compound', 'LapTime_s']].to_string(index=False))


def plot_driver_lap(session, driver, lap_number=None):
    # Load telemetry for driver's laps
    laps = session.laps.pick_driver(driver)
    if lap_number is None:
        lap = laps.pick_fastest()
    else:
        lap = laps[laps['LapNumber'] == lap_number].iloc[0]

    tel = lap.get_telemetry()
    plt.figure(figsize=(10, 4))
    plt.plot(tel['Distance'], tel['Speed'])
    plt.xlabel('Distance (m)')
    plt.ylabel('Speed (km/h)')
    plt.title(f"{driver} Lap {lap['LapNumber']} Speed")
    plt.grid(True)
    plt.show()


def plot_lap_comparison(session, drivers, interactive=False):
    """Plot lap time comparison between multiple drivers."""
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    if interactive:
        fig = go.Figure()
        for i, driver in enumerate(drivers):
            laps = session.laps.pick_driver(driver)
            fig.add_trace(go.Scatter(
                x=laps['LapNumber'], 
                y=laps['LapTime'].dt.total_seconds(),
                mode='lines+markers',
                name=driver,
                line=dict(color=colors[i % len(colors)])
            ))
        fig.update_layout(
            title='Lap Time Comparison',
            xaxis_title='Lap Number',
            yaxis_title='Lap Time (seconds)',
            height=500
        )
        return fig
    else:
        plt.figure(figsize=(12, 6))
        for i, driver in enumerate(drivers):
            laps = session.laps.pick_driver(driver)
            plt.plot(laps['LapNumber'], laps['LapTime'].dt.total_seconds(), 
                    'o-', label=driver, color=colors[i % len(colors)])
        plt.xlabel('Lap Number')
        plt.ylabel('Lap Time (seconds)')
        plt.title('Lap Time Comparison')
        plt.legend()
        plt.grid(True)
        plt.show()


def plot_sector_comparison(session, drivers):
    """Plot sector time comparison between drivers."""
    sector_data = []
    
    for driver in drivers:
        fastest_lap = session.laps.pick_driver(driver).pick_fastest()
        if pd.notna(fastest_lap['Sector1Time']) and pd.notna(fastest_lap['Sector2Time']) and pd.notna(fastest_lap['Sector3Time']):
            sector_data.append({
                'Driver': driver,
                'Sector 1': fastest_lap['Sector1Time'].total_seconds(),
                'Sector 2': fastest_lap['Sector2Time'].total_seconds(),
                'Sector 3': fastest_lap['Sector3Time'].total_seconds()
            })
    
    if not sector_data:
        print("No sector time data available for selected drivers")
        return None
        
    df = pd.DataFrame(sector_data)
    df_melted = df.melt(id_vars=['Driver'], var_name='Sector', value_name='Time')
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_melted, x='Sector', y='Time', hue='Driver')
    plt.title('Sector Time Comparison (Fastest Laps)')
    plt.ylabel('Time (seconds)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
    return df


def plot_telemetry_comparison(session, drivers, telemetry_type='Speed'):
    """Plot telemetry comparison (Speed, Throttle, Brake, etc.) between drivers."""
    fig = go.Figure()
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    for i, driver in enumerate(drivers):
        fastest_lap = session.laps.pick_driver(driver).pick_fastest()
        tel = fastest_lap.get_telemetry()
        
        fig.add_trace(go.Scatter(
            x=tel['Distance'],
            y=tel[telemetry_type],
            mode='lines',
            name=f"{driver}",
            line=dict(color=colors[i % len(colors)])
        ))
    
    fig.update_layout(
        title=f'{telemetry_type} Comparison (Fastest Laps)',
        xaxis_title='Distance (m)',
        yaxis_title=telemetry_type,
        height=500
    )
    return fig


def plot_lap_time_distribution(session):
    """Plot lap time distribution for all drivers."""
    valid_laps = session.laps[session.laps['LapTime'].notnull()]
    
    fig = px.box(
        x=valid_laps['Driver'],
        y=valid_laps['LapTime'].dt.total_seconds(),
        title='Lap Time Distribution by Driver'
    )
    fig.update_layout(
        xaxis_title='Driver',
        yaxis_title='Lap Time (seconds)',
        height=500
    )
    return fig


def main():
    parser = argparse.ArgumentParser(description='F1 Lap Time Analyser (fastf1)')
    parser.add_argument('--year', type=int, default=2023, help='Season year')
    parser.add_argument('--gp', type=str, default='Monza', help='Grand Prix name or round number')
    parser.add_argument('--session', type=str, default='Q', help='Session: FP1/FP2/FP3/Q/R')
    parser.add_argument('--cache', type=str, default=os.path.expanduser('~/.fastf1-cache'), help='Cache directory')
    parser.add_argument('--top', type=int, default=10, help='Show top N best laps')
    parser.add_argument('--plot', type=str, help='Driver to plot a lap for (e.g. HAM)')
    parser.add_argument('--lap', type=int, help='Specify lap number to plot')
    args = parser.parse_args()

    setup_cache(args.cache)

    print(f"Loading {args.year} {args.gp} {args.session} (cache: {args.cache})...")
    session = load_session(args.year, args.gp, args.session)
    print('Session loaded. Computing best laps...')
    best = best_laps_dataframe(session)
    print_top_laps(best, n=args.top)

    if args.plot:
        print(f"Plotting lap for {args.plot}...")
        plot_driver_lap(session, args.plot, args.lap)


if __name__ == '__main__':
    main()
