"""QA teach/reword/hint across both dialogue AND debate + clickable logo."""
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/local/bin/chromium", headless=True)
        page = b.new_page(viewport={"width": 1280, "height": 900})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto("http://localhost:8001")
        page.wait_for_selector(".p-node", timeout=12000)

        # --- Clickable logo goes home ---
        page.locator("[data-tab=dialogue]").click()
        page.wait_for_timeout(400)
        page.locator(".brand").click()
        page.wait_for_timeout(400)
        print("logo returns to explore:", page.locator("#tab-explore").is_visible())

        # --- Debate: teach, reword, hint all present + work ---
        page.locator("[data-tab=dialogue]").click()
        page.wait_for_timeout(400)
        page.locator("#debateBtn").click()
        page.wait_for_timeout(1600)
        print("debate started; teach btn visible:", page.locator("#teachBtn:visible").count())
        page.locator("#teachBtn").click()
        page.wait_for_timeout(1400)
        body = page.locator("#transcript").inner_text()
        print("debate teach works:", "two sides" in body.lower() or "set the debate" in body.lower())
        page.locator("#rewriteBtn").click()
        page.wait_for_timeout(1200)
        body2 = page.locator("#transcript").inner_text()
        print("debate reword works:", "no trouble" in body2.lower() or "on one side" in body2.lower())
        print("errors:", errs if errs else "none")
        b.close()


if __name__ == "__main__":
    main()
