import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import datetime
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import fastf1
from lap_analyser import setup_cache, load_session, best_laps_dataframe


class F1RealTimeAnalyser:
    def __init__(self, root):
        self.root = root
        self.root.title("🏎️ F1 Real-Time Lap Analyser")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Variables
        self.current_session = None
        self.is_monitoring = False
        self.last_update = None
        self.cache_dir = os.path.expanduser("~/.fastf1-cache")
        
        # Style configuration
        self.setup_styles()
        
        # Setup GUI
        self.create_widgets()
        
        # Setup cache
        setup_cache(self.cache_dir)
        
        # Start checking for live sessions
        self.check_live_sessions()
    
    def setup_styles(self):
        """Configure custom styles for the GUI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       background='#1a1a2e',
                       foreground='#ffffff')
        
        style.configure('Header.TLabel',
                       font=('Arial', 12, 'bold'),
                       background='#16213e',
                       foreground='#00ff88')
        
        style.configure('Status.TLabel',
                       font=('Arial', 10),
                       background='#1a1a2e',
                       foreground='#ffaa00')
    
    def create_widgets(self):
        """Create the main GUI layout"""
        
        # Main title
        title_frame = tk.Frame(self.root, bg='#1a1a2e')
        title_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = ttk.Label(title_frame, text="🏎️ F1 Real-Time Lap Analyser", style='Title.TLabel')
        title_label.pack()
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#16213e', relief='ridge', bd=2)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Checking for live sessions...", style='Status.TLabel')
        self.status_label.pack(pady=5)
        
        self.last_update_label = ttk.Label(status_frame, text="", style='Status.TLabel')
        self.last_update_label.pack()
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#1a1a2e')
        control_frame.pack(fill='x', padx=10, pady=5)
        
        self.refresh_btn = tk.Button(control_frame, text="🔄 Refresh", 
                                   command=self.manual_refresh,
                                   bg='#00aa44', fg='white', font=('Arial', 10, 'bold'))
        self.refresh_btn.pack(side='left', padx=5)
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_cb = tk.Checkbutton(control_frame, text="Auto Refresh (30s)",
                                       variable=self.auto_refresh_var,
                                       bg='#1a1a2e', fg='white',
                                       selectcolor='#16213e')
        auto_refresh_cb.pack(side='left', padx=10)
        
        # Main content notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Live session tab
        self.live_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.live_frame, text="🔴 Live Session")
        self.setup_live_tab()
        
        # Historical data tab
        self.historical_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.historical_frame, text="📊 Historical Data")
        self.setup_historical_tab()
        
        # No session content tab
        self.offline_frame = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.offline_frame, text="📺 F1 Info")
        self.setup_offline_tab()
    
    def setup_live_tab(self):
        """Setup the live session monitoring tab"""
        
        # Live session info
        info_frame = tk.LabelFrame(self.live_frame, text="Session Information", 
                                  bg='#16213e', fg='white', font=('Arial', 10, 'bold'))
        info_frame.pack(fill='x', padx=10, pady=5)
        
        self.session_info_text = scrolledtext.ScrolledText(info_frame, height=6, 
                                                          bg='#0f0f23', fg='#00ff88',
                                                          font=('Courier', 9))
        self.session_info_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Live timing table
        timing_frame = tk.LabelFrame(self.live_frame, text="Live Timing", 
                                   bg='#16213e', fg='white', font=('Arial', 10, 'bold'))
        timing_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Treeview for timing data
        columns = ('Position', 'Driver', 'Team', 'Best Lap', 'Last Lap', 'Gap')
        self.timing_tree = ttk.Treeview(timing_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.timing_tree.heading(col, text=col)
            self.timing_tree.column(col, width=100, anchor='center')
        
        # Scrollbar for treeview
        timing_scroll = ttk.Scrollbar(timing_frame, orient='vertical', command=self.timing_tree.yview)
        self.timing_tree.configure(yscrollcommand=timing_scroll.set)
        
        self.timing_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        timing_scroll.pack(side='right', fill='y')
    
    def setup_historical_tab(self):
        """Setup historical data analysis tab"""
        
        # Session selector
        selector_frame = tk.LabelFrame(self.historical_frame, text="Select Session", 
                                     bg='#16213e', fg='white', font=('Arial', 10, 'bold'))
        selector_frame.pack(fill='x', padx=10, pady=5)
        
        # Year selection
        current_year = datetime.datetime.now().year
        tk.Label(selector_frame, text="Year:", bg='#16213e', fg='white').grid(row=0, column=0, padx=5, pady=5)
        self.year_var = tk.StringVar(value=str(current_year))
        year_combo = ttk.Combobox(selector_frame, textvariable=self.year_var, 
                                 values=[str(y) for y in range(2018, current_year + 1)], width=10)
        year_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # GP selection
        tk.Label(selector_frame, text="Grand Prix:", bg='#16213e', fg='white').grid(row=0, column=2, padx=5, pady=5)
        self.gp_var = tk.StringVar(value="Monza")
        gp_combo = ttk.Combobox(selector_frame, textvariable=self.gp_var, 
                               values=["Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami", "Monaco",
                                     "Spain", "Canada", "Austria", "Great Britain", "Hungary", "Belgium", 
                                     "Netherlands", "Italy", "Singapore", "Japan", "Qatar", "United States",
                                     "Mexico", "Brazil", "Las Vegas", "Abu Dhabi"], width=15)
        gp_combo.grid(row=0, column=3, padx=5, pady=5)
        
        # Session selection
        tk.Label(selector_frame, text="Session:", bg='#16213e', fg='white').grid(row=0, column=4, padx=5, pady=5)
        self.session_var = tk.StringVar(value="Q")
        session_combo = ttk.Combobox(selector_frame, textvariable=self.session_var, 
                                   values=["FP1", "FP2", "FP3", "Q", "R"], width=8)
        session_combo.grid(row=0, column=5, padx=5, pady=5)
        
        # Load button
        load_btn = tk.Button(selector_frame, text="Load Session", 
                           command=self.load_historical_session,
                           bg='#0066cc', fg='white', font=('Arial', 9, 'bold'))
        load_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Results display
        results_frame = tk.LabelFrame(self.historical_frame, text="Session Results", 
                                    bg='#16213e', fg='white', font=('Arial', 10, 'bold'))
        results_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, 
                                                    bg='#0f0f23', fg='#ffffff',
                                                    font=('Courier', 9))
        self.results_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_offline_tab(self):
        """Setup the offline content tab for when no live sessions are available"""
        
        # F1 Calendar
        current_year = datetime.datetime.now().year
        calendar_frame = tk.LabelFrame(self.offline_frame, text=f"{current_year} F1 Calendar", 
                                     bg='#16213e', fg='white', font=('Arial', 10, 'bold'))
        calendar_frame.pack(fill='x', padx=10, pady=5)
        
        calendar_text = scrolledtext.ScrolledText(calendar_frame, height=8,
                                                bg='#0f0f23', fg='#ffaa00',
                                                font=('Courier', 9))
        calendar_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add F1 calendar information - dynamically generate based on current year
        current_year = datetime.datetime.now().year
        
        if current_year == 2025:
            calendar_info = """
