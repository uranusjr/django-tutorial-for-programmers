前情提要：

1. [x] 已登入的使用者可以在 store detail view 看到一個按鈕，按下去可以根據該店家建立新 event 讓大家來點餐。
2. [x] 建立完 event 後進入 event detail view。
3. [ ] 所有人的點餐都會記錄在 event detail view 裡面。
4. [ ] 已登入的使用者可以進入 event detail view 填 form 點餐。點完之後頁面會重新整理顯示最新狀態。
5. [ ] 使用者也可以在同一頁面修改或刪除自己的 order。

所以接下來是 3。

打開 `events/templates/events/event_detail.html`，在

```html
<h1>今天吃：{{ event }}。快點餐！</h1>
```

下面加入一個 table，用來列出點餐記錄：

```html
<table class="table">
  <thead>
    <tr><th>使用者</th><th>項目</th></tr>
  </thead>
  <tbody>
    {% for order in event.orders.all %}
    <tr><td>{{ order.user }}</td><td>{{ order.item }}</td></tr>
    {% endfor %}
  </tbody>
</table>
```

這個東西現在應該沒什麼好解釋的了。但它目前什麼都不會顯示——因為還沒有辦法點餐。所以首先我們要在新增點餐用的表單：

```python
# events/forms.py

from .models import Order

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('item', 'notes',)

    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].empty_label = None
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', submit_title))
```

雖然 `Order` 有四個欄位，但我們這裡只顯示兩個，因為 `user` 和 `event` 要自動帶入。但注意看 `__init__`，似乎有一行不認識的。

前面說過（好像不止一次），Django 會自動把 foreign key render 成 HTML select widget。但 Django 預設會為每個可能的物件（在這裡就是所有的 menu items）建立一個 option tag，並在最前面加上一個代表空值的 option（預設顯示 `------` 這樣子）。但點餐時根本不可能什麼都不點吧！所以我們在這裡用 form 的 `fields` attribute 取出 item 欄位（`fields` 會回傳一個 dict，其中包含所有表單中的欄位），然後把空值的顯示值設成 `None`，讓 Django 直接把這個 option tag 拿掉。

接著我們要想辦法把這個 form 丟進 `EventDetailView`。在 function-based views 中，我們必須初始化一個 form instance，然後把它丟進 `render` 的 context 參數。在 class-based views 中，則是要 override（暫停三秒製造高潮氣氛）`get_context_data`！

```python
# events/views.py

from .forms import OrderForm

class EventDetailView(DetailView):

    model = Event

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        order_form = OrderForm()
        data['order_form'] = order_form
        return data
```

我們先用 `super()` 呼叫 superclass 的 `get_context_data` 實作，然後在裡面多加一個 `OrderForm` instance。這樣就可以在 template 中使用了：

```html
{# events/templates/events/event_detail.html #}

{# 千萬要記得它！不然沒辦法用 "crispy" tag！ #}
{% load crispy_forms_tags %}

{# ... #}

{# 加在 content block 的最後面 #}
{% crispy order_form %}

{% endblock content %}
```

看起來不錯，不過不太對。我們希望使用者可以點任何這個店家的產品，但**不能點其他店的東西**。現在這樣使用者可以亂點！所以我們要限制使用者能選擇的項目。Django 的 select widget 可以擁有一個 `queryset` attribute，用來限制能選擇的選項。我們這裡要限制成**所屬店家與目前 event 店家相同的項目**，所以可以這樣寫：

```python
# events/views.py

# ...
def get_context_data(self, **kwargs):
    data = super().get_context_data(**kwargs)
    order_form = OrderForm()
    # 注意這行！
    order_form.fields['item'].queryset = self.object.store.menu_items.all()
    data['order_form'] = order_form
    return data
# ...
```

我們限制它必須從當下 event（`self.object`）所屬店家（`store`）中的 `menu_items` 裡面選擇。記得 `menu_items` 是一個 reverse key，所以會回傳一個 manager；後面的 `all` 會回傳這個 manager 中的所有物件，所以就是我們想要的限制。

