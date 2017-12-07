先從簡單的開始。一個 Django 網站的 deployment 包含以下項目：

1. Django、你的網站程式碼、第三方套件。
2. 靜態檔（static files）。在 Django 中這代表所有你的網站有用到，但不是 Python 程式與 templates 的檔案，例如圖片、CSS、JavaScript 檔案等等。
3. 媒體檔（media files）。在 Django 中這代表在網站執行時動態產生的非程式檔案，例如使用者上傳的照片。
4. WSGI HTTP 伺服器，用來執行 Python 程式。
5. 檔案 HTTP 伺服器，用來 serve static 與 media files。
6. HTTP 伺服器，用來作為 WSGI 與檔案伺服器的統一入口。在比較小的網站中，這可以和檔案 HTTP 伺服共用同一個伺服器程式。

我們這裡從簡單的開始：Heroku。

Heroku 已經提供 HTTP 伺服器功能，而且本身不支援檔案上傳（當然你可以選擇把檔案伺服架在其他服務上，不過這邊先不談），所以我們不需要管 3 和 6，5 的設定也只要做一半。

對了，你必須安裝 Git 與 Heroku Toolbelt。在遙遠的第一章裡有個安裝教學連結，如果你當初照著做，應該就已經有了。如果沒有，現在把它們裝起來。

首先我們要讓 Heroku 使用 Python。建立一個檔案 `runtime.txt`，內容只有一行：

```
python-3.4.2
```

這個檔案必須被放在專案的最上層，也就是與你的 apps（`base`、`stores` 等等）同一層。

接著要告訴 Heroku 必須裝哪些東西。Heroku 使用 PIP 的 requirements file 格式，所以我們可以在專案頂層用下面的指令快速匯出目前使用的套件：

```bash
pip freeze > requirements.txt
```

打開產生的 `requirements.txt`，在最後面加入下面這行：

```
django-toolbelt
```

這個套件包含所有 Heroku 需要的額外套件，包括：

* Django（這我們其實上面有列了，不過沒關係）
* Gunicorn（WSGI server）
* DJ-Static（靜態檔伺服）
* dj-database-url 與 Psycopg2

其中最後兩個是 Heroku 專用套件。Heroku 不支援檔案伺服，但是我們可以藉由 DJ-Static，用 WSGI 伺服模擬一個。最後一項則是用來存取資料庫；Heroku 使用 PostgreSQL，所以必須安裝它的 Python binding——Psycopg2，dj-database-url 則可以方便我們設定資料庫的參數。

再來，告訴 Heroku 要怎麼執行這個網站。同樣在頂層目錄，建立 `Procfile`（注意沒有副檔名！）：

```
web: gunicorn lunch.wsgi --log-file -
```

這裡我們使用 `gunicorn` 這個 WSGI server，要求執行 WSGI 程式。後面的參數代表把 error log 輸出至 stderr，這樣才能讓這些 logs 被 Heroku 紀錄。

很久很久以前我們提過，開發機與部署時會需要不同的設定。我們要為 Heroku 增加一個設定檔：

```python
# lunch/settings/deploy_heroku.py

from .base import *     # noqa
import dj_database_url

# 把 debug 模式關掉。
DEBUG = False

# 設定 secret key。
SECRET_KEY = get_env_var('DJANGO_SECRET_KEY')

# 尊重 HTTPS 連線中的 "X-Forwarded-Proto" header。
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 設定靜態檔位置。
STATIC_ROOT = 'static'

# 設定資料庫。
DATABASES = {
    'default': dj_database_url.config()
}

# 允許所有網址連至本網站。
ALLOWED_HOSTS = ['*']
```

如果你看不懂其中某些設定，沒關係，只要先記得這樣設就可以了。其中有些設定是專為 Heroku 設定的，但大部份我們之後都會再解釋。

注意上面我們用到了一個 function `get_env_var`。我們要在 `lunch/settings/base.py` 定義它：[註 1]

```python
from django.core.exceptions import ImproperlyConfigured

def get_env_var(key):
    try:
        return os.environ[key]
    except KeyError:
        raise ImproperlyConfigured(
            'Environment variable {key} required.'.format(key=key)
        )
```

最後修改 `lunch/wsgi.py`，啟用 DJ-Static：

```python
# lunch/wsgi.py

import os
from django.core.wsgi import get_wsgi_application
from dj_static import Cling

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lunch.settings")
application = Cling(get_wsgi_application())     # 注意這一行。
```

這樣就準備完成了！接著是建立 Git repository。你可能會想要先建立一個 `.gitignore` 檔案（同樣放在最頂層，和 `requirements.txt` 一起）：

```
*.py[co]
__pycache__

.env
```

然後執行指令：

```bash
git init
git add .
git commit -m "Make it so"
```

接下來我們要在 Heroku 建立一個 instance，好把我們的程式上傳。先到 <http://heroku.com/> 註冊一個帳號。註冊認證完成後，你應該會進入你的 Heroku dashboard。接著在終端機登入你的 Heroku 帳號：

```bash
heroku login
```

如果你是第一次登入，系統會要求上傳一個 SSH public key。請直接允許。

接著建立 project：

```bash
heroku create <project_name>
```

名稱可以隨意取，之後這就會顯示在你的網站網址裡（不過如果有人用過這個名稱就不能再用，所以還滿容易撞名）；如果你留白，Heroku 會隨機幫你取一個很電波的名字。

然後用 Git Push 上傳整個 respository：（這應該會跑一段時間）

```bash
git push heroku master
```

再建立一個 instance：

```bash
heroku ps:scale web=1
```

接著我們要設定 secret key 用到的環境變數，以及設定檔的位置。你可以自己產生一個字串來當成 secret key，或者如果不知道怎麼產生，請參考 <https://djskgen.herokuapp.com/>。

這樣設定：

```bash
heroku config:set DJANGO_SECRET_KEY=<your_secret_key>
heroku config:set DJANGO_SETTINGS_MODULE=lunch.settings.deploy_heroku
```

注意 shell 中某些字元會被視為 escape sequence，所以你可能會需要用單引號把 secret key 包起來。如果你搞不定，其實 Heroku 網頁上也有地方可以設。

接著重跑 migration，讓遠端的資料庫與我們之前的設定相符：

```bash
heroku run python manage.py migrate
```

如果你想在 Heroku 上執行某些指令，只要在原本的指令前面加上 `heroku run` 即可。你也可以用一樣的方法建立 superuser：

```bash
heroku run python manage.py createsuperuser
```

這樣就搞定了！打開你的網站看看：

```bash
heroku open
```

以上是最簡單的 deploy 設定，實務上還有一些可以改的東西，例如[有人建議](http://blog.etianen.com/blog/2014/01/19/gunicorn-heroku-django/)用 [Waitress](https://github.com/Pylons/waitress) 取代 Gunicorn（我個人也推薦用這個），或者有人習慣用 [Whitenoise](http://whitenoise.evans.io/en/latest/) 而非 DJ-Static。不過基本上的設定都一樣。明天我們會試著把 Django deploy 到一個 Linux server 上，來看看比較進階的 deploy 設定。

---

註 1：當然其實我們可以在 `deploy_heroku.py` 定義就好，但這個 function 很有用，所以我們把它丟在頂層，未來在其他地方也可以用。
