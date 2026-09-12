"""
AluSense AI - Dataset and Standards Module
"""

from .standards import (
    ALLOY_STANDARDS,
    MANUFACTURING_PROCESSES,
    PROCESS_LIMITS,
    PRESET_SCENARIOS,
    CUSTOM_ELEMENTS,
    CUSTOM_ELEMENT_KEYS,
    ALLOY_CALIBRATION_OFFSETS,
    ELEMENT_CALIBRATION_OFFSETS,
    get_alloy_details,
    get_process_limits,
    get_presets,
    get_custom_element
)

__all__ = [
    "ALLOY_STANDARDS",
    "MANUFACTURING_PROCESSES",
    "PROCESS_LIMITS",
    "PRESET_SCENARIOS",
    "CUSTOM_ELEMENTS",
    "CUSTOM_ELEMENT_KEYS",
    "ALLOY_CALIBRATION_OFFSETS",
    "ELEMENT_CALIBRATION_OFFSETS",
    "get_alloy_details",
    "get_process_limits",
    "get_presets",
    "get_custom_element",
]

