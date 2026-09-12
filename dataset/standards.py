"""
AluSense AI - Aluminium Alloy Manufacturing Standards & Calibration Dataset
Standard references: ISO/ASTM 52900, ASTM F3055, AMS 4999, DIN EN 1706
"""

from typing import Dict, Any

ALLOY_STANDARDS: Dict[str, Dict[str, Any]] = {
    "AlSi10Mg": {
        "name": "AlSi10Mg (Al-10Si-Mg)",
        "code": "AlSi10Mg",
        "standard": "ASTM F3055 / DIN EN 1706",
        "description": "Hypoeutectic aluminium-silicon casting alloy tailored for additive laser fusion.",
        "density": 2.67,  # g/cm3
        "melting_range": "570 – 590 °C",
        "thermal_conductivity": "130 – 150 W/(m·K)",
        "composition": "Al (Bal), Si 9.0–11.0%, Mg 0.20–0.45%, Fe ≤0.55%, Mn ≤0.45%, Ti ≤0.15%",
        "applications": "Automotive heat exchangers, lightweight aerospace structural brackets, robotic arms",
        "nominal_mechanical": {
            "yield_strength": 260,  # MPa
            "uts": 395,            # MPa
            "elongation": 8.0,      # %
            "hardness": 120,        # HV
            "rel_density": 99.85    # %
        }
    },
    "Scalmalloy": {
        "name": "Scalmalloy® (Al-Mg-Sc-Zr)",
        "code": "Scalmalloy",
        "standard": "AMS 4999 / ISO/ASTM 52900",
        "description": "High-strength scandium-modified alloy developed specifically for high-stress aerospace applications.",
        "density": 2.77,
        "melting_range": "630 – 655 °C",
        "thermal_conductivity": "110 – 130 W/(m·K)",
        "composition": "Al (Bal), Mg 4.0–4.9%, Sc 0.6–0.8%, Zr 0.2–0.5%, Mn 0.3–0.7%",
        "applications": "Formula 1 suspension components, satellite structural mounts, rocket turbopump brackets",
        "nominal_mechanical": {
            "yield_strength": 475,
            "uts": 520,
            "elongation": 13.5,
            "hardness": 165,
            "rel_density": 99.90
        }
    },
    "Al 6061-RAM2": {
        "name": "Al 6061-RAM2 (Additive Modified)",
        "code": "Al 6061-RAM2",
        "standard": "ASTM B221 / AMS 4027 Mod",
        "description": "Nanoparticle-nucleated wrought 6000-series alloy engineered to eliminate solidification hot-cracking.",
        "density": 2.70,
        "melting_range": "582 – 652 °C",
        "thermal_conductivity": "150 – 170 W/(m·K)",
        "composition": "Al (Bal), Mg 0.8–1.2%, Si 0.4–0.8%, Cu 0.15–0.40%, Cr 0.04–0.35%, TiB2 2.0%",
        "applications": "Marine structural hulls, aerospace cabin frames, semiconductor carrier fixtures",
        "nominal_mechanical": {
            "yield_strength": 295,
            "uts": 335,
            "elongation": 11.0,
            "hardness": 105,
            "rel_density": 99.75
        }
    },
    "Al 7075-AM": {
        "name": "Al 7075-AM (High-Zinc Aerospace)",
        "code": "Al 7075-AM",
        "standard": "AMS 4045 / ASTM B209 Mod",
        "description": "Ultra-high strength Al-Zn-Mg-Cu alloy modified for crack-free laser additive manufacturing.",
        "density": 2.81,
        "melting_range": "477 – 635 °C",
        "thermal_conductivity": "130 W/(m·K)",
        "composition": "Al (Bal), Zn 5.1–6.1%, Mg 2.1–2.9%, Cu 1.2–2.0%, Cr 0.18–0.28%, Sc/Zr 0.4%",
        "applications": "Defense airframe bulkheads, missile fin attachments, high-load kinetic linkages",
        "nominal_mechanical": {
            "yield_strength": 505,
            "uts": 565,
            "elongation": 8.5,
            "hardness": 175,
            "rel_density": 99.80
        }
    },
    "A356-T6": {
        "name": "A356-T6 (Structural Casting/WAAM)",
        "code": "A356-T6",
        "standard": "ASTM B618 / AMS 4218",
        "description": "Primary structural aluminium-silicon casting alloy widely utilized in high-integrity castings and WAAM preforms.",
        "density": 2.68,
        "melting_range": "555 – 615 °C",
        "thermal_conductivity": "150 – 165 W/(m·K)",
        "composition": "Al (Bal), Si 6.5–7.5%, Mg 0.25–0.45%, Fe ≤0.20%, Ti ≤0.20%",
        "applications": "Automotive steering knuckles, large WAAM aerospace stiffened panels, pressure housings",
        "nominal_mechanical": {
            "yield_strength": 215,
            "uts": 290,
            "elongation": 6.5,
            "hardness": 90,
            "rel_density": 99.65
        }
    }
}

