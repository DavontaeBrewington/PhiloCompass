"""Verify cursor-centered zoom: the world point under the mouse must stay fixed
as you wheel-zoom toward it."""
from playwright.sync_api import sync_playwright


def main():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/local/bin/chromium", headless=True)
        page = b.new_page(viewport={"width": 1200, "height": 800})
        page.goto("http://localhost:8001")
        page.wait_for_selector(".p-node", timeout=10000)
        page.wait_for_timeout(400)

        box = page.locator("#constellation").bounding_box()
        # pick two reference points far apart on the right side
        right_pt = {"x": box["x"] + box["width"] * 0.88, "y": box["y"] + box["height"] * 0.55}

        # attach a probe: expose mapView each render via the transform of inner g
        # (read transform before/after)
        def transform():
            return page.eval_on_selector(
                "#constellation > g", "n => n.getAttribute('transform')"
            )

        t0 = transform()
        # zoom IN (wheel up) toward the right-side point
        page.mouse.move(right_pt["x"], right_pt["y"])
        page.mouse.wheel(0, -300)
        page.wait_for_timeout(400)
        t1 = transform()

        # decode translate(tx ty) scale(s)
        import re

        def mv(ss):
            m = re.search(r"translate\(([-\d.]+) ([-\d.]+)\) scale\(([-\d.]+)\)", ss)
            return (float(m.group(1)), float(m.group(2)), float(m.group(3)))

        a0 = mv(t0)
        a1 = mv(t1)
        print("before tx,ty,s:", a0)
        print("after  tx,ty,s:", a1)
        # the point under cursor stays fixed: world_anchor should be ~unchanged
        # world = (px - tx)/s  must equal (px - tx')/s'
        px = right_pt["x"] - box["x"]
        w_before = (px - a0[0]) / a0[2]
        w_after = (px - a1[0]) / a1[2]
        print(f"world-x under cursor before={w_before:.2f} after={w_after:.2f}  drift={abs(w_after-w_before):.3f}")
        assert abs(w_after - w_before) < 1.5, "cursor-anchor drifted!"
        assert a1[2] > a0[2], "scale did not increase"
        print("PASS: zoom is anchored to the mouse cursor")
        b.close()


if __name__ == "__main__":
    main()
