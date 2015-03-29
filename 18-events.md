店家的部分差不多完成了，接著我們來實作點餐部分。因為畫圖很麻煩（喂），我們直接上程式。首先建立 `events` app：

```bash
python manage.py startapp events
```

把它加入設定：

```python
# lunch/settings/base.py

INSTALLED_APPS = (
    'events',
    # ...
)
```

然後建立 models：（該 import 的自己記得加）

```python
# events/models.py

class Event(models.Model):

    store = models.ForeignKey('stores.Store', related_name='events')

    def __str__(self):
        return str(self.store)

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})


class Order(models.Model):

    event = models.ForeignKey('Event', related_name='orders')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders')
    item = models.ForeignKey('stores.MenuItem', related_name='orders')
    notes = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('event', 'user',)

    def __str__(self):
        return '{item} of {user} for {event}'.format(
            item_name=self.item, user=self.user, event=self.event
        )
```

現在你應該可以看懂絕大部分的內容了（`reverse` 的部分先不管，我們之後再建這個 URL pattern）。但好像還是有個新東西——什麼是 `class Meta`？

我們之前在討論 model form 時，就有用到 meta。這並不是 Python 的 [metaclass](http://python-3-patterns-idioms-test.readthedocs.org/en/latest/Metaprogramming.html)，而是 Django 用來提示某個 class 應該擁有什麼屬性的工具。以 model form 而言，在 meta 中指定 `model` 屬性，就可以讓 Django 自動把該 model 中的某些欄位增加至 form 中，並且在 form 被 save 時自動產生對應的 model instance；model meta 則可以用來描述這個 model 的一些性質，以及跨欄位間的關聯。這裡我們指定了 `unique_together`，代表 `event` 和 `user` 這兩個欄位的組合必須 unique——限制一個使用者只能在一次 event 中點一次餐。

把 models 對應的 tables 建出來：

```base
python manage.py makemigrations events
python manage.py migrate events
```

順便把它們也加入 admin：

```python
# events/admin.py

from django.contrib import admin
from .models import Event, Order

class OrderInline(admin.StackedInline):
    model = Order
    extra = 1

class EventAdmin(admin.ModelAdmin):
    inlines = (OrderInline,)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('event', 'item', 'user',)

admin.site.register(Event, EventAdmin)
admin.site.register(Order, OrderAdmin)
```

應該都不用解釋了。我們這裡用 `StackedInline` 替換了 `stores` 裡面用的 `TabularInline`，不過它們只有外觀不同（一個是 div-based，一個是 table-based），用起來效果一樣。

接著是 views。我們想要達成以下的效果：

1. 已登入的使用者可以在 store detail view 看到一個按鈕，按下去可以根據該店家建立新 event 讓大家來點餐。
2. 建立完 event 後進入 event detail view。
3. 所有人的點餐都會記錄在 event detail view 裡面。
4. 已登入的使用者可以進入 event detail view 填 form 點餐。點完之後頁面會重新整理顯示最新狀態。
5. 使用者也可以在同一頁面修改或刪除自己的 order。

所以我們需要為 event 與 order 建立 CRUD 頁面。當然，我們可以和前面一樣，建立需要的 model forms 與 views。不過你不覺得做的事情都重複了嗎？這樣一直寫一樣的東西就飽了！

所以 Django 提供了一個簡化 view 撰寫的工具：generic views。為了達到重用並保持擴充性，generic views 是用 class 配合 factory function 實作（有興趣的話可以[看源碼](http://ccbv.co.uk/projects/Django/1.7/django.views.generic.base/View/)），所以我們不再需要宣告 view functions，而是要繼承 Django 提供的 generic view *classes*。但這些類別裡面做的事情，其實還是和 view functions 相同。

常用的 generic views 有：

* `DetailView`：顯示**一個** model instance 的內容。
* `ListView`：顯示「**數個**」model instances（用 queryset 表示）的內容。支援 pagination。
* `CreateView`：顯示**一個** model form，接收 GET 與 POST 以建立 model instance。
* `UpdateView`：和 `CreateView` 類似，但是是用來更新 model instance（會指定 model form 的 `instance` 參數）。
* `DeleteView`：接收 POST 以刪除 model instance。也可以接收 GET，會顯示一個刪除用的 form（類似 admin 刪除時會出現的確認頁面）。
* `TemplateView`：顯示某個特定的 template 內容。
* `RedirectView`：回傳 `redirect` response。

這些 view classes 都是用 `django.views.generic.View` 與許多 [mixins](http://blog.csdn.net/gzlaiyonghao/article/details/1656969) 組成，所以如果你有一天想做一些沒有內建功能的 view，也不見得就要自己從頭寫 function；說不定你可以重用一些 mixins 來達成目標！

再說下去也有點空泛，我們直接上例子。首先建立 model form：

```python
# events/forms.py

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Event


class EventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ('store',)

    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', submit_title))
```

把 `events/views.py` 的內容換成這樣：

```python
from django.views.generic import CreateView, DetailView
from .models import Event
from .forms import EventForm

class EventCreateView(CreateView):
    form_class = EventForm
    model = Event

class EventDetailView(DetailView):
    model = Event
```

然後建立下面三個 templates：

```html
{# events/templates/events/base.html #}

{% extends 'base.html' %}

{% block body %}
{{ block.super }}
<div class="container">{% block content %}{% endblock content %}</div>
{% endblock body %}
```


```html
{# events/templates/events/event_form.html #}

{% extends 'events/base.html' %}
{% load crispy_forms_tags %}

{% block content %}
{% crispy form %}
{% endblock content %}
```

```html
{# events/templates/events/event_detail.html #}

{% extends 'events/base.html' %}

{% block content %}
<h1>今天吃：{{ event }}。快點餐！</h1>
{% endblock content %}
```

最後是 URL patterns。建立 `events/urls.py`

```python
from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns(
    '',
    url(r'^new/$', views.EventCreateView.as_view(), name='event_create'),
    url(r'^(?P<pk>\d+)/$', views.EventDetailView.as_view(),
        name='event_detail'),
)
```

然後把它包含到 `lunch/urls.py`：

```python
urlpatterns = patterns(
    # ...
    url(r'^event/', include('events.urls')),
    # ...
)
```

完成！去 <http://localhost:8000/event/new/> 新增一個 event。按下 **Submit** 後，你應該會直接被導向 event 的 detail view。

有跟上嗎？為什麼 views 可以這樣找到 templates，而且建立後還能自動重導向？這就是 generic views 的威力——對於簡單的應用而言，幾乎不用設定任何東西，就可以寫出你要的架構。我們明天會詳細解釋它們究竟做了什麼。
