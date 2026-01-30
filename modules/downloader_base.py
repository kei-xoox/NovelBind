# downloader_base.py
import os
import json
import re
from abc import ABC, abstractmethod

class BaseDownloader(ABC):
    def __init__(self, headers=None):
        self.headers = headers or {"User-Agent": "Mozilla/5.0"}

    @abstractmethod
    def get_novel_data(self, url):
        """サイトごとの解析を行い、メタデータと全話のURLリストを返す"""
        pass

    @abstractmethod
    def get_episode_data(self, episode):
        """各話のページを解析し、サブタイトルと本文(HTML)を返す"""
        pass

    def sanitize_filename(self, filename):
        return re.sub(r'[\\/:*?"<>|]', '', filename)

    def save_metadata(self, base_dir, metadata):
        os.makedirs(base_dir, exist_ok=True)
        with open(f"{base_dir}/metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

    def save_episode(self, base_dir, index, subtitle, html_content):
        raw_dir = os.path.join(base_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)
        filename = f"{index:03d}.html"
        path = os.path.join(raw_dir, filename)
        
        # 共通の整形（ルビ変換など）をここに入れても良い
        final_html = f"<h2>{subtitle}</h2>\n{html_content}"
        with open(path, "w", encoding="utf-8") as f:
            f.write(final_html)