F1 2025 RACE CALENDAR:
═══════════════════════════════════════════════════════════════
Round  Date           Grand Prix              Circuit
═══════════════════════════════════════════════════════════════
1      Mar 16         Bahrain GP             Bahrain International Circuit
2      Mar 23         Saudi Arabian GP       Jeddah Corniche Circuit  
3      Apr 6          Australian GP          Melbourne Grand Prix Circuit
4      Apr 13         Japanese GP            Suzuka Circuit
5      Apr 27         Chinese GP             Shanghai International Circuit
6      May 4          Miami GP               Miami International Autodrome
7      May 18         Emilia Romagna GP      Autodromo Enzo e Dino Ferrari
8      May 25         Monaco GP              Circuit de Monaco
9      Jun 8          Canadian GP            Circuit Gilles Villeneuve
10     Jun 15         Spanish GP             Circuit de Barcelona-Catalunya
11     Jun 29         Austrian GP            Red Bull Ring
12     Jul 6          British GP             Silverstone Circuit
13     Jul 20         Hungarian GP           Hungaroring
14     Jul 27         Belgian GP             Circuit de Spa-Francorchamps
15     Aug 31         Dutch GP               Circuit Zandvoort
16     Sep 7          Italian GP             Autodromo Nazionale Monza
17     Sep 21         Azerbaijan GP          Baku City Circuit
18     Oct 5          Singapore GP           Marina Bay Street Circuit
19     Oct 19         United States GP       Circuit of the Americas
20     Oct 26         Mexican GP             Autodromo Hermanos Rodriguez
21     Nov 9          Brazilian GP           Interlagos Circuit
22     Nov 23         Las Vegas GP           Las Vegas Strip Circuit
23     Nov 30         Qatar GP               Lusail International Circuit
24     Dec 7          Abu Dhabi GP           Yas Marina Circuit

CURRENT DATE: """ + datetime.datetime.now().strftime("%B %d, %Y") + """
═══════════════════════════════════════════════════════════════
        """
        else:
            # Fallback for other years
            calendar_info = f"""
