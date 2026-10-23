import base64
import os
from datetime import datetime

from playwright.async_api import async_playwright


async def convert(html_path: str) -> str:
    """Convert an HTML file to a PDF using Playwright (async)."""
    now = datetime.now()
    today_str = now.strftime("%d-%m-%Y %I-%M %p")

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"
    )
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"bhopal-masterplan - {today_str}.pdf")

    abs_html_path = os.path.abspath(html_path)
    url = f"file:///{abs_html_path.replace(os.sep, '/')}"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until="load")

        client = await context.new_cdp_session(page)

        pdf_data = await client.send(
            "Page.printToPDF",
            {
                "printBackground": True,
                "displayHeaderFooter": True,
                "headerTemplate": "",
                "footerTemplate": """
                <div style="width:100%;padding: 5px 20px 2px 20px;font-family: Arial, sans-serif;border-top: 1px solid #e2e8f0;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                    <span style="font-size:9px;">Powered by:</span>
                    <span style="font-size:11px;font-weight:600;margin-left:8px;">ML INFOMAP PVT LTD</span>
                    </div>
                    <div style="font-size:9px;">
                    Page <span class="pageNumber" style="font-weight:600;font-size:11px;"></span>
                    of <span class="totalPages" style="font-weight:600;font-size:11px;"></span>
                    </div>
                </div>
                </div>
                """,
                "paperWidth": 8.27,
                "paperHeight": 11.69,
                "marginTop": 0.2,
                "marginBottom": 0.5,
                "marginLeft": 0.0,        # ↓ removed — CSS handles it now
                "marginRight": 0.0,
                "preferCSSPageSize": False,
            },
        )

        pdf_bytes = base64.b64decode(pdf_data["data"])
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)

        await browser.close()

    return output_path