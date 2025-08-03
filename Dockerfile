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
EXPOSE 5000

# 必要なシステムパッケージをインストール
# curl, wget, unzip はWebDriverのダウンロードと解凍に必要
# jq はChromeDriverの最新版URLをプログラム的に取得する際に便利
# Google Chromeが動作するために必要なライブラリもインストール
# RUN apt-get update && apt-get install -y --no-install-recommends \
#    curl \
#    wget \
#    unzip \
#    jq \
    # Google Chromeの依存関係
#    libnss3 \
#    libxss1 \
#    libappindicator3-1 \
#    fonts-liberation \
#    libasound2 \
#    libatk-bridge2.0-0 \
#    libatk1.0-0 \
#    libcairo2 \
#    libcups2 \
#    libdbus-1-3 \
#    libdrm2 \
#   libegl1 \
#    libgbm1 \
#    libgdk-pixbuf2.0-0 \
#    libgl1 \
#    libnspr4 \
#    libnss3 \
#    libxcomposite1 \
#    libxdamage1 \
#    libxext6 \
#    libxfixes3 \
#    libxkbcommon0 \
#    libxrandr2 \
#    libxshmfence6 \
#    libxtst6 \
#    xdg-utils \
    # その他の基本的なビルドツールなど（必要であれば）
#    build-essential \
#    && rm -rf /var/lib/apt/lists/*

# Google Chrome（ブラウザ本体）をインストール
# 最新版の安定版Chromeをインストールするための公式リリポジトリを追加
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# ChromeDriverのインストール
# Googleの "Chrome for Testing" APIを使って、インストールされたChromeバージョンに対応する最新のChromeDriverを動的に取得します。
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') \
    && echo "Detected Chrome version: ${CHROME_VERSION}" \
    && CHROMEDRIVER_URL=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | \
       jq -r ".channels.Stable.downloads.chromedriver[] | select(.platform == \"linux64\") | .url") \
    && if [ -z "$CHROMEDRIVER_URL" ]; then echo "Error: Could not find ChromeDriver download URL."; exit 1; fi \
    && echo "Downloading ChromeDriver from: ${CHROMEDRIVER_URL}" \
    && wget -q --continue -P /tmp/ "${CHROMEDRIVER_URL}" \
    && unzip "/tmp/$(basename "${CHROMEDRIVER_URL}")" -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    # && chmod +x /usr/local/bin/chromedriver \
    && echo "ChromeDriver installed to /usr/local/bin/chromedriver"

# コンテナ起動時のコマンド (Gunicorn を使用)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]