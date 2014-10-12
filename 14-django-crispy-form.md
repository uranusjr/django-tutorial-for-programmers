Django 預設的 form 格式實在不好看。如果我們想要，也可以每個 widget 自己輸出，例如：（以 create form 為例）

```html
<form action="" method="post" role="form">
  {% csrf_token %}
  <div class="form-group{% if form.name.errors %} has-error{% endif %}">
    <label for="{{ form.name.auto_id }}" class="control-label">{{ form.name.label }}</label>
    <input type="text" class="form-control" id="{{ form.name.auto_id }}" name="{{ form.name.name }}">
    {% for error in form.name.errors %}
    <p class="help-block">{{ error }}</p>
    {% endfor %}
  </div>
  <div class="form-group{% if form.notes.errors %} has-error{% endif %}">
    <label for="{{ form.notes.auto_id }}" class="control-label">{{ form.notes.label }}</label>
    <textarea class="form-control" id="{{ form.notes.auto_id }}" name="{{ form.notes.name }}" rows="10"></textarea>
    {% for error in form.notes.errors %}
    <p class="help-block">{{ error }}</p>
    {% endfor %}
  </div>
  <button type="submit" class="btn btn-primary">建立</button>
</form>
```

如果你難以理解上面的東西，好像也不奇怪，因為這真的有點麻煩。幸好這種重複性高又繁瑣的東西早就有人幫你做好了。


## 第三方套件：Django Crispy Forms

我們來用第三方套件 Django Crispy Forms 來快速美化 form。首先安裝：

```bash
pip install django-crispy-forms
```

在 `lunch/settings/base.py` 裡設定：

```python
INSTALLED_APPS = (
    # ...
    'crispy_forms',     # 新增這個 app。我習慣放在自己的 apps 與 Django apps 中間。
)

# 新增這個設定
CRISPY_TEMPLATE_PACK = 'bootstrap3'
```

然後就可以使用了。把 `store_create.html` 改成這樣：

```html
{% extends 'stores/base.html' %}
{% load crispy_forms_tags %}

{% block title %}建立店家 | {{ block.super }}{% endblock title %}

{% block content %}
<form action="" method="post" role="form">
  {% csrf_token %}
  {{ form|crispy }}
  <button type="submit" class="btn btn-primary">建立</button>
</form>
{% endblock content %}
```

我們其實只改了兩行：

1. 在 `extends` tag 下面加上 `load` tag。這個 tag 類似 Python 的 import，可以把某個 template tag library 讀進來。

2. 把 `{{ form.as_p }}` 改成 `{{ form|crispy }}`。這個語法叫做 template filter，可以想成是很簡單的 Python function。例如 `crispy` filter 就差不多對應到下面的 Python function：

    ```python
    def crispy(form):
        # ... 處理
        return something
    ```
    
Django template filter 還有很多玩法。例如用來把日期轉字串的 `date` filter 可以多吃一個參數，像這樣：

```html
{{ created_at|date:'Y-m-d' }}
```

就類似於這樣的函數呼叫：

```python
date(created_at, 'Y-m-d')
```

詳情請看[文件](https://docs.djangoproject.com/en/1.7/ref/templates/builtins/#built-in-filter-reference)！

重新整理看看，你的 form 應該瞬間變得很 Bootstrap 了。而且如果表單有誤（例如 `name` 留空），錯誤訊息也會有合適的格式！

Update 頁面也可以用同樣的方式美化。自己試試看！希望你可以自行參透，不過如果你卡關，答案在下面：

```html
{% extends 'stores/base.html' %}
{% load crispy_forms_tags %}

{% block title %}更新 {{ store.name }} | {{ block.super }}{% endblock title %}

{% block content %}
<form action="" method="post" role="form">
  {% csrf_token %}
  {{ form|crispy }}
  <button type="submit" class="btn btn-primary">更新</button>
</form>
{% endblock content %}
```

繼續新增更新幾個店家試試。表單的行為應該完全不會變，只有外觀不同。

## Model Forms

但其實 Crispy Forms 的威力不僅止于此。它還支援自訂 layout，以及自動幫你產生 `<form>` tag、CSRF token tag、甚至 submit button！不過要使用這些功能之前，我們得稍微改寫一下 Django form。

在 `stores` 裡新增 `forms.py`，加入以下內容：

```python
from django import forms
from .models import Store

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
```

接著把 `stores/views.py` 裡的下面幾行刪除：

```python
from django.forms.models import modelform_factory

StoreForm = modelform_factory(Store)   # 在 create 與 update 各有一行
```

並加上這一行：

```python
from .forms import StoreForm
```

基本上我們就是把產生 `StoreForm` 的方法替換，並將它拿到另一個檔案裡。這樣產生出來的結果與 `modelform_factory` 一模一樣。要使用什麼方法則視你的需求而定；在一般狀況下，直接使用 `modelform_factory` 就很夠，不過如果你要自訂比較多東西，直接 subclass `ModelForm` 會更方便一些，擴充性比較好，也比較容易維護。

馬上來擴充一下 `StoreForm`：

```python
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class StoreForm(forms.ModelForm):

    class Meta:
        model = Store

    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', submit_title))
```

如果你不太熟悉 Python 語法，`args` 與 `kwargs` 代表[可變參數](http://www.cnblogs.com/fengmk2/archive/2008/04/21/1163766.html)。我們在這裡使用它們，以免得需要寫出所有 `ModelForm` 的 init 參數——反正我們用不到，只想把它們 relay 進 `super().__init__` 而已。`submit_title` 是一個 [keyword-only argument](http://blog.gahooa.com/2009/12/08/python-has-keyword-only-parameters/)，代表我們必須在呼叫時明確指定它的名稱，而不能直接傳。這保證我們不會因為誤傳，而不小心覆蓋到 `ModelForm` 原本的 init 參數（除非它也有定義一模一樣名稱的參數——應該不會）。

為了讓 Crispy Forms 協助我們處理表單，我們加入了一個 `helper` attribute，並且告訴它為我們加上一個 submit button。

接著把 create 與 update templates 裡的 form tag 通通刪掉，換成下面這行：

```html
{% crispy form %}
```

換完之後你的 `content` block 應該就只會剩下這一行。

重新整理。看起來好像還是差不多，不過程式碼又更精簡了！

為了讓 create 與 update view 中的 submit button 顯示不同的內容，我們可以在 view function 中使用前面的 `submit_title` 參數。修改後應該會像這樣：

```python
def store_create(request):
    if request.method == 'POST':
        form = StoreForm(request.POST, submit_title='建立')   # 注意這行
        if form.is_valid():
            store = form.save()
            return redirect(store.get_absolute_url())
    else:
        form = StoreForm(submit_title='建立')                 # 注意這行
    return render(request, 'stores/store_create.html', {'form': form})


def store_update(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        # 注意這行
        form = StoreForm(request.POST, instance=store, submit_title='更新')
        if form.is_valid():
            store = form.save()
            return redirect(store.get_absolute_url())
    else:
        # 注意這行
        form = StoreForm(instance=store, submit_title='更新')
    return render(request, 'stores/store_update.html', {
        'form': form, 'store': store,
    })
```

今天就到這裡。恭喜你有個（比較）好看的表單了！你可以參考 Crispy Forms 的文件，把它弄得更好看一些，例如改成 horizontal form 之類的。明天我們會進入下一個主題：使用者認證，以準備實作 delete 功能。