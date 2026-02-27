import os, tomllib
from pathlib import Path
from dynaconf import Dynaconf

BASE_DIR = Path(__file__).resolve().parent.parent.parent
settings_file_path = os.path.join(BASE_DIR, 'configs', 'settings.toml')
env_file_path = os.path.join(BASE_DIR, '.env')

settings = Dynaconf(
    settings_files=[settings_file_path],
    env_file=env_file_path,
    load_dotenv=True,
    environments=True,
    env_switcher='AC_ENV',
    verbose=True,
    envvar_prefix="AC" # Prefix for environment variables, AI Concierge
)

def get_version() -> str:
    """Read version from pyproject.toml"""
    pyproject_path = BASE_DIR / "pyproject.toml"
    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
            return pyproject_data.get("project", {}).get("version", "0.0.0")
    except Exception:
        return "0.0.0"

VERSION = get_version()