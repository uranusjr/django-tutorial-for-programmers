希望你還記得我們前天做了什麼。

首先，找到你之前建立的 `lunch` 目錄，`cd` 進去，然後啟用虛擬環境。

接著用以下的指令建立新專案

```
pipenv run django-admin startproject lunch .
```

這會在目前的目錄下建立所有專案需要的檔案。

你現在的檔案結構應該會類似這樣：

```
lunch
├── lunch
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── Pipfile
└── Pipfile.lock
```

根目錄裡有一個檔案 `manage.py`，以及一個與專案同名的目錄。前者的用途看名字大概也能猜到，是用來管理你的專案；我們之後用到的時候再來慢慢解釋。後者則是用來存放專案共用的檔案。我們來看看裡面各檔案的作用：

* `__init__.py`：Python 用來標示某個目錄是 module 的檔案。`lunch` 裡面有這個檔案，就代表 `lunch` 本身是個合法的 Python module，其他程式可以用 `import` 把它載入。

* `settings.py`：顧名思義，這個檔案是用來存放 `lunch` 這個專案的設定。Django 的設定檔其實就是一個 Python 檔，裡面的變數會被當作設定值。

    除了你現在在 `settings.py` 裡看得到的內容外，Django 其實還有很多預設值。完整的 Django 設定列表可以在[官網文件](https://docs.djangoproject.com/en/2.0/ref/settings/)找到；如果某個設定值在設定檔裡沒有，則會使用內建的預設值。

    Django 在很多地方都提供了合理的預設值，所以在設定檔裡需要修改的項目並不多。我們之後會回來處理必要的設定。

* `urls.py`：當伺服器收到網路要求時，要求裡面會有一個路徑資訊，也就是你在使用瀏覽器時看到的那個網址。這個檔案的內容是用來告訴 Django，當它收到某個（或某些）路徑的要求時，應該要呼叫哪個函式來處理。我們之後會再回來詳細討論路徑，以及 Django 怎麼把它對應到函式。

* `wsgi.py`：如果你還記得昨天的內容，應該可以猜到它的作用。這個檔案就是讓你的 Django 專案變成 WSGI 應用程式的關鍵。當 WSGI 伺服器收到請求時，就會執行這個檔案，以獲得一個 WSGI 應用程式。

我們來看看 `wsgi.py` 的內容：

```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lunch.settings")

application = get_wsgi_application()
```

檔案前面有一串 docstring，用來解釋這個檔案的用途，這裡省略。這個檔案分成兩個部分。上面兩行是用來指定專案設定檔位置。在預設狀況下，我們的檔案是放在 `lunch` module 裡面的 `settings.py`，所以這邊設定成 `lunch.settings`。

這個設定檔路徑用 `os.environ` 被設定到環境變數 `DJANGO_SETTINGS_MODULE` 裡。接著 Django 導入一個 WSGI application，並執行它。當這個 WSGI 應用被執行時，會讀取我們剛剛設定的 `DJANGO_SETTINGS_MODULE` 環境變數，並依此找到設定檔來使用。這也代表，如果我們**不想**使用 `lunch.settings` 當我們的設定檔，只要把環境變數設成其他值就可以了！請記住這個概念，我們之後會用到。

不過今天先到這裡。我們明天會把專案設定完成，讓它可以執行。
