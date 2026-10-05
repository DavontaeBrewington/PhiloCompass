"""QA the cognitive-state / constructivist dialogue upgrades."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/local/bin/chromium", headless=True)
    page = b.new_page(viewport={"width": 1200, "height": 900})
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://localhost:8001")
    page.wait_for_selector(".p-node", timeout=10000)
    page.locator("[data-tab=dialogue]").click()
    page.wait_for_timeout(400)
    page.locator("#beginBtn").click()
    page.wait_for_timeout(1800)
    utterance = ["I think happiness is what matters.", "Because pain is the only true bad.", "But punishing the innocent seems wrong."]
    for a in utterance:
        page.wait_for_function("document.getElementById('sendBtn') && !document.getElementById('sendBtn').disabled && document.getElementById('sendBtn').offsetParent !== null", timeout=25000)
        page.fill("#answerBox", a)
        page.locator("#sendBtn").click()
        page.wait_for_timeout(3500)
    page.wait_for_timeout(1000)
    body = page.locator("#tab-dialogue").inner_text()
    print("momentum shown:", "Reasoning momentum" in body)
    print("teacher lens shown:", "Why I asked that" in body)
    print("conclusion/takeaway:", "takeaway" in body.lower())
    print("errors:", errs if errs else "none")
    b.close()
