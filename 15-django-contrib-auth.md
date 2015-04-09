由於使用者認證在太多網站都會用到，Django 在出廠時就會附上預設的 `django.contrib.auth` 模組。雖然是預設，但這個模組非常好用，其實沒什麼可以挑剔的地方。當你前面用到 `createsuperuser` 與 admin 介面時，其實就是用這個模組來登入。之前檢查資料庫結構時也有看到相關的 tables（名稱以 auth 開頭的就是）。

Django 的權限管理系統包含以下資料：

1. 一個 table 保存所有使用者資料。
2. 權限系統。每個使用者都可以擁有建立、修改、刪除某個 model 的權限。
3. 每個使用者都有一個 `is_staff` 與 `is_superuser` 欄位。只有 staff 可以進入後台，而 superuser 會擁有所有權限。
4. 可以把使用者加入某個群組。改變群組權限可以直接改變內部使用者權限。

首先我們必須建立一個登入頁面。你可以用前面的方法建立 form、view、template，但 Django 其實有內建 form 與 view 可以用；你只要設定 URL patterns 與 templates 就行。Django 提供了以下的 views：

view name                   | 用途
----------------------------|-------
`login`                     | 登入。
`logout`                    | 登出。
`password_change`           | 更換密碼。
`password_change_done`      | 更換密碼完成後會導向這裡。
`password_reset`            | 重設密碼（會寄 email 給使用者）。
`password_reset_done`       | 重設密碼完成後會導向這裡。
`password_reset_confirm`    | 使用者收到重設密碼 email 時，裡面會包含這個網址。
`password_reset_complete`   | 使用者按下 email 中的重設連結，重設完成後，會被導向這裡。

由於篇幅緣故，註冊和修改密碼的頁面就直接跳過；有興趣請參照[官方文件](https://docs.djangoproject.com/en/1.7/topics/auth/default/#module-django.contrib.auth.views)。

把 URL patterns 導向內建 views：

```python
# lunch/urls.py

urlpatterns = [
    # ...
    url(r'^accounts/', include('django.contrib.auth.urls')),
    # ...
]
```

接著在 `base/templates/base.html` 加上登入按鈕：

```html
<!-- ... -->
<nav class="navbar navbar-default navbar-static-top" role="navigation">
  <div class="container">
    <div class="navbar-header">
      <a class="navbar-brand" href="{% url 'home' %}">午餐系統</a>
    </div>
    <div>
      <ul class="nav navbar-nav">
        <li><a href="{% url 'store_list' %}">店家列表</a></li>
      </ul>
      <form class="navbar-right navbar-form" method="post" action="{% url 'logout' %}">
        <a class="btn btn-default" href="{% url 'login' %}">登入</a>
      </form>
    </div>
  </div>
</nav>
<!-- ... -->
```

我們之後會談到為什麼這邊要用 form。目前就先這樣。

如果你現在按下登入按鈕，應該會看到一個 `TemplateDoesNotExist` 錯誤頁面。這是因為 Django 只提供了 views（與 URL patterns），但沒有提供 templates，我們要自己做。前面提過，這種不知道要放哪裡的東西我都丟到 `pages` 裡。所以新增 `pages/templates/registration/login.html`：

```html
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block body %}
{{ block.super }}
<div class="container">
  <div class="row">
    <div class="col-lg-4 col-md-6 col-lg-offset-4 col-md-offset-3">
      <form method="post">
      {% csrf_token %}
      {{ form|crispy }}
      <button type="submit" class="btn btn-primary">登入</button>
      </form>
    </div>
  </div>
</div>
{% endblock body %}
```

這樣你應該可以看到登入頁面了。輸入你的帳號密碼，然後送出看看。呃，出現了一個 Page Not Found 錯誤。這是因為 Django 預設會在登入後把使用者導向至 profile page，而我們並沒有那種東西。我們其實不需要那種東西，只要在登入後把使用者導到首頁就好。所以我們要在 `lunch/settings/base.py` 加入下面的設定：

```python
from django.core.urlresolvers import reverse_lazy

LOGIN_REDIRECT_URL = reverse_lazy('home')
```

設定本身沒什麼，不過什麼是 `reverse_lazy`？我們前面談過 `reverse` 這個函式可以把 URL pattern name 轉回 URL。但我們不能直接在這裡用 `reverse`，因為當設定檔還沒被讀進 Django 時，我們還無法使用 Django 內部的功能，包含 `reverse`。幸好，Django 的很多函式都有一個 lazy 版本——這些 lazy 函式不會立刻執行，而是會在需要結果時（以這個例子就是在 login view 真的需要重導向時）才會實際給出結果。這就避免了需要在設定載入前使用 Django 內部功能的狀況。

如果你現在登入，應該就會被導入到首頁。不過好像看不出來什麼區別。我們要修改 template 來反應登入狀態：

```html
{# base/templates/base.html #}

<form class="navbar-right navbar-form" method="post" action="{% url 'logout' %}">
  {% if user.is_authenticated %}
  {% csrf_token %}
  <input type="hidden" name="next" value="{% url 'home' %}">
  <button class="btn btn-default" type="submit">登出</button>
  {% else %}
  <a class="btn btn-default" href="{% url 'login' %}">登入</a>
  {% endif %}
</form>
```

除了我們在 view 裡傳入的 context data 外，Django 預設也會設定一些全域的 template 變數。這裡用到的 `user` 就是其中之一。如果當下的 request 已經登入，則這個變數會是一個 user object（來自 `auth` 模組裡的 `User` model）；如果沒登入，則 Django 會使用一個叫做 `AnonymousUser` 的 mock object，來讓 `is_authenticated` 回傳 `False`。所以當使用者登入時，就會顯示登出按鈕，而非登入。根據 [best practice](http://stackoverflow.com/questions/3521290)，我們在登出時應該使用 POST 而非 GET。所以你知道為什麼我們要用 form 了吧！

登出時，Django 預設會使用 `registration/logged_out.html` 這個 template 來顯示「你已經登出」頁面。不過我們這裡不需要這麼做，只要在登出時把使用者導回首頁即可。所以我們多加了一個隱藏欄位 `next`；如果你有加這一欄，Django 會使用裡面的內容來重導向，而不是顯示預設頁面。（登入頁面其實也有這個 `next` 參數可以用；如果你想要做動態導向，例如在登入後導回「使用者原本所在頁面」，而不是固定的頁面，就可以用這個參數。）

這樣就把登入登出頁面完成了！明天我們會正式使用這個權限機制，並且實作 delete view。
