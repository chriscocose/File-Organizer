import os
import shutil
import logging
from datetime import datetime
from collections import defaultdict

# =========================
# CONFIG
# =========================
SOURCE_FOLDER = "test_files"
LOG_FOLDER = "logs"
REPORT_FOLDER = "reports"

SORT_BY = "type"  # options: "type" or "date"

# =========================
# SETUP
# =========================
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

log_file = os.path.join(LOG_FOLDER, "organizer.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Track actions for report
report_data = defaultdict(int)
moved_files = []


def get_file_category(filename):
    """Return folder category based on file extension."""
    ext = os.path.splitext(filename)[1].lower()

    categories = {
        "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".csv", ".pptx"],
        "Images": [".jpg", ".jpeg", ".png", ".gif"],
        "Videos": [".mp4", ".mov", ".avi"],
        "Archives": [".zip", ".rar", ".7z"],
    }

    for category, extensions in categories.items():
        if ext in extensions:
            return category

    return "Others"


def get_date_folder(filepath):
    """Return folder name based on file modified date."""
    modified_time = os.path.getmtime(filepath)
    dt = datetime.fromtimestamp(modified_time)
    return dt.strftime("%Y-%m")


def organize_files():
    """Scan source folder and move files into organized subfolders."""
    if not os.path.exists(SOURCE_FOLDER):
        print(f"Source folder '{SOURCE_FOLDER}' does not exist.")
        return

    for item in os.listdir(SOURCE_FOLDER):
        source_path = os.path.join(SOURCE_FOLDER, item)

        if os.path.isfile(source_path):
            if SORT_BY == "type":
                target_folder_name = get_file_category(item)
            elif SORT_BY == "date":
                target_folder_name = get_date_folder(source_path)
            else:
                print("Invalid SORT_BY option. Use 'type' or 'date'.")
                return

            target_folder = os.path.join(SOURCE_FOLDER, target_folder_name)
            os.makedirs(target_folder, exist_ok=True)

            destination_path = os.path.join(target_folder, item)

            # Prevent overwrite issues
            if os.path.exists(destination_path):
                base, ext = os.path.splitext(item)
                timestamp = datetime.now().strftime("%H%M%S")
                new_name = f"{base}_{timestamp}{ext}"
                destination_path = os.path.join(target_folder, new_name)

            shutil.move(source_path, destination_path)

            logging.info(f"Moved '{item}' to '{target_folder_name}'")
            report_data[target_folder_name] += 1
            moved_files.append(f"{item} -> {target_folder_name}")


def generate_report():
    """Generate a text summary report."""
    report_path = os.path.join(REPORT_FOLDER, "summary_report.txt")

    with open(report_path, "w", encoding="utf-8") as report:
        report.write("Automated Document Organizer Report\n")
        report.write("=" * 40 + "\n")
        report.write(f"Run Date: {datetime.now()}\n\n")

        total_files = sum(report_data.values())
        report.write(f"Total files moved: {total_files}\n\n")

        report.write("Files moved by category:\n")
        for category, count in report_data.items():
            report.write(f"- {category}: {count}\n")

        report.write("\nDetailed actions:\n")
        for entry in moved_files:
            report.write(f"- {entry}\n")

    logging.info(f"Report generated at '{report_path}'")
    print(f"Done. Report saved to: {report_path}")


if __name__ == "__main__":
    organize_files()
    generate_report()