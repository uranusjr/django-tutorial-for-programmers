有了昨天的基礎，我們現在要開始重構。先從簡單的開始。

## 首頁

仔細想想，首頁好像不是 `stores` 的一部份。我們應該把它移出來。我個人的習慣是為這些不知道要去哪裡的 views 建一個專屬的 app：

```
python manage.py startapp pages
```

把它加入 `INSTALLED_APPS`：

```python
INSTALLED_APPS = (
    'pages',
    # ...
)
```

接著把 `home` 從 `stores/views.py` 移到 `pages/views.py`，並修改 `lunch/urls.py`：

```python
from pages.views import home    # 原本的 import 刪掉

# ...
url(r'^$', home, name='home'),
# ...
```

既然 view 搬家了，template 好像也應該一起才對。在 `pages` 裡面建立 `templates` 目錄，然後把 `home.html` 搬進去。

測試也一樣應該進去。把 `HomeViewTests` 從 `stores/tests.py` 移到 `pages/tests.py`。跑一下 `python manage.py test`，確認東西沒有壞掉。

不過等等，為什麼 template 搬家了，Django 卻還是找得到？這裡需要解釋一下 Django 的 template lookup。當你在 view（或其他地方）指定一個 template 名稱時，Django 預設會：

1. 根據 `TEMPLATE_DIRS` 設定值，在指定的目錄中尋找名稱符合者。（這個設定的預設值是空 tuple，所以 Django 預設會跳過這個步驟。）
2. 在每個 app 中尋找 `templates` 目錄，並根據 `INSTALLED_APPS` 順序尋找名稱符合者。

以這裡的狀況，Django 會依序檢查 `pages`、`stores`、以及所有列出的 Django 內建 apps 中的 `templates` 目錄，尋找 `home.html`。所以不論你把這個檔案放在任一個 app 中，Django 都找得到。**如果你在 `pages` 和 `stores` 同時有 `home.html`，Django 會優先使用 `pages` 裡的版本**（因為 `pages` 被列在 `stores` 前面）。

為了避免 template 名稱與其他 apps 中的檔案衝突，而不小心被覆蓋，我們通常會在 `templates` 目錄中使用子目錄，達到類似 namespacing 的效果。

所以我們來把 `home.html` 移到更好的地方。在 `pages/templates` 裡新增 `pages` 子目錄，然後把 `home.html` 移進去。

現在你的專案目錄應該會像這樣：

```
lunch
├── lunch
│   └── (省略)
├── stores
│   ├── templates
│   │   ├── store_detail.html
│   │   └── store_list.html
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── pages
│   ├── templates
│   │   └── pages
│   │       └── home.html
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── manage.py
```

當然，改了 template 位置代表我們要修改 `home` view：

```python
def home(request):
    return render(request, 'pages/home.html')
```

記得測試裡的路徑也要修改。重新跑一次 `python manage.py test`，確認東西沒有壞！

## Store URLs

現在可能還好，但是如果你的網站慢慢增長，URL patterns 越來越多，你的 `urls.py` 就會開始越長越大，也越來越難維護。更麻煩的是，因為 Django 是依照順序逐項比對 URL，所以如果你有太多路徑，後面的項目比對起來就會非常慢。所以我們通常會把 URL 分類，只在最頂層（`lunch/urls.py`）留下最常用也最簡單的 patterns，降低 Django 比對時需要的運算量。

把 `lunch/urls.py` 裡關於 `stores` 的兩組 URL patterns 刪掉，換成下面的內容：

```python
url(r'^store/', include('stores.urls')),
```

請確認在 `lunch/urls.py` 的開頭有 import `include`

```python
from django.conf.urls import url, include
```

這代表「如果網址以 `store/` 開頭（注意 pattern 後面沒有 `$`），嘗試從 `stores.urls` 尋找符合項目」。

接著在 `stores` 裡新增一個檔案 `urls.py`，內容如下：

```python
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.store_list, name='store_list'),
    url(r'^(?P<pk>\d+)/$', views.store_detail, name='store_detail'),
]
```

因為路徑前面的 `store/` 部分已經被比對掉了，這裡只檢查路徑的後半段。測試所有路徑都沒有壞掉！我們今天大概完成了一半；因為內容有點長，好像得分成兩天寫。明天仍然是重構。
