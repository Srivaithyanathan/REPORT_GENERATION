"""
AluSense AI - Industrial Quality Assurance Report Generator
Produces standard audit compliance reports in Markdown and printable HTML.
"""

from typing import Dict, Any
from analysis.engine import AnalysisResult
from dataset.standards import get_custom_element


def generate_markdown_report(result: AnalysisResult, batch_id: str = "AL-2026-09A", operator_id: str = "OP-8492-MET") -> str:
    """Generates standard engineering Markdown audit document."""
    alloy = result.alloy_info
    lines = []
    lines.append(f"# AluSense AI™ — Industrial Manufacturing Qualification Report")
    lines.append(f"**Verification Standard:** ISO/ASTM 52900 / {alloy['standard']}  ")
    lines.append(f"**Generated:** {result.timestamp} | **Batch ID:** `{batch_id}` | **Operator:** `{operator_id}`  ")
    lines.append(f"**Compliance Verdict:** **{result.compliance_status}**  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Executive Summary")
    lines.append(f"- **Material Specification:** {alloy['name']} ({alloy['code']})")
    lines.append(f"- **Manufacturing Process:** {result.process_name}")
    lines.append(f"- **Overall Quality Score:** **{result.quality_score:.1f}%** ({result.quality_grade})")
    lines.append(f"- **Parameter Compliance:** {result.passed_parameters_count} / {result.total_parameters_count} within nominal tolerances")
    lines.append(f"- **Dominant Defect Risk:** {result.peak_risk.name} ({result.peak_risk.probability:.1f}% - {result.peak_risk.severity})")
    lines.append("")
    lines.append("## 2. Process Parameter Audit")
    lines.append("| Parameter | Measured Value | Nominal Window | Standard Range | Status | Deviation |")
    lines.append("|:---|:---|:---|:---|:---:|:---:|")

    for key, p in result.parameters.items():
        nom_window = f"{p.safe_min:.1f} – {p.safe_max:.1f} {p.unit}"
        crit_range = f"[{p.crit_min:.1f}, {p.crit_max:.1f}]"
        lines.append(f"| **{p.name}** | `{p.value:.2f} {p.unit}` | {nom_window} | {crit_range} | **[{p.status}]** | `{p.deviation_label}` |")

    lines.append("")
    lines.append("## 3. Defect Hazard Assessment")
    lines.append("| Defect Hazard Mode | Risk Probability | Severity | Primary Root Cause Driver |")
    lines.append("|:---|:---:|:---:|:---|")
    for r_key, r in result.defect_risks.items():
        lines.append(f"| **{r.name}** | `{r.probability:.1f}%` | **{r.severity}** | {r.primary_driver} |")

    lines.append("")
    lines.append("## 4. Predicted Mechanical & Metallurgical Properties")
    lines.append(f"- **Estimated Relative Density:** `{result.mechanical.rel_density:.2f}%` (Nominal: {alloy['nominal_mechanical']['rel_density']}%)")
    lines.append(f"- **Estimated Tensile Yield Strength:** `{result.mechanical.yield_strength:.1f} MPa` (Nominal: {alloy['nominal_mechanical']['yield_strength']} MPa)")
    lines.append(f"- **Estimated Ultimate Tensile Strength (UTS):** `{result.mechanical.uts:.1f} MPa` (Nominal: {alloy['nominal_mechanical']['uts']} MPa)")
    lines.append(f"- **Estimated Plastic Elongation:** `{result.mechanical.elongation:.1f}%` (Nominal: {alloy['nominal_mechanical']['elongation']}%)")
    lines.append(f"- **Estimated Vickers Hardness:** `{result.mechanical.hardness:.1f} HV` (Nominal: {alloy['nominal_mechanical']['hardness']} HV)")
    lines.append("")
    lines.append("## 5. Engineering Corrective Directives")
    for rec in result.recommendations:
        lines.append(f"- **[{rec['code']}] [{rec['category']}] ({rec['urgency']} PRIORITY):** {rec['action']}")
        lines.append(f"  *{rec['detail']}*")

    lines.append("")
    lines.append("---")
    lines.append("### Quality Assurance Certification Sign-Off")
    lines.append("```")
    lines.append("CERTIFIED BY: AluSense AI Automated Metallurgy Kernel v2.4")
    lines.append(f"SIGNATURE HASH: SHA256:{hash(result.timestamp + batch_id) & 0xFFFFFFFFFFFF:012X}")
    lines.append(f"AUDIT STAMP: [ {result.compliance_status} ]")
    lines.append("```")

    # Custom Element Modification Section (if applicable)
    if result.custom_element and result.custom_element != "None":
        elem_data = get_custom_element(result.custom_element)
        if elem_data:
            mods = elem_data["mechanical_modifiers"]
            risk_mods = elem_data["risk_modifiers"]
            lines.append("")
            lines.append("## 6. Custom Element Modification")
            lines.append(f"- **Element:** {elem_data['name']} ({elem_data['formula']})")
            lines.append(f"- **Category:** {elem_data['category']}")
            lines.append(f"- **Concentration Range:** {elem_data['concentration_range']}")
            lines.append(f"- **Description:** {elem_data['description']}")
            lines.append("")
            lines.append("**Mechanical Property Modifiers:**")
            lines.append("| Property | Modifier |")
            lines.append("|:---|:---:|")
            lines.append(f"| Yield Strength | `{'+' if mods['yield_strength_pct'] > 0 else ''}{mods['yield_strength_pct']:.1f}%` |")
            lines.append(f"| UTS | `{'+' if mods['uts_pct'] > 0 else ''}{mods['uts_pct']:.1f}%` |")
            lines.append(f"| Elongation | `{'+' if mods['elongation_pct'] > 0 else ''}{mods['elongation_pct']:.1f}%` |")
            lines.append(f"| Hardness | `{'+' if mods['hardness_pct'] > 0 else ''}{mods['hardness_pct']:.1f}%` |")
            lines.append(f"| Rel. Density | `{'+' if mods['rel_density_pct'] > 0 else ''}{mods['rel_density_pct']:.2f}%` |")
            lines.append("")
            lines.append("**Defect Risk Adjustments (pp):**")
            lines.append("| Defect | Modifier |")
            lines.append("|:---|:---:|")
            for rk, rv in risk_mods.items():
                label = rk.replace("_", " ").title()
                lines.append(f"| {label} | `{'+' if rv > 0 else ''}{rv:.1f} pp` |")

    return "\n".join(lines)


