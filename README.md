# novel2epub

このツールは、指定されたオンライン小説（なろう、カクヨム）をダウンロードし、EPUB形式に変換するためのPythonスクリプトです。

## 機能

- なろう (syosetu.com) およびカクヨム (kakuyomu.jp) から小説をダウンロード
- 保存されたHTMLファイルからEPUB形式の電子書籍を生成
- 縦書き表示対応

## 使い方

### 1. 依存関係のインストール

以下のコマンドを実行して、必要なライブラリをインストールしてください。

```bash
pip install -r requirements.txt
```

### 2. 小説のダウンロードとEPUB変換

`main.py` スクリプトを実行し、プロンプトに従って小説のURLを入力してください。

```bash
python main.py
```

または、コマンドライン引数としてURLを直接指定することもできます。

```bash
python main.py "https://ncode.syosetu.com/nxxxxxx/"
```

スクリプトは以下の処理を自動で行います。

1. 指定されたURLから小説の情報をダウンロードし、`novels/` ディレクトリ内に保存します。
2. ダウンロードされた小説データを使用してEPUBファイルを生成し、カレントディレクトリに保存します。

### 3. ダウンロードのみ行う (オプション)

ダウンロードのみ行い、EPUB作成を行わない場合は、`main_downloader.py` を直接実行てください。

```bash
python main_downloader.py
```

### 4. EPUBファイルの再変換 (オプション)

すでにダウンロード済みの小説フォルダから再度EPUBファイルを作成したい場合は、`epub_converter.py` を直接実行し、小説が保存されているフォルダのパスを指定してください。

```bash
python epub_converter.py
```

## プロジェクト構造

- `main.py`: メインの実行スクリプト。ダウンロードとEPUB変換のワークフローを管理します。
- `main_downloader.py`: 小説のダウンロード処理を管理します。
- `epub_converter.py`: ダウンロードされたHTMLファイルからEPUBファイルを生成します。
- `modules/`: ダウンローダーの基底クラス、サイトごとのダウンローダークラス、CSSファイルが含まれます。
  - `modules/downloader_base.py`: ダウンローダーの基底クラス。
  - `modules/downloader_narou.py`: なろう小説用のダウンローダークラス。
  - `modules/downloader_kakuyomu.py`: カクヨム小説用のダウンローダークラス。
  - `modules/style.css`: EPUBに適用されるCSSスタイルシート。
- `requirements.txt`: プロジェクトの依存関係を定義します。
- `novels/`: ダウンロードされた小説データが保存されるディレクトリ。

## 開発者向け情報

- コードはPython 3.x で動作します。
- 新しい小説サイトに対応する場合は、`modules/downloader_base.py` を継承して新しいダウンローダークラスを作成し、`main_downloader.py` にそのサイトの判別ロジックを追加してください。
- EPUBのスタイルや整形に関する詳細な調整は `modules/style.css` および `epub_converter.py` 内の整形関数 (`_compress_empty_lines`, `_apply_tcy_formatting`) で行えます。

## 免責事項

本ツールは個人利用を目的として作成されています。ダウンロードしたコンテンツの取り扱いについては、各サイトの利用規約および著作権法を遵守してください。本ツールを使用したことによるいかなる損害についても、作者は一切の責任を負いません。

---

※記載されている会社名、製品名、サイト名は各社の登録商標または商標です。
