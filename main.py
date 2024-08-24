import json
import requests
from bs4 import BeautifulSoup

def get_data_script_tag(soup):    
    script_tags = soup.find_all("script")
    data_script_tag = None
    for script_t in script_tags:
        s_t = script_t.get_text().strip()
        if s_t.startswith("window.__DATA__"):
            data_script_tag = s_t
            
    data_script_tag = data_script_tag.replace("window.__DATA__ =", "").replace(";", "")
    return data_script_tag


def get_url_response(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    return response
    
def get_info_from_script_tag(soup):
    data_script_tag = get_data_script_tag(soup)
    ch_data_img_server = data_script_tag.split("window.__info =")
    ch_info = json.loads(ch_data_img_server[0])
    img_server = json.loads(ch_data_img_server[1])

    return ch_info, img_server

def download_img(parsed_data, img_link, img_id):
    from pathlib import Path
    path = Path.home() / "Pictures" / "mangas" / parsed_data['manga_slug'] / parsed_data['ch_number']
    path.mkdir(parents=True, exist_ok=True)
    chapter_img_path = path / f"{img_id}.jpg"
    resp = requests.get(img_link)
    with open(chapter_img_path, 'wb') as handler:
        handler.write(resp.content)

    
def download_chapter(parsed_data, soup):
    imgs_names = soup.find(id="pg")
    imgs_with_ind = json.loads(imgs_names.get_text().strip().replace("window.__pg =", "").replace(";", ""))
    chapter_id = parsed_data['chapter_id']
    path_to_ch = parsed_data['path_img_server'] + "/" + str(chapter_id)
    
    for img in imgs_with_ind:
        img_path = path_to_ch + "/" + img['u']
        print(img_path)
        download_img(parsed_data, img_path, img['p'])



def fetch_and_download(url):
    print(url)
    response = get_url_response(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    ch_info, img_server = get_info_from_script_tag(soup)

    m_img_server = img_server['img']['server']

    parsed_data = {}
    parsed_data['ch_info'] = ch_info
    parsed_data['manga_slug'] = ch_info['manga']['slug']
    parsed_data['path_img_server'] = img_server['servers'][m_img_server] + "/" + "manga" + "/" + parsed_data['manga_slug'] + "/" + "chapters"
    parsed_data['ch_number'] = img_server['current']['number']
    parsed_data['chapter_id'] = parsed_data['ch_info']['current']['id']


    download_chapter(parsed_data, soup)

def main():
    url = "https://mangalib.me/kanojo-mo-kanojo/v16/c136"
    response = get_url_response(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    ch_info, img_server = get_info_from_script_tag(soup)

    
    for ch in ch_info['chapters']:
        url = f"https://mangalib.me/kanojo-mo-kanojo/v{ch['chapter_volume']}/c{ch['chapter_number']}"
        fetch_and_download(url)

main()