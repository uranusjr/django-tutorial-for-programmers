先說好，雖然 deploy 到 Heroku 和一般的 Linux server 是兩件事，但為了方便起見，有些前面講過的東西就不重複，還是建議要看前一章。我們這裡會用 Ubuntu Server 14.04 來示範，如果你習慣使用其他發行版就麻煩自己舉一反三一下。其他版本中最麻煩的可能是要自己想辦法安裝 Python 3.4（預設可能都只有 2.7），這關過了後面應該都還算差不多。

由於這裡可以玩的花樣很多，本章會用 nginx + Gunicorn + Supervisor + PostgreSQL 示範。上面的所有元件都可以替換，例如

* nginx 可以換成 Apache。
* Gunicorn 可以換成 Waitress。
* uWSGI 可以取代 Gunicorn 與 Supervisor。
* 如果你用 Apache，可以用 mod_wsgi 取代 Gunicorn 與 Supervisor。
* PostgreSQL 可以換成 MySQL 或 MariaDB 甚至 Oracle Database。

不過實在是沒辦法全部講完，所以只好先麻煩舉一反三了。或許之後有機會吧。

首先我們建立一個設定檔：

```python
# lunch/settings/production_ubuntu.py

from .base import *

DEBUG = False

SECRET_KEY = get_env_var('DJANGO_LUNCH_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lunch',
        'USER': get_env_var('DJANGO_LUNCH_DATABASE_DEFAULT_USER'),
        'PASSWORD': get_env_var('DJANGO_LUNCH_DATABASE_DEFAULT_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    },
}

ALLOWED_HOSTS = ['*']

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')
```

這裡列出了 PostgreSQL 的所有設定。其中 `NAME` 是資料庫名稱，你可以自己換，`USER` 與 `PASSWORD` 顯然必須有讀寫該資料庫的權限，請自行設定。[註 1] `PORT` 留白代表使用預設 port，如果你有其他需求也可以自行修改。注意有些值我們放在環境變數中，而不直接寫在專案裡，以增加安全性。

`MEDIA_ROOT` 的作用與 `STATIC_ROOT` 類似，只是它是用來告訴 Django 當使用者上傳檔案時，應該把檔案放在哪裡。這裡我們單純就只是把它放在外面一層的 `media` 目錄裡，但你可以設定 NFS 或者各式各樣的服務來用，只要 Django 找得到就行了。

接著我們要安裝一些系統元件：

```bash
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install python3 python3-pip python3-dev postgresql postgresql-contrib libpq-dev nginx supervisor -y
```

其中前兩個是必須，接下來三個是 PostgreSQL 相關，最後兩個則是字面上的意義。可以依照你的需求增減要安裝的東西。我們會用 PIP 安裝 Gunicorn，所以這裡沒有包含。[註 1]

接著用下面的指令修正 Ubuntu 的 Python 沒有包含 `ensurepip` 模組的問題：

```bash
wget -qO - http://d.pr/f/mbQy+ | sudo python3
```

然後就可以開始部署專案。首先進入你想放專案的地方（以下稱 `/project`），建立 venv：

```bash
python3 -m venv venv/lunch
```

然後把你的專案弄上去。隨便你要用什麼方法都行，當然 Git 或許是最方便的。假設你弄上去後，現在 `/project` 的結構應該會和本機端一樣。

把專案有用到的套件裝上去：

```bash
. venv/lunch/bin/activate
pip install -r lunch/requirements.txt
```

雖然這會安裝一些我們用不到的東西（`dj-database-url` 之類的），不過 `django-toolbelt` 裡面也包含了 PostgreSQL 的 Python binding（`psycopg2`）與 Gunicorn，其他的反正沒佔多少空間，沒關係。

先把一些環境變數設起來：

```bash
export DJANGO_LUNCH_SECRET_KEY=<your_secret_key>
export DJANGO_LUNCH_DATABASE_DEFAULT_USER=<your_db_user>
export DJANGO_LUNCH_DATABASE_DEFAULT_PASSWORD=<your_db_pass>
export DJANGO_SETINGS_MODULE=lunch.settings.deploy_ubuntu
```

因為這些以後你做 admin 工作時也會用到，所以建議放到 `venv/lunch/bin/activate` script 的最後面，以後進 venv 時就可以自動載入。

還是得記得 migrate 資料庫：

```bash
python manage.py migrate
```

接著我們要把 static 收集起來，才能讓 static file server 找到它們。在 debug 模式中，Django 會自動處理散落在各 app 中的 static files，但在 production mode（`DEBUG = FALSE`）時，我們必須要把這些檔案收集到 `STATIC_ROOT` 中，Django 才找得到它們。

```bash
python manage.py collectstatic
```

