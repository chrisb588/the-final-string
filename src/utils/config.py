import os
from pathlib import Path
from dotenv import load_dotenv

def get_project_paths():
    """Get project paths from environment variables"""
    load_dotenv()
    
    # Get base paths from env or use defaults relative to project root
    base_path = Path(os.getenv('PROJECT_ROOT', '.'))
    assets_path = base_path / 'assets'
    
    return {
        'project_root': base_path,
        'assets': assets_path,
        'videos': assets_path / 'video' / 'cutscenes'
    }

# Load paths when module is imported
PATHS = get_project_paths()