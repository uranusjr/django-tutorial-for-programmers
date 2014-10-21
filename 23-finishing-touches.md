今天我們要完成這個網站。

第一件事情，是要讓使用者可以修改點餐內容。其實需要用到的東西我們之前都提過了，只需要實行而已。在 `EventDetailView` 新增一個 method：

```python
# events/views.py

class EventDetailView(LoginRequiredMixin, DetailView):
    # ...
    def get_order(self, user):
        try:
            order = Order.objects.get(user=user, event=self.get_object())
        except Order.DoesNotExist:
            order = None
        return order
    # ...
```

注意這裡同樣要使用 `get_object`，因為我們不只會在 `get` 時使用這個 method。

接著在 `get_context_data` 中，用它取出當下使用者的 order：

```python
def get_context_data(self, **kwargs):
    # ...
    order = self.get_order(user=self.request.user)
    # 取代原本初始化 OrderForm 的那行。
    order_form = OrderForm(instance=order)
    # ...
```

這樣就可以在使用者已經有 order 時（`get_order` 會回傳非 `None` 的值），在 form 中直接顯示原本 order 的內容。

接著，如果使用者有更新，我們同樣要先嘗試找到已有的 order；如果找不到才新增：

```python
def post(self, request, *args, **kwargs):
    order = self.get_order(user=request.user)
    form = OrderForm(request.POST, instance=order)
    # ... 後略。
```

就這麼簡單！現在使用者在點過餐後，下面的表單會直接顯示他之前點餐的內容。如果使用者再次送出表格，就會更新既有的點餐內容，而不是新增（而造成錯誤）。

現在我們可以建立活動，但除了直接給活動網址外，根本沒辦法讓其他使用者看到現在的活動。所以接著我們要在首頁加上一個連結，讓大家能進來點餐。首頁上的連結應該動態指向最新的活動，但「最新的」是哪一筆？在我們這個例子裡，會是 primary key 最大的那一筆，也就是最近新增的活動。在 SQL 中，我們可以用 `MAX` 函式來取得這個最大值，但 Django 的 ORM 要怎麼做？

有兩種做法。第一種是用排序，然後取出最新一筆：

```python
current_event = Events.obejcts.order_by('-pk')[0]
```

`order_by` method 的作用和 SQL 的 `ORDER BY` 類似，但當你要指定排序時，不是使用 `ASC` 與 `DESC` 修飾，而是使用 `-` 號。這裡的 `-pk` 代表使用 primary key 反向排序（同 `DESC`）；如果是 `pk`，則會是正向排序（同 `ASC`）。

但這有個問題。如果沒有第一筆，那麼上面的程式會產生 `IndexError`。當然我們可以用一個 `try-catch` block 把它包起來，不過因為這種格式實在太常見，Django 提供了一個方便的 method 來處理：

```python
current_event = Events.obejcts.order_by('-pk').first()
```

或者，如果要更直觀：

```python
current_event = Events.obejcts.order_by('pk').last()
```

另一種做法是把 `Event` 的 `Meta` 改成下面這樣：

```python
class Meta:
    get_latest_by = 'pk'
```

接著你可以這樣取出最新一筆：

```python
current_event = Events.obejcts.lastest()
```

這個做法的好處是，如果你的 model 有很明確的排列順序（例如 blog post 或新聞會依發表時間排序等等），這個做法可以讓你集中邏輯，方便讓你未來知道「最新」的意義，在維護上與城市的語義都比較清楚。另一方面，`first` 與 `last` 就只是單純用來告知「目前這個 query set」的狀態，適合用在特定的排序上。[註 1]

由於 event 使用 primary key 排序是很普遍的做法，不是特殊排序，我們這裡使用後者。修改 `home` view，取出合適的 event instance 來使用：

```python
# pages/views.py

from events.models import Event

def home(request):
    try:
        current_event = Event.objects.latest()
    except Event.DoesNotExist:
        current_event = None
    return render(request, 'pages/home.html', {'current_event': current_event})
```

然後在 template 中使用：

```html
{# pages/templates/pages/home.html #}

{% extends 'pages/base.html' %}

{% block body %}
{{ block.super }}

<div class="container">
  {% if current_event %}
  <div class="row">
    <div class="col-md-6 col-md-offset-3">
      <div class="text-center">
        <h1>今天吃：{{ current_event }}。</h1>
        <a href="{{ current_event.get_absolute_url }}" class="btn btn-primary btn-lg btn-block">快點餐！</a>
      </div>
    </div>
  </div>
  {% endif %}
</div>

{% endblock body %}
```

完成！這樣網站就做得差不多了。明天我們會進入最後階段，教你怎麼 deploy 這個網站，包括 PaaS（用 Heroku 為例）與一般的 Un*x Server（Windows 就⋯⋯再看看）。

---

註 1：另外要注意一點：`latest`（與它的兄弟 `earliest`）會在找不到內容時產生 `IndexError`，不會像 `first` 與 `last` 那樣回傳 `None`。所以使用這兩個 methods 時要確認資料庫中有對應值。