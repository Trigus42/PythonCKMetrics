from typing import Dict, TypedDict
import statistics

from ck_metrics import ProjectMetrics

class CombinedClassMetrics(TypedDict):
    """TypedDict for combined metrics (weighted, mean, or median)"""
    wmc: float             # Weighted Methods per Class
    dit: float             # Depth of Inheritance Tree
    noc: float             # Number of Children
    cbo: float             # Coupling Between Object Classes
    rfc: float             # Response For a Class
    lcom4: float           # Lack of Cohesion in Methods
    lcom4_normalized: float # Normalized Lack of Cohesion in Methods


class CombinedProjectMetrics(TypedDict):
    """TypedDict for combined project metrics"""
    original_metrics: Dict[str, CombinedClassMetrics]  # Original metrics for the project
    weighted_metrics: Dict[str, CombinedClassMetrics]  # Weighted metrics for each class
    weighted_metrics_combined: CombinedClassMetrics    # Combined weighted metrics
    mean_metrics: CombinedClassMetrics                 # Mean metrics for the project
    median_metrics: CombinedClassMetrics               # Median metrics for the project


def get_aggregated_metrics(project_metrics: ProjectMetrics) -> CombinedProjectMetrics:
    """
    Aggregates C&K metrics for a project.
    
    Args:
        project_metrics: Dictionary with project-level metrics
    Returns:
        Dictionary with aggregated metrics
    """
    # Combine metrics using the weighting model
    weighted_metrics = combine_metrics(project_metrics)
    
    # Calculate mean and median metrics
    mean_metrics = calculate_mean_metrics(project_metrics)
    median_metrics = calculate_median_metrics(project_metrics)
    
    # Calculate combined weighted metrics
    weighted_average_metrics = calculate_weighted_metrics_combined(weighted_metrics)

    original_metrics={k: CombinedClassMetrics(
            wmc=v["wmc"],
            dit=v["dit"],
            noc=v["noc"],
            cbo=v["cbo"],
            rfc=v["rfc"],
            lcom4=v["lcom4"],
            lcom4_normalized=v["lcom4_normalized"]
        )
        for k,v in project_metrics["class_summary"].items()
    }

    return CombinedProjectMetrics(
        original_metrics=original_metrics,
        weighted_metrics=weighted_metrics,
        weighted_metrics_combined=weighted_average_metrics,
        mean_metrics=mean_metrics,
        median_metrics=median_metrics
    )

def combine_metrics(project_metrics: ProjectMetrics) -> Dict[str, CombinedClassMetrics]:
    """
    Combines C&K metrics using a weighting model that considers all metrics.
    
    For each metric M of a class i, the weighted value is calculated as:
    M_weighted,i = M_i x (1/k) ∑(X_m,i / ∑X_m,j)

    Where:
    - M_i is the original metric value for class i
    - X_m,i are the other metrics for class i
    - ∑X_m,j is the sum of metric m across all classes j
    - k is the number of other metrics used for weighting
    
    Args:
        project_metrics: Dictionary with project-level metrics
        
    Returns:
        Dictionary with weighted metrics for each class
    """
    # Extract all class metrics from class_summary
    class_metrics = project_metrics["class_summary"]
    
    # Define the C&K metrics we're working with
    ck_metrics = ["wmc", "dit", "noc", "cbo", "rfc", "lcom4", "lcom4_normalized"]
    
    # Calculate the sum of each metric across all classes
    metric_sums = {metric: sum(class_data[metric] for class_data in class_metrics.values()) 
                  for metric in ck_metrics}
    
    # Calculate weighted metrics for each class
    weighted_metrics: Dict[str, CombinedClassMetrics] = {}
    
    for class_name, class_data in class_metrics.items():
        weighted_class_metrics: Dict[str, float] = {}
        
        for target_metric in ck_metrics:
            # Get the original metric value
            original_value = class_data[target_metric]
            
            # Find other metrics (excluding the current one)
            other_metrics = [m for m in ck_metrics if m != target_metric]
            weight_sum = 0
            valid_metrics_count = 0
            
            for other_metric in other_metrics:
                # Skip if sum is zero to avoid division by zero
                if metric_sums[other_metric] == 0:
                    continue
                    
                # Calculate ratio: metric value for this class / sum across all classes
                ratio = class_data[other_metric] / metric_sums[other_metric]
                weight_sum += ratio
                valid_metrics_count += 1
            
            # Calculate average weight (divide by number of valid other metrics)
            avg_weight = weight_sum / valid_metrics_count if valid_metrics_count > 0 else 1
            
            # Calculate weighted metric = original value * average weight
            weighted_class_metrics[target_metric] = original_value * avg_weight

        weighted_metrics[class_name] = CombinedClassMetrics(
            wmc=weighted_class_metrics["wmc"],
            dit=weighted_class_metrics["dit"],
            noc=weighted_class_metrics["noc"],
            cbo=weighted_class_metrics["cbo"],
            rfc=weighted_class_metrics["rfc"],
            lcom4=weighted_class_metrics["lcom4"],
            lcom4_normalized=weighted_class_metrics["lcom4_normalized"]
        )

    return weighted_metrics


