import os
import asyncio
from playwright.async_api import async_playwright


SITE_URL = os.getenv("SITE_URL", "https://dino.ft.tc")


async def check_ui_formatting() -> int:
	async with async_playwright() as p:
		browser = await p.chromium.launch()
		context = await browser.new_context(viewport={"width": 1366, "height": 900})
		page = await context.new_page()
		# Navigate to the dashboard page which uses CSS/JS
		dashboard_url = SITE_URL.rstrip("/") + "/dashboard"
		await page.goto(dashboard_url, wait_until="networkidle")

		# Basic checks: no missing CSS, no obvious unstyled text, and take a screenshot
		console_messages = []
		page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

		# Collect stylesheets and verify they loaded successfully
		stylesheets = await page.evaluate(
			"Array.from(document.styleSheets).map(s => ({href: s.href || 'inline', disabled: s.disabled}))"
		)
		missing_css = [s for s in stylesheets if s.get("disabled")]  # disabled may indicate load problem

		# Heuristic: ensure at least one stylesheet exists
		no_css_present = len(stylesheets) == 0

		# Check for large unstyled default fonts by inspecting computed font family of body
		font_family = await page.evaluate(
			"getComputedStyle(document.body).fontFamily || ''"
		)
		is_default_font = font_family.strip() in ("", "serif", "sans-serif")

		# Detect layout issues: elements overflowing the viewport width badly
		overflow_count = await page.evaluate(
			"""
			(() => {
			  const vw = window.innerWidth;
			  let count = 0;
			  for (const el of document.querySelectorAll('body *')) {
			    const r = el.getBoundingClientRect();
			    if (r.width - vw > 40) count++;
			  }
			  return count;
			})()
			"""
		)

		# Take artifacts
		artifacts_dir = os.path.join(os.getcwd(), "playwright-artifacts")
		os.makedirs(artifacts_dir, exist_ok=True)
		screenshot_path = os.path.join(artifacts_dir, "homepage.png")
		await page.screenshot(path=screenshot_path, full_page=True)
		html_path = os.path.join(artifacts_dir, "homepage.html")
		with open(html_path, "w", encoding="utf-8") as f:
			f.write(await page.content())

		await context.close()
		await browser.close()

		issues = []
		if no_css_present:
			issues.append("No stylesheets detected")
		if missing_css:
			issues.append(f"Disabled stylesheets: {missing_css}")
		if is_default_font:
			issues.append(f"Body appears to use default font: '{font_family}'")
		if overflow_count > 0:
			issues.append(f"{overflow_count} element(s) overflow viewport width")
		if console_messages:
			issues.append(f"Console messages: {console_messages[:10]}")

		if issues:
			print("UI formatting issues detected:\n- " + "\n- ".join(issues))
			print(f"Artifacts saved to: {artifacts_dir}")
			return 1
		else:
			print("UI appears formatted correctly. Artifacts saved for review.")
			print(f"Artifacts saved to: {artifacts_dir}")
			return 0


def main() -> None:
	code = asyncio.run(check_ui_formatting())
	exit(code)


if __name__ == "__main__":
	main()