重新整理看看！現在使用者應該只能從當下 event 所屬店家的菜單中選擇了。

記得我們的需求：**已登入的使用者**可以進入 event detail view 填 form 點餐。但現在所有使用者都可以看到 `EventDetailView`。而且雖然未登入的使用者不會在店家頁面看到按鈕，但如果他直接送一個 POST request（例如用 cURL）給 `EventCreateView`，還是能建立 event。

在 function-based views 中，我們可以使用 `login_required` decorator。在 CBV 中也可以這麼做——但要記得，真正被使用的是 `as_view()` 回傳的 view，所以我們必須覆寫它，自己把 `login_required` 加上去：

```python
from django.utils.decorators import classonlymethod
from django.contrib.auth.decorators import login_required

class EventDetailView(DetailView):
    # ...
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required(view)
```

不過這如果每次都得這麼做，實在也很麻煩。因為這種權限管理太常見，所以也已經有人把它（與其他常見功能）包成可重用的 app。

我們安裝這個 app：

```
pip install django-braces
```

把 `braces` 加入 `INSTALL_APPS`：

```python
# lunch/settings/base.py

INSTALLED_APPS = (
    # ...
    'braces',
    # ...
)
```

然後就可以這樣用：[註 1]

```python
from braces.views import LoginRequiredMixin

class EventCreateView(LoginRequiredMixin, CreateView):
    # ...

class EventDetailView(LoginRequiredMixin, DetailView):
    # ...
```

方便多了吧。Django Braces 包含了許多常見的功能性 mixin，例如限定只有已登入才能看、只有未登入才能看、可以處理 Ajax（類似之前我們在 FBV 用的 `request.is_ajax` 技巧）等等一大堆。如果你覺得某個功能很常見，或許可以去[他們的文件](https://django-braces.readthedocs.org/en/latest/)看看有沒有現成的 mixin 可用！

現在我們可以保證使用者已經登入，就可以來實作 `post` 處理使用者點餐：

```python
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect

class EventDetailView(LoginRequiredMixin, DetailView):
    # ...
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST)
        if not form.is_valid():
            return HttpResponseBadRequest()
        order = form.save(commit=False)
        order.user = request.user
        order.event = self.get_object()
        order.save()
        return redirect(order.event.get_absolute_url())
```

和之前的做法差不多，我們用 `request.POST` 建立 form，產生 object（但先不要存進資料庫），帶入我們想要的資訊，然後儲存物件，接著重導向回自己（以達到刷新頁面需求）。注意因為 select widget 一定會選擇某個項目（我們之前把空值選項拿掉了），而且 `notes` 可以為空，使得這個表單的值應該永遠合法，所以我們這裡就不處理。[註 2] 不過如果使用者亂搞，我們會在執行 `is_valid` 時發現，並回傳一個 400 Bad Request 給他。

在帶入額外資訊時，注意這裡我們不是使用 `self.object`。如果仔細看看 `DetailView` 的[實作](http://ccbv.co.uk/projects/Django/1.7/django.views.generic.detail/DetailView/)，會發現它在 `get` method 中才呼叫 `get_object`，並把它的值賦給 `self.object`。在進入 `post` 時，我們不會經過 `get` method，所以必須自己呼叫 `get_object`。

大功告成！現在使用者可以點餐，並在上面看到自己與別人的記錄。不過如果使用者已經點過餐，第二次再點就會錯誤——因為我們有設定 `unique_together`，一個使用者在一個 event 只能點一次餐。根據規格，在這時應該要讓使用者能修改自己的點餐內容。明天繼續！

---

註 1：`LoginRequiredMixin` 必須要放在最前面，才能達到效果。詳情請參閱 Django Braces 文件。

註 2：其實有部分原因是要處理錯誤很麻煩，懶得寫。如果你需要在這裡處理錯誤，繼承 `FormView` 而非 `DetailView` 會比較容易實作——或者直接改用一個 function-based view 也可以。Class-based views 不是萬能。
