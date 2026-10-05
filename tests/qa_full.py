"""Full QA of all PhiloCompass polish features."""

import os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8001"
OUT = "/home/ubuntu/philocompass/docs/screenshots"
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/usr/local/bin/chromium", headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    # enable service workers via a normal page
    page = ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))

    # 1. Explore loads
    page.goto(BASE)
    page.wait_for_selector(".p-node", timeout=10000)
    page.wait_for_timeout(700)
    print("1 nodes:", page.locator(".p-node").count(), "edges:", page.locator(".p-edge").count())

    # Hero revealed
    print("2 hero visible:", page.locator("#brandHero").evaluate("(n)=>n.classList.contains('show')"))
    # Era row + slider visible
    print("3 era slider:", page.locator("#eraSlider").count(), "| era label:", page.locator("#eraLabel").inner_text())

    # 2. Timeline scrubber: drag to era 1 (Ancient only) -> fewer nodes
    page.locator("#eraSlider").fill("10")
    page.wait_for_timeout(300)
    ancient_nodes = page.locator(".p-node").count()
    print("4 ancient-only nodes:", ancient_nodes, "| label:", page.locator("#eraLabel").inner_text())
    page.screenshot(path=f"{OUT}/05_timeline_ancient.png")
    page.locator("#eraSlider").fill("100")
    page.wait_for_timeout(300)
    all_nodes = page.locator(".p-node").count()
    print("5 back-to-all nodes:", all_nodes)
    assert all_nodes > ancient_nodes, "timeline scrub should hide later-era nodes"

    # 3. Edge rationale tooltip: hover an influence edge
    edge = page.locator("line.p-edge.influence[data-rationale]").first
    edge.hover()
    page.wait_for_timeout(300)
    tip = page.locator("#edgeTooltip")
    print("6 edge tooltip shown:", tip.evaluate("(n)=>n.classList.contains('show')"), "| text starts:", (tip.inner_text() or "")[:40].replace(chr(10),' '))
    page.screenshot(path=f"{OUT}/06_edge_tooltip.png")

    # 4. Node detail + seeded dialogue
    page.eval_on_selector("[data-id=kant]", "(n)=>n.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
    page.wait_for_timeout(500)
    page.locator("#detailDialogue").click()
    page.wait_for_timeout(900)
    print("7 seeded dialogue:", page.locator("#tutorBubble").inner_text()[:55])
    page.screenshot(path=f"{OUT}/07_dialogue.png")

    # 5. Learning path: pick "ethics_introduction", progress list shows
    page.locator("#pathPick [data-p=ethics_introduction]").click()
    page.wait_for_timeout(200)
    print("8 path progress visible:", not page.locator("#pathProgress").evaluate("(n)=>n.classList.contains('is-hidden')"))
    print("   steps:", page.locator(".path-step").count())
    page.screenshot(path=f"{OUT}/08_paths.png")

    # 6. Answer a few times to reach conclusion + takeaway
    for ans in ["Max happiness matters most.", "But punishing the innocent seems wrong.", "So consequences can't be the whole story."]:
        page.fill("#answerBox", ans)
        page.locator("#sendBtn").click()
        page.wait_for_timeout(2400)
    print("9 conclusion visible:", not page.locator("#conclusion").evaluate("(n)=>n.classList.contains('is-hidden')"))
    print("10 takeaway shown:", not page.locator("#takeawayWrap").evaluate("(n)=>n.classList.contains('is-hidden')"))
    page.fill("#takeawayBox", "I now think deontology and consequences both matter.")
    page.screenshot(path=f"{OUT}/09_takeaway.png")

    # 7. Export includes takeaway
    page.locator("#exportMdBtn").click()
    with page.expect_download() as dl:
        page.locator("#exportMdBtn").click()
    content = open(str(dl.value.path()), encoding="utf-8").read()
    print("11 export has takeaway:", "Your takeaway" in content)

    # 8. Pan & zoom changed the map transform
    before = page.eval_on_selector("#constellation g", "(g)=>g.getAttribute('transform')")
    # do a few wheel zooms
    box = page.locator("#constellation").bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.wheel(0, -400)
    page.wait_for_timeout(200)
    after = page.eval_on_selector("#constellation g", "(g)=>g.getAttribute('transform')")
    print("12 pan-zoom changed: ", before, "->", after, "| changed:", before != after)

    # 9. URL hash persistence
    page.locator("[data-tab=dialogue]").click()
    page.wait_for_timeout(200)
    print("13 url hash:", page.evaluate("()=>location.hash"))

    print("\nJS errors:", errors if errors else "none")
    browser.close()
