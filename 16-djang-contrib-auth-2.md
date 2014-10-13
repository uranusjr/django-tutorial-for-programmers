我們想在這個專案達成的權限管理如下：

1. 只有已登入的使用者可以刪除店家。
2. 每個使用者都能刪除自己建立的，以及未登入使用者建立的店家。
3. 擁有店家刪除權限的管理員（含超級使用者）可以刪除別人建立的店家。

所以首先要為 `Store` 增加一個 `owner` 欄位，用來記錄建立者。我們已經知道這要用 `ForeignKey` 欄位⋯⋯不過這個 fk 要指向哪裡？

當需要指向其他 app 中的 model 時，foreign key 的目標必須寫成 `appname.ModelName` 的形式。在預設狀況下，使用者的 model 是 `auth.User`。但我們不直接使用它，因為 Django 提供了**替換使用者 model** 的功能，使用者的 model 可以放在別的地方，不一定是 `auth.User`。當你使用自訂使用者 model 時，必須修改設定中的 `AUTH_USER_MODEL` 值，指向你自己的 model。

為了未來維護方便，雖然我們這裡是用預設的 model，還是建議永遠使用設定值，未來維護上會比較方便。所以我們這樣修改 `stores/models.py`：

```python
from django.conf import settings
# ...

class Store(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name='owned_stores',
    )
    # ...
```

接著用 migration 把這個欄位同步進資料庫：

```bash
python manage.py makemigrations stores
python manage.py migrate stores
```

去 admin 看看，store 應該都多了一個 Owner 欄位可以選。

不過如果你現在去 create 與 update view 看，會發現那裡面也多了一個 owner 欄位。我們不想要這樣；這應該直接帶入現在的使用者，而不是讓它們自己選。所以我們要修改一下 form。打開 `stores/forms.py`，把 `StoreForm` 修改成這樣：

```python
class StoreForm(forms.ModelForm):

    class Meta:
        model = Store
        fields = ('name', 'notes',)

    def __init__(self, *args, submit_title='Submit', **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', submit_title))
```

在 `Meta` 中新增的那行 `fields` 告訴 Django 要包含哪些欄位；沒在裡面的就不會出現。

接著我們要在 view 中自動填入目前的使用者。打開 `stores/views.py`，在 `store_create` 中找到這段：（注意 `store_update` 也有一樣的，不要改錯啊！）

```python
if form.is_valid():
    store = form.save()
    return redirect(store.get_absolute_url())
```

改成下面這樣：

```python
if form.is_valid():
    store = form.save(commit=False)
    if request.user.is_authenticated():
        store.owner = request.user
    store.save()
    return redirect(store.get_absolute_url())
```

之前提過，如果呼叫 model form 的 save，Django 就會用 form 中的資料建立一個 model instance，將它儲存至資料庫，接著回傳。但我們現在不想要直接儲存，而是希望先再填入填入一些東西，所以在儲存 form 時我們傳入 `commit=False` 要求 Django 只建立 model instance 就直接回傳，先不要儲存至資料庫。接著我們判斷目前的登入狀況。這裡的 `request.user` 就和 template 中的 user 相同，所以應該不難理解——只要注意 `is_authenticated` 是 method，不是 variable，所以要加後面的括弧。等我們修改完這個 instance 後，再自己呼叫 model 的 `save` method 來將它儲存至資料庫（在預設情況下，model form 的 `save` 會自動幫你呼叫 model 的 `save`）。

試著用已登入與未登入使用者各建立一個店家，在 admin 看看是否有自動填入使用者。

現在我們可以來實作 delete view 了。在 `stores/view.py` 新增：

```python
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

@login_required
@require_http_methods(['POST'])
def store_delete(request, pk):
    try:
        store = Store.objects.get(pk=pk)
    except Store.DoesNotExist:
        raise Http404
    if (not store.owner or store.owner == request.user
            or request.user.has_perm('store_delete')):
        store.delete()
        return redirect('store_list')
    return HttpResponseForbidden()
```

唔，多了好多沒看過的東西。如果你不熟悉 Python decorator，請先[跳轉](http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/)。我們這裡使用了兩個 decorators：

1. `login_required`：限制只有已登入使用者才能進入這個 view。（如果未登入而使用這個 view 會得到 403 Forbidden。）
2. `require_http_methods`：限制這個 view 可以接收的 HTTP methods。這裡我們限制必須使用 POST。[註 1]

所以這個 method 只有已登入的使用者可以用 POST 進入。

接著我們找到 store object，判斷是否可刪除；如果可以，用 `delete` method 達成目的（否則同樣吐一個 403 Forbidden），接著重導向至 `store_list`。

加入這個 URL pattern：

```python
# stores/urls.py

# ...
url(r'^(?P<pk>\d+)/delete/$', views.store_delete, name='store_delete'),
# ...
```

接著在 detail view 加入 delete form：

```html
<form method="post" action="{% url 'store_delete' store.pk %}">
  {% csrf_token %}
  <input type="submit" value="刪除" class="btn btn-danger">
</form>
```

記得 `{% csrf_token %}` 啊。試著用不同的使用者登入（包含不登入），刪除看看有 owner 屬性的店家，看看結果。應該只有刪除自己的會成功，其他通通都會失敗。

不過這失敗的方法好像不太優秀。使用者在不能 delete 時會看到一片白，也不知道究竟發生了什麼事。能不能只在能刪除的時候才顯示刪除按鈕啊？

當然可以，事實上我們在 view 裡面就有判斷這個，只要拿出來重用就好了。不過這就等明天！

---

註 1：如果你熟悉 REST，可能會覺得這裡不該用 POST，應該換成 DELETE。是這樣沒錯，但 Django 由於瀏覽器相容的緣故，預設並沒有支援除了 GET 與 POST 的 methods。這不是無法克服——其實我們明天就會講到怎麼實作。但目前我們就先用 POST 來示範。