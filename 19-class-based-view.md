和說好的一樣，今天要來解釋 Django 的 generic view classes——又稱 class-based views，簡稱 CBV——的運作原理。

> CBV 能做到的事情跟 function based view 完全相同，然而由於使用 class，所以當你的 view function 中有很多重複的 code 時（例如一堆 views 都需要要取得相同的 context data 時），這時 CBV 的優勢就在於可以繼承 。
>
> 上章有提到 Django 內建了一些常用的 CBV，然而你會發現根本搞不懂他到底是怎麼運作的、也因此不知該如何用。因為 CBV 做了很多 magic，理解要如何使用 CBV 的最好方法可能就是直接看 CBV 的原始碼，以下將會直接從 CBV 的原始碼下手，帶你理解 CBV 的運作方式。但由於 CBV 做的事情跟你寫 view function 能做的事情其實一模一樣，所以如果下面這篇真的看不懂也沒關係，一樣可以先寫 function based view，等很熟悉整個 view function 的流程時再來理解 CBV。

在開始之前，請打開 <http://ccbv.co.uk>，方便我們追蹤 CBV 裡面的源碼。

所有的 generic views 都必須繼承 `View` class，所以我們從它開始看起。在 **BASE** 下面找到 `View`，按下去！

先複習一下 view 的概念：

               ┌──────────────┐
     request   │              │  response
    ─────────> │     view     │ ──────────>
               │              │
               └──────────────┘

但 View 是個 class，要怎麼像上面這樣被執行？在 `urls.py` 裡的使用方法有給線索：

```python
url(r'^new/$', views.EventCreateView.as_view(), name='event_create'),
```

看起來 `as_view` 似乎是個 class method（或 static method）。我們來看看它的實作。在 CCBV 網頁中找到這一行

```
def as_view(cls, **initkwargs):
```

點下去展開它，就可以看到源碼。看來它做了不少事情，不過可以注意到中間有個 `def` 區塊，宣告了一個叫 `view` 的 function，並且在最後把它回傳出去。所以其實 `as_view()` 被呼叫後，仍然產生一個 view function！

但這個 function 做了什麼事？看看裡面：

```python
def view(request, *args, **kwargs):
    self = cls(**initkwargs)
    # ...
    return self.dispatch(request, *args, **kwargs)
```

所以其實它會呼叫 `dispatch`。來看看這個 method 又是做什麼的：

```python
def dispatch(self, request, *args, **kwargs):
    if request.method.lower() in self.http_method_names:
        handler = getattr(
            self, request.method.lower(), self.http_method_not_allowed
        )
    else:
        handler = self.http_method_not_allowed
    return handler(request, *args, **kwargs)
```

所以它會去找 class 裡有沒有對應於目前 HTTP 動詞的 method 來呼叫，例如 GET request 會呼叫 `get`、POST 會呼叫 `post`，依此類推。但是如果動詞在 `http_method_names` 裡，或者找不到對應的 method，就會呼叫 `http_method_not_allowed`。

似乎有點進展了。我們先不管 `http_method_not_allowed`（其實預設行為就只是回傳一個 405 Method not allowed），來繼續追下去。實作動詞方法是 subclasses 的責任，所以我們來看一個我們有用到的：`DetailView`。

在 CCBV 打開 `DetailView` 的頁面。首先注意到上面有個 **Ancestors (MRO)** 欄位——這裡面寫出了 `DetailView` 的所有 superclasses。[註 1] 可以看到 `View` class 也在其中。

回到原本的主題。打開 `get` 看看！

```python
def get(self, request, *args, **kwargs):
    self.object = self.get_object()
    context = self.get_context_data(object=self.object)
    return self.render_to_response(context)
```

所以我們要先來看 `get_object`。這個 method 做了以下的事情：

1. 呼叫 `get_queryset` 取得一個 `QuerySet` instance（根據你在宣告 class 時指定的 `model` attribute）。
2. 取得 `pk` 或 `slug` 參數。（不討論這部分，反正它會取得合適的欄位名，並從網址中得到參數。）
3. 用上面的參數對 query set 呼叫 `get`，取得所要的物件並回傳。如果物件不存在則 `raise Http404`。

`get_object` 結束後，我們回到 `get` method。接著 `get_context_data` 會回傳一個 `dict`，最後 `render_to_response` 會用這個 `dict` 當作 context、取得指定的 template（預設名稱是 **model 名稱轉成小寫 + _detail.html**，但也可以用 `template_name` attribute 來指定），將它們組合以產生一個 `HttpResponse`。所以這部分我們之前習慣用的 `render` function 差不多！而且這邊的 `kwargs` 是一路從 `dispatch` 傳進來的，所以其實就是 URL pattern 中捕捉到的參數。

把上面一整串展開，其實 `DetailView` 做的事情就是：

1. 檢查 HTTP 動詞是否被允許（類似 `require_http_methods` 的作用）。
2. 根據 URL 中的參數，在指定的 model 中取得一個 instance。
3. 用傳入的參數與前面的 instance 變成 `dict`，準備當作 context。
4. 取得指定的 template。
5. 將 context 與 template 組合產生 HTTP response（預設產生 `HttpResponse` 實例，所以是 200 OK）。
6. 這個 response 會一直往上被回傳，直到最外面的 view function。

所以其實和 view function 做的事情差不多！

我們再來看一個，之前應該也很熟悉的 create pattern。這當然是用 `CreateView` 實作。打開來試試，看看你能不能自己搞懂裡面在做什麼！

其實 `get` 的流程和上面差不多，只是 `CreateView` 不使用 `get_object`，而是用 `get_form` 產生 form class（而且就是使用我們之前用過的 `modelform_factory`！），再與 template（預設名稱是 **model 名稱轉成小寫 + _form.html**，同樣可以自行指定）組合成 response。

`post` 一開始同樣產生了一個 form。但接著就不太一樣了——這時會根據 form 合法與否（同樣使用 `is_valid` method）來決定要走哪一條路。`form_invalid`（不合法）時的結果就和 `get` 一樣，會用 `render_to_response` 產生 response；但如果是 `form_valid`（合法），則會執行 `form.save()` 產生新物件，接著回傳 `HttpResponseRedirect` 導向該 object 的 `get_absolute_url` 結果。

整體而言，其實也和我們自己寫的 function 作用一樣嘛！但是用了 generic view class，就可以把落落長的 create function 縮短到只有三行！真是方便。Django 的 generic view classes 可能在一開始比較不易理解，但一旦你搞懂裡面在做什麼，就可以迅速作出簡單的功能。要寫 Django project 而不學 CBV 就太可惜了！

今天我們一行程式都沒寫，但卻看了一大堆別人的程式，希望還是讓你有收獲。明天我們要繼續寫程式，教你怎麼進一步擴充 class-based views。

---

註 1：注意這不是繼承樹！Python 允許多繼承，且使用 MRO 來解決 diamond problem；這個列表的順序就是 MRO。有興趣的話可以看看[這篇教學](http://makina-corpus.com/blog/metier/2014/python-tutorial-understanding-python-mro-class-search-path)。
