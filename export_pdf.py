#!/usr/bin/env python3
"""Export Reveal.js presentation slides to PDF using Playwright."""

import asyncio
import os
from pathlib import Path

async def export_slides():
    from playwright.async_api import async_playwright
    from reportlab.lib.pagesizes import landscape
    from reportlab.pdfgen import canvas
    from PIL import Image

    base_dir = Path(__file__).parent
    url = f"file://{base_dir}/index.html"
    screenshots_dir = base_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    output_pdf = base_dir / "The-4-Questions-GTM-Playbook.pdf"

    # High-res capture at 2x scale (2560x1440 effective)
    width, height = 1280, 720
    scale = 2

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)

        # Load the presentation and wait for Reveal.js
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Get total slide count from DOM
        total = await page.evaluate("document.querySelectorAll('.reveal .slides > section').length")
        print(f"Total slides: {total}")

        # Capture each slide
        for i in range(total):
            await page.goto(f"{url}#/{i}", wait_until="networkidle")
            await page.wait_for_timeout(800)
            screenshot_path = screenshots_dir / f"slide_{i:03d}.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"  Captured slide {i + 1}/{total}")

        await browser.close()

    # Combine screenshots into PDF (use scaled dimensions for sharp rendering)
    print("Creating PDF...")
    pdf_width = width * scale
    pdf_height = height * scale
    c = canvas.Canvas(str(output_pdf), pagesize=(pdf_width, pdf_height))

    for i in range(total):
        screenshot_path = screenshots_dir / f"slide_{i:03d}.png"
        if screenshot_path.exists():
            c.drawImage(str(screenshot_path), 0, 0, pdf_width, pdf_height)
            c.showPage()

    c.save()
    print(f"PDF saved to: {output_pdf}")

    # Clean up screenshots
    for f in screenshots_dir.glob("*.png"):
        f.unlink()
    screenshots_dir.rmdir()
    print("Cleaned up screenshots.")

if __name__ == "__main__":
    asyncio.run(export_slides())
