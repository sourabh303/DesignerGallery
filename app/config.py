import os

# Path to the root folder where all designer folders exist
WATCH_FOLDER = r"\C:\Users\ASUS\Downloads\designs_loc"  # <-- Update this to your real shared folder path

# Folder where picked designs will be copied
ARCHIVE_FOLDER = os.path.join("static", "uploads")

# Allowed file extensions
ALLOWED_EXTENSIONS = [".jpg", ".jpeg",".png"]

# SQLite database path
DB_PATH = "database.db"

# Whether to copy files into archive or just index
COPY_TO_ARCHIVE = True
