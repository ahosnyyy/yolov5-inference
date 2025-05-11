import os
import yaml
from typing import List, Dict, Tuple, Any, Optional

def load_clo_values(yaml_file: str = 'clo_values.yaml') -> Dict[str, Any]:
    """
    Load CLO values from a YAML file.
    
    Args:
        yaml_file: Path to the YAML file containing CLO values
        
    Returns:
        Dictionary containing CLO values and base CLO
    """
    if not os.path.exists(yaml_file):
        raise FileNotFoundError(f"CLO values file not found: {yaml_file}")
    
    with open(yaml_file, 'r') as f:
        clo_data = yaml.safe_load(f)
    
    return clo_data

def get_clothing_clo_values(yaml_file: str = 'clo_values.yaml') -> Dict[str, float]:
    """
    Returns a dictionary mapping clothing items to their CLO values.
    
    Args:
        yaml_file: Path to the YAML file containing CLO values
        
    Returns:
        Dictionary mapping clothing items to their CLO values
    """
    clo_data = load_clo_values(yaml_file)
    return clo_data.get('clo_values', {})

def get_base_clo_value(yaml_file: str = 'clo_values.yaml') -> float:
    """
    Returns the base CLO value for a nude person.
    
    Args:
        yaml_file: Path to the YAML file containing CLO values
        
    Returns:
        Base CLO value
    """
    clo_data = load_clo_values(yaml_file)
    return clo_data.get('base_clo', 0.0)

def map_detections_to_clo(detections: List[Any], yaml_file: str = 'clo_values.yaml') -> Tuple[List[Any], float]:
    """
    Maps detected clothing items to their CLO values and calculates total CLO.
    
    Args:
        detections: List of DetectionResult objects
        yaml_file: Path to the YAML file containing CLO values
        
    Returns:
        Tuple of (updated_detections, total_clo_value)
    """
    clo_mapping = get_clothing_clo_values(yaml_file)
    base_clo = get_base_clo_value(yaml_file)
    total_clo = 0.0
    
    for detection in detections:
        # Convert class name to lowercase for case-insensitive matching
        class_name_lower = detection.class_name.lower()
        
        # Assign CLO value if class is in our mapping
        if class_name_lower in clo_mapping:
            detection.clo_value = clo_mapping[class_name_lower]
            total_clo += detection.clo_value
        else:
            detection.clo_value = 0.0
    
    # Add base CLO value
    total_clo += base_clo
    
    return detections, total_clo
