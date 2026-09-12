"""
AluSense AI - Metallurgy & Process Analysis Engine
Evaluates parameter envelopes against ISO/ASTM 52900, ASTM F3055, and AMS standards.
Predicts multivariable defect probabilities, mechanical properties, and quality scores.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime

from dataset.standards import (
    get_alloy_details,
    get_process_limits,
    get_custom_element,
    ALLOY_CALIBRATION_OFFSETS,
    ELEMENT_CALIBRATION_OFFSETS
)


@dataclass
class ParameterStatus:
    key: str
    name: str
    value: float
    unit: str
    nominal: float
    safe_min: float
    safe_max: float
    crit_min: float
    crit_max: float
    status: str          # "NOMINAL", "WARNING_LOW", "WARNING_HIGH", "CRITICAL_LOW", "CRITICAL_HIGH"
    deviation_pct: float
    deviation_label: str
    severity_level: int  # 0=nominal, 1=warning, 2=critical
    info: str


@dataclass
class DefectRisk:
    name: str
    probability: float   # 0.0 to 100.0%
    severity: str        # "MINIMAL", "MODERATE", "ELEVATED", "CRITICAL"
    primary_driver: str
    microstructure_impact: str
    triggers: List[str] = field(default_factory=list)


@dataclass
class MechanicalPrediction:
    yield_strength: float  # MPa
    uts: float             # MPa
    elongation: float      # %
    rel_density: float     # %
    hardness: float        # HV
    yield_delta: float
    uts_delta: float
    density_delta: float


@dataclass
class AnalysisResult:
    alloy_key: str
    alloy_info: Dict[str, Any]
    process_name: str
    inputs: Dict[str, float]
    parameters: Dict[str, ParameterStatus]
    quality_score: float
    quality_grade: str
    compliance_status: str
    passed_parameters_count: int
    total_parameters_count: int
    defect_risks: Dict[str, DefectRisk]
    peak_risk: DefectRisk
    mechanical: MechanicalPrediction
    recommendations: List[Dict[str, str]]
    timestamp: str
    custom_element: str = "None"


def calculate_ved_from_optics(power_w: float, speed_mms: float, layer_um: float, hatch_spacing_mm: float = 0.13) -> float:
    """
    Computes Volumetric Energy Density (VED) in J/mm³.
    VED = Power / (v * h * t)
    v = speed (mm/s), h = hatch spacing (mm), t = layer thickness (mm)
    """
    if speed_mms <= 0 or hatch_spacing_mm <= 0 or layer_um <= 0:
        return 0.0
    layer_mm = layer_um / 1000.0
    ved = power_w / (speed_mms * hatch_spacing_mm * layer_mm)
    return round(ved, 2)


def evaluate_parameter(key: str, value: float, limits: Dict[str, Any]) -> ParameterStatus:
    """Compares a single process parameter with calibrated boundaries."""
    safe_min = limits["min"]
    nominal = limits["nominal"]
    safe_max = limits["max"]
    crit_min = limits["crit_min"]
    crit_max = limits["crit_max"]
    unit = limits["unit"]
    name = limits["name"]
    info = limits.get("info", "")

    # Calculate deviation percentage from nominal
    if nominal != 0:
        dev_pct = ((value - nominal) / nominal) * 100.0
    else:
        dev_pct = 0.0

    if dev_pct > 0:
        dev_label = f"+{dev_pct:.1f}%"
    else:
        dev_label = f"{dev_pct:.1f}%"

    if value < crit_min:
        status = "CRITICAL_LOW"
        severity = 2
    elif value > crit_max:
        status = "CRITICAL_HIGH"
        severity = 2
    elif value < safe_min:
        status = "WARNING_LOW"
        severity = 1
    elif value > safe_max:
        status = "WARNING_HIGH"
        severity = 1
    else:
        status = "NOMINAL"
        severity = 0

    return ParameterStatus(
        key=key,
        name=name,
        value=round(value, 2),
        unit=unit,
        nominal=nominal,
        safe_min=safe_min,
        safe_max=safe_max,
        crit_min=crit_min,
        crit_max=crit_max,
        status=status,
        deviation_pct=round(dev_pct, 1),
        deviation_label=dev_label,
        severity_level=severity,
        info=info
    )


def calculate_quality_score(
    param_statuses: Dict[str, ParameterStatus],
    defect_risks: Dict[str, Any] = None,
    alloy_key: str = "AlSi10Mg",
    custom_element: str = "None"
) -> float:
    """
    Computes an engineering composite Quality Score (0 to 100%).
    Reflects:
    - Distance of active parameters from calibrated nominals and limits (continuous gradient)
    - Elevated defect risk probabilities
    - Alloy-specific AM processability
    - Custom additive element metallurgical enhancements or volatility penalties
    """
    base_score = 100.0

    weights = {
        "energy_density": 1.4,
        "oxygen_concentration": 1.2,
        "temperature": 1.0,
        "scan_speed": 1.1,
        "laser_power": 0.8,
        "layer_thickness": 0.8
    }

    total_penalty = 0.0

    for key, p in param_statuses.items():
        w = weights.get(key, 1.0)
        if p.status in ("CRITICAL_LOW", "CRITICAL_HIGH"):
            # Distance beyond critical limit
            if p.status == "CRITICAL_LOW":
                dist = abs(p.value - p.crit_min) / max(1.0, (p.nominal - p.crit_min))
            else:
                dist = abs(p.value - p.crit_max) / max(1.0, (p.crit_max - p.nominal))
            p_pen = (24.0 + min(16.0, dist * 20.0)) * w
        elif p.status in ("WARNING_LOW", "WARNING_HIGH"):
            if p.status == "WARNING_LOW":
                dist = (p.safe_min - p.value) / max(1.0, (p.safe_min - p.crit_min))
            else:
                dist = (p.value - p.safe_max) / max(1.0, (p.crit_max - p.safe_max))
            p_pen = (8.0 + dist * 8.0) * w
        else:
            # Nominal zone: continuous gradient so even small adjustments shift score smoothly
            dist_nom = abs(p.value - p.nominal) / max(1.0, (p.safe_max - p.safe_min) / 2.0)
            p_pen = (dist_nom * 3.2) * w

        total_penalty += p_pen

    # Defect risk penalty integration (penalizes defect risks above nominal 5.0% baseline)
    risk_penalty = 0.0
    if defect_risks:
        for r in defect_risks.values():
            prob = getattr(r, "probability", 0.0)
            if prob > 5.0:
                risk_penalty += (prob - 5.0) * 0.12

    # Alloy processability bias
    alloy_bias = ALLOY_CALIBRATION_OFFSETS.get(alloy_key, {}).get("quality_bias", 0.0)

    # Custom element metallurgical quality impact
    elem_impact = ELEMENT_CALIBRATION_OFFSETS.get(custom_element, {}).get("quality_impact", 0.0)

    final_score = max(5.0, min(100.0, base_score - total_penalty - risk_penalty + alloy_bias + elem_impact))
    return round(final_score, 1)


def predict_defects(alloy_key: str, process_name: str, inputs: Dict[str, float], limits: Dict[str, Any]) -> Dict[str, DefectRisk]:
    """
    Metallurgical defect risk predictive models.
    Returns quantitative defect hazard probabilities (0-100%).
    """
    temp = inputs.get("temperature", 200.0)
    ved = inputs.get("energy_density", 62.0)
    speed = inputs.get("scan_speed", 1300.0)
    o2 = inputs.get("oxygen_concentration", 45.0)

    ved_lim = limits["energy_density"]
    temp_lim = limits["temperature"]
    speed_lim = limits["scan_speed"]
    o2_lim = limits["oxygen_concentration"]

    # 1. Keyholing & Overheating Porosity
    # Triggered by excessive VED, low scan speed, or very high substrate temp
    keyhole_prob = 3.0
    kh_triggers = []
    if ved > ved_lim["max"]:
        factor = (ved - ved_lim["max"]) / max(1.0, (ved_lim["crit_max"] - ved_lim["max"]))
        keyhole_prob += 40.0 * min(2.2, factor)
        kh_triggers.append(f"Excessive VED ({ved:.1f} J/mm³ > {ved_lim['max']:.1f})")
    if speed < speed_lim["min"]:
        factor = (speed_lim["min"] - speed) / max(1.0, (speed_lim["min"] - speed_lim["crit_min"]))
        keyhole_prob += 25.0 * min(2.0, factor)
        kh_triggers.append(f"Sub-critical scan speed ({speed:.0f} mm/s)")
    if temp > temp_lim["max"]:
        keyhole_prob += 15.0
        kh_triggers.append(f"Elevated bed temperature ({temp:.0f} °C)")

    keyhole_prob = min(98.5, max(2.0, keyhole_prob))

    # 2. Lack of Fusion (LoF) Porosity
    # Triggered by insufficient VED, excessive scan speed, or low preheat
    lof_prob = 3.0
    lof_triggers = []
    if ved < ved_lim["min"]:
        factor = (ved_lim["min"] - ved) / max(1.0, (ved_lim["min"] - ved_lim["crit_min"]))
        lof_prob += 45.0 * min(2.0, factor)
        lof_triggers.append(f"Insufficient VED ({ved:.1f} J/mm³ < {ved_lim['min']:.1f})")
    if speed > speed_lim["max"]:
        factor = (speed - speed_lim["max"]) / max(1.0, (speed_lim["crit_max"] - speed_lim["max"]))
        lof_prob += 30.0 * min(2.0, factor)
        lof_triggers.append(f"Excessive beam velocity ({speed:.0f} mm/s > {speed_lim['max']:.0f})")
    if temp < temp_lim["min"]:
        lof_prob += 12.0
        lof_triggers.append("Cold platform boundary")

    lof_prob = min(98.5, max(2.0, lof_prob))

    # 3. Atmospheric Oxidation & Alumina Inclusions
    # Triggered by high oxygen ppm and temperature
    ox_prob = 2.0
    ox_triggers = []
    if o2 > o2_lim["max"]:
        factor = (o2 - o2_lim["max"]) / max(1.0, (o2_lim["crit_max"] - o2_lim["max"]))
        ox_prob += 55.0 * min(1.8, factor)
        ox_triggers.append(f"High chamber O2 ({o2:.0f} ppm > {o2_lim['max']:.0f})")
    elif o2 > o2_lim["nominal"]:
        ox_prob += 10.0 * ((o2 - o2_lim["nominal"]) / (o2_lim["max"] - o2_lim["nominal"]))
    if temp > temp_lim["max"]:
        ox_prob += 10.0
        ox_triggers.append("Elevated thermal oxidation rate")

    ox_prob = min(99.0, max(1.5, ox_prob))

    # 4. Thermal Stress, Warpage & Balling
    # Triggered by cold substrate, high thermal gradient, or high speed / low VED ratio
    stress_prob = 4.0
    stress_triggers = []
    if temp < temp_lim["min"]:
        factor = (temp_lim["min"] - temp) / max(1.0, (temp_lim["min"] - temp_lim["crit_min"]))
        stress_prob += 40.0 * min(2.0, factor)
        stress_triggers.append(f"Cold platform ({temp:.0f} °C < {temp_lim['min']:.0f})")
    if speed > speed_lim["nominal"] and ved < ved_lim["nominal"]:
        stress_prob += 20.0
        stress_triggers.append("Melt pool capillary Plateau-Rayleigh instability (Balling)")
    if alloy_key in ("Al 7075-AM", "Al 6061-RAM2") and temp < 160.0:
        stress_prob += 20.0
        stress_triggers.append(f"{alloy_key} solidification shrinkage sensitivity")

    stress_prob = min(97.0, max(3.0, stress_prob))

    def get_sev(p: float) -> str:
        if p >= 65.0:
            return "CRITICAL"
        if p >= 40.0:
            return "ELEVATED"
        if p >= 20.0:
            return "MODERATE"
        return "MINIMAL"

    risks = {
        "keyholing": DefectRisk(
            name="Keyholing & Evaporative Porosity",
            probability=round(keyhole_prob, 1),
            severity=get_sev(keyhole_prob),
            primary_driver="Excess energy concentration / Metal vaporization",
            microstructure_impact="Forms deep spherical gas pores at root of melt track; degrades high-cycle fatigue life.",
            triggers=kh_triggers if kh_triggers else ["Parameters within stable conduction mode"]
        ),
        "lack_of_fusion": DefectRisk(
            name="Lack of Fusion (LoF) Porosity",
            probability=round(lof_prob, 1),
            severity=get_sev(lof_prob),
            primary_driver="Insufficient melt pool depth / Unmolten powder",
            microstructure_impact="Yields sharp, irregular planar voids with unmolten particles; causes abrupt catastrophic tensile failure.",
            triggers=lof_triggers if lof_triggers else ["Adequate inter-track & inter-layer overlap"]
        ),
        "oxidation": DefectRisk(
            name="Atmospheric Oxidation & Bifilms",
            probability=round(ox_prob, 1),
            severity=get_sev(ox_prob),
            primary_driver="Chamber O2 ingress / High thermal reactivity",
            microstructure_impact="Generates brittle Al2O3 oxide skins that pin grain boundaries and induce hot tearing.",
            triggers=ox_triggers if ox_triggers else ["Inert gas atmosphere within clean specification"]
        ),
        "residual_stress": DefectRisk(
            name="Residual Stress & Balling Defect",
            probability=round(stress_prob, 1),
            severity=get_sev(stress_prob),
            primary_driver="Steep thermal gradients / Surface tension instability",
            microstructure_impact="Causes part warpage, delamination from support structures, and severe surface roughness (Ra > 25 µm).",
            triggers=stress_triggers if stress_triggers else ["Thermal gradients controlled by baseplate preheating"]
        )
    }

    return risks


def predict_mechanical_properties(alloy_info: Dict[str, Any], quality_score: float, risks: Dict[str, DefectRisk]) -> MechanicalPrediction:
    """Predicts mechanical response adjusted by defect probabilities."""
    nom = alloy_info["nominal_mechanical"]
    
    # Degradation factors
    max_risk_factor = max(r.probability for r in risks.values()) / 100.0
    quality_ratio = quality_score / 100.0

    # Density drops sharply with LoF and Keyholing
    density_loss = (risks["lack_of_fusion"].probability * 0.035) + (risks["keyholing"].probability * 0.025)
    pred_density = max(94.0, min(nom["rel_density"], nom["rel_density"] - density_loss))

    # Strength degradation
    strength_pen = (1.0 - quality_ratio) * 0.28 + (max_risk_factor * 0.15)
    pred_yield = max(nom["yield_strength"] * 0.55, nom["yield_strength"] * (1.0 - strength_pen))
    pred_uts = max(nom["uts"] * 0.55, nom["uts"] * (1.0 - strength_pen * 1.1))

    # Elongation drops most precipitously with defects
    elong_pen = (1.0 - quality_ratio) * 0.55 + (risks["oxidation"].probability / 100.0 * 0.3)
    pred_elong = max(1.5, nom["elongation"] * (1.0 - elong_pen))

    # Hardness correlates with density and oxidation
    hard_shift = (nom["hardness"] * (pred_density / nom["rel_density"]))
    pred_hard = round(hard_shift, 1)

    return MechanicalPrediction(
        yield_strength=round(pred_yield, 1),
        uts=round(pred_uts, 1),
        elongation=round(pred_elong, 1),
        rel_density=round(pred_density, 2),
        hardness=pred_hard,
        yield_delta=round(pred_yield - nom["yield_strength"], 1),
        uts_delta=round(pred_uts - nom["uts"], 1),
        density_delta=round(pred_density - nom["rel_density"], 2)
    )


def generate_recommendations(param_statuses: Dict[str, ParameterStatus], risks: Dict[str, DefectRisk], limits: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generates precise, actionable engineering recommendations."""
    recs = []

    # Priority 1: Keyholing
    if risks["keyholing"].probability >= 40.0:
        target_ved = limits["energy_density"]["nominal"]
        recs.append({
            "code": "REC-01",
            "category": "THERMAL FLUX",
            "action": f"Reduce Energy Density toward {target_ved:.1f} J/mm³",
            "detail": "Lower laser power by 10-15% or increase scan velocity to suppress metal vaporization and vapor depression collapse.",
            "urgency": "HIGH" if risks["keyholing"].probability >= 65.0 else "MEDIUM"
        })

    # Priority 2: Lack of Fusion
    if risks["lack_of_fusion"].probability >= 40.0:
        target_ved = limits["energy_density"]["nominal"]
        recs.append({
            "code": "REC-02",
            "category": "CONSOLIDATION",
            "action": f"Increase Volumetric Energy Density to ≥ {limits['energy_density']['min']:.1f} J/mm³",
            "detail": "Decrease scan speed or increase laser power to achieve full melt pool penetration and eliminate unmolten powder interstices.",
            "urgency": "HIGH" if risks["lack_of_fusion"].probability >= 65.0 else "MEDIUM"
        })

    # Priority 3: Oxygen
    if risks["oxidation"].probability >= 30.0:
        target_o2 = limits["oxygen_concentration"]["nominal"]
        recs.append({
            "code": "REC-03",
            "category": "ATMOSPHERE",
            "action": f"Purge Chamber Atmosphere to ≤ {target_o2:.0f} ppm O₂",
            "detail": "Inspect chamber door seals, verify recirculating filter integrity, and perform 2-stage argon flush to prevent brittle Al2O3 bifilm generation.",
            "urgency": "CRITICAL" if risks["oxidation"].probability >= 65.0 else "MEDIUM"
        })

    # Priority 4: Temperature / Residual Stress
    if risks["residual_stress"].probability >= 35.0:
        target_temp = limits["temperature"]["nominal"]
        recs.append({
            "code": "REC-04",
            "category": "THERMAL GRADIENT",
            "action": f"Adjust Preheating Bed Temperature to {target_temp:.0f} °C",
            "detail": "Mitigate steep cooling gradients ($dT/dt$) across build envelope to avoid part detachment from build plate and residual stress cracking.",
            "urgency": "MEDIUM"
        })

    # If all nominal
    if not recs:
        recs.append({
            "code": "REC-00",
            "category": "PROCESS CONTROL",
            "action": "Maintain Active Qualified Parameter Window",
            "detail": "All parameters reside within ASTM/ISO nominal tolerances. Proceed with standard batch manufacturing and periodic powder sieve qualification.",
            "urgency": "LOW"
        })

    return recs


