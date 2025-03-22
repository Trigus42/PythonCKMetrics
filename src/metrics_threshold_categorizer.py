from typing import Dict, List, Any, TypedDict, Tuple, Set

from ck_metrics import ProjectMetrics

import pandas as pd

# Constants for categories (using strings for JSON serialization)
CATEGORY_GOOD = "Good"
CATEGORY_NORMAL = "Normal"  
CATEGORY_BAD = "Bad"
CATEGORY_NOT_CATEGORIZED = "Not Categorized"

# TypedDict definitions for the return types with class name lists and counts
class CategoryClasses(TypedDict):
    Good: Tuple[List[str], int]
    Normal: Tuple[List[str], int]
    Bad: Tuple[List[str], int]

class PartialCategoryClasses(TypedDict):
    Bad: Tuple[List[str], int]
    Not_Categorized: Tuple[List[str], int]

class MetricThresholdCategories(TypedDict):
    wmc: CategoryClasses
    dit: CategoryClasses
    noc: CategoryClasses
    lcom4_normalized: CategoryClasses
    cbo: PartialCategoryClasses
    rfc: PartialCategoryClasses

# Hard-coded thresholds based on literature values
THRESHOLDS = {
    "wmc": [(0, 11, CATEGORY_GOOD), (11.001, 34, CATEGORY_NORMAL), (34.001, float('inf'), CATEGORY_BAD)],
    "dit": [(0, 2, CATEGORY_GOOD), (2.001, 4, CATEGORY_NORMAL), (4.001, float('inf'), CATEGORY_BAD)],
    "noc": [(0, 11, CATEGORY_GOOD), (11.001, 28, CATEGORY_NORMAL), (28.001, float('inf'), CATEGORY_BAD)],
    "lcom4_normalized": [(0, 0.167, CATEGORY_GOOD), (0.167001, 0.725, CATEGORY_NORMAL), (0.725001, float('inf'), CATEGORY_BAD)],
    "cbo": [(8.001, float('inf'), CATEGORY_BAD), (0, 8, CATEGORY_NOT_CATEGORIZED)],
    "rfc": [(20.001, float('inf'), CATEGORY_BAD), (0, 20, CATEGORY_NOT_CATEGORIZED)]
}

def categorize_metrics_by_threshold(project_metrics: ProjectMetrics) -> Tuple[MetricThresholdCategories, Dict[str, int]]:
    """
    Categorizes classes by their metric values according to predefined threshold categories.
    Saves both the class names and counts in each category.
    
    Note: These thresholds are hard-coded based on the literature values from the table.
    
    Args:
        project_metrics: Dictionary with project-level metrics

    Returns:
        Tuple containing:
        - TypedDict with tuples containing lists of class names and counts for each metric category
        - Dictionary with total count of classes for each metric
    """
    # Extract all class metrics from class_summary
    class_metrics = project_metrics["class_summary"]
    
    # Initialize result dictionary with empty lists for each category
    result: MetricThresholdCategories = {
        "wmc": {
            CATEGORY_GOOD: ([], 0), 
            CATEGORY_NORMAL: ([], 0), 
            CATEGORY_BAD: ([], 0)
        },
        "dit": {
            CATEGORY_GOOD: ([], 0), 
            CATEGORY_NORMAL: ([], 0), 
            CATEGORY_BAD: ([], 0)
        },
        "noc": {
            CATEGORY_GOOD: ([], 0), 
            CATEGORY_NORMAL: ([], 0), 
            CATEGORY_BAD: ([], 0)
        },
        "lcom4_normalized": {
            CATEGORY_GOOD: ([], 0), 
            CATEGORY_NORMAL: ([], 0), 
            CATEGORY_BAD: ([], 0)
        },
        "cbo": {
            CATEGORY_BAD: ([], 0), 
            CATEGORY_NOT_CATEGORIZED: ([], 0)
        },
        "rfc": {
            CATEGORY_BAD: ([], 0), 
            CATEGORY_NOT_CATEGORIZED: ([], 0)
        }
    }

    # Track classes with each metric
    metric_class_counts = {metric: 0 for metric in THRESHOLDS.keys()}
    
    # For each class, categorize its metrics
    for class_name, metrics in class_metrics.items():
        for metric_name, value in metrics.items():
            if metric_name in THRESHOLDS and not pd.isna(value):  # Skip NaN values
                # Count this class for this metric
                metric_class_counts[metric_name] += 1
                
                categorized = False
                
                for lower, upper, category in THRESHOLDS[metric_name]:
                    # Check if value falls within this range
                    if lower <= value <= upper:
                        # Get current tuple, update it with new class name and incremented count
                        class_list, count = result[metric_name][category]
                        class_list.append(class_name)
                        result[metric_name][category] = (class_list, count + 1)
                        categorized = True
                        break

                if not categorized:
                    print(f"Warning: {class_name} has {metric_name}={value} which doesn't fall into any category")

    # Verify category counts match metric counts
    for metric_name, metric_categories in result.items():
        total_categorized = sum(count for _, count in metric_categories.values())
        total_for_metric = metric_class_counts[metric_name]
        
        if total_categorized != total_for_metric:
            print(f"Warning: {metric_name} has {total_categorized} categorized classes but {total_for_metric} classes with this metric")

    return result, metric_class_counts
