import os
import sys
import subprocess
from datetime import datetime

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   ███████╗ ██╗    ██████╗  █████╗ ███████╗███████╗       ║
    ║   ██╔════╝███║    ██╔══██╗██╔══██╗██╔════╝██╔════╝       ║
    ║   █████╗  ╚██║    ██████╔╝███████║█████╗  █████╗         ║
    ║   ██╔══╝   ██║    ██╔══██╗██╔══██║██╔══╝  ██╔══╝         ║
    ║   ██║      ██║    ██║  ██║██║  ██║███████╗███████╗       ║
    ║   ╚═╝      ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝       ║
    ║                                                          ║
    ║   ██████╗  █████╗  █████╗ ███████╗                       ║
    ║   ██╔══██╗██╔══██╗██╔══██╗██╔════╝                       ║
    ║   ██████╔╝███████║███████║█████╗                         ║
    ║   ██╔══██╗██╔══██║██╔══██║██╔══╝                         ║
    ║   ██║  ██║██║  ██║██║  ██║███████╗                       ║
    ║   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝                       ║
    ║                                                          ║
    ║   F1 Race Relay                                          ║
    ║                                                          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    print("Checking dependencies...")
    
    required = ['fastf1', 'pandas', 'matplotlib', 'seaborn', 'plotly', 'PySide6']
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"    ✓ Installed {package}")
            except:
                print(f"    ✗ Failed to install {package}")
                return False
    
    print("All dependencies installed\n")
    return True

def create_project_structure():
    print("Creating project structure...")
    
    folders = ['modern_plots', 'interactive_plots', 'podium_plots', 
               'dashboards', 'exports', 'data_cache']
    
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"  Created: {folder}/")
        else:
            print(f"  ✓ {folder}/")
    
    print("Project structure ready\n")

def main_menu():
    while True:
        print("\n" + "═" * 60)
        print("F1 RACE RELAY - MAIN MENU")
        print("═" * 60)
        print("1. Launch Modern GUI Application")
        print("2. Generate Professional Visualizations")
        print("3. Run Data Analysis Tools")
        print("4. Test FastF1 Connection")
        print("5. Update Data Cache")
        print("6. Open Output Folder")
        print("7. Exit")
        print("═" * 60)
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == "1":
            print("\nLaunching Modern GUI...")
            subprocess.run([sys.executable, "modern_gui.py"])
            
        elif choice == "2":
            print("\nGenerating visualizations...")
            year = input("Enter year (e.g., 2023): ").strip()
            track = input("Enter track name (e.g., Monaco): ").strip()
            
            if year and track:
                # Import and run visualization
                import modern_plots
                modern_plots.generate_all_visuals(int(year), track)
            else:
                print("Using default: Monaco 2023")
                import modern_plots
                modern_plots.generate_all_visuals(2023, 'Monaco')
            
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            print("\nRunning analysis tools...")
            subprocess.run([sys.executable, "main.py"])
            
        elif choice == "4":
            print("\nTesting FastF1 connection...")
            try:
                import fastf1
                session = fastf1.get_session(2023, 'Monaco', 'R')
                session.load(telemetry=False, weather=False)
                print(f"Success! Loaded {len(session.laps)} laps")
                print(f"   Event: {session.event['EventName']}")
                print(f"   Drivers: {len(session.results)}")
            except Exception as e:
                print(f"Connection failed: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            print("\nUpdating data cache...")
            try:
                import fastf1
                # Enable caching
                fastf1.Cache.enable_cache('data_cache')
                print("Cache enabled in 'data_cache/' folder")
            except Exception as e:
                print(f"Error: {e}")
            
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            print("\nOpening output folder...")
            if sys.platform == "win32":
                os.startdir(".")
            elif sys.platform == "darwin":
                subprocess.run(["open", "."])
            else:
                subprocess.run(["xdg-open", "."])
            
        elif choice == "7":
            print("\nThank you for using F1 Race Relay!")
            print("   Follow @tom.developer for updates!")
            break
            
        else:
            print("\nInvalid choice. Please enter 1-7.")

if __name__ == "__main__":
    print_banner()
    
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python {sys.version.split()[0]}")
    print()
    
    if check_dependencies():
        create_project_structure()
        main_menu()
