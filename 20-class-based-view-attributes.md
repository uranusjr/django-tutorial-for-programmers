複習一下我們前天說的需求：

1. 已登入的使用者可以在 store detail view 看到一個按鈕，按下去可以根據該店家建立新 event 讓大家來點餐。
2. 建立完 event 後進入 event detail view。
3. 所有人的點餐都會記錄在 event detail view 裡面。
4. 已登入的使用者可以進入 event detail view 填 form 點餐。點完之後頁面會重新整理顯示最新狀態。
5. 使用者也可以在同一頁面修改或刪除自己的 order。

我們現在有 `EventCreateView`，可是這不是我們要的——我們是希望可以直接在 store detail view 建立 event，不是在 event create view 自己選。

所以我們要把 event 的 form 放到 `store_detail` 裡：

```python
# stores/views.py

from django.core.urlresolvers import reverse
from events.forms import EventForm

def store_detail(request, pk):
    # ...
    event_form = EventForm(initial={'store': store}, submit_title='建立活動')
    event_form.helper.form_action = reverse('event_create')
    return render(request, 'stores/store_detail.html', {
        'store': store, 'event_form': event_form,
    })
```

我們在初始化 `EventForm` 時用了一個新參數 `initial`，在 form 出現之前先為某個欄位指定初始值。因為我們要把這個 form post 到 `EventCreateView`，所以必須用 `helper` 的 `form_action` 參數自訂 HTML form tag 中的 `action` attribute（預設會被 post 到目前的 URL）。

接著在 template 產生這個 form：

```html
{# stores/templates/stores/store_detail.html #}

{% load crispy_forms_tags %}

{# 加在 "{% endblock content %}" 前面 #}
{% if user.is_authenticated %}
{% crispy event_form %}
{% endif %}
```

打開一個 store detail page 看看，最下面應該多了一個建立活動的 form⋯⋯欸不過都在 store detail view 了，為什麼還能選建立活動要用的店家？雖然已經選好了，不過這根本不該存在吧！？

所以我們要把它藏起來。把 `EventForm` 的 `Meta` 改成這樣：

```python
# events/forms.py

class Meta:
    model = Event
    fields = ('store',)
    widgets = {'store': forms.HiddenInput}   # 加上這行
```

重新整理看看。選擇項消失了！Django 在把 form 轉成 HTML form 時，會自動根據欄位形態選擇合適的 HTML tag；但如果你不滿意預設值，也可以用 `widgets` 來明確要求 Django 在某個欄位使用特定 widget。這裡我們要求 `store` 欄位使用 `HiddenInput`，所以 Django 就會把它 render 成 `<input type="hidden">`。但 form 本身的功能不會變！

試著在 store detail view 中用這個 form 建立 event 看看！效果應該和直接使用 `EventCreateView` 一樣。

既然我們可以直接在店家頁面建立 event，好像就不需要顯示 `EventCreateView` 了。要怎麼像之前的 `store_delete` 一樣，只允許 POST 而不允許 GET？

用 function-based views 時，我們會用 `require_http_methods` decorator。在 class-based views 中，我們使用 `http_method_names` attribute：

```python
# events/views.py

class EventCreateView(CreateView):
    form_class = EventForm
    http_method_names = ('post',)   # 只允許 POST！
    model = Event
```

注意這裡要用小寫——還記得昨天的內容嗎？因為 CBV 在檢查 HTTP 動詞時會用 `lower()` 把 `request.method` 的內容轉成小寫！

直接在瀏覽器中開啟 <http://localhost:8000/event/new/> 看看。你應該會看到空白頁面，且終端機中會出現這樣的 log：

```
"GET /event/new/ HTTP/1.1" 405 0
```

代表你收到了 405 Method not allowed。但如果你從 store detail view 中，還是可以 POST 到 `/event/new/` 沒問題，因為 POST 有被允許。

對了，既然現在不能 GET，而且 POST 成功後會被重導向到 event detail view，其實 event create view 根本完全不會用到 template——所以你其實可以把 `event_form.html` 刪掉了。

今天就到這裡。明天我們會開始實作點餐的部分。
