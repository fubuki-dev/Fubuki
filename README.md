![logo](/assets/logo.png)
# Fubuki: Next generation hybrid web framework

Fubuki is a ASGI-based hybrid web framework that combines the simplicity of Flask with the power of Django to provide a new standard for web development.

Fubukiは、シンプルで柔軟なハイブリッドWebフレームワークです。軽量でありながら強力な機能を提供し、迅速な開発をサポートします。FubukiはLaravelから影響を受けた機能を持ちつつ、ルーティングなどの部分ではFlaskライクな使いやすさを提供します。また、ルート部分で正規表現をサポートし、引数に格納することができます。

## 特徴

- シンプルで直感的なAPI
- ミドルウェアのサポート
- 静的ファイルの提供
- テンプレートエンジンのサポート
- 効率的なルーティング
- ハイブリッドなアーキテクチャで柔軟な開発が可能
- Laravelから影響を受けた機能
- Flaskライクな使いやすいルーティング
- 正規表現をサポートし、ルート引数に格納可能

## インストール

Fubukiをインストールするには、以下のコマンドを使用します。

```sh
pip install fubuki
```

## 使用方法

### プロジェクトの作成

新しいFubukiプロジェクトを作成するには、以下のコマンドを実行します。

```sh
fubuki create_project <project_name>
```

### ディレクトリ構成

新しいプロジェクトのディレクトリ構成は以下の通りです。

```
<project_name>/
├── app/
│   ├── __init__.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── home_controller.py
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── logging_middleware.py
│   ├── static/
│   │   └── styles.css
│   ├── templates/
│   │   └── welcome.html
│   ├── routes.py
├── cli.py
├── app.py
└── main.py
```

### コントローラの追加

コントローラを追加するには、`app/controllers`ディレクトリに新しいPythonファイルを作成し、以下のようにルートを定義します。

```python
from fubuki import Controller, route

class MyController(Controller):
    @classmethod
    @route("/my_path")
    async def my_route(cls, scope, receive, send):
        response = {
            "status": 200,
            "body": "Hello, World!"
        }
        return response
```

### 正規表現を使用したルート

Fubukiでは、Flaskのようにルートで正規表現を使用し、引数に格納することができます。

```python
from fubuki import Controller, route

class UserController(Controller):
    @classmethod
    @route("/user/<int:user_id>")
    async def get_user(cls, user_id, scope, receive, send):
        response = {
            "status": 200,
            "body": f"User ID: {user_id}"
        }
        return response
    
    @classmethod
    @route("/post/<regex('^[a-z0-9_-]{3,16}$'):post_slug>")
    async def get_post(cls, post_slug, scope, receive, send):
        response = {
            "status": 200,
            "body": f"Post Slug: {post_slug}"
        }
        return response
```

### ミドルウェアの追加

ミドルウェアを追加するには、`app/middlewares`ディレクトリに新しいPythonファイルを作成し、以下のようにミドルウェアを定義します。

```python
class MyMiddleware:
    async def __call__(self, scope, receive, send, next_handler):
        # 前処理
        print("Before request")
        
        # 次のミドルウェアまたはハンドラを呼び出し
        response = await next_handler(scope, receive, send)
        
        # 後処理
        print("After request")
        
        return response
```

### アプリケーションの設定

アプリケーションにコントローラとミドルウェアを追加するには、`app.py`を編集します。

```python
from app import App
from app.routes import setup_routes
from app.middlewares.my_middleware import MyMiddleware

app = App()
setup_routes(app)

# ミドルウェアの追加
app.add_middleware(MyMiddleware)
```

### アプリケーションの実行

アプリケーションを実行するには、`main.py`を実行します。

```sh
python main.py
```

## 貢献

貢献を歓迎します！バグ報告、機能リクエスト、プルリクエストはGitHubのリポジトリで受け付けています。

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。詳細については、[LICENSE](LICENSE)ファイルを参照してください。

## 作者

- 名前: AmaseCocoa
- Fediverse: [@AmaseCocoa@misskey.io](https://misskey.io/@AmaseCocoa)