import time
from urllib.request import urlopen
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json


def save_to_json(data, filename):
    # saving the data to a json file
    with open(filename, 'w', encoding='utf-8') as f:
        for entry in data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')


def do_politesse(temps):
    # used to wait between queries
    time.sleep(temps)


def get_html_from_link(link):
    # retreiving HTML webpage from a link
    response = urlopen(link)
    if response.reason == "OK":
        html_bytes = response.read()
        html_string = html_bytes.decode("utf-8")
        return html_string


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


def can_fetch(url, user_agent='*'):
    # getting the robot.txt file from the website
    base_url = get_base_url(url)
    robots_url = urljoin(base_url, '/robots.txt')

    # using the robot rules
    robot = RobotFileParser()
    robot.set_url(robots_url)
    try:
        robot.read()
        return robot.can_fetch(user_agent, url)
    except Exception:
        # if no robot.txt then we assume we can fetch
        return True


def extract_informations(html_string, url):
    soup = BeautifulSoup(html_string, "html.parser")

    # getting the title and first paragraph from the HTML code
    title = soup.title.string if soup.title else "No Title"
    first_paragraph = soup.find('p').get_text() if soup.find('p') else "No Paragraph"  # type:ignore # noqa

    # finding all links
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        text = link.get_text(strip=True)
        # check if it is a https link
        if href and "https://" in href:
            links.append({'href': href, 'text': text})

    return {
        'url': url,
        'title': title,
        'first_paragraph': first_paragraph,
        'links': links
    }


def crawling_logic(fifo_list, links, pages_counter, max_pages):
    for link in links:
        # crawling links till we reach max pages
        if pages_counter < max_pages:
            href = link["href"]
            if "https://" in href:
                if href not in fifo_list:
                    if "product" in href:
                        # prioritizing pages with "product" in it
                        fifo_list.insert(0, href)
                    else:
                        fifo_list.append(href)
                    pages_counter += 1
    return fifo_list, pages_counter


def crawling(main_url, output_name, max_pages):
    # initializing variables
    base_url = get_base_url(main_url)
    authorised_links = []
    pages_counter = 0
    fifo_list = []

    # verifying robot permissions
    if can_fetch(base_url):
        fifo_list.append(main_url)

    viewed_page = []
    final_extraction = []

    # processing the queue
    while len(fifo_list):
        current_url = fifo_list.pop(0)
        print("viewed: ", len(viewed_page)+1)

        # processing unique urls
        if current_url not in viewed_page:
            if current_url not in authorised_links:
                authorised_links.append(current_url)
                html_string = get_html_from_link(current_url)

                # extracting metadata and links
                extraction = extract_informations(html_string, current_url)
                links = extraction["links"]

                # updating queue
                fifo_list, pages_counter = crawling_logic(fifo_list, links,
                                                          pages_counter,
                                                          max_pages)
                # storing results
                final_extraction.append(extraction)
                viewed_page.append(current_url)

                # applying delay
                do_politesse(0.5)

    save_to_json(final_extraction, output_name)


def main():
    MAIN_URL = "https://web-scraping.dev/products"
    output_name = "TP1/output.jsonl"
    max_pages = 50
    crawling(MAIN_URL, output_name, max_pages)


main()
