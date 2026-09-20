import os
import subprocess
import sys

def convert_md_to_pdf():
    md_file = r"d:\Mersa_pfe\script_presentation_b1.md"
    html_file = r"d:\Mersa_pfe\script_presentation_b1.html"
    pdf_file = r"d:\Mersa_pfe\script_presentation_b1.pdf"

    if not os.path.exists(md_file):
        print("MD file not found!")
        return

    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Parse simple markdown to clean styled HTML
    import re

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Script Oral de Présentation PFE (Niveau B1)</title>
<style>
  @page {{
    size: A4;
    margin: 20mm 20mm 20mm 20mm;
  }}
  body {{
    font-family: 'Segoe UI', Arial, Helvetica, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1E293B;
    background: #FFFFFF;
  }}
  h1 {{
    font-size: 20pt;
    color: #0F172A;
    border-bottom: 3px solid #0D9488;
    padding-bottom: 8px;
    margin-bottom: 15px;
  }}
  h2 {{
    font-size: 13pt;
    color: #0D9488;
    background: #F0FDF4;
    border-left: 4px solid #0D9488;
    padding: 6px 12px;
    margin-top: 24px;
    margin-bottom: 12px;
    border-radius: 0 4px 4px 0;
    page-break-after: avoid;
  }}
  blockquote {{
    background: #F8FAFC;
    border-left: 4px solid #6366F1;
    margin: 10px 0 15px 0;
    padding: 12px 16px;
    font-style: italic;
    font-size: 11pt;
    color: #334155;
    border-radius: 0 6px 6px 0;
  }}
  strong {{
    color: #0F172A;
  }}
  p {{
    margin-bottom: 10px;
  }}
  hr {{
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 20px 0;
  }}
  .meta-box {{
    background: #F1F5F9;
    border: 1px solid #CBD5E1;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 10pt;
  }}
</style>
</head>
<body>
"""

    # Convert simple MD syntax
    lines = md_text.split("\n")
    in_block = False

    for line in lines:
        if line.startswith("# "):
            html_content += f"<h1>{line[2:]}</h1>\n"
        elif line.startswith("## "):
            html_content += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith("> "):
            text = line[2:].strip()
            # Replace markdown bold and italic
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            html_content += f"<blockquote>{text}</blockquote>\n"
        elif line.startswith("- ") or line.startswith("* "):
            text = line[2:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            html_content += f"<li>{text}</li>\n"
        elif line.strip() == "---":
            html_content += "<hr>\n"
        elif line.strip():
            text = line.strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            html_content += f"<p>{text}</p>\n"

    html_content += "</body></html>"

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("HTML created successfully.")

    # Convert HTML to PDF using MS Edge headless
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "msedge"
    ]

    edge_cmd = None
    for p in edge_paths:
        if os.path.exists(p) or p == "msedge":
            edge_cmd = p
            break

    if edge_cmd:
        cmd = f'"{edge_cmd}" --headless --disable-gpu --print-to-pdf="{pdf_file}" "{html_file}"'
        print("Executing:", cmd)
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print("Result:", res.returncode)
        if os.path.exists(pdf_file):
            print(f"PDF successfully generated at: {pdf_file}")
            return pdf_file

    print("Could not generate PDF with Edge, trying alternative python PDF library...")

if __name__ == "__main__":
    convert_md_to_pdf()
