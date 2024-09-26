import os
from flask import Flask, Response, jsonify, request, stream_with_context, render_template
from llama_cpp import Llama
import threading

app = Flask(__name__)

# 環境変数から設定値を取得
model_path = os.getenv("MODEL_PATH", "/path/to/your/LLM/model")
n_threads = int(os.getenv("N_THREADS", 2))
chat_format = os.getenv("CHAT_FORMAT", "llama-3")
n_ctx = int(os.getenv("N_CTX", 512))
batch_size = int(os.getenv("BATCH_SIZE", 512))
num_workers = int(os.getenv("NUM_WORKERS", 2))
port = int(os.getenv("PORT", 5000))  # ポートもここで環境変数から取得


model_local = threading.local()
# モデルのマルチスレッド対策。インスタンスを別途取れるようにする。
def get_model():
    if not hasattr(model_local, 'llm'):
        model_local.llm = Llama(
            model_path=model_path,
            n_threads=n_threads,
            chat_format=chat_format,
            n_ctx=n_ctx,
            batch_size=batch_size,
            num_workers=num_workers,
        )
    return model_local.llm


# ストリーミングレスポンス関数
def generate_response_stream(system_prompt, user_input, max_tokens):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}]
    
    llm = get_model()
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


# 非ストリーミングレスポンス関数
def generate_response_non_stream(system_prompt, user_input, max_tokens):
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}]
    
    llm = get_model()
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
        full_response = "No response found."
    
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
        return Response(stream_with_context(generate_response_stream(system_prompt, user_input, max_tokens)), mimetype='text/html')
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
            return Response(stream_with_context(generate_response_stream(system_prompt, user_input, max_tokens)), mimetype='text/html')
        else:
            response = generate_response_non_stream(system_prompt, user_input, max_tokens)
            return response

    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True, threaded=True)
