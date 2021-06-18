import requests
import urllib.parse
import json
import os
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

bearer_token = os.getenv("BEARER_TOKEN")

class Scrape:
    headers = {"Authorization": f"Bearer {bearer_token}"}
    api_id_url = "https://api.twitter.com/2/users/by?usernames={}"
    api_tw_url = "https://api.twitter.com/2/users/{}/tweets"

    def __init__(self, user):
        self.user = user
        url = Scrape.api_id_url.format(user)

        r = requests.get(url, headers=Scrape.headers)
        content = json.loads(r.content)
        if not "data" in content:
            raise RuntimeError(f"User {user} does not exist")

        self.user_id = content["data"][0]["id"]
        self.oldest_id = None

    def get_next(self):
        query = {
            'exclude': 'retweets',
            'expansions': 'attachments.media_keys',
            'max_results': 100,
            'media.fields': 'url',
        }
        if self.oldest_id:
            query["until_id"] = self.oldest_id

        url = f"{Scrape.api_tw_url.format(self.user_id)}?{urllib.parse.urlencode(query)}"
        r = requests.get(url, headers=Scrape.headers)

        content = json.loads(r.content)
        if "oldest_id" not in content["meta"]:
            return None
        self.oldest_id = content["meta"]["oldest_id"]
        return content


class Downloader:
    sizes = {'l':'large', 'm':'medium', 's':'small', 'o':'orig', 't':'thumb'}
    # if complete is False, stop downloading upon encountering a file that's
    # already been downloaded before
    def __init__(self, user, base_dir='artists', complete=False, size='large'):
        self.complete = complete
        self.base_dir = base_dir
        self.download_dir = f"{base_dir}/{user}"
        self.total_size = 0
        self.total_count = 0
        self.size = size

    def download(self, urls):
        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)

        if not os.path.exists(self.download_dir):
            os.mkdir(self.download_dir)

        for url in urls:
            filename = url.rsplit('/', 1)[1]
            if os.path.isfile(f"{self.download_dir}/{filename}"):
                if not self.complete:
                    return True
                continue

            print(f"Downloading {url}")

            r = requests.get(f"{url}:{self.size}", allow_redirects=True)
            total_size = int(r.headers.get('content_length', 0))
            self.total_size += total_size
            self.total_count += 1
            block_size = 1024  # One 1kb
            t = tqdm(total_size, unit="iB", unit_scale=True)
            with open(f"{self.download_dir}/{filename}", 'wb') as f:
                for data in r.iter_content(block_size):
                    t.update(len(data))
                    f.write(data)
            t.close()
        return False


def main():
    user = input("Input username: ")
    size = input("Download image size:\n"
                 "  - [l]arge \n"
                 "  - [m]edium\n"
                 "  - [s]mall \n"
                 "  - [o]rig  \n"
                 "  - [t]humb \n").strip()
    if size in Downloader.sizes:
        size = Downloader.sizes[size]
    
    if size not in Downloader.sizes.values():
        print("Invalid size, using 'large' instead.")
        size = "large"

    try:
        sc = Scrape(user)
    except RuntimeError as e:
        print(e.args[0])
        return

    dl = Downloader(user, complete=True, size=size)

    while (content := sc.get_next()):
        if "includes" not in content:
            continue
        image_urls = (t["url"] for t in content["includes"]["media"])
        stop = dl.download(image_urls)
        if stop:
            break

    print(
        f"Finished downloading {dl.total_count} files ({dl.total_size/1024**2:.2} mb)")


if __name__ == '__main__':
    main()
