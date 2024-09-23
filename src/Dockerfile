# ベースイメージとしてPythonを使用
FROM python:3.11.2

# 作業ディレクトリを作成
WORKDIR /app

# プロジェクトのすべてのファイルをコンテナの /app にコピー
COPY . /app

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションを実行
CMD ["python", "app.py"]