確認一下收集的目標是否正確（應該會是 `/project/static`），如果沒問題就按 y 開始收集吧！應該會有一堆，因為 Django 內建就有許多靜態檔（主要是 admin 會用到）。

設定完成！先把 dev server 跑起來，看到目前為止的設定對不對。

```bash
python manage.py runserver 0.0.0.0:8000
```

如果都正確，你應該可以用 <http://server-ip:8000/> 看到首頁。

接著是 Gunicorn。在 `/project` 建立 `gunicorn.conf.py`：

```python
import os

bind = '127.0.0.1:8080'
worders = (os.sysconf('SC_NPROCESSORS_ONLN') * 2) + 1
loglevel = 'error'
command = '/project/venv/lunch/bin/gunicorn'
pythonpath = '/project/lunch'
```

這會讓 Gunicorn 使用你的 CPU 數乘二加一個 processes，然後把網頁 serve 在 `127.0.0.1:8080`，並把錯誤記錄下來。具體需要幾個 processes 效能比較好要視機器而定，所以你可能必須自己試試看其他組合，不過這個設定在多數情況都還 OK。

接著是 nginx。在 `/etc/nginx/sites-available` 裡建立一個設定檔：

```
upstream lunch {
    server 127.0.0.1:8080;
}

server {
    listen 80 default_server;
    listen 443 default ssl;
    server_name <your_server_name>;
    client_max_body_size 10M;
    keepalive_timeout    15;

    location /static/ {
        alias           /project/static/;
    }

    location /media/ {
        alias           /project/media/;
    }

    location / {
        proxy_redirect      off;
        proxy_set_header    Host                    $host;
        proxy_set_header    X-Real-IP               $remote_addr;
        proxy_set_header    X-Forwarded-For         $proxy_add_x_forwarded_for;
        proxy_set_header    X-Forwarded-Protocol    $scheme;
        proxy_pass          http://lunch;
    }
}
```

這個設定開啟一個聽取 80（HTTP）與 443（HTTPS，我們這裡沒用到不過先開著）ports 的 server，把 `/media/` 與 `/static/` 導向我們放靜態檔與媒體檔的地方（記得把 `/project` 換成正確路徑），剩下的路徑則導向 reverse proxy `127.0.0.1:8080`，也就是上面 Gunicorn 的位置。

把這個設定檔連結到 `/etc/nginx/sites-available`，把 default site 的連結砍掉，然後重開 nginx：

```bash
sudo ln -s /etc/nginx/sites-available/lunch /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default
sudo service nginx restart
```

如果一切正確，你現在應該可以在 `/project` 把 Gunicorn 跑起來：

```bash
gunicorn -c gunicorn.conf.py lunch.wsgi
```

然後用 server IP 看到網站了！

但是這樣我們要手動把 Gunicorn 跑起來才看得到網站，如果用 Ctrl-C 關掉，網站就掛了。最後一個步驟：設定 Supervisor。

Supervisor 是一個可以讓使用者監控機器內 processes 的工具。使用者可以把某個想執行的東西註冊進去，要求 supervisor 在特定的時候執行（例如：當你啟動時，請幫我把它也啟動），並使用 Supervisor 提供的介面查看 processes 的運行狀況，或者手動啟動、停止、重啟某個些 processes。

建立 `/etc/supervisor/conf.d/lunch.conf`：

```
[group:lunch]
programs=site

[program:site]
directory=/project
command=/project/venv/bin/gunicorn -c /project/gunicorn.conf.py -p gunicorn.pod lunch.wsgi
autostart=true
autorestart=true
stdout_logfile=/project/supervisor.log
environment=DJANGO_LUNCH_SECRET_KEY=<your_secret_key>,DJANGO_LUNCH_DATABASE_DEFAULT_USER=<your_db_user>,DJANGO_LUNCH_DATABASE_DEFAULT_PASSWORD=<your_db_pass>,DJANGO_SETINGS_MODULE=lunch.settings.deploy_ubuntu
```

這個設定檔定義了一個群組，裡面有一個程式 `site`。這個程式會自動在 Supervisor 啟動時自動開始執行，切換到 `/poject` 目錄執行適當的 Gunicorn 指令。`environment` 設定指名了需要的環境變數。

現在我們讓 Supervisor 讀進這個設定：

```bash
sudo supervisorctl reread
```

這應該會顯示有一個新設定 `lunch`。重新啟動 Supervisor：

```bash
sudo supervisorctl reload
```

看看它有沒有跟著起來：

```bash
sudo supervisorctl status
```

如果你有看到 `lunch:site` 處於 `RUNNING`，恭喜你！現在你應該可以正常使用網站了。部署成功！

---

註 1：如果你不知道怎麼做，可以參考[這篇](http://www.cyberciti.biz/faq/howto-add-postgresql-user-account/)。
