"""Screenshot the PhiloCompass Explore + Dialogue tabs for QA + portfolio docs."""

from playwright.sync_api import sync_playwright

BASE = "http://localhost:8001"
OUT = "/home/ubuntu/philocompass/docs/screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/local/bin/chromium", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))

    # Explore tab
    page.goto(BASE)
    page.wait_for_selector(".p-node", timeout=10000)
    page.wait_for_timeout(800)
    import os
    os.makedirs(OUT, exist_ok=True)
    page.screenshot(path=f"{OUT}/01_explore_map.png", full_page=False)
    print("saved 01_explore_map.png  nodes=", page.locator(".p-node").count(),
          "edges=", page.locator(".p-edge").count())

    # Open a detail panel (dispatch click in JS to avoid pointer interception)
    page.eval_on_selector(".p-node", "(n) => n.dispatchEvent(new MouseEvent('click', {bubbles:true}))")
    page.wait_for_timeout(700)
    page.screenshot(path=f"{OUT}/02_detail_panel.png")
    print("detail panel open:", page.locator("#detailPanel.open").count())

    # Dialogue tab + start session
    page.locator("[data-tab=dialogue]").click()
    page.wait_for_timeout(200)
    page.locator("#domainPick [data-d=ethics]").click()
    page.locator("#beginBtn").click()
    page.wait_for_timeout(900)
    page.screenshot(path=f"{OUT}/03_dialogue_start.png")
    print("dialogue question shown:", page.locator("#tutorBubble").inner_text()[:70])

    # Post an answer -> LLM follow-up
    page.fill("#answerBox", "I think actions are right if they produce the best consequences overall.")
    page.locator("#sendBtn").click()
    page.wait_for_timeout(2500)
    page.screenshot(path=f"{OUT}/04_dialogue_followup.png")
    print("transcript turns:", page.locator(".turn").count())

    print("JS errors:", errors if errors else "none")
    browser.close()
