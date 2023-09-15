import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from time import sleep
import json
from random import choice


def Send_message(chat_id, Apikey, post, photo_url):
    url = f'https://api.telegram.org/bot{Apikey}/sendPhoto'
    data = {'chat_id': chat_id, 'photo': photo_url, 'caption': post}
    response = requests.post(url, json=data)
    print(response.json())
    response.raise_for_status()


def Coupland_Scraping():
    response = requests.get('https://coop-land.ru/helpguides/new/')
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")

    title = soup.find('h2', class_='title').text
    preview_text = soup.find('div', class_='preview-text').text
    link = soup.find('a', class_='big-link')['href']
    a = soup.find('a', class_='img')
    photo_url = a.find('img')['data-src']
    photo_url = f"https://coop-land.ru{photo_url}"

    post = f"""{title}
    {preview_text}
Ссылка на статью: {link}"""

    return post, photo_url


def Igromania_Scraping():
    response = requests.get('https://www.igromania.ru/news/')
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")

    link_time = soup.find("section", class_="HeadingPage_infiniteWrap__r6OYJ")
    link = link_time.find("a", class_="knb-card--image style_wrap___iepK")["href"]
    link = f"https://www.igromania.ru/{link}"
    response = requests.get(link)

    soup = BeautifulSoup(response.text, features="html.parser")

    title = soup.find('h1').text
    preview_text = soup.find('div', class_="TextContent_text__X7e1a").text
    photo_url_time = soup.find('figure', class_="MaterialCommonImage_image__GyFHp material-common-image MaterialCommonImage_withCaption__wt5H2")
    photo_url = photo_url_time.find('link')['href']

    post = f"""{title}
        {preview_text}
    Ссылка на статью: {link}"""

    return post, photo_url


def main():
    load_dotenv()
    Apikey = os.getenv("Telegram_bot_api")
    chat_id = os.getenv("Chat_id")

    try:
        with open('post.json', mode='r', encoding="CP1251") as file:
            file_contents = file.read()
        file_contents = json.loads(file_contents)

    except (FileNotFoundError, Exception):

        file_contents = {
            "coupland_post_text": [],
            "igromania_post_text": []
        }
        with open('post.json', mode='w', encoding="CP1251") as file:
            file.write(json.dumps(file_contents))

    while True:
        posts_information = {
            'coupland_post_text': Coupland_Scraping(),
            'igromania_post_text': Igromania_Scraping(),
        }

        random_key = choice(list(posts_information.keys()))
        random_tuple = posts_information[random_key]
        if random_tuple[1] in file_contents[random_key]:
            sleep(3600)
            continue

        with open('post.json', mode='w') as file:
            file.write(json.dumps(posts_information))

        Send_message(chat_id, Apikey, random_tuple[0], random_tuple[1])

        sleep(3600)


if __name__ == '__main__':
    main()
