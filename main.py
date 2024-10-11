from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import time

#  using firefox, connect to host.docker.internal:4444
firefox_options = Options()
firefox_options.add_argument("--headless")
driver = webdriver.Remote(
    command_executor="http://host.docker.internal:4444/wd/hub", options=firefox_options
)

# Open 9gag.com
driver.get("https://9gag.com/interest/memes")


def append_to_file(line: str):
    with open("9gag-memes-dataset-stage1.tsv", "a") as f:
        f.write(line + "\n")


def analyze_article(article: WebElement):
    # get id, check id starts with "jsid-post-"
    id = article.get_attribute("id")
    if not id.startswith("jsid-post-"):
        return

    try:
        title = article.find_element(By.CSS_SELECTOR, "header h2").text
    except:
        return None

    image_url = "<video-content>"
    try:
        image_url = article.find_element(
            By.CSS_SELECTOR, ".post-container .image-post img"
        ).get_attribute("src")
    except:
        pass

    upvote = ""
    try:
        upvote = article.find_element(By.CSS_SELECTOR, "span.upvote").text
    except:
        pass

    comment_count = ""
    try:
        comment_count = article.find_element(
            By.CSS_SELECTOR, "a.comment.badge-evt > span"
        ).text
    except:
        pass

    line = f"{id}\t{title}\t{image_url}\t{upvote}\t{comment_count}"
    append_to_file(line)


def analyze_stream_container(stream_container: WebElement):
    articles = stream_container.find_elements(By.TAG_NAME, "article")
    for article in articles:
        analyze_article(article)

stream_container: WebElement | None = None
while True:
    stream_container = driver.find_element(By.CSS_SELECTOR, "div.stream-container")
    if stream_container:
        break

i = 0
try:
    while True:
        analyze_stream_container(stream_container)
        next_stream_container = None
        while True:
            try:
                next_stream_container = stream_container.find_element(
                    By.XPATH, "following-sibling::div[@class='stream-container'][1]"
                )
                break
            except:
                pass
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.1)
        stream_container = next_stream_container
        i += 1
        print(f"Stream {i}")
except KeyboardInterrupt:
    pass

# Close the browser
driver.quit()
