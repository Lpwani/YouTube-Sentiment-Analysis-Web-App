
from scraper import _make_driver, _maybe_handle_consent
from selenium.webdriver.common.by import By
import time

url = input("Paste the YouTube video URL: ").strip()

driver = None

try:
    # Visible Chrome helps us identify consent screens and restrictions.
    driver = _make_driver(headless=False)
    driver.set_page_load_timeout(45)
    driver.get(url)

    time.sleep(5)
    _maybe_handle_consent(driver)

    print("\n--- PAGE DIAGNOSTICS ---")
    print("Current URL:", driver.current_url)
    print("Page title:", driver.title)

    body = driver.find_element(By.TAG_NAME, "body").text
    print("\nVisible page text (first 3000 characters):")
    print(body[:3000])

    selectors = [
        "ytd-comments",
        "#comments",
        "ytd-comment-thread-renderer",
        "ytd-comment-view-model",
        "#content-text",
        "ytd-continuation-item-renderer",
    ]

    print("\n--- ELEMENT COUNTS ---")
    for selector in selectors:
        count = len(driver.find_elements(By.CSS_SELECTOR, selector))
        print(f"{selector}: {count}")

    print("\n--- TESTING COMMENT LAZY LOADING ---")

    comments_section = driver.find_element(By.CSS_SELECTOR, "#comments")

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'start'});",
        comments_section
    )

    for attempt in range(1, 6):
        time.sleep(3)

        driver.execute_script(
            "window.scrollBy(0, 700);"
        )

        time.sleep(1)

        print(f"\nAttempt {attempt}:")
        for selector in [
            "ytd-comment-thread-renderer",
            "ytd-comment-view-model",
            "#content-text",
            "ytd-continuation-item-renderer",
        ]:
            count = len(
                driver.find_elements(By.CSS_SELECTOR, selector)
            )
            print(f"{selector}: {count}")

        body = driver.find_element(By.TAG_NAME, "body").text
        print("Comments heading visible:", "Comments" in body)

    driver.save_screenshot("youtube_debug.png")

    with open("youtube_debug.html", "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    print("\nSaved youtube_debug.png and youtube_debug.html")

    input("\nInspect the Chrome page, then press Enter to close it...")

finally:
    if driver:
        driver.quit()
