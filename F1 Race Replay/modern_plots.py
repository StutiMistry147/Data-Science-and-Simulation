import fastf1
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Circle, Wedge, Rectangle
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

plt.style.use('dark_background')
sns.set_palette("husl")

def create_modern_lap_comparison(year, track, driver_count=5):
    """Create a sleek lap time comparison chart using actual race drivers"""
    try:
        session = fastf1.get_session(year, track, 'R')
        session.load()
        

        top_drivers = session.results['Abbreviation'].head(driver_count).tolist()
        
        if not top_drivers:
            print(f"No driver data found for {year} {track}")
            return None
        
        fig = plt.figure(figsize=(16, 8), facecolor='#0F0F0F')
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Main plot - Lap times
        ax1 = fig.add_subplot(gs[:, 0])
        
        colors = ['#FF1801', '#00D2BE', '#FFFFFF', '#FF8700', '#0090FF', '#9B0000', '#FFD700', '#C0C0C0', '#CD7F32']
        
        for idx, driver in enumerate(top_drivers):
            laps = session.laps.pick_driver(driver)
            if not laps.empty:
                lap_times = laps['LapTime'].dt.total_seconds()
                ax1.plot(laps['LapNumber'], lap_times, 
                        label=driver, linewidth=2.5, color=colors[idx % len(colors)],
                        marker='o', markersize=4, alpha=0.8)
        
        ax1.set_xlabel('Lap Number', fontsize=12, fontweight='bold', color='white')
        ax1.set_ylabel('Lap Time (seconds)', fontsize=12, fontweight='bold', color='white')
        ax1.set_title(f'{year} {track} - Lap Time Comparison', 
                     fontsize=16, fontweight='bold', color='#FF1801', pad=20)
        ax1.legend(frameon=True, facecolor='#1A1A1A', edgecolor='#FF1801')
        ax1.grid(True, alpha=0.2, linestyle='--')
        ax1.set_facecolor('#0F0F0F')
        

        ax2 = fig.add_subplot(gs[0, 1])
        
        fastest_times = []
        driver_labels = []
        
        for driver in top_drivers:
            laps = session.laps.pick_driver(driver)
            if not laps.empty:
                fastest = laps.pick_fastest()
                fastest_times.append(fastest['LapTime'].total_seconds())
                driver_labels.append(driver)
        
        if fastest_times:
            bars = ax2.bar(driver_labels, fastest_times, 
                          color=colors[:len(driver_labels)])
            ax2.set_title('Fastest Lap Comparison', fontsize=14, fontweight='bold', color='white')
            ax2.set_ylabel('Time (seconds)', fontsize=10, color='white')
            ax2.tick_params(colors='white')
            ax2.set_facecolor('#0F0F0F')
            

            for bar, time in zip(bars, fastest_times):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{time:.3f}', ha='center', va='bottom',
                        fontsize=9, color='white', fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No fastest lap data', ha='center', va='center', 
                    color='white', fontsize=12)
            ax2.set_facecolor('#0F0F0F')
        
        # Position changes (heatmap style)
        ax3 = fig.add_subplot(gs[1, 1])
        
        position_data = []
        valid_drivers = []
        for driver in top_drivers:
            laps = session.laps.pick_driver(driver)
            if not laps.empty and len(laps) > 0:
                positions = laps['Position'].values[:20]  # First 20 laps
                position_data.append(positions)
                valid_drivers.append(driver)
        
        if position_data:
            im = ax3.imshow(position_data, cmap='plasma', aspect='auto')
            ax3.set_title('Position Changes (First 20 Laps)', 
                         fontsize=14, fontweight='bold', color='white')
            ax3.set_xlabel('Lap', fontsize=10, color='white')
            ax3.set_yticks(range(len(valid_drivers)))
            ax3.set_yticklabels(valid_drivers, color='white')
            ax3.set_facecolor('#0F0F0F')
            plt.colorbar(im, ax=ax3)
        else:
            ax3.text(0.5, 0.5, 'No position data', ha='center', va='center', 
                    color='white', fontsize=12)
            ax3.set_facecolor('#0F0F0F')
        
        fig.text(0.5, 0.98, 'F1 RACE RELAY', fontsize=24, fontweight='bold',
                color='#FF1801', ha='center', fontfamily='monospace')
        fig.text(0.5, 0.95, 'Professional Racing Analytics', fontsize=12,
                color='white', ha='center', fontfamily='sans-serif')
        
        plt.tight_layout()
        
        os.makedirs('modern_plots', exist_ok=True)
        filename = f'modern_plots/{year}_{track}_lap_comparison.png'
        plt.savefig(filename, dpi=300, facecolor='#0F0F0F', bbox_inches='tight')
        plt.close()
        
        print(f"✓ Lap comparison saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"✗ Error creating lap comparison: {e}")
        return None

def create_interactive_race_replay(year, track):
    """Create an interactive Plotly race replay"""
    try:
        session = fastf1.get_session(year, track, 'R')
        session.load()
        
        # Get top drivers from the race
        top_drivers = session.results['Abbreviation'].head(10).tolist()
        
        if not top_drivers:
            print(f"No driver data found for {year} {track}")
            return None
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Race Position Timeline', 'Speed Telemetry',
                          'Tire Strategy', 'Gap to Leader'),
            vertical_spacing=0.15,
            horizontal_spacing=0.15
        )
        
        # Position timeline for top 5 drivers
        colors = ['#FF1801', '#00D2BE', '#FFFFFF', '#FF8700', '#0090FF']
        
        for idx, driver in enumerate(top_drivers[:5]):
            laps = session.laps.pick_driver(driver)
            if not laps.empty:
                fig.add_trace(
                    go.Scatter(x=laps['LapNumber'], y=laps['Position'],
                              name=driver, mode='lines+markers',
                              line=dict(width=3, color=colors[idx]),
                              marker=dict(size=4)),
                    row=1, col=1
                )
        
        # Speed trace for winner
        if top_drivers:
            winner = top_drivers[0]
            driver_laps = session.laps.pick_driver(winner)
            if not driver_laps.empty and 'Speed' in driver_laps.columns:
                fig.add_trace(
                    go.Scatter(x=driver_laps['LapNumber'], 
                              y=driver_laps['Speed'],
                              name=f"{winner} Speed",
                              line=dict(color='#FF1801', width=2)),
                    row=1, col=2
                )
            else:
                fig.add_trace(
                    go.Scatter(x=[], y=[], name="Speed data unavailable"),
                    row=1, col=2
                )
        
        # Update layout
        fig.update_layout(
            title=f'{year} {track} Grand Prix - Interactive Analysis',
            title_font=dict(size=24, color='#FF1801', family='Arial Black'),
            plot_bgcolor='rgba(10, 10, 10, 1)',
            paper_bgcolor='rgba(15, 15, 15, 1)',
            font=dict(color='white'),
            showlegend=True,
            height=800,
            hovermode='x unified'
        )
        
        # Update axes
        fig.update_xaxes(title_text="Lap Number", gridcolor='#333333')
        fig.update_yaxes(title_text="Position", gridcolor='#333333', autorange="reversed", row=1, col=1)
        fig.update_yaxes(title_text="Speed (km/h)", gridcolor='#333333', row=1, col=2)
        
        # Save interactive plot
        os.makedirs('interactive_plots', exist_ok=True)
        filename = f'interactive_plots/{year}_{track}_interactive.html'
        fig.write_html(filename)
        
        print(f"✓ Interactive replay saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"✗ Error creating interactive replay: {e}")
        return None

def create_podium_visualization(year, track):
    """Create a podium visualization"""
    try:
        session = fastf1.get_session(year, track, 'R')
        session.load()
        
        # Get top 3 drivers
        top3 = session.results.head(3)
        
        if len(top3) < 3:
            print(f"Not enough finishers for podium in {year} {track}")
            return None
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0F0F0F')
        
        # Podium positions
        podium_heights = [2.0, 3.0, 1.5]  # 1st, 2nd, 3rd
        podium_colors = ['#FFD700', '#C0C0C0', '#CD7F32']  # Gold, Silver, Bronze
        positions = [-1, 0, 1]  # X positions
        
        # Draw podium
        for i in range(3):
            # Podium block
            rect = Rectangle((positions[i] - 0.4, 0), 0.8, podium_heights[i],
                           facecolor=podium_colors[i], alpha=0.8,
                           edgecolor='white', linewidth=2)
            ax.add_patch(rect)
            
            # Driver info
            driver = top3.iloc[i]
            driver_name = driver['FullName']
            team = driver['TeamName']
            
            # Position number
            ax.text(positions[i], podium_heights[i] + 0.1, str(i+1),
                   fontsize=40, fontweight='bold', ha='center',
                   color=podium_colors[i], fontfamily='monospace')
            
            # Driver name (shortened if too long)
            display_name = driver_name
            if len(driver_name) > 15:
                # Take first name initial and last name
                parts = driver_name.split()
                if len(parts) >= 2:
                    display_name = f"{parts[0][0]}. {parts[-1]}"
            
            ax.text(positions[i], podium_heights[i] - 0.2, display_name,
                   fontsize=14, fontweight='bold', ha='center',
                   color='white', fontfamily='sans-serif')
            
            # Team name (shortened)
            display_team = team[:12] + "..." if len(team) > 12 else team
            ax.text(positions[i], podium_heights[i] - 0.5, display_team,
                   fontsize=10, ha='center', color='white', alpha=0.8)
            
            # Time
            if pd.notna(driver['Time']):
                time_str = str(driver['Time'])
                ax.text(positions[i], -0.2, time_str,
                       fontsize=11, ha='center', color='white')
            elif i == 0:  # Winner should have time
                ax.text(positions[i], -0.2, "Winner",
                       fontsize=11, ha='center', color='white')
        
        # the plot
        ax.set_xlim(-2, 2)
        ax.set_ylim(-0.5, 4)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # title
        ax.text(0, 3.8, f'{year} {track} GRAND PRIX',
               fontsize=24, fontweight='bold', ha='center',
               color='#FF1801', fontfamily='Arial Black')
        
        ax.text(0, 3.5, 'PODIUM FINISHERS',
               fontsize=16, ha='center', color='white', fontfamily='sans-serif')
        
        # F1 logo style
        ax.text(0, -0.4, 'F1 RACE RELAY',
               fontsize=18, fontweight='bold', ha='center',
               color='#FF1801', fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save
        os.makedirs('podium_plots', exist_ok=True)
        filename = f'podium_plots/{year}_{track}_podium.png'
        plt.savefig(filename, dpi=300, facecolor='#0F0F0F', bbox_inches='tight')
        plt.close()
        
        print(f"✓ Podium visualization saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"✗ Error creating podium visualization: {e}")
        return None

def create_dashboard(year, track):
    """Create a comprehensive race dashboard"""
    try:
        session = fastf1.get_session(year, track, 'R')
        session.load()
        
        fig = plt.figure(figsize=(20, 12), facecolor='#0A0A0A')
        gs = fig.add_gridspec(3, 4, hspace=0.4, wspace=0.3)
        
        # 1. Race Result
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.axis('tight')
        ax1.axis('off')
        
        display_count = min(8, len(session.results))
        results_data = []
        for i in range(display_count):
            driver = session.results.iloc[i]
            driver_name = driver['FullName'][:15] + "..." if len(driver['FullName']) > 15 else driver['FullName']
            team_name = driver['TeamName'][:12] + "..." if len(driver['TeamName']) > 12 else driver['TeamName']
            time_str = str(driver['Time']) if pd.notna(driver['Time']) else 'DNF'
            
            results_data.append([
                i+1,
                driver['Abbreviation'],
                driver_name,
                team_name,
                time_str[:15]  # Limit time length
            ])
        
        table = ax1.table(cellText=results_data,
                         colLabels=['POS', 'CODE', 'DRIVER', 'TEAM', 'TIME'],
                         cellLoc='center',
                         loc='center',
                         colColours=['#FF1801']*5,
                         cellColours=[['#1A1A1A']*5 for _ in results_data])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        ax1.set_title('RACE RESULTS', fontsize=16, fontweight='bold',
                     color='white', pad=20)
        
        # 2. Fastest Lap Analysis
        ax2 = fig.add_subplot(gs[0, 2:])
        
        top_drivers = session.results['Abbreviation'].head(6).tolist()
        fastest_times = []
        valid_drivers = []
        
        for driver in top_drivers:
            laps = session.laps.pick_driver(driver)
            if not laps.empty:
                fastest = laps.pick_fastest()
                if 'LapTime' in fastest:
                    fastest_times.append(fastest['LapTime'].total_seconds())
                    valid_drivers.append(driver)
        
        if fastest_times:
            colors = ['#FF1801', '#00D2BE', '#FFFFFF', '#FF8700', '#0090FF', '#9B0000']
            bars = ax2.barh(valid_drivers, fastest_times,
                           color=colors[:len(valid_drivers)])
            ax2.set_xlabel('Fastest Lap Time (seconds)', color='white')
            ax2.set_title('FASTEST LAP ANALYSIS', fontsize=14,
                         fontweight='bold', color='white')
            ax2.tick_params(colors='white')
            ax2.set_facecolor('#0F0F0F')
            
            for bar, time in zip(bars, fastest_times):
                width = bar.get_width()
                ax2.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                        f'{time:.3f}', ha='left', va='center',
                        color='white', fontsize=9)
        else:
            ax2.text(0.5, 0.5, 'No fastest lap data', ha='center', va='center',
                    color='white', fontsize=14)
            ax2.set_facecolor('#0F0F0F')
        
        # 3. Position Changes 
        ax3 = fig.add_subplot(gs[1, :])
        
        drivers_for_heatmap = session.results['Abbreviation'].head(10).tolist()
        position_matrix = []
        valid_heatmap_drivers = []
        
        for driver in drivers_for_heatmap:
            laps = session.laps.pick_driver(driver)
            if not laps.empty and len(laps) > 5:
                positions = laps['Position'].values[:30]  # First 30 laps
                position_matrix.append(positions)
                valid_heatmap_drivers.append(driver)
        
        if position_matrix:
            im = ax3.imshow(position_matrix, cmap='viridis', aspect='auto')
            ax3.set_title('POSITION CHANGES - FIRST 30 LAPS', fontsize=14,
                         fontweight='bold', color='white', pad=15)
            ax3.set_xlabel('Lap Number', color='white')
            ax3.set_ylabel('Driver', color='white')
            ax3.set_yticks(range(len(valid_heatmap_drivers)))
            ax3.set_yticklabels(valid_heatmap_drivers, color='white')
            ax3.set_facecolor('#0F0F0F')
            plt.colorbar(im, ax=ax3)
        else:
            ax3.text(0.5, 0.5, 'No position data available', ha='center', va='center',
                    color='white', fontsize=14)
            ax3.set_facecolor('#0F0F0F')
        
        # 4. Race Statistics
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('off')
        
        stats = []
        stats.append(f"RACE STATISTICS - {year} {track}")
        stats.append("="*40)

        if hasattr(session, 'total_laps'):
            stats.append(f"Total Laps: {session.total_laps}")
        
        if hasattr(session, 'track_length'):
            stats.append(f"Track Length: {session.track_length} km")
        
        if len(session.results) > 0:
            winner = session.results.iloc[0]
            stats.append(f"Winner: {winner['FullName']}")
            stats.append(f"Winning Team: {winner['TeamName']}")
        
        if not session.laps.empty:
            try:
                fastest = session.laps.pick_fastest()
                if 'LapTime' in fastest:
                    stats.append(f"Fastest Lap: {fastest['LapTime']}")
                if 'Driver' in fastest:
                    stats.append(f"Fastest Driver: {fastest['Driver']}")
            except:
                pass
        
        stats.append(f"Number of Finishers: {len(session.results)}")
        
        for i, line in enumerate(stats):
            color = '#FF1801' if i < 2 else 'white'
            weight = 'bold' if i < 2 else 'normal'
            size = 12 if i < 2 else 11
            ax4.text(0.1, 0.9 - i*0.07, line,
                    transform=ax4.transAxes, fontsize=size,
                    color=color, fontweight=weight,
                    verticalalignment='top', fontfamily='monospace')
        
        # Main title
        fig.suptitle('F1 RACE RELAY - PROFESSIONAL DASHBOARD',
                    fontsize=28, fontweight='bold',
                    color='#FF1801', fontfamily='monospace',
                    y=0.98)
        
        fig.text(0.5, 0.95, 'Advanced Racing Analytics & Visualization',
                fontsize=16, color='white', ha='center',
                fontfamily='sans-serif')
        
        plt.tight_layout()
        
        # Save
        os.makedirs('dashboards', exist_ok=True)
        filename = f'dashboards/{year}_{track}_dashboard.png'
        plt.savefig(filename, dpi=300, facecolor='#0A0A0A', bbox_inches='tight')
        plt.close()
        
        print(f"✓ Dashboard saved: {filename}")
        return filename
        
    except Exception as e:
        print(f" Error creating dashboard: {e}")
        return None

def generate_all_visuals(year, track):
    """Generate all modern visualizations for any race"""
    print(f"\n{'='*60}")
    print(f"GENERATING VISUALS FOR: {year} {track}")
    print('='*60)
    
    try:
        # Test if session exists
        session = fastf1.get_session(year, track, 'R')
        session.load(telemetry=False, weather=False)  # Light load for testing
        
        # Generate all visualizations
        print("\n1. Creating lap comparison...")
        create_modern_lap_comparison(year, track)
        
        print("\n2. Creating interactive replay...")
        create_interactive_race_replay(year, track)
        
        print("\n3. Creating podium visualization...")
        create_podium_visualization(year, track)
        
        print("\n4. Creating race dashboard...")
        create_dashboard(year, track)
        
        print(f"\n{'='*60}")
        print("ALL VISUALS GENERATED SUCCESSFULLY!")
        print("Check these folders:")
        print("  - modern_plots/")
        print("  - interactive_plots/")
        print("  - podium_plots/")
        print("  - dashboards/")
        print('='*60)
        
    except Exception as e:
        print(f"\nError: Could not load {year} {track}")
        print(f"   Details: {e}")
        print("\nTry these working examples:")
        print("   - 2023 Monaco")
        print("   - 2023 Bahrain")
        print("   - 2022 Silverstone")
        print("   - 2021 Monza")

def generate_visuals_for_gui(year, track):
    """Wrapper function for GUI to call"""
    try:
        generate_all_visuals(int(year), track)
        return True
    except Exception as e:
        print(f"Error in generate_visuals_for_gui: {e}")
        return False

if __name__ == "__main__":
    # Test with a few working examples
    print("F1 Race Relay - Visualization Generator")
    print("="*50)
    
    # List of working examples
    working_races = [
        (2023, 'Monaco'),
        (2023, 'Bahrain'),
        (2022, 'Silverstone'),
        (2021, 'Monza')
    ]
    
    print("Available working examples:")
    for i, (yr, trk) in enumerate(working_races, 1):
        print(f"  {i}. {yr} {trk}")
    
    print("\nEnter your choice:")
    print("1. Test with 2023 Monaco (recommended)")
    print("2. Enter custom year and track")
    
    choice = input("Choice (1 or 2): ").strip()
    
    if choice == "1":
        generate_all_visuals(2023, 'Monaco')
    elif choice == "2":
        year = input("Enter year (e.g., 2023): ").strip()
        track = input("Enter track name (e.g., Monaco): ").strip()
        generate_all_visuals(int(year), track)
    else:
        print("Invalid choice. Testing with 2023 Monaco...")
        generate_all_visuals(2023, 'Monaco')
