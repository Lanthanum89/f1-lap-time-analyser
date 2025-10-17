#!/usr/bin/env python3
"""
F1 Lap Time Analyser Launcher
Simple script to launch either CLI or GUI version
"""

import sys
import subprocess
import os

def main():
    print("🏎️  F1 Lap Time Analyser")
    print("=" * 35)
    print("1. Real-Time Desktop GUI (Tkinter) 🔴")
    print("2. Interactive Web GUI (Streamlit)")
    print("3. Command Line Interface")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            print("\n� Launching Real-Time Desktop GUI...")
            print("Features: Live session monitoring, auto-refresh, offline content")
            try:
                subprocess.run([sys.executable, "tkinter_app.py"], 
                              cwd=os.path.dirname(__file__))
            except KeyboardInterrupt:
                print("\n👋 Desktop GUI closed.")
            break
        
        elif choice == "2":
            print("\n�🚀 Launching Streamlit Web GUI...")
            print("This will open in your web browser automatically.")
            try:
                subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], 
                              cwd=os.path.dirname(__file__))
            except KeyboardInterrupt:
                print("\n👋 Web GUI closed.")
            break
        
        elif choice == "3":
            print("\n⌨️  CLI Mode")
            print("Example usage:")
            print("  python lap_analyser.py --year 2023 --gp Monza --session Q --top 5")
            print("  python lap_analyser.py --help")
            print("\nRun the commands above in your terminal.")
            break
        
        elif choice == "4":
            print("👋 Goodbye!")
            sys.exit(0)
        
        else:
            print("❌ Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()