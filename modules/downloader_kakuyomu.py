# site_kakuyomu.py
import requests
from bs4 import BeautifulSoup
import json
from modules.downloader_base import BaseDownloader
import re

class KakuyomuDownloader(BaseDownloader):
    def get_novel_data(self, url):
        res = requests.get(url, headers=self.headers)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")

        # タイトルと著者（タイトルタグから抽出：一番確実）
        full_title = soup.title.string if soup.title else ""
        # 「タイトル（著者名） - カクヨム」という形式から抽出
        title = re.sub(r'（.+） - カクヨム$', '', full_title).strip()
        author_match = re.search(r'（(.+?)）', full_title)
        author = author_match.group(1) if author_match else "不明な著者"
        
        novel_id = url.split("/")[-1]
        episodes = []

        # HTML全体を文字列として取得
        html_text = res.text
        
        # エピソードのIDとタイトルをペアで探すパターン
        # JSON内の {"__typename":"Episode","id":"数字","title":"タイトル"} を狙い撃ち
        pattern = r'\{"__typename":"Episode","id":"(\d+)","title":"(.+?)"'
        matches = re.findall(pattern, html_text)

        seen_ids = set()
        for ep_id, ep_title in matches:
            if ep_id not in seen_ids:
                try:
                    # 1. まず \uXXXX 形式を文字として解釈
                    # 2. それを latin-1 でバイトに戻し、utf-8 で正しくデコードし直す
                    decoded_title = ep_title.encode('utf-8').decode('unicode-escape').encode('latin-1').decode('utf-8')
                except Exception:
                    # 上記で失敗する場合は、シンプルにデコードを試みる
                    try:
                        decoded_title = ep_title.encode().decode('unicode-escape')
                    except:
                        decoded_title = ep_title # 最悪そのまま

                episodes.append({
                    "subtitle": decoded_title,
                    "url": f"https://kakuyomu.jp/works/{novel_id}/episodes/{ep_id}"
                })
                seen_ids.add(ep_id)

        print(f"確認：{len(episodes)} 話のエピソードを検出しました。")
        
        metadata = {"title": title, "author": author, "id": novel_id}
        return metadata, episodes

    def get_episode_data(self, episode):
        res = requests.get(episode['url'], headers=self.headers)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        # サブタイトル取得
        subtitle_tag = soup.select_one(".widget-episodeTitle") or soup.find("h1")
        subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else "無題"

        # 本文要素の取得
        content_element = soup.select_one(".widget-episodeBody")
        if not content_element:
            return subtitle, ""

        # --- 本文のクレンジング ---
        html_str = str(content_element)
        
        # 1. 各行のID属性 (id="L123") を削除して軽量化
        html_str = re.sub(r' id="L\d+"', '', html_str)
        
        # 2. カクヨム独自の傍点記法 《《傍点》》 を emタグに変換（昨日の分）
        html_str = re.sub(r'《《(.+?)》》', r'<em class="bouten">\1</em>', html_str)

        # 3. 空のクラス属性などを削除
        html_str = html_str.replace(' class="js-vertical-composition-item"', '')
        
        return subtitle, html_str
    