接下來就談一些比較小的題目。

## Logging

Logging 是未來讓你知道程式運作狀況的最好方法。在 web services 中，因為我們沒辦法人力監控伺服器對所有請求的反應，所以 logging 做得好，要飯要…（不對）

總之 logging 很重要。

Django 的 logging 機能基於 Python 內建的 `logging` 模組。這個模組提供一個完整的 logging 系統，主要分成四個部分：

1. Loggers 把某個訊息紀錄（log）進 logging system。Python 提供五種紀錄級別，重要性由低而高：
    1. `DEBUG` 代表用來 debug 的訊息，通常很低階而且詳盡。
    2. `INFO` 代表一般性的系統訊息，記錄系統的狀態。
    3. `WARNING` 代表系統遇到小問題。這種問題雖然在意料之外，但本身不見得有大影響。
    4. `ERROR` 代表系統遇到大問題，需要注意。
    5. `CRITICAL` 代表系統遇到嚴重問題，應該馬上處理。
2. Handlers 負責處理（handle）進入 logging system 的訊息。它可以把訊息記錄到檔案，輸出到某個裝置，甚至上傳到某個地方等等，隨使用者開心（只要提供合適的 functions）。Handlers 可以要求只處理某個程度或以上（例如「`ERROR` 以上」代表「`ERROR` 與 `CRITICAL`」）的訊息，且只會「反應」而不會「消化」訊息，所以同一條訊息可以同時被很多 handlers 處理。
3. Filters 可以進一步篩選你想要的訊息。例如你可以要求某個 handler 只處理「來自 email 系統」的訊息（然後再用 handler 中的設定調整接收訊息的層級）。
4. Formatters 用來把訊息轉成文字。你可以用它來為紀錄加上時間戳記等等。

例如，假設我們要在使用者建立新店家時，紀錄一個 info level log，就可以這麼做：

```python
# stores/views.py

import logging

logger = logging.getLogger(__name__)

def store_create(request):
    # ...
    store.save()
    logger.info('New store {store} created by {user}!'.format(
        store=store, user=request.user
    ))
    # ...
```

首先我們需要給一個名稱，以從 loggin frameowkr 中取得一個 logger。我們習慣為每個檔案建立自己的 logger，其名稱就是 `__name__`（模組名稱）。但你也可以用自己喜歡的方法來命名 logger，好分類你的 logging messages。Logger 的名稱有階層順序，例如如果你有兩個 loggers，分別長這樣：

```python
logger1 = logging.getLogger('stores.views.create')
logger2 = logging.getLogger('stores.views')
```

那麼 `logger1` 的 logs 會 propagate 到 `logger2`。同理，如果你有另一個 logger 名稱是 `stores`，則 `logger1` 與 `logger2` 的 logs 都會 propagate 到那裡！

Django 的設定檔中提供了一個 `LOGGING` 設定，讓你可以調整 logging system 的行為。下面是一個範例：

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'lunch.log'),
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

