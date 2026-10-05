"""Verify un-clicking an active domain chip: re-click toggles off, and
clicking elsewhere on the page clears it too."""
from playwright.sync_api import sync_playwright


def active_count(page):
    return page.evaluate(
        "document.querySelectorAll('.domain-ticker-track .chip.is-active').length"
    )


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/local/bin/chromium", headless=True)
        page = b.new_page(viewport={"width": 1280, "height": 900})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto("http://localhost:8001")
        page.wait_for_selector(".p-node", timeout=12000)
        # pause the ticker so the chip is stable to click
        page.hover(".chips-scroller")
        page.wait_for_timeout(300)
        c = page.locator(".domain-ticker-track .chip").first
        c.click(force=True)
        page.wait_for_timeout(300)
        print("after selecting first chip, active:", active_count(page))

        # unclick by clicking the same chip again
        c.click(force=True)
        page.wait_for_timeout(300)
        print("after re-clicking same chip, active:", active_count(page))

        # select again, then unclick by clicking empty map area
        page.locator('.domain-ticker-track .chip[data-d="ethics"]').first.click(force=True)
        page.wait_for_timeout(300)
        print("after selecting ethics, active:", active_count(page))
        page.mouse.click(600, 750)  # empty space on the map
        page.wait_for_timeout(300)
        print("after clicking empty map, active:", active_count(page))
        print("errors:", errs if errs else "none")
        b.close()


if __name__ == "__main__":
    main()
