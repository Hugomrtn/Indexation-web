import time
from urllib.request import urlopen
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json

MAIN_URL = "https://web-scraping.dev/products"


def politesse(temps):
    time.sleep(temps)


def get_html_from_link(link):
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

    base_url = get_base_url(url)
    robots_url = urljoin(base_url, '/robots.txt')

    robot = RobotFileParser()
    robot.set_url(robots_url)
    try:
        robot.read()
        return robot.can_fetch(user_agent, url)
    except Exception:
        return True


def extract_informations(html_string, href):
    soup = BeautifulSoup(html_string, "html.parser")

    title = soup.title.name if soup.title else "No Title"

    first_paragraph = soup.find('p').get_text() if soup.find('p') else "No Paragraph"

    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        text = link.get_text(strip=True)
        if href:
            links.append({'href': href, 'text': text})

    return {
        'title': title,
        'link': href,
        'first_paragraph': first_paragraph,
        'links': links
    }


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def crawling_logic(fifo_list, links, pages_counter):
    for link in links:
        if pages_counter < 50:
            href = link["href"]
            if "https://" in href:
                if href not in fifo_list:
                    if "product" in href:
                        fifo_list.insert(0, href)
                    else:
                        fifo_list.append(href)
                    pages_counter += 1
    return fifo_list, pages_counter


def crawling(main_url):
    base_url = get_base_url(main_url)
    authorised_links = []
    pages_counter = 0
    fifo_list = []
    if can_fetch(base_url):
        fifo_list.append(main_url)
    viewed_page = []
    final_extraction = []

    while len(fifo_list):
        current_url = fifo_list.pop(0)
        print(pages_counter)
        print("viewed : ", len(viewed_page))
        if current_url not in viewed_page:
            if current_url not in authorised_links:
                authorised_links.append(current_url)
                html_string = get_html_from_link(current_url)
                extraction = extract_informations(html_string, current_url)
                links = extraction["links"]
                fifo_list, pages_counter = crawling_logic(fifo_list, links,
                                                          pages_counter)
                final_extraction.append(extraction)
                viewed_page.append(current_url)
                politesse(0.5)
    print(fifo_list)
    print(pages_counter)
    print(authorised_links)

    save_to_json(final_extraction, "output.json")


final_extraction = crawling(MAIN_URL)
