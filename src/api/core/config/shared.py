from pathlib import Path
from os import getenv

config_base = getenv("APPDATA") or getenv("XDG_CONFIG_HOME") or "~/.config"
config_path = Path(config_base).expanduser() / "jiku"
config_path.mkdir(parents=True, exist_ok=True)
