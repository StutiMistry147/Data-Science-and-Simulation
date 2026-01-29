import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox, QFrame, QTextEdit, QGridLayout, 
    QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import fastf1
import pandas as pd

class ModernF1GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 Race Relay")
        self.setGeometry(50, 50, 1200, 800)
        
        # Simple dark theme
        self.setStyleSheet("""
            QMainWindow { background-color: #0d1117; }
            QLabel { color: #c9d1d9; }
            QComboBox {
                background-color: #161b22; color: #c9d1d9; border: 1px solid #30363d; 
                border-radius: 6px; padding: 8px; font-size: 13px;
            }
            QComboBox:hover { border-color: #58a6ff; }
            QPushButton {
                background-color: #21262d; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; padding: 10px 16px; font-size: 13px;
            }
            QPushButton:hover { background-color: #30363d; border-color: #58a6ff; }
            QTextEdit {
                background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d;
                border-radius: 6px; font-family: 'Courier New', monospace; font-size: 12px;
            }
            QGroupBox {
                color: #c9d1d9; border: 1px solid #30363d; border-radius: 8px;
                margin-top: 10px; padding-top: 15px; font-size: 13px; font-weight: 500;
            }
            QProgressBar {
                border: 1px solid #30363d; border-radius: 3px; background-color: #0d1117;
                height: 4px;
            }
            QProgressBar::chunk { background-color: #238636; border-radius: 2px; }
        """)
        
        # Available years and tracks (only those with good data)
        self.years = ['2023', '2022', '2021']
        self.tracks = ['Bahrain', 'Monaco', 'Silverstone', 'Spa', 'Monza', 'Hungaroring', 'Suzuka']
        
        self.init_ui()
        
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("F1 Race Relay")
        title.setStyleSheet("font-size: 24px; font-weight: 300; color: #ffffff;")
        header.addWidget(title)
        header.addStretch()
        author = QLabel("Stuti Mistry")
        author.setStyleSheet("color: #8b949e; font-size: 12px;")
        header.addWidget(author)
        main_layout.addLayout(header)
        
        # Control section
        control_grid = QGridLayout()
        control_grid.setVerticalSpacing(8)
        control_grid.setHorizontalSpacing(15)
        
        # Labels
        labels = ["Season", "Grand Prix", "Driver 1", "Driver 2"]
        for i, text in enumerate(labels[:2]):
            label = QLabel(text)
            label.setStyleSheet("color: #8b949e; font-size: 11px; font-weight: 500;")
            control_grid.addWidget(label, 0, i*3)
        
        # Comboboxes
        self.year_combo = QComboBox()
        self.year_combo.addItems(self.years)
        self.year_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.track_combo = QComboBox()
        self.track_combo.addItems(self.tracks)
        self.track_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        drivers = ['HAM', 'VER', 'LEC', 'NOR', 'SAI', 'RUS']
        self.driver1_combo = QComboBox()
        self.driver1_combo.addItems(drivers)
        self.driver1_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.driver2_combo = QComboBox()
        self.driver2_combo.addItems(drivers)
        self.driver2_combo.setCurrentText('VER')
        self.driver2_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Add to grid
        control_grid.addWidget(self.year_combo, 1, 0, 1, 3)
        control_grid.addWidget(self.track_combo, 1, 3, 1, 3)
        control_grid.addWidget(self.driver1_combo, 3, 0, 1, 3)
        control_grid.addWidget(self.driver2_combo, 3, 3, 1, 3)
        
        main_layout.addLayout(control_grid)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("LOAD RACE DATA")
        self.load_btn.setFixedHeight(40)
        self.load_btn.clicked.connect(self.load_race_data)
        self.load_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.visualize_btn = QPushButton("GENERATE VISUALS")
        self.visualize_btn.setFixedHeight(40)
        self.visualize_btn.clicked.connect(self.generate_visuals)
        self.visualize_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.compare_btn = QPushButton("COMPARE DRIVERS")
        self.compare_btn.setFixedHeight(40)
        self.compare_btn.clicked.connect(self.compare_drivers)
        self.compare_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.visualize_btn)
        button_layout.addWidget(self.compare_btn)
        
        main_layout.addLayout(button_layout)
        
        # Content area
        content = QHBoxLayout()
        content.setSpacing(20)
        
        # Left panel - Stats
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: transparent;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        
        # Stats cards (simplified)
        stats_data = [
            ("Race Info", [
                ("Year", "2023"),
                ("Track", "Monaco"),
                ("Laps", "78"),
                ("Winner", "Verstappen")
            ], "#238636"),
            ("Fastest Lap", [
                ("Driver", "Hamilton"),
                ("Time", "1:12.909"),
                ("Lap", "44"),
                ("Tire", "Medium")
            ], "#1f6feb")
        ]
        
        for title, items, color in stats_data:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: #161b22;
                    border-radius: 8px;
                    border-left: 3px solid {color};
                }}
            """)
            
            layout = QVBoxLayout(card)
            layout.setContentsMargins(15, 15, 15, 15)
            layout.setSpacing(10)
            
            title_label = QLabel(title)
            title_label.setStyleSheet(f"""
                color: {color};
                font-size: 13px;
                font-weight: 500;
            """)
            layout.addWidget(title_label)
            
            for label, value in items:
                item_layout = QHBoxLayout()
                label_widget = QLabel(label)
                label_widget.setStyleSheet("color: #8b949e; font-size: 11px;")
                item_layout.addWidget(label_widget)
                item_layout.addStretch()
                value_widget = QLabel(value)
                value_widget.setStyleSheet("color: #c9d1d9; font-size: 11px; font-weight: 500;")
                item_layout.addWidget(value_widget)
                layout.addLayout(item_layout)
            
            left_layout.addWidget(card)
        
        left_layout.addStretch()
        content.addWidget(left_panel, 1)
        
        # Right panel - Results
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: transparent;")
        right_layout = QVBoxLayout(right_panel)
        
        # Results header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #161b22; border-radius: 6px; padding: 12px;")
        header_layout = QHBoxLayout(header_frame)
        
        results_label = QLabel("RACE RESULTS")
        results_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        header_layout.addWidget(results_label)
        
        header_layout.addStretch()
        
        self.results_status = QLabel("Ready")
        self.results_status.setStyleSheet("color: #238636; font-size: 11px;")
        header_layout.addWidget(self.results_status)
        
        right_layout.addWidget(header_frame)
        
        # Results display
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.results_display.setMinimumHeight(400)
        right_layout.addWidget(self.results_display)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        right_layout.addWidget(self.progress_bar)
        
        content.addWidget(right_panel, 2)
        main_layout.addLayout(content)
        
        # Status bar
        self.status_bar = QLabel("Ready to analyze Formula 1 races")
        self.status_bar.setStyleSheet("color: #8b949e; font-size: 11px; padding-top: 5px;")
        main_layout.addWidget(self.status_bar)
        
        # Footer
        footer_label = QLabel("F1 Race Relay v1.0")
        footer_label.setStyleSheet("color: #484f58; font-size: 10px;")
        footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_label)
        
    def update_progress(self, value, message):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)
        self.status_bar.setText(message)
        QApplication.processEvents()
    
    def load_race_data(self):
        year = self.year_combo.currentText()
        track = self.track_combo.currentText()
        
        self.progress_bar.setVisible(True)
        self.results_status.setText("Loading...")
        self.results_status.setStyleSheet("color: #d29922; font-size: 11px;")
        self.update_progress(10, f"Loading {year} {track}...")
        
        try:
            session = fastf1.get_session(int(year), track, 'R')
            self.update_progress(30, "Downloading data...")
            session.load(telemetry=False, weather=False)
            
            self.update_progress(70, "Processing results...")
            
            # Format results
            results_text = f"{'='*80}\n"
            results_text += f"{year} {track.upper()} GRAND PRIX - RESULTS\n"
            results_text += f"{'='*80}\n\n"
            
            # Race info
            event_date = session.event.get('EventDate', 'N/A')
            official_name = session.event.get('OfficialEventName', 'N/A')
            
            results_text += f"Date: {event_date}\n"
            results_text += f"Circuit: {official_name}\n"
            
            if hasattr(session, 'total_laps'):
                results_text += f"Total Laps: {session.total_laps}\n"
            results_text += "\n"
            
            # Results table
            results_text += f"{'POS':^4} {'DRIVER':^20} {'TEAM':^20} {'TIME':^15}\n"
            results_text += f"{'-'*80}\n"
            
            if hasattr(session, 'results') and len(session.results) > 0:
                for i in range(min(15, len(session.results))):
                    driver = session.results.iloc[i]
                    
                    pos = str(i + 1)
                    name = driver.get('FullName', 'N/A')
                    if len(name) > 18:
                        name = name[:15] + "..."
                    
                    team = driver.get('TeamName', 'N/A')
                    if len(team) > 18:
                        team = team[:15] + "..."
                    
                    time_val = driver.get('Time', 'DNF')
                    if pd.notna(time_val):
                        time = str(time_val)[:12]
                    else:
                        time = "DNF"
                    
                    results_text += f"{pos:^4} {name:^20} {team:^20} {time:^15}\n"
                
                results_text += f"\n{'='*80}\n"
                results_text += f"Total drivers: {len(session.results)}\n"
                
                # Fastest lap
                if not session.laps.empty:
                    try:
                        fastest = session.laps.pick_fastest()
                        fastest_time = fastest.get('LapTime', 'N/A')
                        fastest_driver = fastest.get('Driver', 'N/A')
                        results_text += f"Fastest lap: {fastest_time} ({fastest_driver})\n"
                    except:
                        pass
            else:
                results_text += "No race results available\n"
            
            self.results_display.setText(results_text)
            self.results_status.setText("Loaded")
            self.results_status.setStyleSheet("color: #238636; font-size: 11px;")
            self.update_progress(100, f"Successfully loaded {year} {track}")
            
        except Exception as e:
            error_msg = f"Error loading data:\n{str(e)}\n\n"
            error_msg += "Try these combinations:\n"
            error_msg += "- 2023 Monaco\n- 2023 Bahrain\n- 2022 Silverstone\n- 2021 Monza"
            self.results_display.setText(error_msg)
            self.results_status.setText("Error")
            self.results_status.setStyleSheet("color: #f85149; font-size: 11px;")
            self.status_bar.setText(f"Error: {str(e)[:50]}")
        
        finally:
            QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
    
    def generate_visuals(self):
        year = self.year_combo.currentText()
        track = self.track_combo.currentText()
        
        self.status_bar.setText(f"Generating visualizations for {year} {track}...")
        
        if not os.path.exists("modern_plots.py"):
            error_msg = "modern_plots.py not found!\n"
            error_msg += "Please make sure the file is in the same folder."
            self.results_display.setText(error_msg)
            self.results_status.setText("Error")
            self.results_status.setStyleSheet("color: #f85149; font-size: 11px;")
            return
        
        try:
            import modern_plots
            import importlib
            importlib.reload(modern_plots)
            
            modern_plots.generate_all_visuals(int(year), track)
            
            self.results_status.setText("Visuals Ready")
            self.results_status.setStyleSheet("color: #238636; font-size: 11px;")
            self.status_bar.setText(f"Visualizations generated! Check output folders.")
            
        except Exception as e:
            self.results_status.setText("Error")
            self.results_status.setStyleSheet("color: #f85149; font-size: 11px;")
            self.status_bar.setText(f"Error: {str(e)[:50]}")
    
    def compare_drivers(self):
        driver1 = self.driver1_combo.currentText()
        driver2 = self.driver2_combo.currentText()
        year = self.year_combo.currentText()
        track = self.track_combo.currentText()
        
        if driver1 == driver2:
            self.status_bar.setText("Please select two different drivers")
            return
        
        self.results_status.setText("Comparing...")
        self.results_status.setStyleSheet("color: #d29922; font-size: 11px;")
        self.status_bar.setText(f"Comparing {driver1} vs {driver2} at {year} {track}...")
        
        try:
            session = fastf1.get_session(int(year), track, 'R')
            session.load()
            
            laps1 = session.laps.pick_driver(driver1)
            laps2 = session.laps.pick_driver(driver2)
            
            if laps1.empty or laps2.empty:
                self.results_status.setText("Error")
                self.results_status.setStyleSheet("color: #f85149; font-size: 11px;")
                self.status_bar.setText(f"No data for one or both drivers")
                return
            
            # Create comparison text
            comp_text = f"{'='*60}\n"
            comp_text += f"DRIVER COMPARISON: {driver1} vs {driver2}\n"
            comp_text += f"Race: {year} {track}\n"
            comp_text += f"{'='*60}\n\n"
            
            # Fastest lap
            fastest1 = laps1.pick_fastest()
            fastest2 = laps2.pick_fastest()
            
            comp_text += "FASTEST LAP:\n"
            comp_text += f"  {driver1}: {fastest1['LapTime']} (Lap {fastest1['LapNumber']})\n"
            comp_text += f"  {driver2}: {fastest2['LapTime']} (Lap {fastest2['LapNumber']})\n\n"
            
            # Time difference
            time1 = fastest1['LapTime'].total_seconds()
            time2 = fastest2['LapTime'].total_seconds()
            diff = abs(time1 - time2)
            faster = driver1 if time1 < time2 else driver2
            comp_text += f"  {faster} was {diff:.3f}s faster\n\n"
            
            # Finishing position
            final_pos1 = session.results[session.results['Abbreviation'] == driver1]
            final_pos2 = session.results[session.results['Abbreviation'] == driver2]
            
            if not final_pos1.empty and not final_pos2.empty:
                pos1 = final_pos1.iloc[0].get('Position', 'N/A')
                pos2 = final_pos2.iloc[0].get('Position', 'N/A')
                comp_text += f"FINISHING POSITION:\n"
                comp_text += f"  {driver1}: P{pos1}\n"
                comp_text += f"  {driver2}: P{pos2}\n"
            
            self.results_display.setText(comp_text)
            self.results_status.setText("Comparison")
            self.results_status.setStyleSheet("color: #238636; font-size: 11px;")
            self.status_bar.setText(f"Comparison complete: {driver1} vs {driver2}")
            
        except Exception as e:
            error_msg = f"Error comparing drivers:\n{str(e)}\n"
            self.results_display.setText(error_msg)
            self.results_status.setText("Error")
            self.results_status.setStyleSheet("color: #f85149; font-size: 11px;")
            self.status_bar.setText(f"Error: {str(e)[:50]}")

def main():
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = ModernF1GUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