MANUFACTURING_PROCESSES = [
    "Laser Powder Bed Fusion (LPBF)",
    "Direct Metal Laser Sintering (DMLS)",
    "Wire Arc Additive Manufacturing (WAAM)",
    "High Pressure Die Casting (HPDC)"
]

# Baseline standard operating windows for combinations
# Each parameter: [min_safe, nominal, max_safe, critical_min, critical_max, unit, description]
PROCESS_LIMITS: Dict[str, Dict[str, Any]] = {
    "Laser Powder Bed Fusion (LPBF)": {
        "temperature": {
            "min": 150.0,
            "nominal": 200.0,
            "max": 250.0,
            "crit_min": 80.0,
            "crit_max": 320.0,
            "unit": "°C",
            "name": "Bed Preheating Temp",
            "info": "Minimizes thermal gradient and residual stress buildup during rapid solidification."
        },
        "energy_density": {
            "min": 48.0,
            "nominal": 62.0,
            "max": 75.0,
            "crit_min": 35.0,
            "crit_max": 95.0,
            "unit": "J/mm³",
            "name": "Volumetric Energy Density (VED)",
            "info": "Energy input per unit volume. Below 48 J/mm³ causes lack-of-fusion; above 75 J/mm³ causes keyholing."
        },
        "scan_speed": {
            "min": 900.0,
            "nominal": 1300.0,
            "max": 1600.0,
            "crit_min": 600.0,
            "crit_max": 2100.0,
            "unit": "mm/s",
            "name": "Laser Scan Velocity",
            "info": "Beam travel velocity across powder bed. Governs cooling rate and melt pool stability."
        },
        "oxygen_concentration": {
            "min": 10.0,
            "nominal": 50.0,
            "max": 120.0,
            "crit_min": 0.0,
            "crit_max": 350.0,
            "unit": "ppm",
            "name": "Chamber O2 Concentration",
            "info": "Inert gas atmosphere purity (Argon/Nitrogen). >150 ppm promotes heavy alumina film entrapment."
        },
        "laser_power": {
            "min": 280.0,
            "nominal": 370.0,
            "max": 450.0,
            "crit_min": 180.0,
            "crit_max": 550.0,
            "unit": "W",
            "name": "Laser Optical Power",
            "info": "Continuous wave fiber laser power output at focal plane."
        },
        "layer_thickness": {
            "min": 25.0,
            "nominal": 30.0,
            "max": 50.0,
            "crit_min": 20.0,
            "crit_max": 80.0,
            "unit": "µm",
            "name": "Powder Layer Thickness",
            "info": "Recoater blade deposit height per fusion slice."
        }
    },
    "Direct Metal Laser Sintering (DMLS)": {
        "temperature": {
            "min": 140.0,
            "nominal": 180.0,
            "max": 230.0,
            "crit_min": 70.0,
            "crit_max": 290.0,
            "unit": "°C",
            "name": "Platform Temperature",
            "info": "Baseplate heating to relieve consolidation micro-stresses."
        },
        "energy_density": {
            "min": 52.0,
            "nominal": 65.0,
            "max": 78.0,
            "crit_min": 38.0,
            "crit_max": 100.0,
            "unit": "J/mm³",
            "name": "Volumetric Energy Density (VED)",
            "info": "Critical envelope for particle coalescence without excessive plasma plume."
        },
        "scan_speed": {
            "min": 850.0,
            "nominal": 1200.0,
            "max": 1500.0,
            "crit_min": 550.0,
            "crit_max": 1950.0,
            "unit": "mm/s",
            "name": "Scan Speed",
            "info": "Defines hatch vector traverse rate."
        },
        "oxygen_concentration": {
            "min": 15.0,
            "nominal": 60.0,
            "max": 140.0,
            "crit_min": 0.0,
            "crit_max": 400.0,
            "unit": "ppm",
            "name": "Atmospheric Oxygen",
            "info": "Governs gas atomized powder oxidation in chamber."
        },
        "laser_power": {
            "min": 260.0,
            "nominal": 350.0,
            "max": 420.0,
            "crit_min": 170.0,
            "crit_max": 500.0,
            "unit": "W",
            "name": "Laser Power",
            "info": "Focal beam power."
        },
        "layer_thickness": {
            "min": 25.0,
            "nominal": 30.0,
            "max": 45.0,
            "crit_min": 20.0,
            "crit_max": 70.0,
            "unit": "µm",
            "name": "Layer Slicing",
            "info": "Consolidated powder height."
        }
    },
    "Wire Arc Additive Manufacturing (WAAM)": {
        "temperature": {
            "min": 120.0,
            "nominal": 160.0,
            "max": 210.0,
            "crit_min": 50.0,
            "crit_max": 280.0,
            "unit": "°C",
            "name": "Interpass Temperature",
            "info": "Max allowed temperature before depositing adjacent bead pass."
        },
        "energy_density": {
            "min": 70.0,
            "nominal": 95.0,
            "max": 120.0,
            "crit_min": 50.0,
            "crit_max": 160.0,
            "unit": "J/mm³",
            "name": "Heat Input Ratio",
            "info": "Linear arc energy / deposited bead area."
        },
        "scan_speed": {
            "min": 350.0,
            "nominal": 600.0,
            "max": 850.0,
            "crit_min": 200.0,
            "crit_max": 1100.0,
            "unit": "mm/s",
            "name": "Torch Travel Velocity",
            "info": "Robotic torch positioning speed along track."
        },
        "oxygen_concentration": {
            "min": 20.0,
            "nominal": 80.0,
            "max": 180.0,
            "crit_min": 0.0,
            "crit_max": 500.0,
            "unit": "ppm",
            "name": "Shield Gas Purity (O2)",
            "info": "Shield gas shroud integrity (Ar + 30% He)."
        },
        "laser_power": {
            "min": 1200.0,
            "nominal": 1800.0,
            "max": 2400.0,
            "crit_min": 800.0,
            "crit_max": 3200.0,
            "unit": "W",
            "name": "Arc Power Equivalent",
            "info": "Arc voltage x current RMS power."
        },
        "layer_thickness": {
            "min": 1000.0,
            "nominal": 1500.0,
            "max": 2200.0,
            "crit_min": 800.0,
            "crit_max": 3500.0,
            "unit": "µm",
            "name": "Bead Layer Height",
            "info": "Vertical bead build height per pass."
        }
    },
    "High Pressure Die Casting (HPDC)": {
        "temperature": {
            "min": 220.0,
            "nominal": 280.0,
            "max": 340.0,
            "crit_min": 150.0,
            "crit_max": 420.0,
            "unit": "°C",
            "name": "Die Tooling Temperature",
            "info": "Pre-heated die cavity temperature to regulate solidification rate."
        },
        "energy_density": {
            "min": 40.0,
            "nominal": 55.0,
            "max": 70.0,
            "crit_min": 25.0,
            "crit_max": 90.0,
            "unit": "J/mm³",
            "name": "Specific Injection Energy",
            "info": "Hydraulic ram injection energy equivalent per volume."
        },
        "scan_speed": {
            "min": 1500.0,
            "nominal": 2500.0,
            "max": 3800.0,
            "crit_min": 900.0,
            "crit_max": 5000.0,
            "unit": "mm/s",
            "name": "Plunger Injection Velocity",
            "info": "High speed second-phase plunger velocity."
        },
        "oxygen_concentration": {
            "min": 50.0,
            "nominal": 180.0,
            "max": 350.0,
            "crit_min": 0.0,
            "crit_max": 800.0,
            "unit": "ppm",
            "name": "Cavity Entrapped Gas (O2)",
            "info": "Vacuum-assisted cavity gas residue."
        },
        "laser_power": {
            "min": 300.0,
            "nominal": 400.0,
            "max": 500.0,
            "crit_min": 200.0,
            "crit_max": 600.0,
            "unit": "W",
            "name": "Furnace Induction Equivalent",
            "info": "Thermal hold rating."
        },
        "layer_thickness": {
            "min": 1200.0,
            "nominal": 2000.0,
            "max": 3500.0,
            "crit_min": 600.0,
            "crit_max": 6000.0,
            "unit": "µm",
            "name": "Wall Thickness Profile",
            "info": "Average section thickness."
        }
    }
}

