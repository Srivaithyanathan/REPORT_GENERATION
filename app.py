"""
AluSense AI™ — Aluminium Manufacturing Intelligence Platform
Commercial Industrial Quality Assessment Interface
"""

import textwrap
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

from dataset.standards import (
    ALLOY_STANDARDS,
    MANUFACTURING_PROCESSES,
    PROCESS_LIMITS,
    PRESET_SCENARIOS,
    CUSTOM_ELEMENT_KEYS,
    get_alloy_details,
    get_process_limits,
    get_presets,
    get_custom_element
)
from analysis.engine import (
    analyze_manufacturing_process,
    calculate_ved_from_optics,
    AnalysisResult
)
from utils.report_generator import generate_markdown_report, generate_html_report


# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AluSense AI™ | Aluminium Manufacturing Intelligence",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Helper function to prevent multiline markdown from turning into code blocks
def render_html(html_str: str):
    st.markdown(textwrap.dedent(html_str), unsafe_allow_html=True)


# ==========================================
# INDUSTRIAL DESIGN SYSTEM (CSS)
# ==========================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap');

:root {
    --bg-canvas: #F5F5F5;
    --bg-card: #FFFFFF;
    --bg-subtle: #F9FAFB;
    --border-card: #E5E7EB;
    --border-strong: #D1D5DB;
    --text-primary: #111111;
    --text-secondary: #4B5563;
    --text-muted: #6B7280;
    --charcoal-btn: #111111;
    --charcoal-hover: #262626;
    --shadow-subtle: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
    --shadow-hover: 0 4px 10px rgba(0,0,0,0.06);
}

/* Page Reset & Soft Grey Canvas */
html, body, [data-testid="stAppViewContainer"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-canvas) !important;
    color: var(--text-primary) !important;
}

[data-testid="stHeader"] {
    display: none !important;
}

/* Header Container */
.product-header {
    background: #FFFFFF;
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 18px 24px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-subtle);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.product-title-group {
    display: flex;
    align-items: center;
    gap: 14px;
}
.brand-mark {
    width: 38px;
    height: 38px;
    background: #111111;
    color: #FFFFFF;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 16px;
    font-family: 'JetBrains Mono', monospace;
}
.product-title {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.01em;
    color: #111111;
    margin: 0;
    line-height: 1.2;
}
.product-subtitle {
    font-size: 12.5px;
    color: #4B5563;
    font-weight: 500;
    margin-top: 2px;
}
.header-meta-group {
    display: flex;
    align-items: center;
    gap: 12px;
}
.meta-chip {
    background: #F9FAFB;
    border: 1px solid var(--border-card);
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 11.5px;
    font-weight: 600;
    color: #374151;
    font-family: 'JetBrains Mono', monospace;
    display: flex;
    align-items: center;
    gap: 6px;
}
.status-dot-green {
    width: 7px;
    height: 7px;
    background: #10B981;
    border-radius: 50%;
    display: inline-block;
}
.demo-chip {
    background: #111111;
    color: #FFFFFF;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 10.5px;
    font-weight: 700;
    letter-spacing: 0.06em;
    font-family: 'JetBrains Mono', monospace;
}

/* LEVEL 1: Decision View Card */
.decision-view-card {
    background: #FFFFFF;
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 22px;
    box-shadow: var(--shadow-subtle);
    display: grid;
    grid-template-columns: 1.2fr 2fr;
    gap: 28px;
    align-items: center;
}
.score-center-box {
    border-right: 1px solid #F3F4F6;
    padding-right: 24px;
}
.decision-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6B7280;
    font-family: 'JetBrains Mono', monospace;
}
.decision-score-large {
    font-size: 58px;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.04em;
    color: #111111;
    font-family: 'JetBrains Mono', monospace;
    margin: 8px 0 10px 0;
}
.condition-pill {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.06em;
    font-family: 'JetBrains Mono', monospace;
}
.pill-optimal {
    background: #111111;
    color: #FFFFFF;
}
.pill-acceptable {
    background: #F3F4F6;
    color: #111111;
    border: 1.5px solid #111111;
}
.pill-critical {
    background: #111111;
    color: #FFFFFF;
    border: 2px solid #111111;
    text-decoration: underline;
}
.window-ratio-text {
    font-size: 12px;
    font-weight: 600;
    color: #4B5563;
    margin-top: 8px;
    font-family: 'JetBrains Mono', monospace;
}
.recommendation-callout {
    background: #F9FAFB;
    border: 1px solid var(--border-card);
    border-left: 4px solid #111111;
    border-radius: 8px;
    padding: 16px 20px;
}
.rec-callout-title {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #6B7280;
    font-family: 'JetBrains Mono', monospace;
}
.rec-callout-action {
    font-size: 15px;
    font-weight: 800;
    color: #111111;
    margin: 4px 0 6px 0;
}
.rec-callout-desc {
    font-size: 12.5px;
    color: #4B5563;
    line-height: 1.5;
}

/* LEVEL 2: Industrial Cards */
.eng-card {
    background: #FFFFFF;
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-subtle);
}
.eng-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #F3F4F6;
    padding-bottom: 12px;
    margin-bottom: 16px;
}
.eng-card-title {
    font-size: 13.5px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #111111;
}
.eng-card-badge {
    font-size: 10.5px;
    color: #6B7280;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
}

/* Actionable Engineering Risk Cards */
.risk-action-card {
    background: #FFFFFF;
    border: 1px solid var(--border-card);
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.risk-card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.risk-card-name {
    font-size: 13.5px;
    font-weight: 700;
    color: #111111;
}
.risk-metric-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #E5E7EB;
    background: #F9FAFB;
    color: #111111;
}
.risk-metric-high {
    background: #111111;
    color: #FFFFFF;
    border-color: #111111;
}
.risk-row {
    font-size: 12px;
    color: #4B5563;
    line-height: 1.45;
    margin-top: 3px;
}
.risk-label {
    font-weight: 700;
    color: #111111;
}

/* Micro Mechanical Metric Grid */
.mech-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-top: 14px;
}
.mech-card {
    background: #F9FAFB;
    border: 1px solid var(--border-card);
    border-radius: 8px;
    padding: 12px 14px;
}
.mech-card-title {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    color: #6B7280;
    letter-spacing: 0.05em;
    font-family: 'JetBrains Mono', monospace;
}
.mech-card-val {
    font-size: 18px;
    font-weight: 800;
    color: #111111;
    font-family: 'JetBrains Mono', monospace;
    margin-top: 2px;
}
.mech-card-target {
    font-size: 10.5px;
    color: #9CA3AF;
    margin-top: 2px;
}

