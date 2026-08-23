import logging
import os
import sys
from app import create_app

logger = logging.getLogger("automation_hub.server")

try:
    app = create_app()
except Exception as app_err:
    print(f"[FATAL] Failed to initialize Flask application: {app_err}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    try:
        raw_port = os.getenv("PORT", "5000")
        try:
            port = int(raw_port)
        except ValueError:
            print(f"[WARNING] Invalid PORT environment variable '{raw_port}'. Defaulting to 5000.")
            port = 5000

        host = os.getenv("HOST", "127.0.0.1").strip() or "127.0.0.1"
        debug = os.getenv("FLASK_DEBUG", "1").strip().lower() in ("1", "true", "yes")

        print(f"\n=======================================================")
        print(f"🚀 Automation Hub Server Starting...")
        print(f"   Address : http://{host}:{port}")
        print(f"   Debug   : {debug}")
        print(f"=======================================================\n")

        app.run(host=host, port=port, debug=debug)

    except KeyboardInterrupt:
        print("\n[INFO] Server gracefully stopped by user (KeyboardInterrupt).")
        sys.exit(0)
    except OSError as os_err:
        print(f"[ERROR] Socket error while starting server on {host}:{port}: {os_err}", file=sys.stderr)
        if "Address already in use" in str(os_err) or "10048" in str(os_err):
            print(f"[HINT] Port {port} is already in use by another process. Set PORT in .env to a different port.", file=sys.stderr)
        sys.exit(1)
    except Exception as fatal_err:
        print(f"[FATAL] Unexpected error starting server: {fatal_err}", file=sys.stderr)
        sys.exit(1)
