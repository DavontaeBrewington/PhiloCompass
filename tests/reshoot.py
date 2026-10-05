"""Reshoot the portfolio screenshots against the current build."""
import os
from playwright.sync_api import sync_playwright

OUT = "/home/ubuntu/philocompass/docs/screenshots"


def shoot(page, name, wait=1200):
    page.wait_for_timeout(wait)
    page.screenshot(path=os.path.join(OUT, name), full_page=False)
    print("saved", name)


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/local/bin/chromium", headless=True)
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto("http://localhost:8001")
        page.wait_for_selector(".p-node", timeout=15000)
        page.wait_for_timeout(600)
        shoot(page, "01_explore_map.png")

        # open a detail panel (use the delegation fallback via evaluate)
        page.evaluate("document.querySelector('.p-node').__click();")
        page.wait_for_timeout(1000)
        shoot(page, "02_detail_panel.png")
        # close
        page.keyboard.press("Escape")

        # dialogue tab, loaded
        page.locator("[data-tab=dialogue]").click()
        page.wait_for_timeout(600)
        shoot(page, "03_dialogue_home.png")

        # start a dialogue with buttons visible
        page.locator("#beginBtn").click()
        page.wait_for_timeout(1500)
        shoot(page, "04_dialogue_active.png")

        # an active debate
        page.locator("[data-tab=dialogue]").click()
        page.locator("#debateBtn").click()
        page.wait_for_timeout(1500)
        shoot(page, "05_debate_active.png")

        b.close()


if __name__ == "__main__":
    main()