Django 預設提供了兩個 handlers：當 `DEBUG` 是 `True` 時，所有的 log messages 都會被送到 `stdout`；而當 `DEBUG` 是 `False` 時，所有 `ERROR` 層級以上的訊息會用 email 寄到 admin 的信箱（必須另外設定 [`ADMINS`](https://docs.djangoproject.com/en/1.7/ref/settings/#admins) 與[相關 email 伺服設定](https://docs.djangoproject.com/en/1.7/topics/email/)，才能正確寄出，這邊不提）。我們可以用 `disable_existing_loggers` 來設定是要完全取消這些內建 handlers，還是要保留它們，只是加上一些自己的 handlers。

在設定 loggers 時，首先你要用 `handlers` 與 `filters` 子設定來宣告，接著再設定 `loggers` dict，為每一個可能的 logger 設定它們要使用的設定。每個 logger 設定的 key 就是該 logger 的名稱，如果名稱是空字串就會是所有 loggers 的 parent，會接收到系統中**所有** propagate 上來的訊息。

請參考 Python 官方與 Django 官方文件，以進一步了解：

* [內建 handler 列表](https://docs.python.org/3/library/logging.handlers.html)。
* [Django 提供的 loggers、handlers 與 filters](https://docs.djangoproject.com/en/1.7/topics/logging/#django-s-logging-extensions)。
* [其他範例與說明](https://docs.djangoproject.com/en/1.7/topics/logging/)。

## Data Migration

當你 deploy 上 server 時，必須重新建立 superuser，因為開發時建立的 superuser 是在本機的資料庫。只是個 superuser 當然沒關係，但如果我們需要輸入很多 model 資料，就可以考慮使用 data migration 來自動化。舉例而言，如果我們想要在 deploy 時自動輸入一些新店家，就可以用以下的做法：

首先建立一個新的 migration。

```bash
python manage.py makemigrations --empty stores
```

這會讓 Django 在 `stores/migrations` 目錄裡建立一個檔案，名稱類似這樣：

```
0003_auto_20141025_1144.py
```

我們之前也用過 `makemigrations` 這個指令，但 `--empty` 則是第一次見到。在預設狀況下，Django 會自動偵測專案內 model 的變化，並為它產生對應的 schema migration 指令。但我們這裡並不是要這麼做（而且我們也沒有改 model schema 啊！），只是希望 Django 為我們產生一個 migration 檔案，所以要加上 `--empty` 參數。這樣，Django 就不會自動填入 migration 指令，而為留白讓我們自己寫。

回到剛剛那個檔案。檔名後面那串數字很明顯是現在時間（如果你發現好像時間不太對，可能是因為 Django 用了 UTC 而不是本地時間，所以會差八小時）。但這個檔名本身其實沒有任何意義，所以你可以隨意修改。不過習慣上，我們會保留最前面的四位數字，好讓 migration file 照時間排序。

接著來看內容。每個 migration file 裡面都必須包含一個 `migrations.Migration` subclass instance。這個 subclass 會宣告兩個東西：

1. `dependencies` 告訴 Django 必須在執行這個 migration 前先執行哪些 migrations。每個 migration 是用 `(app 名, migration module 名)` 表示，所以例如如果我們想要 depend 一個位於 `stores/migrations/0001_auto.py` 的檔案，就應該填入 `stores.0001_auto`。
2. `operations` 告訴 Django 這個 migration 包含哪些步驟。

我們首先加入一個 operation：

```python
def create_stores(apps, schema_editor):
    Store = apps.get_model('stores', 'Store')
    MenuItem = apps.get_model('stores', 'MenuItem')
    Store.objects.create(name='肯德基', notes='沒有薄皮嫩雞倒一倒算了啦')
    mcdonalds = Store.objects.create(name='McDonalds')
    MenuItem.objects.create(store=mcdonalds, name='大麥克餐', price=99)
    MenuItem.objects.create(store=mcdonalds, name='蛋捲冰淇淋', price=15)
    
class Migration(migrations.Migration):
    # ...
    operations = [
        migrations.RunPython(create_stores),
    ]
```

我們在 `operations` 列表裡加入一個 `RunPython` 指令，所以當這個 migration 被執行時，就會執行上面的 `create_stores` 函式。在函式中我們建立了兩個店家，並在其中之一建立兩個菜單項目。

不過注意，我們這裡不是使用 import 把 model 定義讀入，而必須使用 `apps.get_model`。這是因為這個 migration 被執行時，model 的定義並不一定與現在相同，所以 Django 會在執行 migration 時動態根據之前的 migration 結果產生 model 定義，並存在傳入的 `apps` 參數中。也因為這個理由，Django 不見得能正確追蹤所有的 model 定義，所以如果你建立物件的過程需要用到一些沒有存在資料庫內的資訊（例如要使用某個 model method），就有可能會出問題。詳情請參照 [migration 官方文件](https://docs.djangoproject.com/en/1.7/topics/migrations/)。但在這裡我們只是想簡單建立 model 物件，所以沒什麼問題。

完成之後，執行

```bash
python manage.py migrate stores
```

Django 就會自動偵測尚未被使用的 migration 並執行它。所以只要把這個 migration 檔上傳到伺服器上（例如 commit 到 Git repository），再在 server 上 migrate，就可以迅速套用你想要的資料了！

## Media Files

回顧一下 deploy to Ubuntu 的內容：

> `MEDIA_ROOT` 的作用與 `STATIC_ROOT` 類似，只是它是用來告訴 Django 當使用者上傳檔案時，應該把檔案放在哪裡。這裡我們單純就只是把它放在外面一層的 `media` 目錄裡，但你可以設定 NFS 或者各式各樣的服務來用，只要 Django 找得到就行了。

所以只要加上 `MEDIA_ROOT` 設定，你就可以用 Django 處理使用者的檔案上傳。我們在介紹 form 時沒有提到，但如果你想在 form 中讓使用者上傳檔案（HTML 的 `<input type="file">`），也可以使用 [`django.forms.FileField`](https://docs.djangoproject.com/en/dev/ref/forms/fields/#filefield)，配合 [`django.db.models.FileField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#django.db.models.FileField) 把圖片資訊存入資料庫。

等等，存入資料庫？大家不是都說**不要**把 binary data 存進資料庫嗎？其實 Django 在處理檔案時，只會在資料庫存入檔案**路徑**。檔案本身則會被存入你在 `MEDIA_ROOT` 中指定的位置。[註 1]

這個檔案在 HTML 裡就要靠 `MEDIA_URL` 設定來處理。如果你這樣設定：

```python
MEDIA_ROOT = '/home/django/media'

MEDIA_URL = 'http://tw.pyconusercontent.org/'
```

那麼 `/home/django/media/PyCon_Day1-720.jpg` 這個檔案就會被對應到 `http://tw.pyconusercontent.org/PyCon_Day1-720.jpg`（網址是我亂掰的，別亂按否則後果自負 XD）。

這裡有個特殊狀況：如果你只是想把 media file 上傳到「目前這台機器」（亦即你的 media server 和 web server 是同一台機器），就可以像這樣設定：

```python
MEDIA_ROOT = '/home/django/media'

MEDIA_URL = '/media/'
```

然後直接在 web server 做 alias。例如如果你用 nginx：

```nginx
server {
    # ...
    location /media/ {
        alias           /home/django/media/;
    }
    # ...
}
```

而不需要在設定檔指定 host name。但如果你這麼做，就需要自己在開發機上的 URL config 設定 media URL——不然 Django 根本不知道要去哪裡找你的 media file。

一般的設定長這樣子：

```python
# lunch/urls.py

from django.conf import settings
from django.conf.urls.static import static

# 和原本一樣。

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
```

如果是在 debug 模式，則多加上一組 URL pattern，把 `MEDIA_URL` 對應到 `MEDIA_ROOT`。Django 提供了 `static` function 來自動產生這個 pattern，所以我們只要這樣呼叫即可（事實上 Django 在 debug 模式中就是用完全相同的方法找到你的 static files）。

---

註 1：如果不想存在 `MEDIA_ROOT` 而是想放在裡面的子目錄，或者你有自動修改檔名之類特殊需求，還可以另外設定 [`upload_to` 參數](https://docs.djangoproject.com/en/1.7/ref/models/fields/#django.db.models.FileField.upload_to)。
