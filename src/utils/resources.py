from pathlib import Path

RESOURCE_DIR = Path(__file__).parent.parent.parent / 'resources'
ICON_DIR = RESOURCE_DIR / 'icons'

# Ensure directories exist
ICON_DIR.mkdir(parents=True, exist_ok=True)
