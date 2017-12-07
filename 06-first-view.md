來幫網站加個首頁。因為這是 Django 教學，不是前端教學，所以這個範例會直接拼一個簡單的介面。我最近很愛 [Bulma](https://bulma.io)，所以就趁這個機會用用看。Django 本身不管前端，所以只要 Django 的部分做好，其他完全可以直接抽換，舉一反三應該不難。

當 Django 收到一個 HTTP request 時，會首先確認該 request 的 URI 應該對應到哪個 view（如果對應不到，直接回傳 [404 Not Found](http://zh.wikipedia.org/zh-hant/HTTP_404)），並把 request 交給它。View 要負責處理這個 request，並回傳一個 HTTP response：

               ┌──────────────┐
     request   │              │  response
    ─────────> │     view     │ ──────────>
               │              │
               └──────────────┘

這顯然是一個 [function](http://sco.wikipedia.org/wiki/Function_(mathematics))！所以在 Django 中，每個 view 其實就是一個 function。這個 function 接受一個 request 引數（與其他參數，我們之後會提到），回傳一個 `django.http.HttpResponse` 物件。由於 HTTP response 格式需要設定很多東西，所以 Django 提供了一個 shortcut `django.shortcuts.render` 來方便我們產出 response 物件。

所以我們來實作 `home` 這個 view。首先我們要在 `lunch/urls.py` 新增一個 URL pattern，讓 Django 知道如何把網址導向至 view 的 function：

```python
from django.contrib import admin
from django.urls import path
from stores.views import home

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
]
```

這個 `path` 會符合首頁，也就是 URL 中路徑是空字串的狀況，並把它對應到 `home`。

接著我們實際實作 `home` function：

```python
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')
```

`render` 的第二個參數是 template 的位置（我們稍後會看到怎麼建立它）。`render` 會負責處理 template，產生一個合法的 HTML 檔案，並依此建立 HTTP response。

最後是 `home.html`。在 `stores` 裡建立一個目錄，叫做 `templates`，並在裡面新增 `home.html`：

```html
{# stores/templates/home.html #}

<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>午餐系統</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.6.1/css/bulma.min.css" integrity="sha256-v5YlJGWVLS5hQ+o48fBzCKHEP2vMNsku57x3CosYykc=" crossorigin="anonymous" />
</head>
<body>
<nav class="navbar is-dark" role="navigation" aria-label="main navigation">
    <div class="container">
        <div class="navbar-brand">
            <span class="navbar-item">午餐系統</span>
        </div>
    </div>
</nav>
</body>
</html>

```

可以看到，這基本上就是一個 HTML 檔案。`render` 會讀取這個檔案，並以它作為 content，建立 HTTP response。

把 server 跑起來，然後打開 <http://localhost:8000/> 看看。內容應該不再是 **It works!** 了，而是你剛剛放的 navbar。恭喜你完成了第一個 Django 頁面！

上面的 HTML 有一個小問題。我們沒有放**午餐系統**的連結。這個區塊應該要指向首頁，所以我們可以這樣寫：

```html
<a class="navbar-item" href="/">午餐系統</a>
```

但這不好。Django 不鼓勵你把 URL 直接寫死，因為如果你的網站之後要修改架構，更換所有的 URL 會很痛苦。我們真正想做的，其實不是讓它指向 `/`，而是指向 `stores.views.home` 對應的那個 URL，**不管它是什麼**。所以我們應該這麼做：

1. 幫我們的 URL 加上一個名稱。

    把 `lunch/urls.py` 中 `home` 的那行修改成下面這樣：

    ```python
    path('', home, name='home'),
    ```

2. 用這個 name 來 refer 我們要的 URL：

    ```html
    <a class="navbar-item" href="{% url 'home' %}">午餐系統</a>
    ```

等等！`{% url 'home' %}` 是什麼？

這叫 template tag。我們不能在 template 中寫 Python，所以如果你需要在 template 中使用任何邏輯（JavaScript 不算），就必須使用 template tags。

Django 的 template tag 語法是下面這樣：

```
{% tag_name [ argument ... ] %}
```

所以上面那個例子中，我們呼叫了 `url` 這個 tag，並傳入一個參數 `'home'`。這個 tag 會幫你找到名稱為 `home`  的 URL pattern（名稱就是 `urls.py` 裡的 `name='home'` ），並輸出該 pattern 對應的網址。在這裡，輸出的就會是 `/`。

這就是你的第一個 Django view。接著我們要實際建立資料，把下面的內容也做出來。
