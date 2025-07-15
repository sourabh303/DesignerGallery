import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.config import WATCH_FOLDER, ARCHIVE_FOLDER, COPY_TO_ARCHIVE
from app.models import insert_design, init_db
from app.utils import is_valid_image, get_designer_name_from_path


class DesignEventHandler(FileSystemEventHandler):
    """Handles file system events for design files."""
    
    def on_created(self, event):
        """Triggered when a file is created."""
        if event.is_directory:
            return  # Skip directories

        file_path = event.src_path
        if not is_valid_image(file_path):
            return  # Skip invalid image files

        designer = get_designer_name_from_path(file_path)
        filename = os.path.basename(file_path)

        if COPY_TO_ARCHIVE:
            self.copy_to_archive(file_path, designer, filename)
        else:
            self.link_design(designer, filename, file_path)

    def copy_to_archive(self, file_path, designer, filename):
        """Copy the file to the archive folder with a timestamped name."""
        archive_path = os.path.join(ARCHIVE_FOLDER, designer)
        os.makedirs(archive_path, exist_ok=True)

        # Create a timestamped filename to avoid conflicts
        name, ext = os.path.splitext(filename)
        timestamped_name = f"{name}_{int(time.time())}{ext}"
        dest_path = os.path.join(archive_path, timestamped_name)

        try:
            shutil.copy2(file_path, dest_path)
            insert_design(designer, timestamped_name, dest_path)
            print(f"[✔] {designer} → {timestamped_name}")
        except Exception as e:
            print(f"[✘] Failed to copy {filename}: {e}")

    def link_design(self, designer, filename, file_path):
        """Link the design without copying."""
        insert_design(designer, filename, file_path)
        print(f"[✔] {designer} → {filename} (linked only)")


def start_monitor():
    """Start monitoring the designated folder for new design files."""
    print(f"🔍 Watching folder: {WATCH_FOLDER}")
    event_handler = DesignEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path=WATCH_FOLDER, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Monitoring stopped.")
    observer.join()


# Run if executed directly
if __name__ == "__main__":
    init_db()  # Initialize the database
    start_monitor()  # Start monitoring the folder
