import requests
from bs4 import BeautifulSoup
import os
import re


MAIN_URL = "https://www.namasha.com/"
PLAYLIST_KEYWORD = "/playlists"
ROOT = ""  # type your address
QUALITY = "144p"


def create_homepage_url(main_url, page_name, playlist_keyword):
    return main_url + page_name + playlist_keyword


def extract_playlists_links(url):
    response = requests.get(url)
    content = BeautifulSoup(response.text, "html.parser")
    result = [item.attrs.get("href") for item in content.find_all("a", string="مشاهده لیست پخش")]
    return result


def finding_download_link(page_link, quality):
    response = requests.get(page_link)
    content = BeautifulSoup(response.text, "html.parser")
    pattern = ".*" + quality + ".mp4"
    result = content.find("a", attrs={"download": "download"}, href=re.compile(pattern))
    if result:
        return result.attrs.get("href")


def extract_download_links_for_each_playlist(url, quality):
    response = requests.get(url)
    content = BeautifulSoup(response.text, "html.parser")
    title = content.find("h1").text
    episods = content.find_all("a", class_="thumbnail-url stretched-link ml-4")
    episods_list = []
    for num, item in enumerate(episods):
        video_name = str(num) + "-" + item.attrs.get("title")
        video_link = finding_download_link(item.attrs["href"], quality)
        episods_list.append({"title": video_name, "link": video_link})
    return title, episods_list


def create_playlists_data(playlists, quality):
    output = {}
    for playlist in playlists:
        playlist_title, playlist_info = extract_download_links_for_each_playlist(playlist, quality)
        output.update({playlist_title: playlist_info})
    return output


def download_specific_file(link, path, file_name):
    downloader = requests.get(link, allow_redirects=True)
    file_addres = path + "/" + file_name + ".mp4"
    open(file_addres, 'wb').write(downloader.content)


def download(root, data):
    for key, value in data.items():
        path = os.path.join(root, key)
        os.mkdir(path)
        for info in value:
            download_specific_file(info.get("link"), path, info.get("title"))


if __name__ == "__main__":
    homepage_url = create_homepage_url(MAIN_URL, "kalasanati.com", PLAYLIST_KEYWORD)
    playlists_links = extract_playlists_links(homepage_url)
    playlists_data = create_playlists_data(playlists_links, QUALITY)
    download(ROOT, playlists_data)
