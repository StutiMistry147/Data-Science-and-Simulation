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

def create_modern_lap_comparison(year, track, drivers):
    """Create a sleek lap time comparison chart"""
    try:
        session = fastf1.get_session(year, track, 'R')
        session.load()
        
        fig = plt.figure(figsize=(16, 8), facecolor='#0F0F0F')
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Main plot - Lap times
        ax1 = fig.add_subplot(gs[:, 0])
        
        colors = ['#FF1801', '#00D2BE', '#FFFFFF', '#FF8700', '#0090FF']
        
        for idx, driver in enumerate(drivers[:5]):
            laps = session.laps.pick_driver(driver)
            if not laps.empty:
                lap_times = laps['LapTime'].dt.total_seconds()
                ax1.plot(laps['LapNumber'], lap_times, 
                        label=driver, linewidth=2.5, color=colors[idx],
                        marker='o', markersize=4, alpha=0.8)
        
        ax1.set_xlabel('Lap Number', fontsize=12, fontweight='bold', color='white')
        ax1.set_ylabel('Lap Time (seconds)', fontsize=12, fontweight='bold', color='white')
        ax1.set_title(f'{year} {track} - Lap Time Comparison', 
                     fontsize=16, fontweight='bold', color='#FF1801', pad=20)
        ax1.legend(frameon=True, facecolor='#1A1A1A', edgecolor='#FF1801')
        ax1.grid(True, alpha=0.2, linestyle='--')
        ax1.set_facecolor('#0F0F0F')
        
        # Fastest lap comparison (bar chart)
        ax2 = fig.add_subplot(gs[0, 1])
        
        fastest_times = []
        driver_labels = []
        
        for driver in drivers[:5]:
            laps = session.laps.pick_driver(driver)
            if not laps.empty:
                fastest = laps.pick_fastest()
                fastest_times.append(fastest['LapTime'].total_seconds())
                driver_labels.append(driver)
        
        bars = ax2.bar(driver_labels, fastest_times, color=colors[:len(driver_labels)])
        ax2.set_title('Fastest Lap Comparison', fontsize=14, fontweight='bold', color='white')
        ax2.set_ylabel('Time (seconds)', fontsize=10, color='white')
        ax2.tick_params(colors='white')
        ax2.set_facecolor('#0F0F0F')
        
        # Add value labels on bars
        for bar, time in zip(bars, fastest_times):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{time:.3f}', ha='center', va='bottom',
                    fontsize=9, color='white', fontweight='bold')
        
        # Position changes (heatmap style)
        ax3 = fig.add_subplot(gs[1, 1])
        
        position_data = []
        for driver in drivers[:5]:
            laps = session.laps.pick_driver(driver)
            if not laps.empty and len(laps) > 0:
                positions = laps['Position'].values[:20]  # First 20 laps
                position_data.append(positions)
        
        if position_data:
            im = ax3.imshow(position_data, cmap='plasma', aspect='auto')
            ax3.set_title('Position Changes (First 20 Laps)', 
                         fontsize=14, fontweight='bold', color='white')
            ax3.set_xlabel('Lap', fontsize=10, color='white')
            ax3.set_yticks(range(len(drivers[:5])))
            ax3.set_yticklabels(drivers[:5], color='white')
            ax3.set_facecolor('#0F0F0F')
            plt.colorbar(im, ax=ax3)
        
        # Add F1 styling
        fig.text(0.5, 0.98, 'F1 RACE RELAY', fontsize=24, fontweight='bold',
                color='#FF1801', ha='center', fontfamily='monospace')
        fig.text(0.5, 0.95, 'Professional Racing Analytics', fontsize=12,
                color='white', ha='center', fontfamily='sans-serif')
        
        plt.tight_layout()
        
        # Save with high quality
        os.makedirs('modern_plots', exist_ok=True)
        filename = f'modern_plots/{year}_{track}_lap_comparison.png'
        plt.savefig(filename, dpi=300, facecolor='#0F0F0F', bbox_inches='tight')
        plt.close()
        
        print(f"Modern plot saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error creating modern plot: {e}")
        return None

