import requests, json
from bs4 import BeautifulSoup, os
from shutil import copyfileobj, sys

def cleanFilename(fn):
    string = fn
    for char in '\\/:*?"<>|;`':
        if char in fn:
            string = string.replace(char, '')
    return string.strip() + '.mp4'

def main(username, saveto):

    def _downloadVideos(html):
        for vi in html.find_all('li', attrs={'class': 'video-item'}):
            media_src = vi.find('source', attrs={'type': 'video/mp4'})
            if media_src:
                media_src = 'https:' + os.path.dirname(media_src['src']) + '/720.mp4'
                media_title = vi.find('a', attrs={'class': 'title'}).get_text()
                media_saveas = os.path.join(saveto, cleanFilename(media_title))
                
                response = requests.get(media_src, stream=True, allow_redirects=True)
                sys.stdout.write(f"Downloading: {media_title}\n")
                sys.stdout.flush()
                with open(media_saveas, 'wb') as im:
                    copyfileobj(response.raw, im)

    FIRST_REQUEST = True
    CRAWLING = True

    url_init = f'https://plays.tv/u/{username}/videos'
    url_after = f'https://plays.tv/ws/module?'
    response = requests.get(url_init, allow_redirects=True)
    
    page_num = 1

    params = {
        "infinite_scroll": "true",
        "infinite_scroll_fire_only": "true",
        "custom_loading_module_state": "appending",
        "page_num": "",
        "target_user_id": "",
        "last_id": "",
        "section": "videos",
        "format": "application/json",
        "id": "UserVideosMod"
    }

    while CRAWLING:
        if FIRST_REQUEST:
            soup = BeautifulSoup(response.content, 'html.parser')
            data_feed = soup.find('div', attrs={'class': 'mod mod-user-videos activity-feed'})
            data_conf = json.loads(data_feed['data-conf'])
            
            params['last_id'] = data_conf['last_id']
            params['target_user_id'] = data_conf['target_user_id']
            
            _downloadVideos(soup)
            FIRST_REQUEST = False
        else:
            params['page_num'] = page_num

            response = requests.get(url_after, params=params, allow_redirects=True)
            resdata = response.json()

            if resdata['body'] == "":
                CRAWLING = False
            
            params['last_id'] = resdata['config']['last_id']
            soup = BeautifulSoup(resdata['body'], 'html.parser')
            _downloadVideos(soup)

        page_num += 1

if __name__ == "__main__":
    assert os.path.isdir(sys.argv[2])
    main(sys.argv[1], sys.argv[2])





