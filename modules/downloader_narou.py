# downloader_narou.py
import requests
from bs4 import BeautifulSoup
from modules.downloader_base import BaseDownloader
import time

class NarouDownloader(BaseDownloader):
    def get_novel_data(self, url):
        # 1. 最初のページを取得
        res = requests.get(url, headers=self.headers)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        title = soup.select_one(".p-novel__title").get_text(strip=True)
        author = soup.select_one(".p-novel__author a").get_text(strip=True)
        ncode = url.split("/")[-2]
        
        episodes = []
        
        # 1ページ目のエピソードURLを比較用に記録しておく
        first_page_urls = [a["href"] for a in soup.select(".p-eplist .p-eplist__sublist a")]
        
        page_num = 1
        while True:
            current_links = soup.select(".p-eplist .p-eplist__sublist a")
            
            # ページ内にリンクがない、または2ページ目以降なのに中身が1ページ目と同じなら終了
            if not current_links:
                break
            
            current_urls = [a["href"] for a in current_links]
            if page_num > 1 and current_urls == first_page_urls:
                print("次のページはありません（1ページ目にループしました）。解析を終了します。")
                break
                
            print(f"目次ページ {page_num} を解析中...")
            for a in current_links:
                episodes.append({
                    "subtitle": a.get_text(strip=True),
                    "url": "https://ncode.syosetu.com" + a["href"]
                })
            
            # 次のページへ
            page_num += 1
            next_url = f"https://ncode.syosetu.com/{ncode}/?p={page_num}"
            
            time.sleep(1)
            res = requests.get(next_url, headers=self.headers)
            soup = BeautifulSoup(res.text, "html.parser")

        metadata = {"title": title, "author": author, "ncode": ncode}
        return metadata, episodes

    def get_episode_data(self, episode):
        res = requests.get(episode['url'], headers=self.headers)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        subtitle = episode['subtitle']
        content = soup.select_one(".p-novel__body") or soup.select_one("#novel_honbun")
        return subtitle, str(content)