PRESET_SCENARIOS = {
    "Optimal Aerospace Baseline": {
        "alloy": "AlSi10Mg",
        "process": "Laser Powder Bed Fusion (LPBF)",
        "temperature": 200.0,
        "energy_density": 62.5,
        "scan_speed": 1300.0,
        "oxygen_concentration": 45.0,
        "laser_power": 370.0,
        "layer_thickness": 30.0,
        "hatch_spacing": 0.13,
        "notes": "Fully compliant with ASTM F3055 Class A flight criteria. Optimal melt pool stability."
    },
    "High-Speed Productivity Window": {
        "alloy": "AlSi10Mg",
        "process": "Laser Powder Bed Fusion (LPBF)",
        "temperature": 180.0,
        "energy_density": 54.0,
        "scan_speed": 1550.0,
        "oxygen_concentration": 95.0,
        "laser_power": 410.0,
        "layer_thickness": 40.0,
        "hatch_spacing": 0.15,
        "notes": "Higher build rate mode. Marginal lack-of-fusion risk at contour boundaries."
    },
    "High-Strength Scalmalloy Qualified": {
        "alloy": "Scalmalloy",
        "process": "Laser Powder Bed Fusion (LPBF)",
        "temperature": 220.0,
        "energy_density": 64.0,
        "scan_speed": 1250.0,
        "oxygen_concentration": 35.0,
        "laser_power": 380.0,
        "layer_thickness": 30.0,
        "hatch_spacing": 0.12,
        "notes": "Strict low-oxygen environment to preserve Sc/Zr submicron Al3(Sc,Zr) precipitations."
    },
    "Severe Keyholing & Overheating (Defect)": {
        "alloy": "AlSi10Mg",
        "process": "Laser Powder Bed Fusion (LPBF)",
        "temperature": 275.0,
        "energy_density": 88.0,
        "scan_speed": 750.0,
        "oxygen_concentration": 80.0,
        "laser_power": 460.0,
        "layer_thickness": 25.0,
        "hatch_spacing": 0.10,
        "notes": "Excessive energy concentration triggers metal vaporization, plasma cavity collapse, and spherical gas pores."
    },
    "Lack of Fusion / Cold Boundary (Defect)": {
        "alloy": "Al 6061-RAM2",
        "process": "Laser Powder Bed Fusion (LPBF)",
        "temperature": 110.0,
        "energy_density": 41.0,
        "scan_speed": 1850.0,
        "oxygen_concentration": 110.0,
        "laser_power": 290.0,
        "layer_thickness": 50.0,
        "hatch_spacing": 0.17,
        "notes": "Insufficient melt track overlap causes unmolten powder pockets and sharp planar defects."
    },
    "Atmospheric Oxidation Contamination (Defect)": {
        "alloy": "Al 7075-AM",
        "process": "Laser Powder Bed Fusion (LPBF)",
        "temperature": 190.0,
        "energy_density": 63.0,
        "scan_speed": 1200.0,
        "oxygen_concentration": 280.0,
        "laser_power": 360.0,
        "layer_thickness": 30.0,
        "hatch_spacing": 0.13,
        "notes": "Critical O2 leak leads to extensive Al2O3 oxide bifilms, embrittlement, and hot tearing."
    }
}


