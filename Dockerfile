# ベースイメージの指定
FROM python:3.9-slim-buster

# 環境変数の設定
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係ファイル (requirements.txt) をコピーし、インストール
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポートの公開
EXPOSE 8080

# コンテナ起動時のコマンド (Gunicorn を使用)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]