/* Material Properties Formatted Table */
.alloy-spec-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
    margin-top: 8px;
}
.alloy-spec-table td {
    padding: 8px 10px;
    border-bottom: 1px solid #F3F4F6;
}
.alloy-spec-table td.label-col {
    color: #4B5563;
    font-weight: 600;
    width: 45%;
}
.alloy-spec-table td.val-col {
    color: #111111;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    text-align: right;
}

/* Dark Charcoal Buttons */
div.stButton > button:first-child {
    background-color: var(--charcoal-btn) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--charcoal-btn) !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 12.5px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    padding: 8px 16px !important;
    transition: all 0.15s ease !important;
}
div.stButton > button:first-child:hover {
    background-color: var(--charcoal-hover) !important;
    border-color: var(--charcoal-hover) !important;
    transform: translateY(-1px);
}

div.stDownloadButton > button:first-child {
    background-color: var(--charcoal-btn) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--charcoal-btn) !important;
    border-radius: 8px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 12.5px !important;
    font-weight: 700 !important;
    padding: 8px 16px !important;
    transition: all 0.15s ease !important;
}
div.stDownloadButton > button:first-child:hover {
    background-color: var(--charcoal-hover) !important;
    transform: translateY(-1px);
}

/* Streamlit Widget Polishing */
.stSelectbox label, .stSlider label, .stNumberInput label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #374151 !important;
    margin-bottom: 2px !important;
}
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border-card) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 10px !important;
    margin-bottom: 14px !important;
    box-shadow: var(--shadow-subtle) !important;
}
</style>
"""
render_html(CUSTOM_CSS)


# ==========================================
# APPLICATION STATE & PRESETS
# ==========================================
if "current_preset" not in st.session_state:
    st.session_state.current_preset = "Optimal Aerospace Baseline"

presets = get_presets()

def apply_preset(preset_key: str):
    p = presets[preset_key]
    st.session_state["selected_alloy"] = p["alloy"]
    st.session_state["selected_process"] = p["process"]
    st.session_state["alloy_selector"] = p["alloy"]
    st.session_state["proc_selector"] = p["process"]
    st.session_state["input_temp"] = float(p["temperature"])
    st.session_state["input_ved"] = float(p["energy_density"])
    st.session_state["input_speed"] = float(p["scan_speed"])
    st.session_state["input_o2"] = float(p["oxygen_concentration"])
    st.session_state["input_power"] = float(p["laser_power"])
    st.session_state["input_layer"] = float(p["layer_thickness"])
    st.session_state["input_hatch"] = float(p.get("hatch_spacing", 0.13))
    st.session_state["slider_temp_key"] = float(p["temperature"])
    st.session_state["slider_ved_key"] = float(p["energy_density"])
    st.session_state["slider_speed_key"] = float(p["scan_speed"])
    st.session_state["slider_o2_key"] = float(p["oxygen_concentration"])
    st.session_state["opt_power_key"] = float(p["laser_power"])
    st.session_state["opt_layer_key"] = float(p["layer_thickness"])
    st.session_state["opt_hatch_key"] = float(p.get("hatch_spacing", 0.13))
    st.session_state["preset_note"] = p["notes"]


# ==========================================
# 1. PROFESSIONAL PRODUCT HEADER
# ==========================================
cur_alloy = st.session_state.get("selected_alloy", "AlSi10Mg")
cur_process_raw = st.session_state.get("selected_process", "Laser Powder Bed Fusion (LPBF)")
cur_element = st.session_state.get("selected_element", "None")
proc_abbr = "LPBF" if "LPBF" in cur_process_raw else ("DMLS" if "DMLS" in cur_process_raw else ("WAAM" if "WAAM" in cur_process_raw else "HPDC"))

element_chip_html = ""
if cur_element != "None":
    element_chip_html = f'<div class="meta-chip">Additive Element: <strong>{cur_element}</strong></div>'

header_html = f"""<div class="product-header">
<div class="product-title-group">
<div class="brand-mark">Al</div>
<div>
<h1 class="product-title">AluSense AI™</h1>
<div class="product-subtitle">Aluminium Manufacturing Intelligence Platform</div>
</div>
</div>
<div class="header-meta-group">
<div class="meta-chip"><span class="status-dot-green"></span> System Status: <strong>Online</strong></div>
<div class="meta-chip">Current Material: <strong>{cur_alloy}</strong></div>
{element_chip_html}
<div class="meta-chip">Process: <strong>{proc_abbr}</strong></div>
<div class="meta-chip">Analysis Mode: <strong>Quality Assessment</strong></div>
<div class="demo-chip">DEMO MODE &bull; Simulated Analysis</div>
</div>
</div>"""
st.markdown(header_html, unsafe_allow_html=True)


# ==========================================
# PROCESS CONTROLS & BACKEND EXECUTION SETUP
# ==========================================
# Pre-fetch calibrated limits for active alloy, process, and custom element
limits = get_process_limits(cur_process_raw, alloy_key=cur_alloy, custom_element=cur_element)

# Sidebar or Top Collapsible Configuration for Controls
# Let's organize the layout into Level 1 (Decision), Level 2 (Engineering), Level 3 (Details)

# We gather the parameters from session state or inputs
# To maintain intuitive flow, let's create a 2-column operational layout below Decision View


# ==========================================
# LEVEL 2 (A): GATHER INPUT PARAMETERS FIRST
# ==========================================
# To compute Decision View (Level 1), we execute the backend with the inputs:
# Let's inspect session state defaults:
t_lim = limits["temperature"]
e_lim = limits["energy_density"]
s_lim = limits["scan_speed"]
o_lim = limits["oxygen_concentration"]
p_lim = limits["laser_power"]
l_lim = limits["layer_thickness"]

# Detect process change to reset sliders within valid range
if st.session_state.get("_prev_process") != cur_process_raw:
    st.session_state["_prev_process"] = cur_process_raw
    st.session_state["slider_temp_key"] = float(t_lim["nominal"])
    st.session_state["slider_ved_key"] = float(e_lim["nominal"])
    st.session_state["slider_speed_key"] = float(s_lim["nominal"])
    st.session_state["slider_o2_key"] = float(o_lim["nominal"])
    st.session_state["opt_power_key"] = float(p_lim["nominal"])
    st.session_state["opt_layer_key"] = float(l_lim["nominal"])
    st.session_state["input_temp"] = float(t_lim["nominal"])
    st.session_state["input_ved"] = float(e_lim["nominal"])
    st.session_state["input_speed"] = float(s_lim["nominal"])
    st.session_state["input_o2"] = float(o_lim["nominal"])

def _sync_val(widget_key, backup_key, default_val, min_v, max_v):
    if widget_key in st.session_state:
        val = float(st.session_state[widget_key])
    elif backup_key in st.session_state:
        val = float(st.session_state[backup_key])
    else:
        val = float(default_val)
    clamped = float(max(min_v, min(max_v, val)))
    st.session_state[backup_key] = clamped
    st.session_state[widget_key] = clamped
    return clamped

input_temp_val = _sync_val("slider_temp_key", "input_temp", t_lim["nominal"], t_lim["crit_min"], t_lim["crit_max"])
input_ved_val = _sync_val("slider_ved_key", "input_ved", e_lim["nominal"], e_lim["crit_min"], e_lim["crit_max"])
input_speed_val = _sync_val("slider_speed_key", "input_speed", s_lim["nominal"], s_lim["crit_min"], s_lim["crit_max"])
input_o2_val = _sync_val("slider_o2_key", "input_o2", o_lim["nominal"], o_lim["crit_min"], o_lim["crit_max"])
input_power_val = _sync_val("opt_power_key", "input_power", p_lim["nominal"], p_lim["crit_min"], p_lim["crit_max"])
input_layer_val = _sync_val("opt_layer_key", "input_layer", l_lim["nominal"], l_lim["crit_min"], l_lim["crit_max"])


# ==========================================
# EXECUTE METALLURGICAL ANALYSIS BACKEND
# ==========================================
result: AnalysisResult = analyze_manufacturing_process(
    alloy_key=cur_alloy,
    process_name=cur_process_raw,
    temperature=input_temp_val,
    energy_density=input_ved_val,
    scan_speed=input_speed_val,
    oxygen_concentration=input_o2_val,
    laser_power=input_power_val,
    layer_thickness=input_layer_val,
    custom_element=cur_element
)
alloy_meta = result.alloy_info
nom_m = alloy_meta["nominal_mechanical"]


# ==========================================
# LEVEL 1: DECISION VIEW (VISUAL CENTER)
# ==========================================
# Conformance condition styling
if result.quality_score >= 90.0 and result.passed_parameters_count == result.total_parameters_count:
    condition_label = "OPTIMAL"
    pill_class = "pill-optimal"
elif result.quality_score >= 65.0:
    condition_label = "ACCEPTABLE"
    pill_class = "pill-acceptable"
else:
    condition_label = "CRITICAL"
    pill_class = "pill-critical"

primary_rec = result.recommendations[0] if result.recommendations else {
    "action": "Maintain active parameter envelope",
    "detail": "All parameters reside comfortably within standard flight limits."
}

render_html(f"""
<div class="decision-view-card">
    <div class="score-center-box">
        <div class="decision-label">PROCESS HEALTH &bull; OVERALL QUALITY SCORE</div>
        <div class="decision-score-large">{result.quality_score:.1f}%</div>
        <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:11px; font-weight:700; color:#6B7280; font-family:'JetBrains Mono';">PROCESS CONDITION:</span>
            <span class="condition-pill {pill_class}">{condition_label}</span>
        </div>
        <div class="window-ratio-text">
            {result.passed_parameters_count}/{result.total_parameters_count} parameters within operating window
        </div>
    </div>
    <div>
        <div class="recommendation-callout">
            <div class="rec-callout-title">PRIMARY QUALITY DECISION & DIRECTIVE</div>
            <div class="rec-callout-action">{primary_rec['action']}</div>
            <div class="rec-callout-desc">{primary_rec['detail']}</div>
        </div>
    </div>
