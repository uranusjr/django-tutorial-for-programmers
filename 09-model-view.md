我們現在要來自己寫個 view，把前面製作的 model 顯示出來。我們把這個 view 放在 `/stores/`，所以：

```python
# lunch/urls.py

from django.conf.urls import patterns, include, url
from django.contrib import admin
from stores.views import home, store_list

urlpatterns = patterns(
    '',
    url(r'^$', home, name='home'),
    url(r'^store/$', store_list, name='store_list'),   # 新增這一行
    url(r'^admin/', include(admin.site.urls)),
)
```

接著是 `store_list` function。為了把店家列表顯示在這個頁面上，我們要使用 Django 的 ORM query。Django 的 ORM query 模式如下：

* Model class 的某些 attributes（預設是 `objects`）會回傳一個 model manager。
* Model manager 提供 query methods，回傳 query 物件——這是一個 [iterable](https://docs.python.org/2/glossary.html#term-iterable)，所以你可以對它使用 index 與 iterator 介面。
* Query 物件同樣提供 query methods，可以產生新的 Query 物件。
* 當你實際需要 `Query` 物件中包含的 model 物件時，Django 才會真正從資料庫把資料拿出來。

以 `store_list` 而言，我們需要 `Store` 的全部資料。所以我們可以使用下面的語法：

```python
stores = Store.objects.all()
```

其中 `Store.objects` 會回傳一個 model manager。這個 manager 提供了 `all` method，回傳一個 query 物件。所以 `stores` 包含的是一個 query 物件，其中包含一個 SQL 指令（但尚未執行），大致等同於下面的格式：

```sql
SELECT * FROM "stores";
```

所以我們可以用上面的語法，建立列表頁面的 view function：

```python
# stores/views.py

from .models import Store

def store_list(request):
    stores = Store.objects.all()
    return render(request, 'store_list.html', {'stores': stores})
```

我們取出所有的 store objects 後，在 `render` 的最後面增加一個參數。這個參數為 `render` 提示了額外的 context data，可以在處理 template 時使用。

再來是 `store_list.html`：

```html
{# stores/templates/store_list.html #}

<!DOCTYPE html>
<html>
<head>
<title>店家列表 | 午餐系統</title>
<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
</head>

<body>
<nav class="navbar navbar-default navbar-static-top" role="navigation">
  <div class="container">
    <div class="navbar-header">
      <a class="navbar-brand" href="{% url 'home' %}">午餐系統</a>
    </div>
  </div>
</nav>

<div class="container">
  {% for store in stores %}
  <div class="store">
    <h2>{{ store.name }}</h2>
    <p>{{ store.notes }}</p>
  </div>
  {% endfor %}
</div>

</body>
</html>
```

我們看到了一組新的 template tags `for` 與 `endfor`。這是 Django templates 中表示迴圈的方法，對 Python programmers 而言這應該不難理解。在 templates 裡沒辦法用縮排表示階層，所以我們是用一個 `endfor` 標籤來標示迴圈結束。取用物件內 attributes 的方法仍然是用一個點，不過我們必須在旁邊加上兩組大括弧，來標注這是 template 語法，而不是真的要在 HTML 中印出 `store.name` 這個字串。

把 server 跑起來，你應該可以在 <http://localhost:8000/store/> 看到列表頁。不錯吧！接著是每個店家的獨立頁面。

第一件事情：我們要規劃如何把網址對應到合適的頁面。Django 的做法就是用 capturing groups：

```python
# lunch/urls.py

from django.conf.urls import patterns, include, url
from django.contrib import admin
from stores.views import home, store_list, store_detail

urlpatterns = patterns(
    '',
    url(r'^$', home, name='home'),
    url(r'^store/$', store_list, name='store_list'),
    url(r'^store/(?P<pk>\d+)/$', store_detail, name='store_detail'),    # 新增這行
    url(r'^admin/', include(admin.site.urls)),
)
```

如果你懂 regular expression，這應該很容易理解。`pk` 在這裡指 primary key，是 Django 慣用的命名法。

接者是 view function。在 URL 中被捕捉的值會直接被傳入，所以：

```python
# stores/views.py

from django.http import Http404

def store_detail(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    return render(request, 'store_detail.html', {'store': store})
```

我們前面提過，model manager 與 query 物件會提供 query methods，用來建構新的 query object。但它們也有一些可以直接回傳單一物件的 query methods——例如這裡的 `get`。這個 method 的用途就是取得「一個」物件來回傳，或者如果找不到，就 raise 一個 `Model.DoesNotExist` exception。在這個例子裡，我們把這個 exception 用 try-except block 包起來，在找不到對應物件時回應 404 Not Found。[註 1]

不過為什麼我們可以直接使用 `pk`？我們的 model 裡沒有這個值吧？其實 `pk` 是 Django model 的特殊性質，永遠指向該 model 的 primary key（當然）。前面提過，Django model 一定要有 primary key，而且如果你沒有特別設定，預設會在每一個 model 加上一個 `id` 欄位來當作 primary key。所以在這個例子中使用 `pk` 就等同於 `id`，但是用 `pk` 在大多時候比較有彈性，因為事實上 primary key 可以隨意設定，不見得要是 `id`。

最後是 template：

```html
{# stores/templates/store_detail.html #}

<!DOCTYPE html>
<html>
<head>
<title>{{ store.name }} | 午餐系統</title>
<link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
</head>

<body>
<nav class="navbar navbar-default navbar-static-top" role="navigation">
  <div class="container">
    <div class="navbar-header">
      <a class="navbar-brand" href="{% url 'home' %}">午餐系統</a>
    </div>
  </div>
</nav>

<div class="container">
  <h1>{{ store.name }}</h1>
  <p>{{ store.notes }}</p>
  <table class="table">
    <thead>
      <tr><th>品項</th><th>單價</th></tr>
    </thead>
    <tbody>
      {% for item in store.menu_items.all %}
      <tr><td>{{ item.name }}</td><td>{{ item.price }}</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>

</body>
</html>
```

我們這裡又多玩了一個小花樣。還記得 `Store` 與 `MenuItem` 之間的多對一關聯嗎？我們這裡用了 `menu_items` 這個 reverse relation key，來獲得所有與 `Store` 物件有關聯的 `MenuItem` 實例。由於 `Store` 到 `MenuItem` 是多對一，所以 `menu_items` 同樣會回傳一個 model manager；我們這裡同樣用 `all` 把所有物件列出。注意在 template 中，呼叫方法時並不用加括弧！

現在我們有 detail 頁了，所以可以在列表頁加上連結。把 `stores/templates/store_list.html` 的 `<h2>` 那行改成這樣：

```html
<h2><a href="{% url 'store_detail' pk=store.pk %}">{{ store.name }}</a></h2>
```

我們再次使用了 `url` tag，不過這次除了 name 之外多加了一個參數。這裡傳入的參數會被用在 URL 的 capturing group 上，所以這樣就可以得到某個 store 的 URL！

如果你熟悉 CRUD 的話，我們今天實作的其實就是那個 R。其實不難吧！不過上面的程式其實不是很優秀，所以我們明天會花一點來改寫，讓它符合 best practice。


---

註 1：那麼，如果有很多個物件符合，會回傳哪一個？答案是都不會！如果 `get` 找到超過一個結果，會 raise `Model.MultipleObjectReturned` 例外。不過在實務上，這個 method 通常是用在有 UNIQUE 屬性的欄位，所以這個 exception 比較少被使用。詳細的用法可參考[官方文件](https://docs.djangoproject.com/en/dev/ref/models/querysets/#django.db.models.query.QuerySet.get)。
