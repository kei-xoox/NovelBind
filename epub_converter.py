import os
import sys
import re
import json
from ebooklib import epub
from bs4 import BeautifulSoup

def compress_empty_lines(html_str):
    """
    1行のみの空行を削除し、2行以上の空行は維持する
    """
    # 1. まず、<p><br/></p> が1つだけ独立している（前後に空行がない）パターンを削除
    #    前後のタグの状態をチェックしながら置換します
    
    # なろうの空行は通常 <p><br/></p> なので、これをターゲットにします。
    # 「空行・ターゲット・空行以外」または「空行以外・ターゲット・空行」を判定して
    # 孤立した空行を消す処理です。
    
    # シンプルかつ確実な方法として、一度全ての空行を特殊記号に置き換え、
    # その連続数に応じて戻す処理を行います。
    
    # 連続する空行タグ（改行コード含む）を抽出
    pattern = r'(<p><br/></p>\s*)+'
    
    def replacer(match):
        count = match.group(0).count('<p><br/></p>')
        if count == 1:
            return ''  # 1行だけの空行は削除
        else:
            return '<p><br/></p>' * count # 2行以上はそのまま残す
            # もし2行以上に集約したいなら return '<p><br/></p>' * 2
            
    return re.sub(pattern, replacer, html_str)

def apply_upright_to_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    
    # テキストノード（人間が読む文字）だけを抽出してループ
    for text_node in soup.find_all(string=True):
        # 親タグが script や style の場合は除外（念のため）
        if text_node.parent.name in ['script', 'style']:
            continue
            
        # 半角英数字を見つける正規表現
        new_text = re.sub(r'([a-zA-Z0-9]+)', r'<span class="upright">\1</span>', text_node)
        
        # 置換が発生した場合のみ、テキストノードをHTMLとして差し替える
        if new_text != text_node:
            text_node.replace_with(BeautifulSoup(new_text, "html.parser"))
            
    # bodyの中身だけを文字列として返す
    return str(soup)

def create_titlepage(book, meta):
    # 扉用のHTMLを作成
    title_page = epub.EpubHtml(
        title='扉',
        file_name='titlepage.xhtml',
        lang='ja'
    )
    
    # コンテンツの構成
    title_page.content = f'''
        <div class="p-titlepage hltr">
            <div class="main">
                <div class="book-title">
                    <h1 class="p-titlepage__title">{meta['title']}</h1>
                </div>
                <div class="author">
                    <p class="p-titlepage__author">{meta['author']}</p>
                </div>
            </div>
        </div>
    '''
    
    # スタイルシートをリンク
    title_page.add_link(href="book-style.css", rel="stylesheet", type="text/css")
    
    return title_page

def create_epub(ncode_dir):
    metadata_path = os.path.join(ncode_dir, 'metadata.json')
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    book = epub.EpubBook()
    novel_id = meta.get('ncode') or meta.get('id') or 'unknown_id'
    book.set_identifier(novel_id)
    book.set_title(meta['title'])
    book.set_language('ja')
    book.add_author(meta['author'])
    book.set_direction('rtl')

    # 1. CSSを「EpubItem」として読み込む
    css_files = [
        'style-reset.css',
        'style-standard.css',
        'style-advance.css',
        'book-style.css'
    ]

    for css_name in css_files:
        with open(f'modules/{css_name}', 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        css_item = epub.EpubItem(
            uid=css_name.replace('.', '_'),
            file_name=f"{css_name}",
            media_type="text/css",
            content=css_content
        )
        book.add_item(css_item)

    book.add_metadata(None, 'meta', '', {'name': 'primary-writing-mode', 'content': 'horizontal-rl'})

    chapters = []
    raw_dir = os.path.join(ncode_dir, 'raw')
    raw_files = sorted([f for f in os.listdir(raw_dir) if f.endswith('.html')])

    for filename in raw_files:
        path = os.path.join(raw_dir, filename)
        with open(path, "r", encoding="utf-8") as f:
            html_content = f.read().strip()
            
        if not html_content: continue

        # --- サブタイトルの抽出 ---
        # <h2>タグの中身を探す（例: <h2>序文</h2>）
        subtitle_match = re.search(r'<h2>(.*?)</h2>', html_content)
        subtitle = subtitle_match.group(1) if subtitle_match else ""
        
        # ファイル名から話数番号を取得（例: 001.html -> 001）
        episode_num = filename.replace('.html', '')
        
        # 目次用のタイトルを整形（例: 001. 序文）
        display_title = f"{episode_num}. {subtitle}" if subtitle else f"第{episode_num}話"

        # --- HTMLの整形 ---
        # もしHTML本文内に既に<h2>が含まれているなら、二重にならないよう調整
        # (必要に応じて apply_tcy などを適用)
        processed_body = compress_empty_lines(html_content)
        processed_body = apply_upright_to_text(processed_body)  

        # EpubHtmlの作成 (titleに新しい整形済みタイトルを指定)
        chapter = epub.EpubHtml(
            title=display_title, 
            file_name=f"chap_{episode_num}.xhtml", 
            lang='ja'
        )
        
        chapter.content = f'<body class="bodymatter vrtl" epub:type="bodymatter">{processed_body}</body>'
        chapter.add_link(href="book-style.css", rel="stylesheet", type="text/css")

        book.add_item(chapter)
        chapters.append(chapter)

    # 扉ページを作成
    title_page = create_titlepage(book, meta)
    book.add_item(title_page)
    book.toc = tuple(chapters)
    book.add_item(epub.EpubNcx())

    nav_page = epub.EpubNav()
    nav_page.add_link(href="book-style.css", rel="stylesheet", type="text/css")
    nav_page.body_attrs = "class='vrtl p-text'"
    book.add_item(nav_page)
    
    book.spine = [title_page, 'nav'] + chapters
    book.page_progression_direction = 'rtl'

    output_filename = f"{meta['title']}.epub".replace(' ', '_')
    
    # 4. 書き出し
    epub.write_epub(output_filename, book, {})
    print(f"\n>>> 出力しました: {output_filename}")

    return output_filename

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
        print(f"引数からフォルダ名を読み込みました: {target_dir}")
    else:
        # ダウンロードしたフォルダパスを指定
        target_dir = input("フォルダ名を入力してください: ").strip()

    if os.path.exists(target_dir):
        create_epub(target_dir)
    else:
        print("フォルダが見つかりません。")