# Python 3.11 ベースのランタイムイメージ
FROM python:3.11.2-slim AS runtime

# 作業ディレクトリを設定
WORKDIR /app

# ビルドプラットフォームのチェックを行い、amd64 か arm64 に応じて分岐
ARG TARGETPLATFORM

# 必要な依存パッケージをインストール
RUN apt-get update && \
    apt-get install -y cmake make build-essential libopenblas-dev git pkg-config libgomp1 && \
    apt-get clean

# Pythonの依存関係をインストール
# - ARM64の場合はバイナリホイールを使用
# - AMD64の場合はソースからビルド
COPY requirements.txt .
RUN if [ "$TARGETPLATFORM" = "linux/arm64" ]; then \
        pip install --no-cache-dir -r requirements.txt --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu; \
    elif [ "$TARGETPLATFORM" = "linux/amd64" ]; then \
        CMAKE_ARGS="-DGGML_OPENMP=ON -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS -DCMAKE_EXE_LINKER_FLAGS='-lpthread -Wl,--no-as-needed -pthread'" pip install --no-cache-dir -r requirements.txt; \
    fi

# llama-cpp-python のインストールディレクトリに libllama.so が存在するので、LD_LIBRARY_PATH を設定
# 未定義の際は LD_LIBRARY_PATH のデフォルト値を空にする
RUN export LD_LIBRARY_PATH=/usr/local/lib/python3.11/site-packages/lib64:${LD_LIBRARY_PATH:-}
# 永続的に環境変数を設定するために ENV を使用する
ENV LD_LIBRARY_PATH="/usr/lib:${LD_LIBRARY_PATH}"

# アプリケーションのソースコードをコピー
COPY . /app

# エントリーポイントを設定
CMD ["python", "app.py"]
