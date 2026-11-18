import os
import sys
import webbrowser
import uvicorn
from pathlib import Path

def main():
    port = 8000
    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    
    print("=" * 60)
    print(f"🚀 Starting Bugfix Loop Observability Dashboard")
    print(f"📡 Serving at: {url}")
    print("=" * 60)
    
    # Try to open the browser automatically
    try:
        webbrowser.open(url)
    except Exception:
        pass

    # Run uvicorn
    uvicorn.run("backend.app:app", host=host, port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()
