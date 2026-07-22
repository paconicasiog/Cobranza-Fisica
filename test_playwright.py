from playwright.sync_api import sync_playwright

def html_to_pdf(html_content, output_path):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content)
        page.pdf(path=output_path, format="A4", print_background=True)
        browser.close()

if __name__ == "__main__":
    html = "<html><body style='background: blue; color: white;'><h1>Test</h1></body></html>"
    html_to_pdf(html, "test.pdf")
    print("PDF generated successfully.")