def create_interactive_race_replay(year, track):
    """Create an interactive Plotly race replay"""
    try:
        session = fastf1.get_session(year, track, 'R')
        session.load()
        
        # Get top 10 drivers
        top_drivers = session.results['Abbreviation'].head(10).tolist()
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Race Position Timeline', 'Speed Telemetry',
                          'Tire Strategy', 'Gap to Leader'),
            vertical_spacing=0.15,
            horizontal_spacing=0.15
        )
        
        # Position timeline
        for driver in top_drivers[:5]:
            laps = session.laps.pick_driver(driver)
            if not laps.empty:
                fig.add_trace(
                    go.Scatter(x=laps['LapNumber'], y=laps['Position'],
                              name=driver, mode='lines+markers',
                              line=dict(width=3)),
                    row=1, col=1
                )
        
        # Speed trace for one driver
        if top_drivers:
            driver_laps = session.laps.pick_driver(top_drivers[0])
            if not driver_laps.empty and 'Speed' in driver_laps.columns:
                fig.add_trace(
                    go.Scatter(x=driver_laps['LapNumber'], 
                              y=driver_laps['Speed'],
                              name=f"{top_drivers[0]} Speed",
                              line=dict(color='#FF1801', width=2)),
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
            height=800
        )
        
        # Save interactive plot
        os.makedirs('interactive_plots', exist_ok=True)
        filename = f'interactive_plots/{year}_{track}_interactive.html'
        fig.write_html(filename)
        
        print(f"Interactive plot saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error creating interactive plot: {e}")
        return None

def create_podium_visualization(year, track):
    """Create a podium visualization with driver photos"""
    try:
        session = fastf1.get_session(year, track, 'R')
        session.load()
        
        fig, ax = plt.subplots(figsize=(12, 8), facecolor='#0F0F0F')
        
        # Get top 3 drivers
        top3 = session.results.head(3)
        
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
            driver_name = driver['FullName'].split()[-1]  # Last name only
            team = driver['TeamName']
            
            # Position number
            ax.text(positions[i], podium_heights[i] + 0.1, str(i+1),
                   fontsize=40, fontweight='bold', ha='center',
                   color=podium_colors[i], fontfamily='monospace')
            
            # Driver name
            ax.text(positions[i], podium_heights[i] - 0.2, driver_name,
                   fontsize=14, fontweight='bold', ha='center',
                   color='white', fontfamily='sans-serif')
            
            # Team name
            ax.text(positions[i], podium_heights[i] - 0.5, team,
                   fontsize=10, ha='center', color='white', alpha=0.8)
            
            # Time
            if pd.notna(driver['Time']):
                ax.text(positions[i], -0.2, str(driver['Time']),
                       fontsize=11, ha='center', color='white')
        
        # Style the plot
        ax.set_xlim(-2, 2)
        ax.set_ylim(-0.5, 4)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add title
        ax.text(0, 3.8, f'{year} {track} GRAND PRIX',
               fontsize=24, fontweight='bold', ha='center',
               color='#FF1801', fontfamily='Arial Black')
        
        ax.text(0, 3.5, 'PODIUM FINISHERS',
               fontsize=16, ha='center', color='white', fontfamily='sans-serif')
        
        # Add F1 logo style
        ax.text(0, -0.4, 'F1 RACE RELAY',
               fontsize=18, fontweight='bold', ha='center',
               color='#FF1801', fontfamily='monospace')
        
        plt.tight_layout()
        
        # Save
        os.makedirs('podium_plots', exist_ok=True)
        filename = f'podium_plots/{year}_{track}_podium.png'
        plt.savefig(filename, dpi=300, facecolor='#0F0F0F', bbox_inches='tight')
        plt.close()
        
        print(f"Podium visualization saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error creating podium visualization: {e}")
        return None

