import os
import shutil
import logging
import csv
from datetime import datetime
from collections import defaultdict

# =========================
# SETUP FOLDERS
# =========================
LOG_FOLDER = "logs"
REPORT_FOLDER = "reports"

os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

log_file = os.path.join(LOG_FOLDER, "organizer.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Track report data
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


def get_unique_destination(destination_path):
    """
    Prevent overwriting files by appending a timestamp if needed.
    Example: report.pdf -> report_143520.pdf
    """
    if not os.path.exists(destination_path):
        return destination_path

    folder, filename = os.path.split(destination_path)
    base, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%H%M%S")
    new_filename = f"{base}_{timestamp}{ext}"
    return os.path.join(folder, new_filename)


def organize_files(source_folder, sort_by="type"):
    """Scan source folder and move files into organized subfolders."""
    if not os.path.exists(source_folder):
        print(f"Error: The folder '{source_folder}' does not exist.")
        return

    files_found = False

    for item in os.listdir(source_folder):
        source_path = os.path.join(source_folder, item)

        # Only process files, not folders
        if os.path.isfile(source_path):
            files_found = True

            if sort_by == "type":
                target_folder_name = get_file_category(item)
            elif sort_by == "date":
                target_folder_name = get_date_folder(source_path)
            else:
                print("Invalid sort option. Use 'type' or 'date'.")
                return

            target_folder = os.path.join(source_folder, target_folder_name)
            os.makedirs(target_folder, exist_ok=True)

            destination_path = os.path.join(target_folder, item)
            final_destination = get_unique_destination(destination_path)

            final_filename = os.path.basename(final_destination)

            shutil.move(source_path, final_destination)

            logging.info(f"Moved '{item}' to '{target_folder_name}' as '{final_filename}'")

            report_data[target_folder_name] += 1
            moved_files.append({
                "original_name": item,
                "new_name": final_filename,
                "destination_folder": target_folder_name
            })

    if not files_found:
        print("No files found to organize.")
    else:
        print("Files organized successfully.")


def generate_text_report():
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
        for file_info in moved_files:
            report.write(
                f"- {file_info['original_name']} -> "
                f"{file_info['destination_folder']} "
                f"(saved as {file_info['new_name']})\n"
            )

    logging.info(f"Text report generated at '{report_path}'")
    return report_path


def generate_csv_report():
    """Generate a CSV report that can be opened in Excel."""
    csv_path = os.path.join(REPORT_FOLDER, "summary_report.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Original File Name", "New File Name", "Destination Folder"])

        for file_info in moved_files:
            writer.writerow([
                file_info["original_name"],
                file_info["new_name"],
                file_info["destination_folder"]
            ])

    logging.info(f"CSV report generated at '{csv_path}'")
    return csv_path


def print_summary():
    """Print a summary to the console."""
    total_files = sum(report_data.values())

    print("\nOrganization Summary")
    print("=" * 25)
    print(f"Total files moved: {total_files}")

    if total_files == 0:
        print("No files were moved.")
        return

    for category, count in report_data.items():
        print(f"{category}: {count} file(s)")


def main():
    print("=== Automated Document Organizer ===")
    source_folder = input("Enter the folder path to organize: ").strip()
    sort_by = input("Sort files by 'type' or 'date': ").strip().lower()

    organize_files(source_folder, sort_by)

    text_report = generate_text_report()
    csv_report = generate_csv_report()
    print_summary()

    print(f"\nText report saved to: {text_report}")
    print(f"CSV report saved to: {csv_report}")
    print(f"Log file saved to: {log_file}")


if __name__ == "__main__":
    main()