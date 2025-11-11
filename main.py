"""
Main entry point for the uRISK application.
This file handles the correct imports and runs the FastAPI app.

Usage:
    python main.py  # Start the development server
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main application entry point"""
    try:
        from backend.app import app
        
        if __name__ == "__main__":
            import uvicorn
            print("🚀 Starting QuantVerse uRISK Server...")
            print("📊 Access API documentation at: http://127.0.0.1:8002/docs")
            print("💬 Chat interface will be available at: http://127.0.0.1:8002/chat")
            
            uvicorn.run(
                app, 
                host="127.0.0.1", 
                port=8002, 
                reload=True,  # Enable reload for development
                log_level="info"
            )
    except ImportError as e:
        print(f"❌ Error importing backend app: {e}")
        print("💡 Make sure you have installed all requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