F1 {current_year} RACE CALENDAR:
═══════════════════════════════════════════════════════════════
Calendar data for {current_year} season would be displayed here.
Check official F1 website for exact dates and circuits.

CURRENT DATE: """ + datetime.datetime.now().strftime("%B %d, %Y") + """
═══════════════════════════════════════════════════════════════
        """
        
        calendar_text.insert('1.0', calendar_info)
        calendar_text.configure(state='disabled')
        
        # Statistics and info
        stats_frame = tk.LabelFrame(self.offline_frame, text="F1 Quick Stats", 
                                  bg='#16213e', fg='white', font=('Arial', 10, 'bold'))
        stats_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        stats_text = scrolledtext.ScrolledText(stats_frame,
                                             bg='#0f0f23', fg='#00ff88',
                                             font=('Courier', 9))
        stats_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        stats_info = """
F1 QUICK STATISTICS & RECORDS:
══════════════════════════════════════════════════════════════════

🏆 MOST WINS (ALL TIME):
   • Lewis Hamilton: 103 wins
   • Michael Schumacher: 91 wins  
   • Sebastian Vettel: 53 wins
   • Alain Prost: 51 wins
   • Ayrton Senna: 41 wins

🥇 MOST CHAMPIONSHIPS:
   • Lewis Hamilton: 7 titles
   • Michael Schumacher: 7 titles
   • Juan Manuel Fangio: 5 titles
   • Alain Prost: 4 titles
   • Sebastian Vettel: 4 titles

⚡ FASTEST LAP RECORDS:
   • Monza 2020: Lewis Hamilton - 1:18.887
   • Silverstone 2020: Max Verstappen - 1:27.097
   • Spa 2020: Daniel Ricciardo - 1:46.286

🏎️ CURRENT SEASON LEADERS (""" + str(datetime.datetime.now().year) + """):
   • Check live sessions for real-time standings
   • Use Historical Data tab to analyze past sessions
   • Monitor this tab during race weekends for updates

📊 SESSION TYPES:
   • FP1, FP2, FP3: Free Practice (90, 60, 60 minutes)
   • Q: Qualifying (Q1, Q2, Q3 knockout format)
   • R: Race (varies by circuit, ~300km or 2 hours max)

🔄 AUTO-REFRESH ENABLED
   This application automatically checks for live sessions every 30 seconds.
   When a session is detected, live timing data will appear in the Live Session tab.
        """
        
        stats_text.insert('1.0', stats_info)
        stats_text.configure(state='disabled')
    
    def check_live_sessions(self):
        """Check for live F1 sessions and update accordingly"""
        def check_thread():
            while True:
                try:
                    current_time = datetime.datetime.now()
                    
                    # Try to detect live session (this is a simulation - real implementation would use F1 API)
                    live_session = self.detect_live_session()
                    
                    if live_session:
                        self.update_status("🔴 LIVE SESSION DETECTED", "success")
                        self.load_live_session(live_session)
                        self.notebook.select(0)  # Switch to live tab
                    else:
                        self.update_status("⏱️ No live sessions - Showing offline content", "info")
                        self.notebook.select(2)  # Switch to offline tab
                    
                    self.last_update = current_time
                    self.update_last_update_display()
                    
                except Exception as e:
                    self.update_status(f"❌ Error checking sessions: {str(e)}", "error")
                
                # Wait 30 seconds before next check if auto-refresh is enabled
                for _ in range(30):
                    if not self.auto_refresh_var.get():
                        break
                    time.sleep(1)
                
                if not self.auto_refresh_var.get():
                    time.sleep(5)  # Still check periodically even if auto-refresh is off
        
        thread = threading.Thread(target=check_thread, daemon=True)
        thread.start()
    
    def detect_live_session(self):
        """Simulate live session detection - replace with real F1 API integration"""
        
        # This is a simulation - in reality, you'd check:
        # 1. F1 official timing API
        # 2. Current time vs race weekend schedule
        # 3. FastF1 live timing capabilities
        
        current_time = datetime.datetime.now()
        
        # For demo purposes, simulate a live session on weekends during F1 hours
        if current_time.weekday() >= 5:  # Saturday or Sunday
            hour = current_time.hour
            if 12 <= hour <= 18:  # Typical F1 session times (adjust for timezone)
                return {
                    'year': current_time.year,
                    'gp': 'Monaco',  # Simulated
                    'session': 'Q' if current_time.weekday() == 5 else 'R',
                    'type': 'Qualifying' if current_time.weekday() == 5 else 'Race'
                }
        
        return None
    
    def load_live_session(self, session_info):
        """Load and display live session data"""
        
        info_text = f"""
