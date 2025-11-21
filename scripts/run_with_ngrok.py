import sys
import os
import subprocess

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from pyngrok import ngrok
except ImportError:
    print("pyngrok is not installed. Run: pip install pyngrok")
    sys.exit(1)

# Configure ngrok - set your auth token here
# Get one free at https://dashboard.ngrok.com/auth/your-authtoken
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTHTOKEN")
if NGROK_AUTH_TOKEN:
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    print(f"✓ Using ngrok auth token from environment")
else:
    print("\n⚠ No NGROK_AUTHTOKEN found in environment.")
    print("  Free account required: https://dashboard.ngrok.com/")
    print("  Then set: $env:NGROK_AUTHTOKEN = 'your_token_here'")
    print("  Or uncomment and hardcode in this script.\n")

# Start the FastAPI app in the background
print("Starting FastAPI app on http://127.0.0.1:8000...")
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=project_root
)

try:
    # Create ngrok tunnel
    print("Opening ngrok tunnel...")
    public_url = ngrok.connect(8000, "http")
    print(f"\n✓ App is now accessible at: {public_url}")
    print(f"  Local URL: http://127.0.0.1:8000")
    print(f"  Docs: {public_url}/docs")
    print("\nPress Ctrl+C to stop.\n")
    
    # Open the app in browser
    import webbrowser
    webbrowser.open(f"{public_url}/docs")
    
    # Keep the tunnel alive
    ngrok_process = ngrok.get_ngrok_process()
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print("\nShutting down...")
    ngrok.kill()
    proc.terminate()
    proc.wait()
finally:
    proc.terminate()