</div>
""")


# ==========================================
# LEVEL 2: ENGINEERING ANALYSIS
# ==========================================
col_eng_left, col_eng_right = st.columns([1.15, 1.85], gap="large")


# ------------------------------------------
# COLUMN 1: PROCESS PARAMETERS & VALIDATION
# ------------------------------------------
with col_eng_left:
    render_html("""
    <div class="eng-card">
        <div class="eng-card-header">
            <span class="eng-card-title">Process Parameters</span>
            <span class="eng-card-badge">INPUT TELEMETRY</span>
        </div>
    """)

    # Quick Preset Selector
    selected_preset_name = st.selectbox(
        "Load Engineering Preset",
        options=list(presets.keys()),
        index=list(presets.keys()).index(st.session_state.get("last_loaded_preset", list(presets.keys())[0])) if st.session_state.get("last_loaded_preset") in presets else 0,
        key="preset_select_widget"
    )

    col_btn_load, col_info_note = st.columns([1, 1.8])
    with col_btn_load:
        if st.button("APPLY PRESET", use_container_width=True):
            st.session_state["last_loaded_preset"] = selected_preset_name
            apply_preset(selected_preset_name)
            st.rerun()

    # Material, Custom Element & Process selectors
    col_mat1, col_mat_elem, col_mat2 = st.columns(3)
    with col_mat1:
        alloy_options = list(ALLOY_STANDARDS.keys())
        new_alloy = st.selectbox(
            "Alloy Grade",
            options=alloy_options,
            index=alloy_options.index(cur_alloy),
            key="alloy_selector"
        )
        if new_alloy != cur_alloy:
            st.session_state["selected_alloy"] = new_alloy
            st.rerun()

    with col_mat_elem:
        new_element = st.selectbox(
            "Custom Element Selection",
            options=CUSTOM_ELEMENT_KEYS,
            index=CUSTOM_ELEMENT_KEYS.index(cur_element) if cur_element in CUSTOM_ELEMENT_KEYS else 0,
            key="element_selector"
        )
        if new_element != cur_element:
            st.session_state["selected_element"] = new_element
            st.rerun()

    with col_mat2:
        new_proc = st.selectbox(
            "Process",
            options=MANUFACTURING_PROCESSES,
            index=MANUFACTURING_PROCESSES.index(cur_process_raw),
            key="proc_selector"
        )
        if new_proc != cur_process_raw:
            st.session_state["selected_process"] = new_proc
            st.rerun()

    st.markdown("<div style='height:1px; background:#F3F4F6; margin:14px 0;'></div>", unsafe_allow_html=True)

    # Updated Terminology: "Build Plate Preheat (°C)" as requested
    slider_temp = st.slider(
        f"Build Plate Preheat ({t_lim['unit']})",
        min_value=float(t_lim["crit_min"]),
        max_value=float(t_lim["crit_max"]),
        value=input_temp_val,
        step=5.0,
        help=f"Substrate preheating. Nominal: {t_lim['nominal']} {t_lim['unit']} | Safe: {t_lim['min']} – {t_lim['max']}",
        key="slider_temp_key"
    )

    slider_ved = st.slider(
        f"Energy Density ({e_lim['unit']})",
        min_value=float(e_lim["crit_min"]),
        max_value=float(e_lim["crit_max"]),
        value=input_ved_val,
        step=0.5,
        help=f"Volumetric energy density. Nominal: {e_lim['nominal']} {e_lim['unit']}",
        key="slider_ved_key"
    )

    slider_speed = st.slider(
        f"Scan Speed ({s_lim['unit']})",
        min_value=float(s_lim["crit_min"]),
        max_value=float(s_lim["crit_max"]),
        value=input_speed_val,
        step=25.0,
        help=f"Laser scan velocity. Nominal: {s_lim['nominal']} {s_lim['unit']}",
        key="slider_speed_key"
    )

    slider_o2 = st.slider(
        f"Oxygen Concentration ({o_lim['unit']})",
        min_value=float(o_lim["crit_min"]),
        max_value=float(o_lim["crit_max"]),
        value=input_o2_val,
        step=5.0,
        help=f"Chamber residual oxygen. Max allowed: {o_lim['max']} {o_lim['unit']}",
        key="slider_o2_key"
    )

    # Seamlessly persist slider telemetry in session state without triggering redundant reruns
    st.session_state["input_temp"] = slider_temp
    st.session_state["input_ved"] = slider_ved
    st.session_state["input_speed"] = slider_speed
    st.session_state["input_o2"] = slider_o2

    # Secondary Optics Expander
    with st.expander("Secondary Optics & Slicing Controls"):
        opt_power = st.number_input(
            f"Laser Power ({p_lim['unit']})",
            min_value=float(p_lim["crit_min"]),
            max_value=float(p_lim["crit_max"]),
            value=input_power_val,
            step=10.0,
            key="opt_power_key"
        )
        opt_layer = st.number_input(
            f"Layer Thickness ({l_lim['unit']})",
            min_value=float(l_lim["crit_min"]),
            max_value=float(l_lim["crit_max"]),
            value=input_layer_val,
            step=5.0,
            key="opt_layer_key"
        )
        opt_hatch = st.number_input(
            "Hatch Spacing (mm)",
            min_value=0.05,
            max_value=0.30,
            value=float(st.session_state.get("input_hatch", 0.13)),
            step=0.01,
            key="opt_hatch_key"
        )
        derived_ved = calculate_ved_from_optics(opt_power, slider_speed, opt_layer, opt_hatch)
        st.markdown(f"<div style='font-size:11px; font-family:JetBrains Mono; background:#F9FAFB; padding:6px 10px; border:1px solid #E5E7EB; border-radius:6px; margin-top:6px;'>OPTICAL VED: <strong>{derived_ved:.1f} J/mm³</strong></div>", unsafe_allow_html=True)
        if st.button("SYNC VED WITH OPTICS", use_container_width=True):
            st.session_state["input_ved"] = derived_ved
            st.session_state["input_power"] = opt_power
            st.session_state["input_layer"] = opt_layer
            st.session_state["input_hatch"] = opt_hatch
            st.rerun()

    render_html("</div>")

    # Parameter Validation Table Card
    render_html("""
    <div class="eng-card">
        <div class="eng-card-header">
            <span class="eng-card-title">Parameter Validation</span>
            <span class="eng-card-badge">STANDARD LIMITS</span>
        </div>
    """)

    validation_rows = []
    for p_key, p in result.parameters.items():
        disp_name = "Build Plate Preheat" if "temp" in p_key else p.name
        # Clean numeric formatting for safe bounds
        win_fmt = f"{p.safe_min:.0f}–{p.safe_max:.0f} {p.unit}" if p.safe_max >= 10 else f"{p.safe_min:.1f}–{p.safe_max:.1f} {p.unit}"
        validation_rows.append({
            "Parameter": disp_name,
            "Measured": f"{p.value:.1f} {p.unit}",
            "Operating Window": win_fmt,
            "Drift": p.deviation_label,
            "Status": p.status
        })
    df_val = pd.DataFrame(validation_rows)
    st.dataframe(
        df_val,
        column_config={
            "Parameter": st.column_config.TextColumn("Parameter", width=130),
            "Measured": st.column_config.TextColumn("Value", width=80),
            "Operating Window": st.column_config.TextColumn("Window", width=105),
            "Drift": st.column_config.TextColumn("Drift", width=55),
            "Status": st.column_config.TextColumn("Status", width=65),
        },
        hide_index=True,
        use_container_width=True
    )
    render_html("</div>")


# ------------------------------------------
# COLUMN 2: DEFECT RISK & MECHANICAL PROPERTIES
# ------------------------------------------
with col_eng_right:
    # 1. Defect Risk Action Cards (As specifically requested!)
    render_html("""
    <div class="eng-card">
        <div class="eng-card-header">
            <span class="eng-card-title">Defect Risk Analysis</span>
            <span class="eng-card-badge">ENGINEERING ACTION CARDS</span>
        </div>
    """)

    # Map each defect to exact Cause and Actionable Recommendation
    risk_mapping = {
        "keyholing": {
            "name": "Keyholing Porosity",
            "cause": "Excessive volumetric energy density or slow scan velocity",
            "rec": "Decrease optical power or increase scan velocity to suppress metal vaporization."
        },
        "lack_of_fusion": {
            "name": "Lack of Fusion (LoF)",
            "cause": "Insufficient energy density or excessive beam scan speed",
            "rec": f"Increase volumetric energy density to ≥ {limits['energy_density']['min']:.1f} J/mm³ for full melt penetration."
        },
        "oxidation": {
            "name": "Atmospheric Oxidation",
            "cause": f"Chamber oxygen concentration ({input_o2_val:.0f} ppm) above nominal limits",
            "rec": f"Purge argon atmosphere to maintain chamber oxygen below {limits['oxygen_concentration']['max']:.0f} ppm."
        },
        "residual_stress": {
            "name": "Residual Stress & Warpage",
            "cause": "Steep thermal gradients during solidification",
            "rec": f"Regulate build plate preheat toward {limits['temperature']['nominal']:.0f} °C to reduce internal stress."
        }
    }

    for r_key, r in result.defect_risks.items():
        meta_rec = risk_mapping.get(r_key, {
            "name": r.name.split('&')[0].strip(),
            "cause": r.primary_driver,
            "rec": "Maintain current verified operating envelope."
        })
        
        # Risk status label
        if r.probability >= 50.0:
            stat_label = "CRITICAL RISK"
            badge_style = "risk-metric-high"
        elif r.probability >= 30.0:
            stat_label = "HIGH RISK"
            badge_style = "risk-metric-high"
        elif r.probability >= 15.0:
            stat_label = "MODERATE RISK"
            badge_style = ""
        else:
            stat_label = "LOW RISK"
            badge_style = ""

        render_html(f"""
        <div class="risk-action-card">
            <div class="risk-card-top">
                <span class="risk-card-name">{meta_rec['name']}</span>
                <div style="display:flex; gap:8px; align-items:center;">
                    <span style="font-size:11px; font-weight:700; color:#6B7280; font-family:'JetBrains Mono';">Risk: {r.probability:.1f}%</span>
                    <span class="risk-metric-pill {badge_style}">{stat_label}</span>
                </div>
            </div>
            <div class="risk-row"><span class="risk-label">Cause:</span> {meta_rec['cause']}</div>
            <div class="risk-row"><span class="risk-label">Recommendation:</span> {meta_rec['rec']}</div>
        </div>
        """)

    render_html("</div>")

    # 1b. Custom Element Effect Card (if element selected)
    active_element_data = get_custom_element(cur_element)
    if active_element_data is not None:
        mods = active_element_data["mechanical_modifiers"]
        risk_mods = active_element_data["risk_modifiers"]

        # Build property delta chips
        def fmt_delta(label, val, unit="%"):
            sign = "+" if val > 0 else ""
            return f"<span style='display:inline-block; background:#F9FAFB; border:1px solid #E5E7EB; border-radius:4px; padding:2px 8px; margin:2px; font-family:JetBrains Mono; font-size:11px; font-weight:700;'>{label}: <strong>{sign}{val:.1f}{unit}</strong></span>"

        prop_chips = "".join([
            fmt_delta("Yield", mods["yield_strength_pct"]),
            fmt_delta("UTS", mods["uts_pct"]),
            fmt_delta("Elong", mods["elongation_pct"]),
            fmt_delta("Hard", mods["hardness_pct"]),
            fmt_delta("Density", mods["rel_density_pct"])
        ])

        risk_chips = "".join([
            fmt_delta("Keyhole", risk_mods["keyholing"], "pp"),
            fmt_delta("LoF", risk_mods["lack_of_fusion"], "pp"),
            fmt_delta("Oxidation", risk_mods["oxidation"], "pp"),
            fmt_delta("Stress", risk_mods["residual_stress"], "pp")
        ])

        elem_card_html = (
            f'<div class="eng-card">'
            f'<div class="eng-card-header">'
            f'<span class="eng-card-title">Custom Element Modification — {active_element_data["formula"]}</span>'
            f'<span class="eng-card-badge">{active_element_data["category"].split("—")[0].strip().upper()}</span>'
            f'</div>'
            f'<div style="font-size:12.5px; color:#4B5563; line-height:1.55; margin-bottom:12px;">'
            f'{active_element_data["description"]}'
            f'</div>'
            f'<div style="margin-bottom:8px;">'
            f'<div style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#6B7280; font-family:JetBrains Mono; margin-bottom:4px;">Mechanical Property Shifts</div>'
            f'{prop_chips}'
            f'</div>'
            f'<div style="margin-bottom:8px;">'
            f'<div style="font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#6B7280; font-family:JetBrains Mono; margin-bottom:4px;">Defect Risk Adjustments</div>'
            f'{risk_chips}'
            f'</div>'
            f'<div style="font-size:11px; color:#6B7280; font-family:JetBrains Mono; background:#F9FAFB; border:1px solid #E5E7EB; border-radius:6px; padding:6px 10px; margin-top:6px;">'
            f'CONCENTRATION: <strong>{active_element_data["concentration_range"]}</strong> &bull; '
            f'CATEGORY: <strong>{active_element_data["category"]}</strong>'
            f'</div>'
            f'</div>'
        )
        st.markdown(elem_card_html, unsafe_allow_html=True)

    # 2. Predicted Mechanical Properties & Processing Window
    render_html("""
    <div class="eng-card">
        <div class="eng-card-header">
            <span class="eng-card-title">Mechanical Performance & Processing Map</span>
            <span class="eng-card-badge">CONSTITUTIVE PREDICTIONS</span>
        </div>
    """)

    render_html(f"""
    <div class="mech-grid">
        <div class="mech-card">
            <div class="mech-card-title">Yield (Rp0.2)</div>
            <div class="mech-card-val">{result.mechanical.yield_strength:.0f} <span style="font-size:11px; color:#6B7280;">MPa</span></div>
            <div class="mech-card-target">Nominal: {nom_m['yield_strength']} MPa</div>
        </div>
        <div class="mech-card">
            <div class="mech-card-title">UTS (Tensile)</div>
            <div class="mech-card-val">{result.mechanical.uts:.0f} <span style="font-size:11px; color:#6B7280;">MPa</span></div>
            <div class="mech-card-target">Nominal: {nom_m['uts']} MPa</div>
        </div>
        <div class="mech-card">
            <div class="mech-card-title">Elongation</div>
            <div class="mech-card-val">{result.mechanical.elongation:.1f} <span style="font-size:11px; color:#6B7280;">%</span></div>
            <div class="mech-card-target">Nominal: {nom_m['elongation']}%</div>
        </div>
        <div class="mech-card">
            <div class="mech-card-title">Rel. Density</div>
            <div class="mech-card-val">{result.mechanical.rel_density:.2f} <span style="font-size:11px; color:#6B7280;">%</span></div>
            <div class="mech-card-target">Nominal: {nom_m['rel_density']}%</div>
        </div>
    </div>
    """)

    # -------------------------------------------------------------
    # Interactive Melt Pool Processing Window — Professional Redesign
    # -------------------------------------------------------------
    fig_window = go.Figure()

    # Extract limits
    sp_min = limits["scan_speed"]["min"]
    sp_max = limits["scan_speed"]["max"]
    sp_nom = limits["scan_speed"]["nominal"]
    sp_cmin = limits["scan_speed"]["crit_min"]
    sp_cmax = limits["scan_speed"]["crit_max"]
    ed_min = limits["energy_density"]["min"]
    ed_max = limits["energy_density"]["max"]
    ed_nom = limits["energy_density"]["nominal"]
    ed_cmin = limits["energy_density"]["crit_min"]
    ed_cmax = limits["energy_density"]["crit_max"]

    # Determine real-time regime & styling of the operating point
    in_safe_ved = (ed_min <= input_ved_val <= ed_max)
    in_safe_speed = (sp_min <= input_speed_val <= sp_max)

    if in_safe_ved and in_safe_speed:
        regime_status = "OPTIMAL CONDUCTION"
        regime_sub = "Within Qualified Parameter Window"
        regime_color = "#10B981"
        regime_halo = "rgba(16, 185, 129, 0.28)"
        regime_badge_bg = "#ECFDF5"
        regime_badge_border = "#A7F3D0"
        regime_badge_text = "#065F46"
    elif input_ved_val > ed_max:
        regime_status = "KEYHOLING / OVERHEATING"
        regime_sub = f"High VED (+{input_ved_val - ed_max:.1f} J/mm³ above safe limit) triggers vaporization"
        regime_color = "#EF4444"
        regime_halo = "rgba(239, 68, 68, 0.28)"
        regime_badge_bg = "#FEF2F2"
        regime_badge_border = "#FECACA"
        regime_badge_text = "#991B1B"
    elif input_ved_val < ed_min:
        regime_status = "LACK OF FUSION"
        regime_sub = f"Low VED ({ed_min - input_ved_val:.1f} J/mm³ below safe limit) leaves unbonded powder"
        regime_color = "#3B82F6"
        regime_halo = "rgba(59, 130, 246, 0.28)"
        regime_badge_bg = "#EFF6FF"
        regime_badge_border = "#BFDBFE"
        regime_badge_text = "#1E40AF"
    elif input_speed_val > sp_max:
        regime_status = "BALLING / INSTABILITY"
        regime_sub = f"Excess scan speed (+{input_speed_val - sp_max:.0f} mm/s) causes bead breakup"
        regime_color = "#F59E0B"
        regime_halo = "rgba(245, 158, 11, 0.28)"
        regime_badge_bg = "#FFFBEB"
        regime_badge_border = "#FDE68A"
        regime_badge_text = "#92400E"
    else:
        regime_status = "MARGINAL / LOW VELOCITY"
        regime_sub = "Low scan velocity promotes excessive heat buildup"
        regime_color = "#F59E0B"
        regime_halo = "rgba(245, 158, 11, 0.28)"
        regime_badge_bg = "#FFFBEB"
        regime_badge_border = "#FDE68A"
        regime_badge_text = "#92400E"

    # Drift calculations
    dist_speed = input_speed_val - sp_nom
    dist_ved = input_ved_val - ed_nom
    drift_speed_pct = (dist_speed / sp_nom) * 100
    drift_ved_pct = (dist_ved / ed_nom) * 100
    total_dist = (dist_speed**2 + dist_ved**2)**0.5
    max_possible_dist = ((sp_cmax - sp_nom)**2 + (ed_cmax - ed_nom)**2)**0.5
    drift_overall_pct = min(100.0, (total_dist / max(1, max_possible_dist)) * 100.0)

    active_element_data = get_custom_element(cur_element)
    mat_pill_text = f"{cur_alloy} + {cur_element}" if cur_element != "None" else cur_alloy

    # Render intuitive telemetry banner right above the chart
    render_html(f"""
    <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:8px; padding:10px 14px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span style="background:#F3F4F6; color:#1F2937; font-size:11px; font-weight:800; padding:3px 8px; border-radius:6px; font-family:'JetBrains Mono'; border:1px solid #D1D5DB;">
                {mat_pill_text}
            </span>
            <span style="background:{regime_badge_bg}; border:1px solid {regime_badge_border}; color:{regime_badge_text}; font-size:11.5px; font-weight:800; padding:3px 9px; border-radius:6px; font-family:'JetBrains Mono';">
                ● {regime_status}
            </span>
            <span style="font-size:11.5px; color:#6B7280; font-family:'Inter', sans-serif;">{regime_sub}</span>
        </div>
        <div style="display:flex; gap:14px; font-size:11.5px; font-family:'JetBrains Mono'; color:#374151;">
            <span>Speed: <strong>{input_speed_val:.0f} mm/s</strong> ({drift_speed_pct:+.1f}%)</span>
            <span>VED: <strong>{input_ved_val:.1f} J/mm³</strong> ({drift_ved_pct:+.1f}%)</span>
            <span>Drift: <strong style="color:{regime_color};">{drift_overall_pct:.0f}%</strong></span>
        </div>
    </div>
    """)

    # Dynamic Axis Bounds: Ensure the OP is always comfortably visible with a margin
    x_axis_min = min(sp_cmin * 0.95, input_speed_val * 0.92)
    x_axis_max = max(sp_cmax * 1.05, input_speed_val * 1.08)
    y_axis_min = min(ed_cmin * 0.90, input_ved_val * 0.90)
    y_axis_max = max(ed_cmax * 1.05, input_ved_val * 1.08)

    # 1. KEYHOLING ZONE (Top) - mode="lines" prevents stray marker dots
    fig_window.add_trace(go.Scatter(
        x=[x_axis_min, x_axis_max, x_axis_max, x_axis_min, x_axis_min],
        y=[y_axis_max, y_axis_max, ed_max, ed_max, y_axis_max],
        fill="toself",
        fillcolor="rgba(239, 68, 68, 0.08)",
        mode="lines",
        line=dict(color="rgba(239, 68, 68, 0.35)", width=1, dash="dash"),
        name="Keyholing Regime",
        hoverinfo="skip",
        showlegend=False
    ))

    # 2. LACK OF FUSION ZONE (Bottom)
    fig_window.add_trace(go.Scatter(
        x=[x_axis_min, x_axis_max, x_axis_max, x_axis_min, x_axis_min],
        y=[ed_min, ed_min, y_axis_min, y_axis_min, ed_min],
        fill="toself",
        fillcolor="rgba(59, 130, 246, 0.08)",
        mode="lines",
        line=dict(color="rgba(59, 130, 246, 0.35)", width=1, dash="dash"),
        name="Lack of Fusion Regime",
        hoverinfo="skip",
        showlegend=False
    ))

    # 3. BALLING ZONE (Right, high velocity)
    fig_window.add_trace(go.Scatter(
        x=[sp_max, x_axis_max, x_axis_max, sp_max, sp_max],
        y=[ed_min, ed_min, ed_max, ed_max, ed_min],
        fill="toself",
        fillcolor="rgba(245, 158, 11, 0.08)",
        mode="lines",
        line=dict(color="rgba(245, 158, 11, 0.35)", width=1, dash="dash"),
        name="Balling / Instability",
        hoverinfo="skip",
        showlegend=False
    ))

    # 4. OPTIMAL SAFE CONDUCTION ENVELOPE (Center)
    fig_window.add_shape(
        type="rect",
        x0=sp_min, y0=ed_min,
        x1=sp_max, y1=ed_max,
        line=dict(color="#059669", width=2, dash="dash"),
        fillcolor="rgba(16, 185, 129, 0.12)",
        layer="below"
    )

    # Clean, non-colliding zone annotations
    # Safe Envelope: Upper-left corner of the green box so it NEVER collides with nominal/operating center points!
    safe_env_label = f"{cur_alloy} + {cur_element}" if cur_element != "None" else f"{cur_alloy} Qualified"
    fig_window.add_annotation(
        x=sp_min + (sp_max - sp_min) * 0.03,
        y=ed_max - (ed_max - ed_min) * 0.06,
        text=f"<b>✔ SAFE CONDUCTION WINDOW</b><br><span style='font-size:9px;color:#047857'>{safe_env_label} Envelope</span>",
        showarrow=False,
        xanchor="left",
        yanchor="top",
        font=dict(size=10, color="#065F46", family="Plus Jakarta Sans, sans-serif"),
        align="left"
    )

    # Keyholing label (centered in upper band)
    fig_window.add_annotation(
        x=(sp_min + sp_max) / 2,
        y=ed_max + (y_axis_max - ed_max) * 0.45,
        text=f"<b>▲ KEYHOLING / OVERHEATING ZONE</b><br><span style='font-size:9.5px;color:#991B1B'>Excess energy density (&gt;{ed_max:.0f} J/mm³) triggers vaporization & keyhole collapse</span>",
        showarrow=False,
        font=dict(size=10, color="#991B1B", family="Plus Jakarta Sans, sans-serif"),
        align="center"
    )

    # Lack of Fusion label (centered in lower band)
    fig_window.add_annotation(
        x=(sp_min + sp_max) / 2,
        y=y_axis_min + (ed_min - y_axis_min) * 0.55,
        text=f"<b>▼ LACK OF FUSION ZONE</b><br><span style='font-size:9.5px;color:#1E40AF'>Insufficient energy input (&lt;{ed_min:.0f} J/mm³) causes powder voids</span>",
        showarrow=False,
        font=dict(size=10, color="#1E40AF", family="Plus Jakarta Sans, sans-serif"),
        align="center"
    )

    # Balling label (centered in right band)
    fig_window.add_annotation(
        x=sp_max + (x_axis_max - sp_max) * 0.5,
        y=(ed_min + ed_max) / 2,
        text="<b>▶ BALLING</b><br><span style='font-size:9px;color:#92400E'>Capillary bead<br>breakup</span>",
        showarrow=False,
        font=dict(size=9.5, color="#92400E", family="Plus Jakarta Sans, sans-serif"),
        align="center"
    )

    # Custom Element Indicator badge inside chart if active
    if cur_element != "None" and active_element_data is not None:
        cat_short = active_element_data['category'].split('—')[0].strip()
        fig_window.add_annotation(
            x=x_axis_max * 0.98,
            y=y_axis_min + (ed_min - y_axis_min) * 0.40,
            text=f"<b>INOCULANT: {active_element_data['formula']}</b><br><span style='font-size:8.5px;color:#475569;'>{cat_short}</span>",
            showarrow=False,
            xanchor="right",
            font=dict(size=9, color="#1E293B", family="JetBrains Mono"),
            bgcolor="rgba(255, 255, 255, 0.92)",
            bordercolor="#CBD5E1",
            borderwidth=1,
            borderpad=5
        )

    # 5. NOMINAL TARGET POINT (Benchmark Reference)
    fig_window.add_trace(go.Scatter(
        x=[sp_nom], y=[ed_nom],
        mode="markers",
        marker=dict(
            size=12,
            symbol="diamond",
            color="#059669",
            line=dict(width=2, color="#FFFFFF")
        ),
        name="Nominal Standard Target",
        hovertemplate=(
            "<b>Nominal Standard Target</b><br>"
            f"Velocity: {sp_nom:.0f} mm/s<br>"
            f"Energy Density: {ed_nom:.1f} J/mm³<br>"
            "Qualification: Qualified Baseline<extra></extra>"
        )
    ))

    # 6. DRIFT VECTOR (Connecting line between nominal and current operating point)
    fig_window.add_trace(go.Scatter(
        x=[sp_nom, input_speed_val],
        y=[ed_nom, input_ved_val],
        mode="lines",
        line=dict(color="#94A3B8", width=1.8, dash="dot"),
        showlegend=False,
        hoverinfo="skip"
    ))

    # 7. CROSSHAIR GUIDES through current operating point
    fig_window.add_shape(
        type="line",
        x0=input_speed_val, y0=y_axis_min,
        x1=input_speed_val, y1=y_axis_max,
        line=dict(color=regime_color, width=1.2, dash="dot"),
        opacity=0.45
    )
    fig_window.add_shape(
        type="line",
        x0=x_axis_min, y0=input_ved_val,
        x1=x_axis_max, y1=input_ved_val,
        line=dict(color=regime_color, width=1.2, dash="dot"),
        opacity=0.45
    )

    # 8. CURRENT OPERATING POINT — Prominent glowing marker
    # Halo ring
    fig_window.add_trace(go.Scatter(
        x=[input_speed_val], y=[input_ved_val],
        mode="markers",
        marker=dict(
            size=28,
            color=regime_halo,
            symbol="circle"
        ),
        showlegend=False,
        hoverinfo="skip"
    ))

    # Core point
    fig_window.add_trace(go.Scatter(
        x=[input_speed_val], y=[input_ved_val],
        mode="markers",
        marker=dict(
            size=14,
            color=regime_color,
            symbol="circle",
            line=dict(width=2.5, color="#FFFFFF")
        ),
        name="Current Operating Point",
        hovertemplate=(
            "<b>Current Operating Point</b><br>"
            f"Scan Velocity: {input_speed_val:.0f} mm/s<br>"
            f"Energy Density: {input_ved_val:.1f} J/mm³<br>"
            f"Regime: {regime_status}<br>"
            f"Overall Drift: {drift_overall_pct:.0f}%<extra></extra>"
        )
    ))

    # Real-time Callout Annotation tracking the point cleanly
    callout_ay = -52 if input_ved_val < (y_axis_min + y_axis_max) * 0.55 else 52
    callout_ax = 0

    fig_window.add_annotation(
        x=input_speed_val,
        y=input_ved_val,
        ax=callout_ax,
        ay=callout_ay,
        text=(
            f"<b>CURRENT OPERATING POINT</b><br>"
            f"<span style='font-size:9.5px;'>{input_speed_val:.0f} mm/s • {input_ved_val:.1f} J/mm³</span><br>"
            f"<span style='color:{regime_color};font-weight:700;'>● {condition_label}</span>"
        ),
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor=regime_color,
        font=dict(size=10, color="#111827", family="JetBrains Mono"),
        align="center",
        bgcolor="rgba(255, 255, 255, 0.95)",
        bordercolor="#CBD5E1",
        borderwidth=1.5,
        borderpad=6
    )

    # 9. CHART LAYOUT
    fig_window.update_layout(
        xaxis=dict(
            title=dict(
                text=f"Laser Scan Velocity ({limits['scan_speed']['unit']})",
                font=dict(size=12, color="#1E293B", family="Plus Jakarta Sans, sans-serif", weight=600)
            ),
            range=[x_axis_min, x_axis_max],
            gridcolor='rgba(226, 232, 240, 0.7)',
            gridwidth=1,
            linecolor='#CBD5E1',
            linewidth=1,
            tickfont=dict(color='#475569', family='JetBrains Mono', size=10),
            zeroline=False,
            showspikes=True,
            spikecolor="#94A3B8",
            spikethickness=1,
            spikedash="dot",
            spikemode="across"
        ),
        yaxis=dict(
            title=dict(
                text=f"Volumetric Energy Density ({limits['energy_density']['unit']})",
                font=dict(size=12, color="#1E293B", family="Plus Jakarta Sans, sans-serif", weight=600)
            ),
            range=[y_axis_min, y_axis_max],
            gridcolor='rgba(226, 232, 240, 0.7)',
            gridwidth=1,
            linecolor='#CBD5E1',
            linewidth=1,
            tickfont=dict(color='#475569', family='JetBrains Mono', size=10),
            zeroline=False,
            showspikes=True,
            spikecolor="#94A3B8",
            spikethickness=1,
            spikedash="dot",
            spikemode="across"
        ),
        paper_bgcolor='#FFFFFF',
        plot_bgcolor='#F8FAFC',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
            font=dict(size=10, family="JetBrains Mono", color="#334155"),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#E2E8F0",
            borderwidth=1,
            itemsizing="constant"
        ),
        margin=dict(l=60, r=25, t=40, b=50),
        height=420,
        hovermode="closest",
        dragmode="pan"
    )

    chart_config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'responsive': True
    }
    st.plotly_chart(fig_window, use_container_width=True, config=chart_config, key="processing_window_chart")

    render_html("</div>")


# ==========================================
# LEVEL 3: DETAILED INFORMATION & EXPORTS
# ==========================================
st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

with st.expander("Detailed Engineering Information: Alloy Metallurgy Profile & Standard References"):
    col_det1, col_det2 = st.columns([1, 1], gap="medium")
    
    with col_det1:
        # Chemical Composition Card (Zero HTML leakage, clean formatting)
        render_html(f"""
        <div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:16px;">
            <div style="font-size:13px; font-weight:800; color:#111111; margin-bottom:4px;">
                {alloy_meta['name']}
            </div>
            <div style="font-size:12px; color:#4B5563; line-height:1.45; margin-bottom:14px;">
                {alloy_meta['description']}
            </div>
            <div style="font-size:10.5px; font-weight:700; color:#6B7280; font-family:'JetBrains Mono'; text-transform:uppercase; margin-bottom:4px;">
                Nominal Chemical Composition (wt%)
            </div>
            <div style="font-family:'JetBrains Mono', monospace; font-size:12px; font-weight:600; color:#111111; background:#FFFFFF; border:1px solid #E5E7EB; border-radius:6px; padding:10px 12px;">
                {alloy_meta['composition']}
            </div>
            <div style="font-size:11.5px; color:#4B5563; margin-top:10px;">
                <strong>Standard Specification:</strong> {alloy_meta['standard']}
            </div>
        </div>
        """)

    with col_det2:
        # Formatted Material Properties Table (Clean table with zero HTML leakage)
        render_html(f"""
        <div style="background:#F9FAFB; border:1px solid #E5E7EB; border-radius:8px; padding:16px;">
            <div style="font-size:13px; font-weight:800; color:#111111; margin-bottom:10px;">
                Thermophysical & Mechanical Specifications
            </div>
            <table class="alloy-spec-table">
                <tr>
                    <td class="label-col">Theoretical Density</td>
                    <td class="val-col">{alloy_meta['density']} g/cm³</td>
                </tr>
                <tr>
                    <td class="label-col">Melting Solidus-Liquidus Range</td>
                    <td class="val-col">{alloy_meta['melting_range']}</td>
                </tr>
                <tr>
                    <td class="label-col">Thermal Conductivity (20°C)</td>
                    <td class="val-col">{alloy_meta['thermal_conductivity']}</td>
                </tr>
                <tr>
                    <td class="label-col">Nominal Yield Strength (Rp0.2)</td>
                    <td class="val-col">{nom_m['yield_strength']} MPa</td>
                </tr>
                <tr>
                    <td class="label-col">Nominal UTS</td>
                    <td class="val-col">{nom_m['uts']} MPa</td>
                </tr>
                <tr>
                    <td class="label-col">Typical Applications</td>
                    <td class="val-col" style="font-family:'Plus Jakarta Sans'; font-size:11px;">{alloy_meta['applications'][:38]}...</td>
                </tr>
            </table>
        </div>
        """)

with st.expander("Quality Assurance Certificate Export & Inspection Audit"):
    md_report = generate_markdown_report(result, batch_id="AL-2026-09A", operator_id="OP-8492-MET")
    html_report = generate_html_report(result, batch_id="AL-2026-09A", operator_id="OP-8492-MET")

    c_dl1, c_dl2, c_sp = st.columns([1, 1, 2])
    with c_dl1:
        st.download_button(
            label="⬇ DOWNLOAD AUDIT (MARKDOWN)",
            data=md_report,
            file_name=f"AluSense_Report_{cur_alloy}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with c_dl2:
        st.download_button(
            label="⬇ DOWNLOAD QA CERTIFICATE (HTML)",
            data=html_report,
            file_name=f"AluSense_QA_Certificate_{cur_alloy}.html",
            mime="text/html",
            use_container_width=True
        )

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.components.v1.html(html_report, height=450, scrolling=True)