LIVE SESSION ACTIVE
═══════════════════════════════════════════════════════════════

📍 Event: {session_info['year']} {session_info['gp']} Grand Prix
🏁 Session: {session_info['type']} ({session_info['session']})
⏰ Status: LIVE
🔄 Last Update: {datetime.datetime.now().strftime('%H:%M:%S')}

═══════════════════════════════════════════════════════════════
        """
        
        self.session_info_text.delete('1.0', tk.END)
        self.session_info_text.insert('1.0', info_text)
        
        # Simulate live timing data
        self.update_live_timing()
    
    def update_live_timing(self):
        """Update the live timing display with simulated data"""
        
        # Clear existing items
        for item in self.timing_tree.get_children():
            self.timing_tree.delete(item)
        
        # Simulated live timing data
        drivers_data = [
            ("1", "VER", "Red Bull", "1:12.345", "1:12.567", "Leader"),
            ("2", "HAM", "Mercedes", "1:12.456", "1:12.678", "+0.111"),
            ("3", "LEC", "Ferrari", "1:12.567", "1:12.789", "+0.222"),
            ("4", "RUS", "Mercedes", "1:12.678", "1:12.890", "+0.333"),
            ("5", "SAI", "Ferrari", "1:12.789", "1:12.901", "+0.444"),
            ("6", "NOR", "McLaren", "1:12.890", "1:13.012", "+0.545"),
            ("7", "PIA", "McLaren", "1:12.901", "1:13.123", "+0.556"),
            ("8", "ALO", "Aston Martin", "1:13.012", "1:13.234", "+0.667"),
            ("9", "STR", "Aston Martin", "1:13.123", "1:13.345", "+0.778"),
            ("10", "GAS", "Alpine", "1:13.234", "1:13.456", "+0.889")
        ]
        
        for data in drivers_data:
            self.timing_tree.insert('', 'end', values=data)
    
    def load_historical_session(self):
        """Load historical session data"""
        
        def load_thread():
            try:
                year = int(self.year_var.get())
                gp = self.gp_var.get()
                session_type = self.session_var.get()
                
                self.update_status(f"Loading {year} {gp} {session_type}...", "info")
                
                session = load_session(year, gp, session_type)
                best_laps = best_laps_dataframe(session)
                
                # Format results
                results = f"""
SESSION LOADED: {year} {gp} {session_type}
═══════════════════════════════════════════════════════════════

TOP 10 BEST LAPS:
Pos  Driver  Team           Lap#  Compound  Time(s)
─────────────────────────────────────────────────────────────
"""
                
                for idx, row in best_laps.head(10).iterrows():
                    results += f"{idx+1:3d}  {row['Driver']:6s}  {row['Team']:12s}  {row['LapNumber']:4d}  {row['Compound']:8s}  {row['LapTime_s']:7.3f}\n"
                
                self.results_text.delete('1.0', tk.END)
                self.results_text.insert('1.0', results)
                
                self.update_status(f"✅ Loaded {year} {gp} {session_type}", "success")
                
            except Exception as e:
                error_msg = f"❌ Error loading session: {str(e)}"
                self.update_status(error_msg, "error")
                self.results_text.delete('1.0', tk.END)
                self.results_text.insert('1.0', f"ERROR:\n{str(e)}")
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def manual_refresh(self):
        """Manually refresh/check for sessions"""
        self.update_status("🔄 Refreshing...", "info")
        
        def refresh_thread():
            try:
                live_session = self.detect_live_session()
                if live_session:
                    self.load_live_session(live_session)
                    self.notebook.select(0)
                else:
                    self.notebook.select(2)
                
                self.last_update = datetime.datetime.now()
                self.update_last_update_display()
                self.update_status("✅ Refresh complete", "success")
                
            except Exception as e:
                self.update_status(f"❌ Refresh failed: {str(e)}", "error")
        
        thread = threading.Thread(target=refresh_thread, daemon=True)
        thread.start()
    
    def update_status(self, message, status_type="info"):
        """Update the status display"""
        colors = {
            "info": "#ffaa00",
            "success": "#00ff88", 
            "error": "#ff4444"
        }
        
        self.status_label.configure(text=message)
        # Note: ttk.Label doesn't support fg parameter directly in style
    
    def update_last_update_display(self):
        """Update the last update timestamp"""
        if self.last_update:
            time_str = self.last_update.strftime("Last update: %H:%M:%S")
            self.last_update_label.configure(text=time_str)


def main():
    """Main application entry point"""
    
    root = tk.Tk()
    app = F1RealTimeAnalyser(root)
    
    # Handle window closing
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit the F1 Analyser?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()