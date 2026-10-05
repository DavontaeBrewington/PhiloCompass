"""QA the improved PhiloCompass UI + reshoot portfolio screenshots."""

import os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8001"
OUT = "/home/ubuntu/philocompass/docs/screenshots"
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/local/bin/chromium", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))

    page.goto(BASE)
    page.wait_for_selector(".p-node", timeout=10000)
    page.wait_for_timeout(600)
    page.screenshot(path=f"{OUT}/01_explore_map.png", full_page=False)
    print("01 map: nodes=", page.locator(".p-node").count(), "edges=", page.locator(".p-edge").count())

    # Verify hand-placed layout: Kant node should have nonzero position
    kant = page.eval_on_selector("[data-id=kant]", "(n) => n.getAttribute('transform')")
    print("kant transform:", kant)

    # Open a node -> dialog seeded on that node
    page.eval_on_selector("[data-id=plato]", "(n) => n.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    page.wait_for_timeout(500)
    page.screenshot(path=f"{OUT}/02_detail_panel.png")
    print("02 detail open:", page.locator("#detailPanel.open").count(), "| name:", page.locator("#detailName").inner_text())

    page.locator("#detailDialogue").click()
    page.wait_for_timeout(900)
    q = page.locator("#tutorBubble").inner_text()
    print("03 seeded dialogue question:", q[:70])
    page.screenshot(path=f"{OUT}/03_dialogue_seeded.png")
    print("   export row visible:", page.locator("#exportRow").count() > 0 and not page.locator("#exportRow").evaluate("n=>n.classList.contains('is-hidden')"))

    # Post an answer -> follow-up
    page.fill("#answerBox", "I think Plato's Forms are real but hard to know.")
    page.locator("#sendBtn").click()
    page.wait_for_timeout(2500)
    print("   turns so far:", page.locator(".turn").count())
    page.screenshot(path=f"{OUT}/04_dialogue_followup.png")

    # Verify exported text via download handler
    page.locator("#exportMdBtn").click()
    with page.expect_download() as dl:
        page.locator("#exportMdBtn").click()
    dl = dl.value
    path = dl.path()
    content = open(str(path)).read()
    print("05 md download bytes:", len(content), "| starts:", content[:40].replace(chr(10),' '))

    print("JS errors:", errors if errors else "none")
    browser.close()