# ================================================================
# CUSTOM ADDITIVE ELEMENTS — Metallurgical Modification Database
# ================================================================
CUSTOM_ELEMENTS: Dict[str, Dict[str, Any]] = {
    "Al₂O₃": {
        "name": "Aluminium Oxide (Al₂O₃)",
        "formula": "Al₂O₃",
        "category": "Ceramic Oxide — Oxide Dispersion Strengthening (ODS)",
        "description": (
            "Nano-scale Al₂O₃ oxide particles act as Zener pinning agents, "
            "restricting grain boundary migration during solidification and heat treatment. "
            "This refines grain structure and elevates hardness, but the brittle ceramic "
            "inclusions reduce ductility and elongation at break."
        ),
        "concentration_range": "0.5 – 2.0 wt%",
        "mechanical_modifiers": {
            "yield_strength_pct": +8.0,
            "uts_pct": +5.0,
            "elongation_pct": -18.0,
            "hardness_pct": +12.0,
            "rel_density_pct": -0.08
        },
        "risk_modifiers": {
            "keyholing": +3.0,
            "lack_of_fusion": +5.0,
            "oxidation": +10.0,
            "residual_stress": +4.0
        }
    },
    "ZrO₂": {
        "name": "Zirconium Dioxide (ZrO₂)",
        "formula": "ZrO₂",
        "category": "Ceramic Oxide — Thermal Barrier & Grain Refiner",
        "description": (
            "ZrO₂ nanoparticles provide heterogeneous nucleation sites during solidification, "
            "promoting columnar-to-equiaxed transition (CET). The high melting point (~2715 °C) "
            "creates thermal barriers that reduce melt pool instabilities. Moderate ductility "
            "loss due to ceramic particle-matrix interface debonding."
        ),
        "concentration_range": "0.3 – 1.5 wt%",
        "mechanical_modifiers": {
            "yield_strength_pct": +6.0,
            "uts_pct": +4.0,
            "elongation_pct": -12.0,
            "hardness_pct": +10.0,
            "rel_density_pct": -0.05
        },
        "risk_modifiers": {
            "keyholing": -2.0,
            "lack_of_fusion": +4.0,
            "oxidation": +6.0,
            "residual_stress": -3.0
        }
    },
    "Zr": {
        "name": "Zirconium (Zr)",
        "formula": "Zr",
        "category": "Grain Refiner — Peritectic Nucleant",
        "description": (
            "Zr forms metastable Al₃Zr (L1₂) precipitates that serve as potent "
            "heterogeneous nucleation sites, transforming columnar dendrites into fine "
            "equiaxed grains. This suppresses hot-cracking susceptibility in high-strength "
            "alloys (7xxx, 6xxx) and improves both yield strength and fatigue life."
        ),
        "concentration_range": "0.1 – 0.5 wt%",
        "mechanical_modifiers": {
            "yield_strength_pct": +10.0,
            "uts_pct": +7.0,
            "elongation_pct": -4.0,
            "hardness_pct": +6.0,
            "rel_density_pct": +0.03
        },
        "risk_modifiers": {
            "keyholing": -1.0,
            "lack_of_fusion": -3.0,
            "oxidation": +2.0,
            "residual_stress": -8.0
        }
    },
    "Sc": {
        "name": "Scandium (Sc)",
        "formula": "Sc",
        "category": "High-Performance Grain Refiner — Coherent Precipitate Former",
        "description": (
            "Sc produces coherent nanoscale Al₃Sc (L1₂) precipitates with minimal lattice "
            "mismatch (~1.3%), providing exceptional Orowan strengthening without significant "
            "ductility loss. Combined with Zr (Scalmalloy-type), it creates thermally stable "
            "Al₃(Sc,Zr) core-shell precipitates resistant to coarsening up to 350 °C."
        ),
        "concentration_range": "0.2 – 0.8 wt%",
        "mechanical_modifiers": {
            "yield_strength_pct": +18.0,
            "uts_pct": +12.0,
            "elongation_pct": +5.0,
            "hardness_pct": +14.0,
            "rel_density_pct": +0.05
        },
        "risk_modifiers": {
            "keyholing": -2.0,
            "lack_of_fusion": -5.0,
            "oxidation": +3.0,
            "residual_stress": -12.0
        }
    },
    "CaO": {
        "name": "Calcium Oxide (CaO)",
        "formula": "CaO",
        "category": "Flux / Deoxidizer — Inclusion Scavenger",
        "description": (
            "CaO acts as a deoxidizing flux that reacts preferentially with dissolved oxygen "
            "and harmful oxide inclusions (Al₂O₃ bifilms), converting them into less harmful "
            "calcium aluminate (CaO·Al₂O₃) slag. This reduces oxide-related embrittlement "
            "and improves melt pool cleanliness, but excess CaO can introduce porosity."
        ),
        "concentration_range": "0.1 – 0.5 wt%",
        "mechanical_modifiers": {
            "yield_strength_pct": +2.0,
            "uts_pct": +2.0,
            "elongation_pct": +6.0,
            "hardness_pct": -1.0,
            "rel_density_pct": +0.02
        },
        "risk_modifiers": {
            "keyholing": +2.0,
            "lack_of_fusion": +1.0,
            "oxidation": -15.0,
            "residual_stress": -2.0
        }
    },
    "Mg": {
        "name": "Magnesium (Mg)",
        "formula": "Mg",
        "category": "Solid-Solution & Precipitation Strengthener",
        "description": (
            "Additional Mg enhances solid-solution strengthening of the aluminium matrix and "
            "promotes formation of Mg₂Si (β'') strengthening precipitates during T6 aging. "
            "However, Mg is highly reactive with oxygen, increasing susceptibility to MgO "
            "oxide formation and spatter during laser processing."
        ),
        "concentration_range": "0.5 – 2.0 wt%",
        "mechanical_modifiers": {
            "yield_strength_pct": +12.0,
            "uts_pct": +9.0,
            "elongation_pct": -6.0,
            "hardness_pct": +8.0,
            "rel_density_pct": -0.02
        },
        "risk_modifiers": {
            "keyholing": +4.0,
            "lack_of_fusion": -2.0,
            "oxidation": +12.0,
            "residual_stress": +3.0
        }
    },
    "Ti": {
        "name": "Titanium (Ti)",
        "formula": "Ti",
        "category": "Grain Refiner — Heterogeneous Nucleant",
        "description": (
            "Ti additions form TiB₂ and Al₃Ti intermetallic particles that serve as "
            "powerful heterogeneous nucleation catalysts during solidification. This produces "
            "ultra-fine equiaxed grain structures, improves isotropy, and significantly "
            "enhances part density by reducing shrinkage porosity."
        ),
        "concentration_range": "0.05 – 0.3 wt%",
        "mechanical_modifiers": {
            "yield_strength_pct": +7.0,
            "uts_pct": +5.0,
            "elongation_pct": +3.0,
            "hardness_pct": +5.0,
            "rel_density_pct": +0.06
        },
        "risk_modifiers": {
            "keyholing": -1.0,
            "lack_of_fusion": -6.0,
            "oxidation": +4.0,
            "residual_stress": -5.0
        }
    },
    "Zn": {
        "name": "Zinc (Zn)",
        "formula": "Zn",
        "category": "Precipitation Hardener — η' Phase Former",
        "description": (
            "Zn enables formation of MgZn₂ (η') Guinier-Preston zones and metastable "
            "precipitates during aging, producing dramatic increases in yield strength "
            "(7xxx-series mechanism). However, Zn has high vapor pressure at melt pool "
            "temperatures, increasing spatter and keyholing risk during laser processing."
        ),
        "concentration_range": "1.0 – 6.0 wt%",
        "mechanical_modifiers": {
            "yield_strength_pct": +20.0,
            "uts_pct": +15.0,
            "elongation_pct": -15.0,
            "hardness_pct": +18.0,
            "rel_density_pct": -0.03
        },
        "risk_modifiers": {
            "keyholing": +10.0,
            "lack_of_fusion": -2.0,
            "oxidation": +5.0,
            "residual_stress": +8.0
        }
    }
}

