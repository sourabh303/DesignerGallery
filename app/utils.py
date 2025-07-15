import os
from app.config import ALLOWED_EXTENSIONS, WATCH_FOLDER

# Check if the file is an image
def is_valid_image(file_path):
    _, ext = os.path.splitext(file_path)
    return ext.lower() in ALLOWED_EXTENSIONS

# Extract designer name from path like: \\...\\Designs\\Ramesh\\design1.jpg
def get_designer_name_from_path(file_path):
    normalized = os.path.normpath(file_path)
    parts = normalized.split(os.sep)

    try:
        # Find the index of WATCH_FOLDER in the path
        watch_parts = os.path.normpath(WATCH_FOLDER).split(os.sep)
        index = len(watch_parts)
        return parts[index]  # This is the folder under WATCH_FOLDER
    except (ValueError, IndexError):
        return "Unknown"
