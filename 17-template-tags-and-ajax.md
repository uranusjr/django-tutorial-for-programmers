我們現在是在 view 裡判斷是否能 delete。但是這種繁瑣的東西實在應該被放到 model 才對。我們在 `Store` 新增一個 method，來把這些東西 refactor 出去：

```python
# stores/models.py

class Store(models.Model):
    # ...
    def can_user_delete(self, user):
        if not self.owner or self.owner == user:
            return True
        if user.has_perm('stores.delete_store'):
            return True
        return False
```

這樣 view 就簡單多了：

```python
# stores/views.py

def store_delete(request, pk):
    # ...
    if store.can_user_delete(request.user):
        store.delete()
        return redirect('store_list')
    # ...
```

但這要怎麼在 template 使用？這樣嗎？

```html
{{ store.can_user_delete(user) }}
```

餓，好像不行。因為 Django 不允許在 template 中呼叫帶引數的 methods。為了這個目的，我們必須實作一個 template tag。

我們前面已經看過幾個 template tags：內建的 `urls`、`for`、`extends` 等等都是。我們也看過第三方的元件，例如 Django Crispy Forms 的 `crispy` tag 與 filter。不過這些東西究竟是怎麼寫的？

在 `stores` 目錄下建立 `templatetags` 目錄，在裡面新增兩個檔案：`__init__.py` 與 `stores_tags.py`。在後者輸入以下內容：

```python
from django.template import Library

register = Library()

@register.filter
def deletable(store, user):
    return store.can_user_delete(user)
```

Django template tag/filter 其實就是 Python function，只是我們要用一個 decorator 把它註冊到 template system 裡，才能被 Django 辨識。這個 filter 的作用其實就只是把 `can_user_delete` 包起來。

用法就和一般的 template tag/filter 一樣：

```html
{# stores/templates/stores/store_detail.html #}

{% load stores_tags %}

{% if store|deletable:user %}
<input type="submit" value="刪除" class="btn btn-danger">
{% endif %}
```

這樣我們就實作完成 detail view 的刪除了。現在我們想在列表頁也加上同樣的東西。不過這次我們來用 Ajax 實作。我們想要做到：

1. 在列表頁的每個店家旁邊都增加一個刪除按鈕（如果使用者可以刪除該店家）。
2. 按下按鈕後，用 Ajax 發一個 DELETE request。
3. Django 收到 DELETE request 後進行刪除，成功則回傳 200 OK。
4. 當 JavaScript 接收到刪除成功的訊息，直接把列表頁中的對應項目移出 DOM。

第一步很簡單：

```html
{# stores/templates/stores/store_list.html #}

{% load stores_tags %}

<!-- ... -->
<div class="store">
  {% if store|deletable:user %}
  <button data-href="{% url 'store_delete' store.pk %}"
      class="btn btn-danger pull-right btn-delete">
    刪除
  </button>
  {% endif %}
<!-- ... -->
```

接著是第二步。我們要寫 JavaScript 了。首先把 jQuery 加進來，然後新增一個 block：

```html
{# base/templates/base.html #}

<!-- 放在 body 最後面 -->
<script src="//code.jquery.com/jquery-2.1.1.min.js"></script>
{% block js %}{% endblock js %}

</body>
</html>
```

接著我們要來寫 Ajax⋯⋯不，等等！我們還得做一件事情。還記得 Django 會檢查 CSRF token 嗎？當你使用 Ajax 時，它還是會檢查。所以我們必須多做一些設定。幸好 Django 官方文件就有[教你怎麼做](https://docs.djangoproject.com/en/dev/ref/contrib/csrf/#ajax)。不過這要放哪裡？

Django 把網站中不是動態產生的檔案統稱為 static files，並用 `django.contrib.staticfiles` 來管理它們。管理的邏輯和 templates 很像。我們來建立一個 `base.js`。首先建立 `base/static/base/js/` 目錄，並在其中建立一個 `base.js`，然後把官方文件中的範例程式碼抄進去：

```javascript
// base/static/base/js/base.js

(function ($) {

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = $.trim(cookies[i]);
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
function csrfSafeMethod(method) {
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
  'beforeSend': function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
  }
});

})(jQuery);
```

然後在 `base/templates/base.html` 中引入：

```html
{% load staticfiles %}

<!-- 要放在 jQuery 後面 -->
<script src="{% static 'base/js/base.js' %}"></script>
```

可以看到路徑的邏輯也和 template 很像。

在設定 CSRF token 後，我們就可以實作第二步與第四步。同樣在 `stores` 目錄中也建立 static 目錄，加入以下檔案：

```javascript
// stores/static/stores/js/store_list.js

(function ($) {
$('.btn-delete').click(function () {
  var button = this;
  $.ajax({
    'url': $(button).data('href'),
    'type': 'DELETE'
  }).done(function () {
    $(button).parent('.store').remove();
  }).fail(function (e) {
    console.log(e);
  });
});
})(jQuery);
```

錯誤處理就不管了，如果需要的話自己寫。把這個檔案引入 template：

```html
{# stores/templates/stores/store_list.html #}

{% load staticfiles %}

{# 放在 endblock content 後面 #}

{% block js %}
<script src="{% static 'stores/js/store_list.js' %}"></script>
{% endblock js %}
```

最後是第三步，也就是 Python 部分：

```python
# stores/views.py
from django.http import HttpResponse

@login_required
@require_http_methods(['POST', 'DELETE'])
def store_delete(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    if store.can_user_delete(request.user):
        store.delete()
        if request.is_ajax():
            return HttpResponse()
        return redirect('store_list')
    return HttpResponseForbidden()
```

我們把 `DELETE` 也加入允許列表，並且在成功時使用 `request.is_ajax()` 判斷，如果是 Ajax request 則直接回傳 `HTTPResponse` 代表 200 OK。

大功告成！試著刪除點東西試試吧。
