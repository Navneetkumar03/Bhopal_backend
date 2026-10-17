import os
import re
import base64
from datetime import datetime
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape


# ============================================================
# CONSTANTS
# ============================================================
CATEGORY_COLORS = {
    "Road": "#ef4444",
    "Residential": "#f59e0b",
    "Landuse": "#3b82f6",
    "Green Zone": "#22c55e",
}

METADATA_LABELS = [
    "आवेदक", "पता", "मोबाइल", "मो", "दिनांक", "सेवा में",
    "संबंधित भूमि", "विषय", "आपत्ति विषय", "प्रति", "प्रेषक",
    "नाम", "पिता का नाम", "ईमेल", "Email",
]

SECTION_BOUNDARIES = [
    "महोदय", "विनम्र निवेदन", "प्रार्थना", "भवदीय", "सादर", "धन्यवाद",
]

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
FONTS_DIR = os.path.join(STATIC_DIR, "fonts")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


# ============================================================
# HTML ESCAPE
# ============================================================
def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


# ============================================================
# DESCRIPTION PARSER — same logic as the frontend DescriptionsReader
# ============================================================
def _insert_structural_breaks(text: str) -> str:
    text = re.sub(r"(\s)(\d{1,2})\.\s+", r"\n\1\2. ", text)
    text = re.sub(r"\s([•▪●○])\s+", r"\n\1 ", text)
    text = re.sub(r"(महोदय[,,]?)\s+", r"\1\n", text)
    pattern = "(" + "|".join(map(re.escape, SECTION_BOUNDARIES)) + r")[\s:]*"
    text = re.sub(pattern, r"\1\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _split_metadata_inline(text: str) -> str:
    for label in METADATA_LABELS:
        pattern = rf"\s({re.escape(label)})\s*:\s*"
        text = re.sub(pattern, rf"\n\1: ", text)
    return text


def description_to_html(description: str) -> str:
    """Convert an objection description into styled HTML blocks."""
    if not description:
        return '<p class="desc-para">No description available.</p>'

    prepared = re.sub(r"\r?\n", " ", description)
    prepared = _split_metadata_inline(prepared)
    prepared = _insert_structural_breaks(prepared)

    lines = [line.strip() for line in prepared.split("\n") if line.strip()]
    parts: List[str] = []

    for line in lines:
        # Bullets
        if re.match(r"^[•▪●○\-\u2022]\s+", line):
            text = re.sub(r"^[•▪●○\-\u2022]\s+", "", line)
            parts.append(
                f'<div class="desc-bullet">'
                f'<span class="desc-bullet-dot"></span>'
                f'<span>{_esc(text)}</span>'
                f'</div>'
            )
            continue

        # Numbered items: header if the next line is a bullet, else regular item
        m = re.match(r"^(\d{1,2})\.\s+(.*)$", line)
        if m:
            num, text = m.group(1), m.group(2).strip()
            text = re.sub(r":\s*$", "", text)
            # Look ahead — treat as section header if next line is a bullet
            parts.append(
                f'<div class="desc-section">'
                f'<span class="desc-section-num">{_esc(num)}.</span>'
                f'<span>{_esc(text)}</span>'
                f'</div>'
            )
            continue

        # Metadata: "Label: value"
        meta = re.match(r"^([^:]{1,50}?):\s*(.+)$", line)
        if meta:
            label = meta.group(1).strip()
            value = meta.group(2).strip()
            if any(lbl in label for lbl in METADATA_LABELS):
                parts.append(
                    f'<div class="desc-meta">'
                    f'<strong>{_esc(label)}:</strong> {_esc(value)}'
                    f'</div>'
                )
                continue

        # Plain paragraph
        parts.append(f'<p class="desc-para">{_esc(line)}</p>')

    return "\n".join(parts)


# ============================================================
# IMAGE HELPERS
# ============================================================
def _to_data_uri(path_or_data: str) -> str:
    """Accepts a file path, a data: URI, or raw base64 and returns a data: URI."""
    if not path_or_data:
        return ""
    if path_or_data.startswith("data:") or path_or_data.startswith("http"):
        return path_or_data
    if os.path.isfile(path_or_data):
        ext = os.path.splitext(path_or_data)[1].lower().replace(".", "")
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "svg": "image/svg+xml"}.get(ext, "image/png")
        with open(path_or_data, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"
    # Assume raw base64 already
    return f"data:image/png;base64,{path_or_data}"


# ============================================================
# MAIN BUILDER
# ============================================================
def build(
    markers: List[Dict[str, Any]],
    map_image: str,
    report_title: str,
    report_subtitle: str,
    village: str,
    khasra: str,
    map_scale: float = None, # <--- ADD THIS
) -> str:
    """
    Renders the report HTML and returns the absolute path to the saved file.
    """
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("bhopal_report.html")

    # No longer enriching with description_html since description is gone.
    # We just pass the markers straight through.
    
    # Normalize map image into a data URI
    map_image_uri = _to_data_uri(map_image)

    html = template.render(
        report_title=report_title,
        report_subtitle=report_subtitle,
        exported_on=datetime.now().strftime("%d %b %Y"),
        map_image=map_image_uri,
        markers=markers, # passed directly
        category_colors=CATEGORY_COLORS,
        fonts_dir=FONTS_DIR.replace("\\", "/"),
        village=village,
        khasra=khasra,
        map_scale=map_scale,
    )

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "bhopal_report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return os.path.abspath(output_path)