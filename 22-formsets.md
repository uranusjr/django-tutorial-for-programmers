其實這個內容跟本應該放在更前面，只是我**忘記了**，所以只好現在補講。昨天我們說要做讓使用者修改點餐的功能，就先延到明天。

我們現在可以在 admin 新增修改店家與菜單內容，但是在一般頁面中只能新增修改店家，不能修改菜單（雖然已經加入的會被列出）。我們可以像店家的表單一樣，把它獨立成一個 model form，但是這種做法有個問題：一次只能新增一個項目。要怎麼像 Django Admin 那樣，有個表格可以一次建立很多個項目？

答案就是 formsets。事實上 admin 裡的那個表格就是用它做的！顧名思義，一個 formset 就是「很多表單的集合體」。這有很多用途，例如一次讓使用者上傳很多圖片，或者更常見的，是用來處理一對多關係中的多個項目。

在這裡，我們想要建立指向某個 `Store` object 的 `MenuItem` model instances。所以我們可以使用內建的 factory method：

```python
# stores/views.py

from django.forms.models import inlineformset_factory
from .models import MenuItem

def store_update(request, pk):
    # ...
    MenuItemFormSet = inlineformset_factory(
        parent_model=Store, model=MenuItem, extra=1,
    )
    menu_item_formset = MenuItemFormSet(instance=store)
    return render(request, 'stores/store_update.html', {
        'form': form, 'store': store, 'menu_item_formset': menu_item_formset,
    })
```

之前已經看過 `modelform_factory`，這裡的用法類似，只是我們需要多指定一個 `parent_model` 參數，Django 才知道要用哪一個 foreign key 建立一對多關聯。[註 1] 在 `instance` 指定 foreign key 指向的 parent instance，Django 就會自動幫你把關聯的物件預先取出，並根據 `extra` 的數值增加空白欄位。

在 template 中顯示這個 formset：

```html
{# stores/templates/stores/store_update.html #}

{# ... #}

{% crispy form %}
{% crispy menu_item_formset %}   <!-- 新增這一行 -->
```

選一個店家，按「更新店家資訊」進去，應該會看到下面多出了可以填入菜單的欄位！不過這些欄位還沒有作用，因為它們沒有在 form tag 裡面，我們也還沒在 post method 實作儲存。

首先為 menu item formset 實作一個 helper，把我們不需要的東西清掉：

```python
# stores/forms.py

from django.forms.models import inlineformset_factory
from .models import MenuItem

BaseMenuItemFormSet = inlineformset_factory(
    parent_model=Store, model=MenuItem, fields=('name', 'price',), extra=1,
)

class MenuItemFormSet(BaseMenuItemFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False        # 我們要自己包。
        self.helper.disable_csrf = True     # StoreForm 已經有 CSRF token，不需要重複產生。
```

把 `store_update` 改成下面這樣：

```python
from .forms import MenuItemFormSet

def store_update(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store, submit_title='更新')

        # 用 post data 建立 formset，並在其（與 store form）合法時儲存。
        menu_item_formset = MenuItemFormSet(request.POST, instance=store)
        if form.is_valid() and menu_item_formset.is_valid():
            store = form.save()
            menu_item_formset.save()
            return redirect(store.get_absolute_url())
    else:
        # 移除 submit button 與 form tag。
        form = StoreForm(instance=store, submit_title=None)
        form.helper.form_tag = False

        menu_item_formset = MenuItemFormSet(instance=store)

    return render(request, 'stores/store_update.html', {
        'form': form, 'store': store, 'menu_item_formset': menu_item_formset,
    })
```

注意有註解的段落。接著在 template 中手動加上 form tag 與 submit button：

```html
{# stores/templates/stores/store_update.html #}

{# 替換 content block 的內容 #}
<form method="post">
  {% crispy form %}
  {% crispy menu_item_formset %}
  <button type="submit" class="btn btn-primary">更新</button>
</form>
```

這樣結構就正確了！新增刪除幾個項目看看吧。

接著我們要實作 admin 裡面新增欄位的功能。在實作之前，我們必須先了解 formset 的運作原理。每個 formset 其實都分為兩個部分：

