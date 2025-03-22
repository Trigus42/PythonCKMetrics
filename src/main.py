import json
import argparse

from ck_metrics import process_path
from combine import get_aggregated_metrics
from metrics_threshold_categorizer import categorize_metrics_by_threshold
from display import print_latex_table, print_latex_table_categorization

def json_save(file_path, aggregated_metrics):
    """
    Save the data to a JSON file.

    Args:
        file_path (str): The path to the JSON file.
        data (dict): The data to save.
    """
    with open(file_path, 'w') as json_file:
        json.dump(aggregated_metrics, json_file, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Calculate CK metrics for Python code')
    parser.add_argument('path', help='Path to a Python file or directory')
    parser.add_argument('--classes', nargs='+', help='List of class names to analyze (if not specified, all classes will be analyzed)')
    args = parser.parse_args()

    metrics = process_path(args.path, args.classes)
    aggregated_metrics = get_aggregated_metrics(metrics)
    threshold_metrics = categorize_metrics_by_threshold(metrics)
    print_latex_table(aggregated_metrics)
    print_latex_table_categorization(*threshold_metrics)

    json_save("metrics_analyzed.json", threshold_metrics)
    json_save("metrics.json", aggregated_metrics)

if __name__ == "__main__":
    main()
