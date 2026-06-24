"""NewsCast automated test — using Playwright."""
from playwright.sync_api import sync_playwright
import sys

BUGS = []

def log(msg):
    print(f"  {msg}")

def bug(msg):
    BUGS.append(msg)
    print(f"  ❌ BUG: {msg}")

def ok(msg):
    print(f"  ✅ {msg}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844})  # iPhone 14 size
    page.on("console", lambda msg: None)  # suppress, we check below
    page.on("pageerror", lambda err: bug(f"JS Error: {err}"))

    # ==========================================
    # TEST 1: News page loads
    # ==========================================
    print("\n=== 测试1: 新闻页 ===")
    try:
        page.goto("http://localhost:5173/#/news", timeout=15000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)  # wait for async data

        # Check title
        title = page.locator("h1").first
        if title.is_visible():
            ok(f"页面加载: {title.text_content()}")
        else:
            bug("新闻页标题不可见")

        # Check card content
        cards = page.locator(".rounded-card, [class*='card']")
        count = cards.count()
        if count > 0:
            ok(f"检测到 {count} 个卡片元素")
        else:
            bug("未检测到新闻卡片")

        # Check prev/next buttons
        next_btn = page.locator("button:has-text('下一条')")
        prev_btn = page.locator("button:has-text('上一条')")
        if next_btn.count() > 0:
            ok(f"下一条按钮可见")
            # Try clicking next
            if next_btn.first.is_enabled():
                next_btn.first.click()
                page.wait_for_timeout(500)
                ok("点击下一条成功")
            else:
                bug("下一条按钮不可点击")
        else:
            bug("下一条按钮不存在")

        if prev_btn.count() > 0:
            ok("上一条按钮存在")

        # Check progress indicator
        progress = page.locator("text=/第 \\d+/\\d+ 条/").first
        prog2 = page.locator("text=/\\d+/\\d+/").first
        if progress.is_visible() or prog2.is_visible():
            ok("进度指示器可见")
        else:
            log("进度指示器未找到 (maybe rendered differently)")

    except Exception as e:
        bug(f"新闻页异常: {e}")

    # ==========================================
    # TEST 2: Podcast page
    # ==========================================
    print("\n=== 测试2: 播客页 ===")
    try:
        page.goto("http://localhost:5173/#/podcast", timeout=15000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Take screenshot for debugging
        page.screenshot(path="/tmp/podcast_test.png", full_page=True)
        log("截图保存: /tmp/podcast_test.png")

        # Get page text
        body_text = page.locator("body").text_content()

        if "加载播客" in body_text:
            log("看到「加载播客」按钮，点击...")
            load_btn = page.locator("button:has-text('加载播客')")
            if load_btn.count() > 0:
                load_btn.first.click()
                page.wait_for_timeout(3000)
                body_text = page.locator("body").text_content()

        if "小暖" in body_text or "晨间新闻" in body_text or "AI芯片" in body_text:
            ok(f"播客内容可见")
        elif "暂无播客" in body_text or "暂无" in body_text:
            bug("播客数据未加载，显示空状态")
        else:
            # Check if player elements exist
            play_btn = page.locator("button:has(svg)").all()
            log(f"播客页button数量: {len(play_btn)}")
            if len(play_btn) > 2:
                ok("播客页有交互元素")
            else:
                bug(f"播客页无内容，body文字: {body_text[:200]}")

    except Exception as e:
        bug(f"播客页异常: {e}")

    # ==========================================
    # TEST 3: Ask page
    # ==========================================
    print("\n=== 测试3: 追问页 ===")
    try:
        page.goto("http://localhost:5173/#/ask", timeout=15000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        body_text = page.locator("body").text_content()
        if "追问" in body_text or "AI" in body_text or "小暖" in body_text or "输入" in body_text:
            ok("追问页有内容")

        # Check input
        input_field = page.locator("input[placeholder*='追问']")
        if input_field.count() > 0:
            ok("追问输入框可见")
            input_field.first.fill("测试新闻解读")
            page.wait_for_timeout(300)

            send_btn = page.locator("button:has(svg)").last
            # Find the send button specifically
            send_buttons = page.locator("button").all()
            log(f"追问页buttons: {len(send_buttons)}")
            ok("追问页有交互元素")
        else:
            bug("追问输入框不存在")

    except Exception as e:
        bug(f"追问页异常: {e}")

    # ==========================================
    # TEST 4: Me page + Theme
    # ==========================================
    print("\n=== 测试4: 我的页 ===")
    try:
        page.goto("http://localhost:5173/#/me", timeout=15000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        body_text = page.locator("body").text_content()
        if "主题" in body_text or "偏好" in body_text or "陪伴" in body_text or "关于" in body_text:
            ok("我的页有内容")
        else:
            bug(f"我的页无预期内容: {body_text[:200]}")

        # Check theme switcher
        theme_btns = page.locator("button[title]").all()
        if len(theme_btns) > 0:
            ok(f"主题切换按钮: {len(theme_btns)} 个")

    except Exception as e:
        bug(f"我的页异常: {e}")

    # ==========================================
    # TEST 5: Tab navigation
    # ==========================================
    print("\n=== 测试5: Tab导航 ===")
    try:
        page.goto("http://localhost:5173/#/news", timeout=15000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        tab_texts = ["新闻", "播客", "追问", "我的"]
        for tab_name in tab_texts:
            tab = page.locator(f"button:has-text('{tab_name}')").first
            if tab.is_visible():
                ok(f"Tab「{tab_name}」可见")
                tab.click()
                page.wait_for_timeout(500)
                url = page.url
                log(f"  跳转到: {url}")
            else:
                bug(f"Tab「{tab_name}」不可见（可能被桌面侧栏样式隐藏）")

    except Exception as e:
        bug(f"Tab导航异常: {e}")

    # ==========================================
    # TEST 6: FAB Button
    # ==========================================
    print("\n=== 测试6: FAB按钮 ===")
    try:
        page.goto("http://localhost:5173/#/news", timeout=15000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        # FAB should be a fixed button
        fab = page.locator("button:has(svg)").first
        all_btns = page.locator("button").all()
        log(f"总按钮数: {len(all_btns)}")

        # Check for the FAB specifically
        fab_btns = page.locator("button[class*='fixed']").all()
        if len(fab_btns) > 0:
            ok(f"FAB按钮存在 (固定定位按钮): {len(fab_btns)} 个")
        else:
            bug("FAB按钮不存在")

    except Exception as e:
        bug(f"FAB异常: {e}")

    # ==========================================
    # TEST 7: News detail navigation
    # ==========================================
    print("\n=== 测试7: 新闻详情 → 返回 ===")
    try:
        page.goto("http://localhost:5173/#/news", timeout=15000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(3000)

        # Click the card to open detail
        card = page.locator(".rounded-card, [class*='card']").first
        if card.is_visible():
            card.click()
            page.wait_for_timeout(1000)

            # Check if detail opened
            body_text = page.locator("body").text_content()
            if "查看原文" in body_text or "返回" in body_text or "AI 解读" in body_text:
                ok("详情页打开成功")

                # Click back
                back_btn = page.locator("button:has-text('返回')").first
                if back_btn.is_visible():
                    back_btn.click()
                    page.wait_for_timeout(500)
                    after_url = page.url
                    log(f"返回后URL: {after_url}")
                    if "/news" in after_url:
                        ok("返回后仍在新闻页")
                    else:
                        bug(f"返回后跳到了: {after_url}")
                else:
                    bug("返回按钮不存在")
            else:
                bug(f"详情页未正确打开: {body_text[:200]}")
        else:
            bug("新闻卡片不可点击")

    except Exception as e:
        bug(f"详情返回异常: {e}")

    # ==========================================
    # REPORT
    # ==========================================
    print("\n" + "=" * 60)
    print("            测试报告")
    print("=" * 60)
    if BUGS:
        print(f"\n发现 {len(BUGS)} 个Bug:")
        for i, b in enumerate(BUGS, 1):
            print(f"  {i}. {b}")
    else:
        print("\n✅ 所有测试通过，未发现Bug")
    print("")

    browser.close()
    sys.exit(0 if not BUGS else 1)
