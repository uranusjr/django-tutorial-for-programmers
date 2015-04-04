我們現在可以顯示在 admin 建立的餐廳給所有人看，可是其他人並不能建立餐廳——除非他們有管理員權限。可是讓大家都有管理權限也不好。所以我們要做一個給一般人使用的 CRUD 介面。

要實作 create 與 update，就需要使用 HTML form。Django 提供了一個方便的介面，方便你建立表單。

Django 的表單支援源自於 `djanfo.forms.Form` class。表單的宣告與 model 類似，只是使用的 field classes 不同。舉例而言，如果你想要有一個包含使用者名稱、密碼、以及一個「記住我」方塊的登入表單，就可以這樣宣告：

```python
from django import forms
from django.forms import widgets

class LogInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=widgets.PasswordInput)
    remember_me = forms.BooleanField(required=False)
```

如果在 template 中使用這個 form（例如 `{{ form }}`），Django 就會自動選擇合適的 tag，把這個 form class 轉成 HTML。如果預設的元件不合適（例如 `password` 應該要用 `<input type="password">`），也可以自己指定。如果某個欄位可填可不填，就使用 `required=False`（否則預設都是必填）。

不過精彩的在後面。如果你已經有一個 model，就可以直接用它的欄位建立 form，不用自己宣告！

立刻做一個 view 來顯示這個 form：

```python
# stores/view.py

from django.forms.models import modelform_factory

def store_create(request):
    # Django 1.8+ 必須明確地指名要用的欄位
    StoreForm = modelform_factory(Store, fields=('name', 'notes'))
    form = StoreForm()
    return render(request, 'stores/store_create.html', {'form': form})
```

就這麼簡單！`modelform_factory` 會自動偵測你的 model 裡有哪些欄位，根據它們的性質選擇合適欄位，並建立一個 form class。如果你想客製化，也可以自己 subclass `django.forms.ModelForm` 來定義，但在大多數狀況下這樣就夠了。

補完需要的東西：

```python
# stores/urls.py

# ...
url(r'^new/$', views.store_create, name='store_create'),
# ...
```

```html
{# stores/templates/stores/store_create.html #}

{% extends 'stores/base.html' %}

{% block title %}建立店家 | {{ block.super }}{% endblock title %}

{% block content %}
<form action="" method="post" role="form">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit" class="btn btn-primary">建立</button>
</form>
{% endblock content %}
```

注意 Django form 只會幫你產生欄位，所以你還是得自己宣告 form tag 與 submit button。`as_p` 告訴 Django 要用 `<p>` 把 form field 包起來（才能換行）。你可能會覺得這 form 很醜，而且一點也不 Bootstrap。確實如此。我們明天再改。

但 `{% csrf_token %}` 是什麼？如果你把 server 跑起來，然後看 `http://localhost:8000/store/new/` 的 HTML，會發現 Django 把它轉成一個像這樣的 input 欄位：

```html
<input type="hidden" name="csrfmiddlewaretoken" value="qfbg5BIB6818xpzy6Yz0OxOUcb8YxB2W">
```

有關 [CSRF](http://zh.wikipedia.org/wiki/跨站请求伪造)（cross-site request forgery）的相關知識可以參考[這篇文章](http://cyrilwang.pixnet.net/blog/post/31813568-%5B技術分享%5D-cross-site-request-forgery-(part-1))。詳細的不談，這裡的重點是 Django 會使用這個 token 來確認你的 form request 有否被偽造。所以如果你要使用 Django form，就必須記得加上這個欄位。

不過如果你現在按新增，什麼事情都不會發生。因為即使你 post 回原本的 view（因為 `action=""`），也沒有人會處理這些資料啊。所以：

```python
# stores/view.py

from django.shortcuts import render, redirect

def store_create(request):
    StoreForm = modelform_factory(Store, fields=('name', 'notes'))
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save()
            return redirect(store.get_absolute_url())
    else:
        form = StoreForm()
    return render(request, 'stores/store_create.html', {'form': form})
```

我們在建立 `StoreForm` 物件時，傳入了 `request.POST`。這裡面會包含 POST 的資料（如果你寫過 PHP，這和 `$._POST` 概念類似）。Django 會自動找到對應的欄位，根據 POST 資料填入值。如果 HTTP method 是 GET，我們直接產生一個空表單。（不考慮其他 HTTP methods，全部當成 GET 處理。）

當 request method 是 POST 時，我們使用 `is_valid` 驗證表單是否完整。如果不完整，就繼續把 form render 出去——試著輸入不合法的值（例如把 `name` 留空）後送出，你應該會發現自己回到原本的頁面，但是表單內的值都還在（因為它們被存在 `request.POST` 中，在第二次 render 時又被填入 form 裡）。而且 Django 還順便幫你 render 了一個錯誤訊息 *This field is required.*！

如果驗證成功，則我們呼叫 model form 的 `save` 方法。這會讓 Django 直接產生一個 model object 存到資料庫，並將它回傳。接著我們重導向到該 object 的內容頁。

接著是 update。東西都差不多，所以直接上 code：

```html
{# stores/templates/stores/store_update.html #}

{% extends 'stores/base.html' %}

{% block title %}更新 {{ store.name }} | {{ block.super }}{% endblock title %}

{% block content %}
<form action="" method="post" role="form">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit" class="btn btn-primary">更新</button>
</form>
{% endblock content %}
```

```python
# stores/urls.py

# ...
url(r'^(?P<pk>\d+)/update/$', views.store_update, name='store_update'),
# ...
```

```python
def store_update(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    StoreForm = modelform_factory(Store, fields=('name', 'notes'))
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            store = form.save()
            return redirect(store.get_absolute_url())
    else:
        form = StoreForm(instance=store)
    return render(request, 'stores/store_update.html', {
        'form': form, 'store': store,
    })
```

我們多傳了一個參數 `instance` 進入 `StoreForm`。這告訴 Django 它應該根據這個 object 建立 form，當 save 的時候也應該 update 它，而不是建立新物件。剩下的都很直觀。

我們在適當的地方新增幾個連結：

```html
{# stores/templates/store_list.html #}

{# 隨你想放哪都好，只要在 content block 裡就行。 #}
<a href="{% url 'store_create' %}" class="btn btn-default">建立店家</a>
```

```html
{# stores/templates/store_detail.html #}

{# 同上，只要在 content block 就好。 #}
<a href="{% url 'store_update' pk=store.pk %}" class="btn btn-default">更新店家資訊</a>
```

到處按按，新增和更新幾個店家資訊看看！功能應該都沒問題了。

明天我們要來稍微美化表單。如果你在疑惑 CRUD 是不是少了一個——我們之後會回來實作 delete！