CUSTOM_ELEMENT_KEYS = ["None"] + list(CUSTOM_ELEMENTS.keys())

ALLOY_CALIBRATION_OFFSETS: Dict[str, Dict[str, float]] = {
    "AlSi10Mg": {
        "energy_density_offset": 0.0,
        "scan_speed_offset": 0.0,
        "temperature_offset": 0.0,
        "quality_bias": 0.0
    },
    "Scalmalloy": {
        "energy_density_offset": +6.0,
        "scan_speed_offset": -100.0,
        "temperature_offset": +10.0,
        "quality_bias": +0.3
    },
    "Al 6061-RAM2": {
        "energy_density_offset": +4.0,
        "scan_speed_offset": -150.0,
        "temperature_offset": +20.0,
        "quality_bias": -0.8
    },
    "Al 7075-AM": {
        "energy_density_offset": -6.0,
        "scan_speed_offset": +80.0,
        "temperature_offset": -15.0,
        "quality_bias": -1.5
    },
    "A356-T6": {
        "energy_density_offset": -3.0,
        "scan_speed_offset": -50.0,
        "temperature_offset": -10.0,
        "quality_bias": -0.4
    }
}

ELEMENT_CALIBRATION_OFFSETS: Dict[str, Dict[str, float]] = {
    "None": {
        "ved_shift": 0.0,
        "speed_shift": 0.0,
        "window_expand_ved": 0.0,
        "window_expand_speed": 0.0,
        "quality_impact": 0.0
    },
    "Al2O3": {
        "ved_shift": -2.0,
        "speed_shift": 0.0,
        "window_expand_ved": -2.0,
        "window_expand_speed": 0.0,
        "quality_impact": -1.2
    },
    "ZrO2": {
        "ved_shift": +3.0,
        "speed_shift": -50.0,
        "window_expand_ved": +1.0,
        "window_expand_speed": +30.0,
        "quality_impact": -0.4
    },
    "Zr": {
        "ved_shift": +1.0,
        "speed_shift": +50.0,
        "window_expand_ved": +2.0,
        "window_expand_speed": +60.0,
        "quality_impact": +0.8
    },
    "Sc": {
        "ved_shift": +2.0,
        "speed_shift": +80.0,
        "window_expand_ved": +4.0,
        "window_expand_speed": +100.0,
        "quality_impact": +1.4
    },
    "CaO": {
        "ved_shift": 0.0,
        "speed_shift": -30.0,
        "window_expand_ved": 0.0,
        "window_expand_speed": +20.0,
        "quality_impact": -0.6
    },
    "Mg": {
        "ved_shift": -4.0,
        "speed_shift": +50.0,
        "window_expand_ved": -3.0,
        "window_expand_speed": -40.0,
        "quality_impact": -1.8
    },
    "Ti": {
        "ved_shift": +1.0,
        "speed_shift": +40.0,
        "window_expand_ved": +2.0,
        "window_expand_speed": +50.0,
        "quality_impact": +0.6
    },
    "Zn": {
        "ved_shift": -5.0,
        "speed_shift": +60.0,
        "window_expand_ved": -4.0,
        "window_expand_speed": -30.0,
        "quality_impact": -2.2
    }
}


