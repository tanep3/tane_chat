
# たねちゃっと

## 1. システムの概要
[HuggingFace](https://huggingface.co/)に掲載されているLlama系のLLM（生成AIの脳みそ）を使用した、WEBチャットシステムです。Llama 3.1やELYZAといった高性能なLLMの会話推論機能をご自宅のPCで簡単に扱えるようになります。

## 2. 機能概要
- ブラウザからインストールしたサーバにアクセスしてChatGPTのように使うことができる。
- WEB-APIを使って、ご自身の作成されたアプリから使う事ができる。

## 3. インストール方法

### (1) LLMのダウンロード
お好きなLLMのggufファイル（llama.cppを使って量子化したモデル。Q4_K_Mの4ビット量子化モデルがオススメです。）を[HuggingFace](https://huggingface.co/)からダウンロードし、任意の場所に配置します。Llama系のLLMなら動作すると思います。オススメは、[ELYZA](https://huggingface.co/elyza)です。

### (2) たねちゃっとのインストール
DockerHub(`tanep/tane_chat`)に掲載しておりますので、Dockerでのインストールが簡単です。  
事前にdocker, docker-composeをインストールして下さい。

```bash
sudo apt update
sudo apt install docker docker-compose
```

1. [docker-compose.yml](docker-compose.yml) をダウンロードし、本アプリ起動用フォルダ（任意の場所）に配置します。  
   `[volumes:]` の `/LLMのggufファイルを置いているディレクトリ` を、LLMを配置した場所に書き換えます。
2. `docker-compose.yml` の環境変数 `[environment:]` の値を好みに応じて調整します。
3. 以下のコマンドで、たねちゃっとのダウンロード＆初期起動を行います。

```bash
docker-compose up -d
```

## 4. 使い方

### (1) WEBチャットとしての活用
以下のURLにアクセスして、チャット画面を開きます。  
`http://インストールしたサーバのIP:5005`

### (2) WEB-APIとしての活用

#### a. APIエンドポイント
- エンドポイント: `/generate`
- HTTPメソッド: `POST`
- リクエスト形式: `application/json`
- レスポンス形式: ストリーミングまたは一括

#### b. リクエストの構造
```json
{
  "system_prompt": "50文字程度に要約して回答してください。",
  "user_input": "AIとは何ですか？",
  "max_tokens": 512,
  "stream": true
}
```

#### c. レスポンスの構造

**(a) ストリーミングレスポンス**
- `stream: true` の場合、レスポンスは逐次送信されます。  
  - Content-Type: `text/html`

**(b) 非ストリーミングレスポンス**
- `stream: false` の場合、一括で返されます。  
  - Content-Type: `application/json`

```json
{
  "response": "AIとは、Artificial Intelligenceの略で、人間の知能を模倣する技術を指します。"
}
```

#### d. 使用例
```bash
curl -X POST -H "Content-Type: application/json" -d '{"system_prompt": "50文字程度に要約して回答してください。","user_input": "AIとは何ですか？","max_tokens": 512,"stream": true}' http://127.0.0.1:5005/generate
```

## 5. ライセンス情報
このプロジェクトはMITライセンスの下で公開されています。詳細については、[LICENSE](LICENSE) ファイルを参照してください。

## 6. 著作者
たねちゃんねる