def apply_element_modifiers_to_mechanical(mech: MechanicalPrediction, alloy_info: Dict[str, Any], element_data: Dict[str, Any]) -> MechanicalPrediction:
    """Applies custom element percentage modifiers to predicted mechanical properties."""
    mods = element_data["mechanical_modifiers"]
    nom = alloy_info["nominal_mechanical"]

    new_yield = mech.yield_strength * (1.0 + mods["yield_strength_pct"] / 100.0)
    new_uts = mech.uts * (1.0 + mods["uts_pct"] / 100.0)
    new_elong = max(1.0, mech.elongation * (1.0 + mods["elongation_pct"] / 100.0))
    new_hard = mech.hardness * (1.0 + mods["hardness_pct"] / 100.0)
    new_density = mech.rel_density + mods["rel_density_pct"]
    new_density = max(94.0, min(99.99, new_density))

    return MechanicalPrediction(
        yield_strength=round(new_yield, 1),
        uts=round(new_uts, 1),
        elongation=round(new_elong, 1),
        rel_density=round(new_density, 2),
        hardness=round(new_hard, 1),
        yield_delta=round(new_yield - nom["yield_strength"], 1),
        uts_delta=round(new_uts - nom["uts"], 1),
        density_delta=round(new_density - nom["rel_density"], 2)
    )


