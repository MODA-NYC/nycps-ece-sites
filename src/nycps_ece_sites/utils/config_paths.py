# %%
from pathlib import Path
import os

def find_project_root(start: Path | None = None) -> Path:
    """
    Walk upward from `start` (or cwd) until pyproject.toml is found.
    Returns the project root directory.
    """
    if start is None:
        start = Path.cwd()

    start = start.resolve()

    for path in [start] + list(start.parents):
        if (path / "pyproject.toml").exists():
            return path

    raise FileNotFoundError("Could not find project root (pyproject.toml not found).")

# %%

ROOT_DIR = find_project_root()
DATA_DIR = ROOT_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
GEOCODE_DIR = DATA_DIR / 'geocode'
SRC_DIR = ROOT_DIR / 'src'


# %%
if __name__ == '__main__':

    dir_dict = {
        'ROOT_DIR': ROOT_DIR, 
        'DATA_DIR': DATA_DIR, 
        'GEOCODE_DIR': GEOCODE_DIR,
        'RAW_DATA_DIR': RAW_DATA_DIR,
        'SRC_DIR': SRC_DIR,
    }
    for name, dir in dir_dict.items():
        if dir.is_dir() == False:
            Path.mkdir(dir)
        assert dir.is_dir()
        print(f'{name}: {str(dir)}')
# %%
