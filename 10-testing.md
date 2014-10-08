昨天結束時，我們說要稍微改寫一下目前的程式。不過在那之前，我們得先建立一個方法，確認這些改寫不會破壞網站目前已有的功能。所以我們要來寫測試。我們的網站目前沒什麼特別的功能，所以或許還不需要[單元測試](http://zh.wikipedia.org/zh/单元测试)；但至少我們要確認每個頁面都沒有壞掉。

Django 主要使用 Python 內建的 [unittest](https://docs.python.org/3/library/unittest.html) 模組進行測試，並為它新增了一些相關功能。所有的 Django 測試都可以寫在 app directory 裡的 `tests` 模組。

來跑跑看 Django 的測試指令：

```bash
python manage.py test
```

```
Creating test database for alias 'default'...

----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK
Destroying test database for alias 'default'...
```

因為我們還沒寫任何測試，所以當然什麼都沒有。即使如此，上面的輸出還是有玄機。Django 在測試時會使用一個測試專用的資料庫，並在測試結束時移除它。所以如果你不是使用 SQLite，請確認你的資料庫帳號有**建立資料庫**的權限，且沒有與測試資料庫同名（`test_` 加上正式使用的資料庫名稱）的資料庫。[註 1]

好，開始正式寫測試吧。打開 `stores/tests.py`，加入以下內容：

```python
class HomeViewTests(TestCase):
    def test_home_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
```

如果你沒用過 `unittest` 模組：Python 會自動尋找 `TestCase` subclass 中以 `test` 開頭的 methods 並執行。`assert` 開頭的 method 是測試的重點，失敗的話整個測試就會被標注為 failed；`assertEqual` 是用來測試兩個引數是否相等。

前面說過，Django 擴充了內建的單元測試工具。`client` 是一個虛擬的瀏覽物件，可以用來測試 Django 有沒有正常運作（但並沒有真的發 HTTP request，而是用 mocking 直接測試 URL routing 與 views）。`assertTemplateUsed` 則是 Django 特製的測試方法，用來測試某個 template 是否有真的被用到。

我們來執行看看：

```
$ python manage.py test
Creating test database for alias 'default'...
.
----------------------------------------------------------------------
Ran 1 test in 0.012s

OK
Destroying test database for alias 'default'...
```

這樣就代表測試成功。把測試內容改一改，故意讓它失敗（例如把 200 改成 201），看看輸出有什麼不同！

接著我們要來測試店家列表與內容頁。不過記得，測試資料庫是另外建立的，所以裡面什麼東西都沒有。我們要想辦法餵東西進去，才有店家資料可以測。為了這個目的，我們必須在每個測試執行之前，都先執行一些程式（建立物件）；並在它們結束之後執行另一段程式（清除物件）。在 `unittest` 裡面，是用 `setUp` 與 `tearDown` 來進行這些工作：

```python
from .models import Store

class StoreViewTests(TestCase):

    def setUp(self):
        Store.objects.create(name='肯德基', notes='沒有薄皮嫩雞倒一倒算了啦')

    def tearDown(self):
        Store.objects.all().delete()
        
    def test_list_view(self):
        r = self.client.get('/store/')
        self.assertContains(
            r, '<a class="navbar-brand" href="/">午餐系統</a>',
            html=True,
        )
        self.assertContains(r, '<a href="/store/1/">肯德基</a>', html=True)
        self.assertContains(r, '沒有薄皮嫩雞倒一倒算了啦')
```

我們用到了一個 manager method `create`，以及一個 query method `delete`。用法應該很直觀，就不特別解釋了。

測試中的 `assertContains` 可以用來檢查 Django 回傳的內容中是否有包含某些特定值。這可以用來檢查純文字，也可以用來檢查 HTML（設定 `html=True`）。在後者的狀況中，Django 會自動把空白與換行等符號去掉，所以即使你不需要寫出與輸入的 HTML 完全相等的測試字串；只要語意上相等即可。

最後是店家內容：

```python
    def setUp(self):    # 修改原本的內容。
        Store.objects.create(name='肯德基', notes='沒有薄皮嫩雞倒一倒算了啦')
        # 新增下面這兩行。記得 import MenuItem。
        mcdonalds = Store.objects.create(name='McDonalds')
        MenuItem.objects.create(store=mcdonalds, name='大麥克餐', price=99)
        
    def test_detail_view(self):
        response = self.client.get('/store/2/')
        self.assertContains(
            response, '<tr><td>大麥克餐</td><td>99</td></tr>',
            html=True,
        )
```

寫太多感覺好像在騙篇幅，所以我就只列一些。事實上在這裡我們同樣應該測試 `store.name`、`store.notes` 與 nav bar 有沒有正確顯示。

這裡也可以看到，其實 `create` 會回傳你剛剛建立的物件，而且可以直接傳入 foreign key 欄位。另外，我們刻意在測試中使用寫死的路徑，而不是 `reverse`——因為我們就是想知道這些路徑的結果；如果壞掉了，我們應該要被通知。

這樣我們應該該測的都有測到了。跑起來看看吧！三個測試都應該成功。有了這些測試，我們改起程式就更有底氣。明天我們會著手進行。

---

註 1：資料庫名稱可以改；如果你沒有合適的權限，也可以手動建立後告訴 Django 不要自己建。不過這些設定就超過本文範圍了。