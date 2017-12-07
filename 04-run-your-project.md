我們昨天解釋了 `django-admin` 為你產生的專案架構。今天我們要把架構中缺少的設定補上，讓這個專案能夠執行。下面是我們的專案架構，以防你忘記了（從現在起我會省略一些無關的檔案，只關注我們會手動修改的程式）：

```
lunch
├── lunch
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

首先我們打開 `lunch/lunch/settings.py`，解釋一下各設定的用途。

## Django 的設定值

所有的全域變數都是用**大寫與底線**構成。這是 Django 設定的命名慣例。我們忽略其他東西（註釋和 `import` 等等），來看看這些設定的用途。

### `BASE_DIR`

這個設定代表專案的根目錄。預設是

```python
os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

亦即「這個檔案的外層的外層」，也就是上面那個樹狀圖的第一個 `lunch`。

### `SECRET_KEY`

這是 Django 用來加密資訊的重要變數。Django 會用它來加密你的 session 內容、處理 cookie 值、以及管理資料庫裡的帳號密碼等等。因為這可以用來推出很多敏感資訊，所以非常重要。

預設值是 Django 隨機產生的。你可以直接使用，也可以自己產生一組。如果不知道怎麼產生，有個網頁 <https://djskgen.herokuapp.com/> 還滿好用的，可以參考。

### `DEBUG`

如果設為 `True`，則 Django 會在遇到錯誤時顯示各式各樣的錯誤訊息，協助你找到問題。所以通常我們在正式開站前要設成 `False`，不然就會和某市長候選人的官方網站一樣被[嘲笑](http://debug-guy-blog.logdown.com/posts/222620-taipeihope-ggininder)。

我們在網站上線時要把 `DEBUG` 關掉。可是在開發時，我們當然想看完整的錯誤訊息。所以這兩個環境的設定不能一樣。可是如果我們每次都在要上線時才改設定，肯定遲早會忘記，然後就像某團隊一樣出包。為了避免這個狀況，我們通常我們會有至少兩個設定檔：一個開發用，一個部署用。[註 1]

為了方便管理這些設定檔，我們建議把它們通通丟到一個 `settings` 模組裡。所以我們在原本 `settings.py` 的位置創建一個目錄，叫做 `settings`，然後把 `settings.py` 丟進去，並改名為 `base.py`。然後在 `settings` 目錄裡多建立三個空白檔案：`__init__.py`、`local.py`、`production.py`。

現在你的專案目錄應該會長這個樣子：

```
lunch
├── lunch
│   ├── __init__.py
│   ├── settings
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
└── manage.py
```

`settings` 裡面除了 `__init__.py` 之外的三個檔案的作用會是：

* `base.py`：用來存放所有設定中共通的部分。
* `local.py`：本機（開發機）用的設定。
* `production.py`：正式部署到 production server 時用的設定。

接著我們把 `local.py` 的內容改成這樣：

```python
from .base import *

SECRET_KEY = '某個產生的 secret key 值，請自行代換'
DEBUG = True
```

然後把 `base.py` 裡的這三個設定刪掉。我們之後在本機開發時，就會改用這個檔案，而不是原本的 `settings.py`。

由於設定檔換位置了，我們就得再改一個參數。打開 `base.py`，把 `BASE_DIR` 改成這樣：

```python
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
)))
```

因為我們把設定檔拿進了一層（原本是 `lunch/settings.py`，現在是 `lunch/settings/local.py`），所以這個路徑要多往外跳一層才會正確。

接著我們還要告訴 Django 我們的設定檔已經換位置了。如果你還記得昨天的內容，Django 是用 `DJANGO_SETTINGS_MODULE` 這個環境變數來檢查設定檔位置。

我們可以每次在執行指令時，從命令列設定環境變數設，不過這樣執行環境每次重開終端機都會重設，很不方便。所以接下來我們要用 Pipenv 附帶的 [Dotenv](https://github.com/theskumar/python-dotenv) 功能，在我們執行指令時自動載入環境變數。在專案根目錄（最外層的 `lunch` 目錄，與 `Pipfile` 同層）建立一個叫 `.env` 的檔案，包含下面這行：

```bash
DJANGO_SETTINGS_MODULE=lunch.settings.local
```

就可以確保你每次執行 `pipenv run` 時，都會把.gi

所以你可以在虛擬環境的 `activate` 指令裡加上這一行。打開 `venv/lunch/bin/activate`（Windows 是 `venv\lunch\Scripts\activate.bat`），在最後面新增一行，加入上面的指令。這樣你之後啟用虛擬環境時，就會自動更新環境變數了。

> 注意：一般而言我們不會把這個檔案放入版本控制。如果你用 Git，請記得在 `.gitignore` 裡加入 `.env`；其他版本控制工具亦同。

接著，在 `base.py` 找到這一段：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

這是用來設定資料庫的設定。預設是使用 SQLite 3，不過如果你的機器裡有 PostgreSQL、MySQL 或 Oracle，Django 也有官方支援（還有些非官方的模組支援其他的）。因為網站正式部署時也會和你本機用的不同，所以我們同樣要把這段放到 `local.py` 裡。把上面這段直接刪掉，然後在 `local.py` 加上這段：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(BASE_DIR), 'db.sqlite3'),
    }
}
```

如果你想用其他資料庫，請參考[官方文件](https://docs.djangoproject.com/en/1.7/ref/databases/)。注意你必須安裝合適的 Python 函式庫：

* PostgreSQL：`pipenv install psycopg2`
* MySQL（或 MariaDB）：`pipenv install mysqlclient`
* Oracle：`pipenv install cx_Oracle`

而且這些都需要 C 編譯器與 Python 頭文件。如果你不知道要怎麼設定，那麼就先暫時用 SQLite 3 吧。

設定完之後，你的 `local.py` 應該會長得像這樣（假設你用 SQLite 3）：

```python
from .base import *

