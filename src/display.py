from typing import Dict, Any
from combine import CombinedProjectMetrics
from metrics_threshold_categorizer import MetricThresholdCategories, CATEGORY_GOOD, CATEGORY_NORMAL, CATEGORY_BAD, CATEGORY_NOT_CATEGORIZED

def format_number(value: float, decimal_places: int = 2, latex: bool = False) -> str:
    """
    Format a number with proper rounding to the specified decimal places.
    
    Args:
        value: The numeric value to format
        decimal_places: Number of decimal places to round to
        latex: Whether to use comma as decimal separator for LaTeX
    
    Returns:
        Formatted string representation of the number
    """
    rounded_value = round(value, decimal_places)
    formatted = f"{rounded_value:.{decimal_places}f}"
    
    if latex:
        return formatted.replace('.', ',')
    return formatted

def display_metrics(
    aggregated_metrics: CombinedProjectMetrics,
) -> None:
    """
    Displays all metrics on the console in a readable format.

    Args:
        aggregated_metrics: Dictionary with project-level metrics
    """
    print(f"Metrics Analysis Report")
    print("=" * 100)

    class_metrics = aggregated_metrics['original_metrics']
    weighted_metrics = aggregated_metrics['weighted_metrics']
    mean_metrics = aggregated_metrics['mean_metrics']
    median_metrics = aggregated_metrics['median_metrics']
    weighted_metrics_combined = aggregated_metrics['weighted_metrics_combined']

    # Display original class metrics
    print("\nORIGINAL CLASS METRICS:")
    print("-" * 100)
    print(f"{'Class Name':<30} {'WMC':>7} {'DIT':>7} {'NOC':>7} {'CBO':>7} {'RFC':>7} {'LCOM4':>7} {'LCOM4_N':>7}")
    print("-" * 100)
    
    for class_name, metrics in class_metrics.items():
        # Integer metrics without rounding
        print(f"{class_name:<30} {metrics['wmc']:>7} {metrics['dit']:>7} {metrics['noc']:>7} "
              f"{metrics['cbo']:>7} {metrics['rfc']:>7} {metrics['lcom4']:>7} "
              f"{format_number(metrics['lcom4_normalized']):>7}")

    # Display weighted metrics
    print("\nWEIGHTED CLASS METRICS:")
    print("-" * 100)
    print(f"{'Class Name':<30} {'WMC':>7} {'DIT':>7} {'NOC':>7} {'CBO':>7} {'RFC':>7} {'LCOM4':>7} {'LCOM4_N':>7}")
    print("-" * 100)
    
    for class_name, metrics in weighted_metrics.items():
        print(f"{class_name:<30} {format_number(metrics['wmc']):>7} {format_number(metrics['dit']):>7} "
              f"{format_number(metrics['noc']):>7} {format_number(metrics['cbo']):>7} "
              f"{format_number(metrics['rfc']):>7} {format_number(metrics['lcom4']):>7} "
              f"{format_number(metrics['lcom4_normalized']):>7}")
    
    # Display aggregated metrics
    print("\nAGGREGATED METRICS:")
    print("-" * 100)
    print(f"{'Aggregation Type':<30} {'WMC':>7} {'DIT':>7} {'NOC':>7} {'CBO':>7} {'RFC':>7} {'LCOM4':>7} {'LCOM4_N':>7}")
    print("-" * 100)

    print(f"{'Arithmetic Mean':<30} {format_number(mean_metrics['wmc']):>7} {format_number(mean_metrics['dit']):>7} "
          f"{format_number(mean_metrics['noc']):>7} {format_number(mean_metrics['cbo']):>7} "
          f"{format_number(mean_metrics['rfc']):>7} {format_number(mean_metrics['lcom4']):>7} "
          f"{format_number(mean_metrics['lcom4_normalized']):>7}")
    
    print(f"{'Weighted Average':<30} {format_number(weighted_metrics_combined['wmc']):>7} "
          f"{format_number(weighted_metrics_combined['dit']):>7} {format_number(weighted_metrics_combined['noc']):>7} "
          f"{format_number(weighted_metrics_combined['cbo']):>7} {format_number(weighted_metrics_combined['rfc']):>7} "
          f"{format_number(weighted_metrics_combined['lcom4']):>7} "
          f"{format_number(weighted_metrics_combined['lcom4_normalized']):>7}")
    
    print(f"{'Median':<30} {format_number(median_metrics['wmc']):>7} {format_number(median_metrics['dit']):>7} "
          f"{format_number(median_metrics['noc']):>7} {format_number(median_metrics['cbo']):>7} "
          f"{format_number(median_metrics['rfc']):>7} {format_number(median_metrics['lcom4']):>7} "
          f"{format_number(median_metrics['lcom4_normalized']):>7}")
    
    print("\nLegend:")
    print("WMC     = Weighted Methods per Class")
    print("DIT     = Depth of Inheritance Tree")
    print("NOC     = Number of Children")
    print("CBO     = Coupling Between Object Classes")
    print("RFC     = Response For a Class")
    print("LCOM4   = Lack of Cohesion in Methods")
    print("LCOM4_N = Normalized Lack of Cohesion in Methods (0.0-1.0)")
    print("=" * 100)

