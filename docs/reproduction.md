# 再生成とファイルの扱い

## 環境

現在のSTEPはCadQuery 2.8.0で生成しています。保存プレビューはBlender 4.5.9を使用しています。Python依存の固定バージョンは[Rev L requirements](../revisions/L/cad/requirements.txt)を参照してください。動作確認環境はUbuntu・Python 3.12です。

```bash
python3 -m venv .venv
.venv/bin/pip install -r revisions/L/cad/requirements.txt
```

画像の日本語ラベルにはNoto Sans CJKのフォントが必要です。6面画像の合成ソースはLinuxの標準フォントパスを使用しています。別のOSではフォントパスを環境に合わせて変更します。

## Rev LのCAD再生成

```bash
.venv/bin/python revisions/L/cad/build_bridge.py
.venv/bin/python revisions/L/cad/verify_travel.py
```

部品STEP・組立STEP・プレビュー用STL・scene manifest・検証JSONが`revisions/L/cad/`以下に生成されます。`parameters.json`は設計値の一覧ですが、寸法の一部は生成コード内にもあります。全寸法が自動連動するパラメトリックモデルではありません。形状変更時にはコード・図面・金物選択を合わせて更新します。

保存STEPを生成し直さず検査する場合は、`build_bridge.py --verify-existing`で、現行ソースから作るB-repとの一致と9条件の機能確認を行えます。

## プレビューと加工資料

```bash
blender --background --python-exit-code 1 --python revisions/L/cad/render_bridge.py
blender --background --python-exit-code 1 --python revisions/L/cad/render_ball_cradle.py
blender --background --python-exit-code 1 --python revisions/L/cad/render_six_views.py
.venv/bin/python revisions/L/cad/compose_six_views.py
.venv/bin/python revisions/L/cad/make_documents.py
.venv/bin/python revisions/L/cad/package_outputs.py
```

CAD生成→通常プレビュー→6面プレビュー→画像合成→PDF/部品表→パッケージの順で実行します。`render_six_views.py`は通常プレビューで保存するBlenderモデルを読みます。生成後はPDFの全ページをレンダーし、図・寸法・文字の重なりと、STEPと同じ改訂になっていることを目視確認します。

再生成したZIPは`revisions/L/`以下にできます。トップレベルの`downloads/`は公開用に保存したコピーなので、自動で差し替わりません。変更を配布する場合は対応ZIPをコピーし、資料・保存ファイルのチェックサムを更新してからコミットします。加工形状を変える場合は、新しい改訂として記録することを推奨します。

## 歴史的版

各版は独立した`revisions/<版>/cad/build_bridge.py`と`parameters.json`を持ちます。その版の`requirements.txt`を使用します。過去READMEの相対パスや元の配布名は当時の記録です。現在は`output_revH/...`ではなく`revisions/H/...`を使用します。

Rev HのA06加工図はRev Gから変更せず流用したため、図面の版表示がRev Gです。Rev LはB10/A10双方の新しい図面を持ちます。保存PDFを最新版と混ぜないでください。

## 開発一覧画像

```bash
python3 tools/make_revision_overview.py
```

各版の保存PNGをそのまま配置し、日本語説明を加えたSVGレイアウトを作ります。Ubuntuのlibrsvg・Cairo・Noto Sans CJKを使用してPNGへ描画します。画像の形状を生成AIで描き直す処理はありません。

## 資料の整合性確認

```bash
python3 tools/check_repository.py
```

このチェックは標準ライブラリだけで実行できます。リンクと配布物の整合性を確認し、加工可否や実物の強度判定は行いません。