def calculate_mean_metrics(project_metrics: ProjectMetrics) -> CombinedClassMetrics:
    """
    Calculates the arithmetic mean for each C&K metric across all classes.
    
    Args:
        project_metrics: Dictionary with project-level metrics
        
    Returns:
        CombinedMetrics object containing the arithmetic mean for each metric
    """
    class_metrics = project_metrics["class_summary"]
    
    # Initialize lists to store values for each metric
    wmc_values = []
    dit_values = []
    noc_values = []
    cbo_values = []
    rfc_values = []
    lcom4_values = []
    lcom4_norm_values = []
    
    # Collect all values for each metric
    for class_data in class_metrics.values():
        wmc_values.append(class_data["wmc"])
        dit_values.append(class_data["dit"])
        noc_values.append(class_data["noc"])
        cbo_values.append(class_data["cbo"])
        rfc_values.append(class_data["rfc"])
        lcom4_values.append(class_data["lcom4"])
        lcom4_norm_values.append(class_data["lcom4_normalized"])
    
    # Calculate the arithmetic mean for each metric
    return CombinedClassMetrics(
        wmc=statistics.mean(wmc_values),
        dit=statistics.mean(dit_values),
        noc=statistics.mean(noc_values),
        cbo=statistics.mean(cbo_values),
        rfc=statistics.mean(rfc_values),
        lcom4=statistics.mean(lcom4_values),
        lcom4_normalized=statistics.mean(lcom4_norm_values)
    )


def calculate_median_metrics(project_metrics: ProjectMetrics) -> CombinedClassMetrics:
    """
    Calculates the median for each C&K metric across all classes.
    
    Args:
        project_metrics: Dictionary with project-level metrics
        
    Returns:
        CombinedMetrics object containing the median for each metric
    """
    class_metrics = project_metrics["class_summary"]
    
    # Initialize lists to store values for each metric
    wmc_values = []
    dit_values = []
    noc_values = []
    cbo_values = []
    rfc_values = []
    lcom4_values = []
    lcom4_norm_values = []
    
    # Collect all values for each metric
    for class_data in class_metrics.values():
        wmc_values.append(class_data["wmc"])
        dit_values.append(class_data["dit"])
        noc_values.append(class_data["noc"])
        cbo_values.append(class_data["cbo"])
        rfc_values.append(class_data["rfc"])
        lcom4_values.append(class_data["lcom4"])
        lcom4_norm_values.append(class_data["lcom4_normalized"])
    
    # Calculate the median for each metric
    return CombinedClassMetrics(
        wmc=statistics.median(wmc_values),
        dit=statistics.median(dit_values),
        noc=statistics.median(noc_values),
        cbo=statistics.median(cbo_values),
        rfc=statistics.median(rfc_values),
        lcom4=statistics.median(lcom4_values),
        lcom4_normalized=statistics.median(lcom4_norm_values)
    )


def calculate_weighted_metrics_combined(weighted_metrics: Dict[str, CombinedClassMetrics]) -> CombinedClassMetrics:
    """
    Calculates the arithmetic mean of weighted metrics for each C&K metric.
    
    Args:
        weighted_metrics: Dictionary with weighted metrics for each class
        
    Returns:
        CombinedMetrics object containing the arithmetic mean of weighted metrics
    """
    # Initialize lists to store weighted values for each metric
    wmc_values = []
    dit_values = []
    noc_values = []
    cbo_values = []
    rfc_values = []
    lcom4_values = []
    lcom4_norm_values = []
    
    # Collect all weighted values for each metric
    for metrics in weighted_metrics.values():
        wmc_values.append(metrics["wmc"])
        dit_values.append(metrics["dit"])
        noc_values.append(metrics["noc"])
        cbo_values.append(metrics["cbo"])
        rfc_values.append(metrics["rfc"])
        lcom4_values.append(metrics["lcom4"])
        lcom4_norm_values.append(metrics["lcom4_normalized"])

    # Calculate the arithmetic mean of the weighted metrics
    return CombinedClassMetrics(
        wmc=sum(wmc_values),
        dit=sum(dit_values),
        noc=sum(noc_values),
        cbo=sum(cbo_values),
        rfc=sum(rfc_values),
        lcom4=sum(lcom4_values),
        lcom4_normalized=sum(lcom4_norm_values)
    )