def apply_element_modifiers_to_risks(risks: Dict[str, DefectRisk], element_data: Dict[str, Any]) -> Dict[str, DefectRisk]:
    """Applies custom element risk modifiers to defect probabilities."""
    mods = element_data["risk_modifiers"]
    modified = {}
    for r_key, r in risks.items():
        delta = mods.get(r_key, 0.0)
        new_prob = min(99.0, max(2.0, r.probability + delta))

        def get_sev(p: float) -> str:
            if p >= 65.0:
                return "CRITICAL"
            if p >= 40.0:
                return "ELEVATED"
            if p >= 20.0:
                return "MODERATE"
            return "MINIMAL"

        modified[r_key] = DefectRisk(
            name=r.name,
            probability=round(new_prob, 1),
            severity=get_sev(new_prob),
            primary_driver=r.primary_driver,
            microstructure_impact=r.microstructure_impact,
            triggers=r.triggers
        )
    return modified


def analyze_manufacturing_process(
    alloy_key: str,
    process_name: str,
    temperature: float,
    energy_density: float,
    scan_speed: float,
    oxygen_concentration: float,
    laser_power: float = 370.0,
    layer_thickness: float = 30.0,
    custom_element: str = "None"
) -> AnalysisResult:
    """
    Main analysis pipeline orchestrator.
    Optionally accepts a custom additive element key to modify predictions.
    """
    alloy_info = get_alloy_details(alloy_key)
    limits = get_process_limits(process_name, alloy_key=alloy_key, custom_element=custom_element)

    inputs = {
        "temperature": temperature,
        "energy_density": energy_density,
        "scan_speed": scan_speed,
        "oxygen_concentration": oxygen_concentration,
        "laser_power": laser_power,
        "layer_thickness": layer_thickness
    }

    # Evaluate each parameter against calibrated limits
    param_statuses = {}
    for p_key, p_val in inputs.items():
        if p_key in limits:
            param_statuses[p_key] = evaluate_parameter(p_key, p_val, limits[p_key])

    # Defect risks
    risks = predict_defects(alloy_key, process_name, inputs, limits)

    # Apply custom element modifiers (if selected)
    element_data = get_custom_element(custom_element)
    if element_data is not None:
        risks = apply_element_modifiers_to_risks(risks, element_data)

    # Quality Score (sensitive to parameters, defect risks, alloy, and custom element)
    quality_score = calculate_quality_score(
        param_statuses,
        defect_risks=risks,
        alloy_key=alloy_key,
        custom_element=custom_element
    )

    # Compliance grade
    passed_count = sum(1 for p in param_statuses.values() if p.severity_level == 0)
    total_count = len(param_statuses)

    if quality_score >= 90.0 and passed_count == total_count:
        quality_grade = "CLASS A — AEROSPACE QUALIFIED"
        compliance_status = "FULL COMPLIANCE (IN-SPEC)"
    elif quality_score >= 75.0:
        quality_grade = "CLASS B — INDUSTRIAL ACCEPTABLE"
        compliance_status = "ACCEPTABLE (ADVISORY TOLERANCE)"
    elif quality_score >= 58.0:
        quality_grade = "CLASS C — CONDITIONAL REWORK"
        compliance_status = "CONDITIONAL (DEVIATION DETECTED)"
    else:
        quality_grade = "CLASS R — CRITICAL REJECT"
        compliance_status = "NON-CONFORMANCE (OUT-OF-SPEC)"

    # Mechanical properties
    mech_pred = predict_mechanical_properties(alloy_info, quality_score, risks)
    if element_data is not None:
        mech_pred = apply_element_modifiers_to_mechanical(mech_pred, alloy_info, element_data)

    # Find peak risk (after element modifiers)
    peak_risk = max(risks.values(), key=lambda r: r.probability)

    # Recommendations
    recs = generate_recommendations(param_statuses, risks, limits)

    # Add element-specific recommendation if applicable
    if element_data is not None:
        mods = element_data["mechanical_modifiers"]
        effect_summary_parts = []
        if mods["yield_strength_pct"] > 0:
            effect_summary_parts.append(f"yield +{mods['yield_strength_pct']:.0f}%")
        elif mods["yield_strength_pct"] < 0:
            effect_summary_parts.append(f"yield {mods['yield_strength_pct']:.0f}%")
        if mods["elongation_pct"] > 0:
            effect_summary_parts.append(f"elongation +{mods['elongation_pct']:.0f}%")
        elif mods["elongation_pct"] < 0:
            effect_summary_parts.append(f"elongation {mods['elongation_pct']:.0f}%")
        effect_str = ", ".join(effect_summary_parts) if effect_summary_parts else "minor adjustments"

        recs.append({
            "code": "REC-EL",
            "category": "ELEMENT ADDITIVE",
            "action": f"Custom Element {element_data['formula']} ({element_data['concentration_range']}) Applied",
            "detail": f"{element_data['description']} Predicted property shifts: {effect_str}.",
            "urgency": "ADVISORY"
        })

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    return AnalysisResult(
        alloy_key=alloy_key,
        alloy_info=alloy_info,
        process_name=process_name,
        inputs=inputs,
        parameters=param_statuses,
        quality_score=quality_score,
        quality_grade=quality_grade,
        compliance_status=compliance_status,
        passed_parameters_count=passed_count,
        total_parameters_count=total_count,
        defect_risks=risks,
        peak_risk=peak_risk,
        mechanical=mech_pred,
        recommendations=recs,
        timestamp=timestamp_str,
        custom_element=custom_element
    )