def create_dashboard(year, track):
    """Create a comprehensive race dashboard"""
    try:
        session = fastf1.get_session(year, track, 'R')
        session.load()
        
        # Create a figure with multiple subplots
        fig = plt.figure(figsize=(20, 12), facecolor='#0A0A0A')
        gs = fig.add_gridspec(3, 4, hspace=0.4, wspace=0.3)
        
        # 1. Race Results (Table-like visualization)
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.axis('tight')
        ax1.axis('off')
        
        results_data = []
        for i in range(min(8, len(session.results))):
            driver = session.results.iloc[i]
            results_data.append([
                i+1,
                driver['Abbreviation'],
                driver['FullName'][:15],
                driver['TeamName'][:12],
                str(driver['Time']) if pd.notna(driver['Time']) else 'DNF'
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
        
        for driver in top_drivers:
            laps = session.laps.pick_driver(driver)
            if not laps.empty:
                fastest = laps.pick_fastest()
                fastest_times.append(fastest['LapTime'].total_seconds())
        
        bars = ax2.barh(top_drivers[:len(fastest_times)], fastest_times,
                       color=['#FF1801', '#00D2BE', '#FFFFFF', 
                              '#FF8700', '#0090FF', '#9B0000'])
        ax2.set_xlabel('Fastest Lap Time (seconds)', color='white')
        ax2.set_title('FASTEST LAP ANALYSIS', fontsize=14,
                     fontweight='bold', color='white')
        ax2.tick_params(colors='white')
        ax2.set_facecolor('#0F0F0F')
        
        # 3. Position Changes (Heatmap)
        ax3 = fig.add_subplot(gs[1, :])
        
        position_matrix = []
        drivers_for_heatmap = session.results['Abbreviation'].head(10).tolist()
        
        for driver in drivers_for_heatmap:
            laps = session.laps.pick_driver(driver)
            if not laps.empty and len(laps) > 10:
                positions = laps['Position'].values[:30]  # First 30 laps
                position_matrix.append(positions)
        
        if position_matrix:
            im = ax3.imshow(position_matrix, cmap='viridis', aspect='auto')
            ax3.set_title('POSITION CHANGES - FIRST 30 LAPS', fontsize=14,
                         fontweight='bold', color='white', pad=15)
            ax3.set_xlabel('Lap Number', color='white')
            ax3.set_ylabel('Driver', color='white')
            ax3.set_yticks(range(len(drivers_for_heatmap)))
            ax3.set_yticklabels(drivers_for_heatmap, color='white')
            ax3.set_facecolor('#0F0F0F')
            plt.colorbar(im, ax=ax3)
        
        # 4. Tire Strategy
        ax4 = fig.add_subplot(gs[2, :2])
        
        # Sample tire strategy for a few drivers
        drivers_for_tires = session.results['Abbreviation'].head(3).tolist()
        
        for idx, driver in enumerate(drivers_for_tires):
            laps = session.laps.pick_driver(driver)
            if not laps.empty:
                tire_stints = []
                current_tire = None
                stint_start = 0
                
                for lap_num, lap in laps.iterrows():
                    if current_tire is None:
                        current_tire = lap['Compound']
                        stint_start = lap['LapNumber']
                    elif lap['Compound'] != current_tire or lap_num == len(laps)-1:
                        tire_stints.append((stint_start, lap['LapNumber'], current_tire))
                        current_tire = lap['Compound']
                        stint_start = lap['LapNumber']
                
                # Plot tire stints
                colors = {'SOFT': '#FF6B6B', 'MEDIUM': '#FFD166', 'HARD': '#A0C4FF'}
                for stint in tire_stints:
                    start, end, compound = stint
                    if compound in colors:
                        ax4.barh(idx, end-start, left=start, height=0.6,
                                color=colors[compound], edgecolor='white')
                        ax4.text(start + (end-start)/2, idx, compound[0],
                               ha='center', va='center', color='black',
                               fontweight='bold')
        
        ax4.set_xlabel('Lap Number', color='white')
        ax4.set_ylabel('Driver', color='white')
        ax4.set_yticks(range(len(drivers_for_tires)))
        ax4.set_yticklabels(drivers_for_tires, color='white')
        ax4.set_title('TIRE STRATEGY', fontsize=14,
                     fontweight='bold', color='white')
        ax4.set_facecolor('#0F0F0F')
        
        # 5. Race Statistics
        ax5 = fig.add_subplot(gs[2, 2:])
        ax5.axis('off')
        
        stats_text = [
            f"RACE STATISTICS - {year} {track}",
            "="*30,
            f"Total Laps: {session.total_laps}",
            f"Track Length: {session.track_length} km",
            f"Winner: {session.results['FullName'].iloc[0]}",
            f"Winning Team: {session.results['TeamName'].iloc[0]}",
            f"Fastest Lap: {session.laps.pick_fastest()['LapTime']}",
            f"Fastest Driver: {session.laps.pick_fastest()['Driver']}",
            f"Number of Finishers: {len(session.results)}"
        ]
        
        for i, line in enumerate(stats_text):
            color = '#FF1801' if i < 2 else 'white'
            weight = 'bold' if i < 2 else 'normal'
            ax5.text(0.1, 0.9 - i*0.1, line,
                    transform=ax5.transAxes, fontsize=11,
                    color=color, fontweight=weight,
                    verticalalignment='top')
        
        # Main title
        fig.suptitle('F1 RACE RELAY - PROFESSIONAL DASHBOARD',
                    fontsize=28, fontweight='bold',
                    color='#FF1801', fontfamily='monospace',
                    y=0.98)
        
        fig.text(0.5, 0.95, 'Advanced Racing Analytics & Visualization',
                fontsize=16, color='white', ha='center',
                fontfamily='sans-serif')
        
        plt.tight_layout()
        
        os.makedirs('dashboards', exist_ok=True)
        filename = f'dashboards/{year}_{track}_dashboard.png'
        plt.savefig(filename, dpi=300, facecolor='#0A0A0A', bbox_inches='tight')
        plt.close()
        
        print(f"Dashboard saved: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error creating dashboard: {e}")
        return None

def generate_all_visuals(year, track):
    """Generate all modern visualizations"""
    print(f"\n{'='*60}")
    print(f"GENERATING MODERN VISUALS: {year} {track}")
    print('='*60)
    
    drivers = ['HAM', 'VER', 'LEC', 'NOR', 'SAI']  # Example drivers

    print("\n1. Creating lap comparison...")
    create_modern_lap_comparison(year, track, drivers)
    
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

if __name__ == "__main__":
    generate_all_visuals(2023, 'Monaco')
