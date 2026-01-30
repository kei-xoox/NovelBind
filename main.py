import os
import sys
import main_downloader
from epub_converter import create_epub 

def main():
    # 1. 既存のダウンローダーのメイン処理を実行
    print("=== Step 1: ダウンロードを開始します ===")

    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"引数からURLを読み込みました: {url}")
    else:
        url = input("小説のURLを入力してください: ").strip()

    if not url:
        print("URLが指定されていません。終了します。")
        return
    
    metadata, save_dir = main_downloader.main(url)
    
    # 2. 保存されたフォルダが存在するか確認してEPUB化
    if save_dir and os.path.exists(save_dir):
        print(f"\n=== Step 2: EPUB変換を開始します ({save_dir}) ===")
        try:
            epub_path = create_epub(save_dir)
            print(f"\n✨ 正常に完了しました！")
        except Exception as e:
            print(f"\n❌ EPUB変換中にエラーが発生しました: {e}")
    else:
        print("\n❌ ダウンロードが正常に完了しなかったか、フォルダが見つかりません。")

if __name__ == "__main__":
    main()