let intervalId;
let responseDiv;
let button;

// 「考え中」アニメーションを開始
function startLoadingAnimation() {
    responseDiv.innerHTML = '';  // クリア
    let toggle = true;
    intervalId = setInterval(() => {
        responseDiv.innerHTML = toggle ? '●' : '○';
        toggle = !toggle;
    }, 500);  // 500msごとに+と-を切り替え
}

// アニメーションを終了
function stopLoadingAnimation() {
    clearInterval(intervalId);  // アニメーションを停止
}

// ストリーミングレスポンスの処理
function startStream() {
    responseDiv = document.getElementById('response');
    button = document.getElementById('submitButton');

    // 送信ボタンを無効化
    button.disabled = true;

    // 「考え中」アニメーション開始
    startLoadingAnimation();

    const systemPrompt = document.getElementById('system_prompt').value;
    const userInput = document.getElementById('user_input').value;
    const maxTokens = parseInt(document.getElementById('max_tokens').value, 10);  // 数値に変換

    // maxTokensが正しい数値であることを確認
    if (isNaN(maxTokens)) {
        responseDiv.innerHTML = "トークンの最大数は数値でなければなりません。";
        stopLoadingAnimation();
        button.disabled = false;
        return;
    }

    fetch("/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            system_prompt: systemPrompt,
            user_input: userInput,
            max_tokens: maxTokens,  // 数値として渡す
            stream: true
        })
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        function readChunk() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    stopLoadingAnimation();  // アニメーション停止
                    button.disabled = false;  // 送信ボタンを再び有効化
                    return;
                }
                stopLoadingAnimation();  // 最初のレスポンスが返ってきたらアニメーション停止
                const text = decoder.decode(value);
                responseDiv.innerHTML += text;  // 応答を追加表示
                readChunk();  // 次のチャンクを読み込み
            });
        }
        readChunk();
    }).catch(error => {
        stopLoadingAnimation();
        responseDiv.innerHTML = "エラーが発生しました。";
        button.disabled = false;
        console.error('Error:', error);
    });
}
