# main_downloader.py
from modules.downloader_narou import NarouDownloader
from modules.downloader_kakuyomu import KakuyomuDownloader
import os

def main(url):
    # サイト判別
    if "syosetu.com" in url:
        dl = NarouDownloader()
    elif "kakuyomu.jp" in url:
        dl = KakuyomuDownloader()
    else:
        print("未対応のサイトです")
        return

    # 共通のダウンロードフロー
    print("情報を取得中...")
    metadata, episodes = dl.get_novel_data(url)
    save_dir = dl.sanitize_filename(metadata['title'])
    base_dir = "novels"
    save_dir = os.path.join(base_dir, save_dir)
    
    dl.save_metadata(save_dir, metadata)
    
    for i, ep in enumerate(episodes, 1):
        print(f"[{i}/{len(episodes)}] {ep['subtitle']}")
        sub, body = dl.get_episode_data(ep)
        dl.save_episode(save_dir, i, sub, body)
    
    print(f"\n完了！フォルダ: {save_dir}")
    return metadata, save_dir

if __name__ == "__main__":
    url = input("小説のURLを入力してください: ").strip()
    main(url)