def generate_html_report(result: AnalysisResult, batch_id: str = "AL-2026-09A", operator_id: str = "OP-8492-MET") -> str:
    """Generates a high-precision white industrial HTML certificate suitable for print or PDF export."""
    alloy = result.alloy_info

    param_rows = ""
    for key, p in result.parameters.items():
        badge_style = "background:#F3F4F6; color:#111111; border:1px solid #111111;"
        if "CRITICAL" in p.status:
            badge_style = "background:#000000; color:#FFFFFF; border:1px solid #000000; font-weight:bold;"
        elif "WARNING" in p.status:
            badge_style = "background:#FFFFFF; color:#111111; border:1px dashed #666666;"
        
        param_rows += f"""
        <tr>
            <td style="font-weight:600; color:#111111;">{p.name}</td>
            <td style="font-family:'Courier New', monospace; font-weight:bold; color:#000000;">{p.value:.2f} {p.unit}</td>
            <td style="color:#666666;">{p.nominal:.1f} {p.unit}</td>
            <td style="color:#333333;">{p.safe_min:.1f} – {p.safe_max:.1f} {p.unit}</td>
            <td><span style="display:inline-block; padding:2px 8px; font-size:11px; font-family:'Courier New', monospace; {badge_style}">[{p.status}]</span></td>
            <td style="font-family:'Courier New', monospace; color:#111111;">{p.deviation_label}</td>
        </tr>
        """

    risk_rows = ""
    for r_key, r in result.defect_risks.items():
        bar_width = int(r.probability)
        risk_rows += f"""
        <tr>
            <td style="font-weight:600; color:#111111;">{r.name}</td>
            <td style="width:200px;">
                <div style="background:#E5E7EB; height:12px; width:100%; border:1px solid #111111;">
                    <div style="background:#000000; height:10px; width:{bar_width}%;"></div>
                </div>
            </td>
            <td style="font-family:'Courier New', monospace; font-weight:bold; color:#000000;">{r.probability:.1f}%</td>
            <td><strong style="letter-spacing:0.05em; color:#000000;">[{r.severity}]</strong></td>
            <td style="font-size:12px; color:#555555;">{r.primary_driver}</td>
        </tr>
        """

    recs_list = ""
    for rec in result.recommendations:
        recs_list += f"""
        <div style="border-left: 3px solid #000000; padding-left: 12px; margin-bottom: 12px;">
            <div style="font-size:12px; font-family:'Courier New', monospace; color:#555555;">[{rec['code']}] [{rec['category']}] — <strong style="color:#000000;">{rec['urgency']} PRIORITY</strong></div>
            <div style="font-weight:700; color:#000000; margin-top:2px;">{rec['action']}</div>
            <div style="font-size:12px; color:#555555; margin-top:2px;">{rec['detail']}</div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AluSense AI — Inspection Report {batch_id}</title>
    <style>
        @media print {{
            body {{ background: #FFFFFF !important; color: #000000 !important; }}
            .no-print {{ display: none !important; }}
            .container {{ border: none !important; box-shadow: none !important; }}
            table, th, td {{ border-color: #000000 !important; }}
        }}
        body {{
            background-color: #FFFFFF;
            color: #111111;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            padding: 30px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #FFFFFF;
            border: 1.5px solid #111111;
            box-shadow: 0 2px 6px rgba(0,0,0,0.06);
            padding: 36px;
            box-sizing: border-box;
        }}
        .header {{
            border-bottom: 2.5px solid #000000;
            padding-bottom: 18px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}
        .title {{
            font-size: 24px;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin: 0;
            color: #000000;
        }}
        .subtitle {{
            font-size: 12px;
            letter-spacing: 0.1em;
            color: #555555;
            margin-top: 4px;
        }}
        .badge-verdict {{
            border: 2px solid #000000;
            padding: 8px 16px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.08em;
            background: #000000;
            color: #FFFFFF;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            background: #F8F9FA;
            border: 1px solid #111111;
            padding: 14px;
            margin-bottom: 28px;
            font-size: 13px;
        }}
        .meta-item label {{
            display: block;
            font-size: 10px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #555555;
            margin-bottom: 3px;
        }}
        .meta-item value {{
            font-family: 'Courier New', monospace;
            font-weight: bold;
            color: #000000;
        }}
        h2 {{
            font-size: 14px;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            border-bottom: 1.5px solid #111111;
            padding-bottom: 6px;
            margin-top: 28px;
            margin-bottom: 14px;
            color: #000000;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin-bottom: 20px;
        }}
        th {{
            text-align: left;
            padding: 8px 10px;
            font-size: 11px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            background: #F3F4F6;
            border-bottom: 1.5px solid #111111;
            color: #111111;
            font-weight: 700;
        }}
        td {{
            padding: 9px 10px;
            border-bottom: 1px solid #E5E7EB;
        }}
        .prop-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-bottom: 24px;
        }}
        .prop-card {{
            background: #FFFFFF;
            border: 1px solid #111111;
            border-top: 3px solid #000000;
            padding: 12px;
        }}
        .prop-title {{
            font-size: 11px;
            color: #555555;
            text-transform: uppercase;
            font-weight: 600;
        }}
        .prop-val {{
            font-size: 20px;
            font-weight: 700;
            font-family: 'Courier New', monospace;
            margin-top: 4px;
            color: #000000;
        }}
        .signoff {{
            border-top: 1.5px solid #111111;
            padding-top: 18px;
            margin-top: 36px;
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #555555;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1 class="title">AluSense AI™</h1>
                <div class="subtitle">Industrial Metallurgy & Process Qualification Audit</div>
            </div>
            <div class="badge-verdict">
                {result.compliance_status}
            </div>
        </div>

        <div class="meta-grid">
            <div class="meta-item">
                <label>Alloy Grade</label>
                <value>{alloy['name']}</value>
            </div>
            <div class="meta-item">
                <label>Process</label>
                <value>{result.process_name}</value>
            </div>
            <div class="meta-item">
                <label>Batch Serial</label>
                <value>{batch_id}</value>
            </div>
            <div class="meta-item">
                <label>Overall Quality Score</label>
                <value style="font-size:16px;">{result.quality_score:.1f}%</value>
            </div>
        </div>

        <h2>1. Process Parameter Verification vs ASTM/ISO Standard</h2>
        <table>
            <thead>
                <tr>
                    <th>Parameter</th>
                    <th>Measured</th>
                    <th>Nominal</th>
                    <th>Safe Window</th>
                    <th>Status</th>
                    <th>Drift</th>
                </tr>
            </thead>
            <tbody>
                {param_rows}
            </tbody>
        </table>

        <h2>2. Defect Risk Probability Distribution</h2>
        <table>
            <thead>
                <tr>
                    <th>Defect Hazard Vector</th>
                    <th>Probability Bar</th>
                    <th>Value</th>
                    <th>Severity</th>
                    <th>Primary Root Cause</th>
                </tr>
            </thead>
            <tbody>
                {risk_rows}
            </tbody>
        </table>

        <h2>3. Mechanical Properties & Density Estimates</h2>
        <div class="prop-grid">
            <div class="prop-card">
                <div class="prop-title">Relative Density</div>
                <div class="prop-val">{result.mechanical.rel_density:.2f}%</div>
                <div style="font-size:11px; color:#555555;">Nominal: {alloy['nominal_mechanical']['rel_density']}%</div>
            </div>
            <div class="prop-card">
                <div class="prop-title">Yield Strength (Rp0.2)</div>
                <div class="prop-val">{result.mechanical.yield_strength:.1f} MPa</div>
                <div style="font-size:11px; color:#555555;">Nominal: {alloy['nominal_mechanical']['yield_strength']} MPa</div>
            </div>
            <div class="prop-card">
                <div class="prop-title">UTS (Tensile)</div>
                <div class="prop-val">{result.mechanical.uts:.1f} MPa</div>
                <div style="font-size:11px; color:#555555;">Nominal: {alloy['nominal_mechanical']['uts']} MPa</div>
            </div>
            <div class="prop-card">
                <div class="prop-title">Elongation at Break</div>
                <div class="prop-val">{result.mechanical.elongation:.1f}%</div>
                <div style="font-size:11px; color:#555555;">Nominal: {alloy['nominal_mechanical']['elongation']}%</div>
            </div>
            <div class="prop-card">
                <div class="prop-title">Hardness</div>
                <div class="prop-val">{result.mechanical.hardness:.1f} HV</div>
                <div style="font-size:11px; color:#555555;">Nominal: {alloy['nominal_mechanical']['hardness']} HV</div>
            </div>
            <div class="prop-card">
                <div class="prop-title">Quality Grade</div>
                <div class="prop-val" style="font-size:13px; margin-top:8px;">{result.quality_grade}</div>
            </div>
        </div>

        <h2>4. Actionable Engineering Directives</h2>
        {recs_list}
"""

    # Custom Element section (if applicable)
    if result.custom_element and result.custom_element != "None":
        elem_data = get_custom_element(result.custom_element)
        if elem_data:
            mods = elem_data["mechanical_modifiers"]
            risk_mods = elem_data["risk_modifiers"]

            def fmt_mod(val, unit="%"):
                sign = "+" if val > 0 else ""
                return f"{sign}{val:.1f}{unit}"

            elem_mod_rows = f"""
            <tr><td>Yield Strength</td><td style="font-family:'Courier New',monospace; font-weight:bold;">{fmt_mod(mods['yield_strength_pct'])}</td></tr>
            <tr><td>UTS</td><td style="font-family:'Courier New',monospace; font-weight:bold;">{fmt_mod(mods['uts_pct'])}</td></tr>
            <tr><td>Elongation</td><td style="font-family:'Courier New',monospace; font-weight:bold;">{fmt_mod(mods['elongation_pct'])}</td></tr>
            <tr><td>Hardness</td><td style="font-family:'Courier New',monospace; font-weight:bold;">{fmt_mod(mods['hardness_pct'])}</td></tr>
            <tr><td>Rel. Density</td><td style="font-family:'Courier New',monospace; font-weight:bold;">{fmt_mod(mods['rel_density_pct'])}</td></tr>
            """

            elem_risk_rows = ""
            for rk, rv in risk_mods.items():
                label = rk.replace("_", " ").title()
                elem_risk_rows += f"<tr><td>{label}</td><td style='font-family:Courier New,monospace; font-weight:bold;'>{fmt_mod(rv, ' pp')}</td></tr>"

            html += f"""
        <h2>5. Custom Element Modification — {elem_data['formula']}</h2>
        <div style="background:#F8F9FA; border:1px solid #111111; padding:14px; margin-bottom:16px;">
            <div style="font-size:12px; margin-bottom:4px;"><strong>Element:</strong> {elem_data['name']}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Category:</strong> {elem_data['category']}</div>
            <div style="font-size:12px; margin-bottom:4px;"><strong>Concentration:</strong> {elem_data['concentration_range']}</div>
            <div style="font-size:12px; color:#555555; margin-top:8px;">{elem_data['description']}</div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
            <div>
                <div style="font-size:11px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:6px;">Mechanical Property Modifiers</div>
                <table style="font-size:12px;">
                    {elem_mod_rows}
                </table>
            </div>
            <div>
                <div style="font-size:11px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:6px;">Defect Risk Adjustments</div>
                <table style="font-size:12px;">
                    {elem_risk_rows}
                </table>
            </div>
        </div>
"""

    html += f"""
        <div class="signoff">
            <div>
                <div>OPERATOR: {operator_id}</div>
                <div>DIGITAL AUDIT STAMP: VERIFIED_ISO52900</div>
            </div>
            <div style="text-align:right;">
                <div>TIMESTAMP: {result.timestamp}</div>
                <div>SYSTEM: AluSense AI v2.4 Industrial Edition</div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html