1. Management form，裡面包含四個欄位：
    * Total forms，代表目前 formset 中有幾個 forms。
    * Initial forms，代表「一開始」有幾個 forms。
    * Minimum 與 maximum forms，代表最多與最少可以有幾個 forms。這可以在建立 formset 時指定，但我們這裡不管，就用預設值（最少 0 個，最多可以有數千個，應該夠用）。
2. Form 列表，包括原本已經存在的項目，以及 `extra` 參數指定的額外空白項目。表單數量會和 initial forms 的值相等。

所以我們可以這樣實作新增欄位按鈕：

1. 按下按鈕時，clone 一個 formset 中的 form。
2. 修改 form 中的 ID 與標籤，讓它能被 Django 識別。
3. 修改 total forms 參數，讓 Django 知道欄位數量有變。

這個動作的主要用意是讓我們可以自訂 menu item form 的格式；我們需要用一個 `div` 把每個單獨的 form 包起來，並為它加上 CSS class。

修改 `store_update.html`：

```html
<!-- 引入 "static" tag -->
{% load staticfiles %}

<!-- 替換原本的 content block -->
{% block content %}
<form method="post">
  {% crispy form %}

  <!-- 手動一個一個產生 formset 中的 forms，並在它們外面包一層 div -->
  {{ menu_item_formset.management_form }}
  {% for form in menu_item_formset %}
    <div class="menu-item form-group">
      {% crispy form menu_item_formset.helper %}
    </div>
  {% endfor %}

  <!-- 增加這行 -->
  <a href="#" class="menu-item-add btn btn-default">新增菜單項目</a>
  <button type="submit" class="btn btn-primary">更新</button>
</form>
{% endblock content %}

<!-- 加上這個 block -->
{% block js %}
{{ block.super }}
<script src="{% static 'stores/js/store_update.js' %}"></script>
{% endblock js %}
```

這裡注意到 `crispy` tag 其實可以接受第二個參數，動態在 template 中指定要用的 form helper。我們這裡讓所有 formset 中的 forms 都沿用 formset 的 helper。

最後建立 `stores/static/stores/js/store_update.js`，實作新增欄位：

```javascript
(function ($) {

$('.menu-item-add').click(function (e) {
  e.preventDefault();

  var lastElement = $('.menu-item:last');
  var totalForms = $('#id_menu_items-TOTAL_FORMS');
  var total = totalForms.val();

  var newElement = lastElement.clone(true);
  newElement.find(':input').each(function() {
    var name = $(this).attr('name').replace(
      '-' + (total - 1) + '-',
      '-' + total + '-'
    );
    var id = 'id_' + name;
    $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
  });
  newElement.find('label').each(function() {
    $(this).attr('for', $(this).attr('for').replace(
      '-' + (total - 1) + '-',
      '-' + total + '-'
    ));
  });

  totalForms.val(total + 1);
  newElement.insertAfter(lastElement);
});

})(jQuery);
```

這段 JavaScript 會找到 formset 中的最後一個項目（所以我們前面要用 div 把每個 form 包起來，這裡才能方便使用）clone 一份，修改其中欄位的 ID 與 name，把原本的值清除，把它 insert 到最後面，再修改 total forms 欄位值。這看起來實在非常麻煩，幸好除非你對 form 做了什麼奇怪的實情，否則這個 script 基本上可以一直沿用下去，只要修改 `lastElement` 與 `totalForms` 的 selector 就好了。[註 2]

重新整理看看！「更新」旁邊應該會多一個「新增」按鈕，可以用來動態新增欄位。

終於完成了！下週我們會回到正常進度。


---

註 1：你或許會問，如果有不止一個 foreign key 指向同一個 model，Django 要怎麼知道應該使用哪一個？為了避免這種狀況，其實 `inlineformset_factory` 可以接受一個叫 `fk_name` 的參數，讓你指定欄位名稱。但在這裡 `MenuItem` 只有一個 foreign key 指向 `Store`，所以不需要指定這個參數，Django 會自動偵測。

註 2：如果你仔細看產生的 HTML，會發現我們沒有改到所有元件的 IDs，只改了 input 欄位。這樣就足夠讓 Django 正確反應，不過如果你有 CSS 或 JavaScript 需求，必須讓所有的元件都被正確修改，或許用 JavaScript template engine（Mustache、Underscore.js 的範本、或者 Handlebars 等等）來產生會是更好的選擇。不過這就超出這個教學的範圍了。