SECRET_KEY = '同上，請自行代換'
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(BASE_DIR), 'db.sqlite3'),
    }
}
```

接著我們用以下的指令，在資料庫裡建立預設需要的表格：（請 `cd` 到 `manage.py` 所在的目錄再執行）

```bash
pipenv run python manage.py migrate
```

你應該會看到這樣的輸出：

    Loading .env environment variables…
    Operations to perform:
      Apply all migrations: admin, auth, contenttypes, sessions
    Running migrations:
      Applying contenttypes.0001_initial... OK
      Applying auth.0001_initial... OK
      Applying admin.0001_initial... OK
      Applying admin.0002_logentry_remove_auto_add... OK
      Applying contenttypes.0002_remove_content_type_name... OK
      Applying auth.0002_alter_permission_name_max_length... OK
      Applying auth.0003_alter_user_email_max_length... OK
      Applying auth.0004_alter_user_username_opts... OK
      Applying auth.0005_alter_user_last_login_null... OK
      Applying auth.0006_require_contenttypes_0002... OK
      Applying auth.0007_alter_validators_add_error_messages... OK
      Applying auth.0008_alter_user_username_max_length... OK
      Applying auth.0009_alter_user_last_name_max_length... OK
      Applying sessions.0001_initial... OK

代表成功。如果你使用 SQLite 3，應該會在專案根目錄發現一個叫 `db.sqlite3` 的檔案，代表我們的資料庫。（如果使用其他資料庫，也可以自己檢查一下裡面是否被建立的新的 tables。）現在我們（終於）可以執行這個網站：

```bash
pipenv run python manage.py runserver
```

執行後應該會看到類似這樣的輸出

```
Loading .env environment variables…
Performing system checks...

System check identified no issues (0 silenced).
December 07, 2017 - 10:16:05
Django version 2.0, using settings 'lunch.settings.local'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

如果你在瀏覽器輸入 `http://127.0.0.1:8000/` 後看到 Django 的預設頁面（上面有個火箭)，就代表成功了。

要停止網站伺服器，請按 control + c。

好，設定都完成了，接下來⋯⋯終於可以開始做網站了？

⋯⋯

如果你還沒被我嚇跑，應該至少也早就暗幹在心：哪有一個 framework 要搞這麼多有的沒的，還不能開始做網站？廢爆了！嗯，如果你只是要讓網站可以動，當然其實根本不需要費這麼多工夫；看看市面上的 Django 教學，例如[官方的這篇](https://docs.djangoproject.com/en/1.7/intro/tutorial01/)，或者[良葛格的這篇](http://www.codedata.com.tw/python/python-tutorial-the-4th-class-1-django-getting-started/)，或者 [Andy 的這篇](http://www.codedata.com.tw/python/python-tutorial-the-4th-class-1-django-getting-started/)，或者 Django Girls Taipei 的這篇，通通都超快 runserver 的啊！

但是這對你沒有好處。反而，如果你可以先把設定都搞定，未來在開發時才能一切順利。我一開始就有說這個教學很硬了嘛。好消息是，你已經把最麻煩的部分都差不多搞定了，接下來的開發會順很多。

所以明日待續。

---

註 1：實務上可能還會更多，例如還要多加一個用來內部測試，部署的機器也可能不止一台所以又會各自不同等等。不過就我們這個自用小網站而言，開發部署各一就夠了。
