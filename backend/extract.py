from pathlib import Path
import subprocess
import sys

if len(sys.argv) < 6:
    print("""
Usage:
python extract.py <html_file> <institute> <department> <url> <city> <state>

Example:
python extract.py data/raw/iith_math.html "IIT Hyderabad" "Mathematics" "https://math.iith.ac.in/faculty.php" Hyderabad Telangana
""")
    sys.exit(1)

html_file = sys.argv[1]
institute = sys.argv[2]
department = sys.argv[3]
url = sys.argv[4]
city = sys.argv[5]
state = sys.argv[6] if len(sys.argv) > 6 else ""

html = Path(html_file).read_text(encoding="utf-8", errors="ignore")

if "faculty-card" in html:
    script = "extract_iitr.py"

elif "gdlr-core-personnel-list" in html:
    script = "extract_kingster.py"

elif "fac-head" in html or "card mb-3" in html:
    script = "extract_bootstrap.py"

elif "data-element_type" in html or "elementor-widget" in html:
    script = "extract_elementor.py"

else:
    print("Unknown template. Need new extractor.")
    sys.exit(1)

print(f"Detected extractor: {script}")

cmd = [
    "python", script,
    "--html", html_file,
    "--institute", institute,
    "--department", department,
    "--url", url,
    "--city", city,
    "--state", state,
]

subprocess.run(cmd)