def get_alloy_details(alloy_key: str) -> Dict[str, Any]:
    return ALLOY_STANDARDS.get(alloy_key, ALLOY_STANDARDS["AlSi10Mg"])

def get_process_limits(process_name: str, alloy_key: str = "AlSi10Mg", custom_element: str = "None") -> Dict[str, Any]:
    import copy
    base_limits = PROCESS_LIMITS.get(process_name, PROCESS_LIMITS["Laser Powder Bed Fusion (LPBF)"])
    limits = copy.deepcopy(base_limits)

    if alloy_key == "AlSi10Mg" and (custom_element == "None" or not custom_element):
        return limits

    alloy_off = ALLOY_CALIBRATION_OFFSETS.get(alloy_key, ALLOY_CALIBRATION_OFFSETS["AlSi10Mg"])
    elem_off = ELEMENT_CALIBRATION_OFFSETS.get(custom_element, ELEMENT_CALIBRATION_OFFSETS["None"])

    # Calibrate Energy Density
    ved_shift = alloy_off.get("energy_density_offset", 0.0) + elem_off.get("ved_shift", 0.0)
    ved_expand = elem_off.get("window_expand_ved", 0.0)
    if "energy_density" in limits:
        ed = limits["energy_density"]
        ed["nominal"] = round(ed["nominal"] + ved_shift, 1)
        ed["min"] = round(max(ed["crit_min"] + 4.0, ed["min"] + ved_shift - ved_expand), 1)
        ed["max"] = round(min(ed["crit_max"] - 4.0, ed["max"] + ved_shift + ved_expand), 1)

    # Calibrate Scan Speed
    spd_shift = alloy_off.get("scan_speed_offset", 0.0) + elem_off.get("speed_shift", 0.0)
    spd_expand = elem_off.get("window_expand_speed", 0.0)
    if "scan_speed" in limits:
        sp = limits["scan_speed"]
        sp["nominal"] = round(sp["nominal"] + spd_shift, 0)
        sp["min"] = round(max(sp["crit_min"] + 40.0, sp["min"] + spd_shift - spd_expand), 0)
        sp["max"] = round(min(sp["crit_max"] - 40.0, sp["max"] + spd_shift + spd_expand), 0)

    # Calibrate Preheat Temperature
    temp_shift = alloy_off.get("temperature_offset", 0.0)
    if "temperature" in limits:
        tp = limits["temperature"]
        tp["nominal"] = round(tp["nominal"] + temp_shift, 0)
        tp["min"] = round(max(tp["crit_min"] + 10.0, tp["min"] + temp_shift), 0)
        tp["max"] = round(min(tp["crit_max"] - 10.0, tp["max"] + temp_shift), 0)

    return limits

def get_presets() -> Dict[str, Any]:
    return PRESET_SCENARIOS

def get_custom_element(element_key: str) -> Dict[str, Any]:
    """Returns the metallurgical data for a custom additive element, or None."""
    if element_key == "None" or element_key not in CUSTOM_ELEMENTS:
        return None
    return CUSTOM_ELEMENTS[element_key]
