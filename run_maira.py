#!/usr/bin/env python3
"""
MAIRA-∞ Quick Start Script

Run this script to start MAIRA with all features.
"""

import sys
import os
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "PySide6", "anthropic", "faster_whisper", "sounddevice", 
        "psutil", "httpx", "numpy", "edge_tts"
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == "PySide6":
                __import__("PySide6")
            else:
                __import__(package.lower().replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[ERROR] Missing dependencies: {', '.join(missing)}")
        print(f"[INSTALL] Run: pip install {' '.join(missing)}")
        return False
    
    print("[OK] All dependencies found")
    return True

def check_ollama():
    """Check if Ollama is running for local LLM."""
    try:
        import httpx
        response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
        if response.status_code == 200:
            print("[OK] Ollama is running (local LLM available)")
            return True
    except:
        pass
    
    print("[WARNING] Ollama not running - only cloud LLMs will work")
    print("[INFO] Install Ollama from https://ollama.ai/ for offline capability")
    return False

def main():
    """Main startup function."""
    setup_logging()
    
    # Use ASCII-safe characters for Windows compatibility
    print(">> Starting MAIRA-Infinity - Limitless AI Desktop Assistant")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Ollama
    check_ollama()
    
    # Check for API keys
    config_dir = Path.home() / ".maira"
    config_file = config_dir / "config.toml"
    
    if not config_file.exists():
        print("\n[CONFIG] First run detected - creating config directory")
        config_dir.mkdir(exist_ok=True)
        
        print("\n[API] API Key Setup:")
        print("   Add your API keys to ~/.maira/config.toml:")
        print("   [llm.keys]")
        print('   anthropic = "sk-ant-..."')
        print('   openai = "sk-..."')
        print('   google = "AI..."')
        print("\n   [INFO] You can run MAIRA without API keys using Ollama (local)")
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    try:
        # Import and run MAIRA
        from maira.__main__ import main as maira_main
        
        print("\n[LAUNCH] Launching MAIRA-Infinity...")
        print("   - Dashboard with live system monitoring")
        print("   - Voice interaction (English + Hinglish)")
        print("   - Multi-LLM support (Claude, OpenAI, Ollama)")
        print("   - Web search and code execution")
        print("   - Animated avatar with real-time lip-sync")
        print("\n[CONTROLS] Press Ctrl+Space for voice input")
        print("[EXIT] Press Ctrl+C to exit")
        print("-" * 60)
        
        # Run MAIRA
        maira_main()
        
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] MAIRA shutdown requested")
        sys.exit(0)
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("[FIX] Make sure you're running from the MAIRA directory")
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()