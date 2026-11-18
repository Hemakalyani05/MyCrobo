import json
from ..models.schemas import AuditReport

class Reporter:
    @staticmethod
    def to_markdown(report: AuditReport) -> str:
        md = []
        md.append(f"# CodeSentinel AI Audit Report: {report.metadata.repo_name}")
        md.append(f"**Date:** {report.created_at} | **Scan ID:** `{report.scan_id}`")
        md.append(f"**Security Score:** **{report.summary.security_score} / 100** (Grade: **{report.summary.grade}**)")
        md.append(f"**Duration:** {report.duration_seconds}s\n")

        md.append("## Executive AI Assessment")
        md.append(f"{report.agent_analysis}\n")

        md.append("## Repository Breakdown")
        md.append(f"- **Total Source Files:** {report.metadata.total_files}")
        md.append(f"- **Total Lines of Code:** {report.metadata.total_lines}")
        md.append(f"- **Frameworks:** {', '.join(report.metadata.frameworks) if report.metadata.frameworks else 'None detected'}")
        md.append("- **Languages:**")
        for l in report.metadata.languages:
            md.append(f"  - {l.language}: {l.percentage}% ({l.lines_count} lines, {l.files_count} files)")
        md.append("")

        md.append("## Findings Summary")
        md.append("| Severity | Count | Category | Count |")
        md.append("|---|---|---|---|")
        sevs = list(report.summary.by_severity.items())
        cats = list(report.summary.by_category.items())
        max_rows = max(len(sevs), len(cats))
        for i in range(max_rows):
            s_cell = f"{sevs[i][0].capitalize()}: {sevs[i][1]}" if i < len(sevs) else ""
            c_cell = f"{cats[i][0].capitalize()}: {cats[i][1]}" if i < len(cats) else ""
            md.append(f"| {s_cell} | | {c_cell} | |")
        md.append("")

        md.append("## Detailed Findings & Actionable Remediations\n")
        for idx, f in enumerate(report.findings, 1):
            md.append(f"### {idx}. [{f.severity.upper()}] {f.title}")
            md.append(f"- **Category:** `{f.category}` | **Location:** `{f.file_path}:{f.line_number}`")
            if f.cwe_id:
                md.append(f"- **CWE:** {f.cwe_id}")
            md.append(f"- **Evidence:** {f.evidence}")
            md.append(f"- **Explanation:** {f.explanation}")
            md.append(f"- **Remediation:** {f.remediation}\n")
            if f.snippet:
                md.append("```\n" + f.snippet + "\n```\n")
            if f.diff_patch:
                md.append("**Suggested AI Patch:**")
                md.append("```diff\n" + f.diff_patch + "\n```\n")
            md.append("---\n")

        return "\n".join(md)

    @staticmethod
    def to_json(report: AuditReport) -> str:
        return report.model_dump_json(indent=2)

    @staticmethod
    def to_html(report: AuditReport) -> str:
        md_text = Reporter.to_markdown(report)
        grade_colors = {
            "A+": "#10b981", "A": "#10b981", "B": "#3b82f6", "C": "#f59e0b", "D": "#f97316", "F": "#ef4444"
        }
        color = grade_colors.get(report.summary.grade, "#6b7280")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeSentinel Audit - {report.metadata.repo_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #e2e8f0; line-height: 1.6; margin: 0; padding: 40px; }}
        .container {{ max-width: 900px; margin: 0 auto; background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; }}
        h1, h2, h3 {{ color: #f8fafc; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #334155; padding-bottom: 20px; margin-bottom: 30px; }}
        .score-box {{ text-align: center; background: #0f172a; padding: 16px 28px; border-radius: 10px; border: 2px solid {color}; }}
        .score-val {{ font-size: 40px; font-weight: 800; color: {color}; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; text-transform: uppercase; }}
        .sev-critical {{ background: #7f1d1d; color: #fca5a5; }}
        .sev-high {{ background: #7c2d12; color: #fdba74; }}
        .sev-medium {{ background: #78350f; color: #fde047; }}
        .sev-low {{ background: #1e3a5f; color: #93c5fd; }}
        .finding-card {{ background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        pre {{ background: #020617; padding: 14px; border-radius: 6px; overflow-x: auto; color: #38bdf8; font-size: 13px; }}
        code {{ font-family: 'JetBrains Mono', Consolas, monospace; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🛡️ CodeSentinel AI Audit</h1>
                <p>Repository: <strong>{report.metadata.repo_name}</strong> | Scanned on {report.created_at}</p>
            </div>
            <div class="score-box">
                <div class="score-val">{report.summary.security_score}</div>
                <div>Grade: <strong>{report.summary.grade}</strong></div>
            </div>
        </div>

        <h2>Executive AI Analysis</h2>
        <p style="background: #0f172a; border-left: 4px solid #6366f1; padding: 16px; border-radius: 4px;">
            {report.agent_analysis.replace(chr(10), '<br/>')}
        </p>

        <h2>Findings ({len(report.findings)})</h2>
        {"".join([f'''
        <div class="finding-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="margin:0;">{f.title}</h3>
                <span class="badge sev-{f.severity}">{f.severity}</span>
            </div>
            <p style="color:#94a3b8; font-size:13px; margin: 8px 0;">{f.file_path}:{f.line_number} | Category: <strong>{f.category}</strong></p>
            <p>{f.explanation}</p>
            <p><strong>Remediation:</strong> {f.remediation}</p>
            <pre><code>{f.snippet}</code></pre>
            {f'<p><strong>Diff Patch:</strong></p><pre><code>{f.diff_patch}</code></pre>' if f.diff_patch else ''}
        </div>
        ''' for f in report.findings])}
    </div>
</body>
</html>
"""
        return html
