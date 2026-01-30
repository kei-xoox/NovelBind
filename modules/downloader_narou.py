# downloader_narou.py
import requests
from bs4 import BeautifulSoup
from modules.downloader_base import BaseDownloader

class NarouDownloader(BaseDownloader):
    def get_novel_data(self, url):
        res = requests.get(url, headers=self.headers)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        # なろう特有の解析
        title = soup.select_one(".p-novel__title").get_text(strip=True)
        author = soup.select_one(".p-novel__author a").get_text(strip=True)
        ncode = url.split("/")[-2]
        
        episodes = []
        for a in soup.select(".p-eplist .p-eplist__sublist a"):
            episodes.append({
                "subtitle": a.get_text(strip=True),
                "url": "https://ncode.syosetu.com" + a["href"]
            })
        
        metadata = {"title": title, "author": author, "ncode": ncode}
        return metadata, episodes

    def get_episode_data(self, episode):
        res = requests.get(episode['url'], headers=self.headers)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        subtitle = episode['subtitle']
        content = soup.select_one(".p-novel__body") or soup.select_one("#novel_honbun")
        return subtitle, str(content)