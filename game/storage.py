import sys
from pathlib import Path
if sys.platform == "emscripten":
    from platform import window
else:
    from base64 import urlsafe_b64encode as b64encode

def save_data(key: str, data: str) -> None:
    if sys.platform == "emscripten":
        window.localStorage.setItem(key, data) # For browser support
    else:
        (
            Path(__file__).parent /
            "storage" /
            b64encode(key.encode()).decode() # This way, any string can be accepted. ("/" and others won't cause problems.)
        ).write_text(data)
        
def read_data(key: str) -> str:
    if sys.platform == "emscripten":
        return window.localStorage.getItem(key) or "" # Return "" if nothing is stored
    else:
        try:
            return (Path(__file__).parent / "storage" / b64encode(key.encode()).decode()).read_text()
        except Exception:
            return ""