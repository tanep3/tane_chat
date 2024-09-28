import os
from flask import Flask, Response, jsonify, request, stream_with_context, render_template
from llama_cpp import Llama
import threading
import logging
from queue import Queue

app = Flask(__name__)

# 環境変数から設定値を取得
model_path = os.getenv("MODEL_PATH", "/path/to/your/LLM/model")
n_threads = int(os.getenv("N_THREADS", 2))
chat_format = os.getenv("CHAT_FORMAT", "llama-3")
n_ctx = int(os.getenv("N_CTX", 512))
batch_size = int(os.getenv("BATCH_SIZE", 512))
num_workers = int(os.getenv("NUM_WORKERS", 1))
port = int(os.getenv("PORT", 5000))  # ポートもここで環境変数から取得
max_instances = int(os.getenv("MAX_INSTANCES", 2))  # インスタンスプールの最大数（デフォルトは2）

# ログの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# インスタンスプールの設定
llm_pool = Queue(maxsize=max_instances)

def initialize_llm_instances():
    """
    LLMのインスタンスを複数つくり、プールさせて運用することでレスポンスを向上させる。
    初期インスタンスをプールに作成して追加します。
    """
    print("俺様！！起動したぜ！！")
    for i in range(max_instances):
        try:
            llm = Llama(
                model_path=model_path,
                n_threads=n_threads,
                chat_format=chat_format,
                n_ctx=n_ctx,
                batch_size=batch_size,
                num_workers=num_workers,
            )
            llm_pool.put(llm)
            logger.info(f"Llamaモデルインスタンス {i+1}/{max_instances} をプールに追加しました。")
        except Exception as e:
            logger.error(f"Llamaモデルインスタンスの初期化に失敗しました: {e}")

# アプリケーション起動時にインスタンスプールを初期化
initialize_llm_instances()

def acquire_llm_instance(timeout=120):
    """
    インスタンスプールからLLMインスタンスを取得します。
    他の人が使用中の場合は、終了するまで待ちます。
    """
    try:
        llm = llm_pool.get(timeout=timeout)
        return llm
    except Exception as e:
        logger.error(f"プールからLlamaインスタンスの取得に失敗しました: {e}")
        return None

def release_llm_instance(llm):
    """使用後にLLMインスタンスをプールに返却します。"""
    try:
        llm_pool.put(llm)
    except Exception as e:
        logger.error(f"Llamaインスタンスのプールへの返却に失敗しました: {e}")


# ストリーミングレスポンス関数
def generate_response_stream(system_prompt, user_input, max_tokens):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}]
    
    llm = acquire_llm_instance()
    if not llm:
        yield "Error: しばらく時間をおいてから、もう一度お試し下さい。"
        return
    try:
        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            stream=True
        )
        
        for chunk in response:
            if "content" in chunk["choices"][0]["delta"]:
                content = chunk["choices"][0]["delta"]["content"]
                yield content
    except Exception as e:
        logger.error(f"LLMストリーミング処理中にエラーが発生しました: {e}")
        yield "Error: LLMストリーミング処理中にエラーが発生しました。"
    finally:
        release_llm_instance(llm)

# 非ストリーミングレスポンス関数
def generate_response_non_stream(system_prompt, user_input, max_tokens):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}]
    
    llm = acquire_llm_instance()
    try:
        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.95,
            stream=False
        )
        
        # "choices" 内の "message" -> "content" を取得
        choices = response.get("choices", [])
        if choices:
            full_response = choices[0]["message"]["content"]
        else:
            full_response = {
                "response": "応答が見つかりませんでした。"
            }
    except Exception as e:
        logger.error(f"LLMの処理中にエラーが発生しました: {e}")
        full_response = {
            "response": "LLMの処理中にエラーが発生しました。"
        }
    finally:
        release_llm_instance(llm)

    return full_response


# Flaskのエンドポイント
@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    system_prompt = data.get("system_prompt", "")
    user_input = data.get("user_input", "")
    
    try:
        max_tokens = int(data.get("max_tokens", 256))
    except ValueError:
        return jsonify({"error": "max_tokens must be an integer"}), 400

    # リクエストからストリームフラグを取得し、TrueまたはFalseにキャスト
    stream = data.get("stream", False)
    if isinstance(stream, str):
        stream = stream.lower() == 'true'  # 文字列として 'true' が来る可能性があるので対処

    if stream:
        return Response(stream_with_context(generate_response_stream(system_prompt, user_input, max_tokens)), mimetype='text/plain')
    else:
        response = generate_response_non_stream(system_prompt, user_input, max_tokens)
        return jsonify({"response": response})


# ホームエントリーポイントの追加
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        system_prompt = request.form.get("system_prompt")
        user_input = request.form.get("user_input")
        max_tokens = int(request.form.get("max_tokens", 256))

        stream = request.form.get("stream") == "on"
        if stream:
            return Response(stream_with_context(generate_response_stream(system_prompt, user_input, max_tokens)), mimetype='text/plain')
        else:
            response = generate_response_non_stream(system_prompt, user_input, max_tokens)
            return response

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