def print_threshold_summary(threshold_categories: MetricThresholdCategories, metric_class_counts: Dict[str, int]) -> None:
    """
    Prints a summary of metric threshold categorization.

    Args:
        threshold_categories: Dictionary with class names and counts for each metric category
        metric_class_counts: Dictionary with total count of classes for each metric
    """
    print("Metric Threshold Categorization Summary:")
    print("---------------------------------------")

    for metric, categories in threshold_categories.items():
        total_classes = metric_class_counts[metric]
        print(f"\n{metric.upper()}: ({total_classes} total classes with this metric)")

        for category, (class_list, count) in categories.items():
            percentage = (count / total_classes * 100) if total_classes > 0 else 0

            print(f"  {category}: {count} classes ({percentage:.1f}%)")
            
            # Optionally print the first few class names as examples
            if class_list:
                examples = class_list[:3]  # Show first 3 as examples
                more = count - len(examples)
                example_str = ", ".join(examples)
                if more > 0:
                    example_str += f" and {more} more"
                print(f"    Examples: {example_str}")

    print("\nNote: These categorizations are based on hard-coded threshold values from literature.")
    print("CBO and RFC only have 'Bad' thresholds defined in the literature source.")
    print("These are hard-coded threshold values and may need adjustment for specific contexts.")

def print_latex_table(aggregated_metrics: CombinedProjectMetrics) -> None:
    """
    Prints metrics in LaTeX table format.
    
    Args:
        aggregated_metrics: Dictionary with project-level metrics
    """
    mean_metrics = aggregated_metrics['mean_metrics']
    median_metrics = aggregated_metrics['median_metrics']
    weighted_metrics_combined = aggregated_metrics['weighted_metrics_combined']
    
    # Calculate ratio between arithmetic mean and median
    ratio = {}
    for metric in ['wmc', 'dit', 'noc', 'cbo', 'rfc', 'lcom4', 'lcom4_normalized']:
        if median_metrics[metric] != 0:
            ratio[metric] = mean_metrics[metric] / median_metrics[metric]
        else:
            ratio[metric] = float('inf')  # Handle division by zero
    
    # Print LaTeX table rows
    print("% LaTeX table rows for metrics")
    print("WMC    & " + format_number(mean_metrics['wmc'], latex=True) + " & " + 
          format_number(median_metrics['wmc'], latex=True) + " & " + 
          format_number(ratio['wmc'], latex=True) + " & " + 
          format_number(weighted_metrics_combined['wmc'], latex=True) + " \\\\")
    
    print("DIT    & " + format_number(mean_metrics['dit'], latex=True) + " & " + 
          format_number(median_metrics['dit'], latex=True) + " & " + 
          format_number(ratio['dit'], latex=True) + " & " + 
          format_number(weighted_metrics_combined['dit'], latex=True) + " \\\\")
    
    print("NOC    & " + format_number(mean_metrics['noc'], latex=True) + " & " + 
          format_number(median_metrics['noc'], latex=True) + " & " + 
          format_number(ratio['noc'], latex=True) + " & " + 
          format_number(weighted_metrics_combined['noc'], latex=True) + " \\\\")
    
    print("CBO    & " + format_number(mean_metrics['cbo'], latex=True) + " & " + 
          format_number(median_metrics['cbo'], latex=True) + " & " + 
          format_number(ratio['cbo'], latex=True) + " & " + 
          format_number(weighted_metrics_combined['cbo'], latex=True) + " \\\\")
    
    print("RFC    & " + format_number(mean_metrics['rfc'], latex=True) + " & " + 
          format_number(median_metrics['rfc'], latex=True) + " & " + 
          format_number(ratio['rfc'], latex=True) + " & " + 
          format_number(weighted_metrics_combined['rfc'], latex=True) + " \\\\")
    
    print("LCOM4  & " + format_number(mean_metrics['lcom4'], latex=True) + " & " + 
          format_number(median_metrics['lcom4'], latex=True) + " & " + 
          format_number(ratio['lcom4'], latex=True) + " & " + 
          format_number(weighted_metrics_combined['lcom4'], latex=True) + " \\\\")
    
    print("LCOM4\_N  & " + format_number(mean_metrics['lcom4_normalized'], latex=True) + " & " + 
          format_number(median_metrics['lcom4_normalized'], latex=True) + " & " + 
          format_number(ratio['lcom4_normalized'], latex=True) + " & " + 
          format_number(weighted_metrics_combined['lcom4_normalized'], latex=True) + " \\\\")


def print_latex_table_categorization(threshold_categories: MetricThresholdCategories, metric_class_counts: Dict[str, int]) -> None:
    """
    Prints the threshold categorization as a LaTeX table.

    Args:
        threshold_categories: Dictionary with class names and counts for each metric category
        metric_class_counts: Dictionary with total count of classes for each metric
    """
    # Display format
    metric_display = {
        "wmc": "WMC",
        "dit": "DIT", 
        "noc": "NOC",
        "lcom4_normalized": "LCOM4\_N",
        "cbo": "CBO",
        "rfc": "RFC"
    }
    
    # Column order for the table
    columns = [CATEGORY_GOOD, CATEGORY_NORMAL, CATEGORY_BAD, CATEGORY_NOT_CATEGORIZED]

    # Print each metric row
    for metric, categories in threshold_categories.items():
        row = []
        row.append(metric_display[metric])
        
        for column in columns:
            if column in categories:
                _, count = categories[column]
                row.append(str(count))
            else:
                row.append("--")
                
        # Format the row with proper LaTeX column separators
        print(f"{row[0]:<8} & {row[1]:<2} & {row[2]:<2} & {row[3]:<2} & {row[4]:<2} \\\\")
