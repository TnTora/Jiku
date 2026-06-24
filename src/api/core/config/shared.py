from pathlib import Path
from os import getenv
from dotenv import load_dotenv

load_dotenv()

config_base = getenv("CONFIG_DIR") or getenv("APPDATA") or getenv("XDG_CONFIG_HOME") or "~/.config"
config_path = Path(config_base).expanduser() / "jiku"
tmp_path = config_path / "tmp"

config_path.mkdir(parents=True, exist_ok=True)
tmp_path.mkdir(parents=True, exist_ok=True)

redis_host = getenv("REDIS_HOST", "localhost")

static_url = getenv("STATIC_URL", "http://127.0.0.1:8000")
