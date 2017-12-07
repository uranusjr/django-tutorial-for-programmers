Django 自稱 MTV 框架，把自己分成三個部分：models、templates、views。如果你最近學過開發框架（web 或 GUI 或其他的），可能會比較熟悉 MVC（model—view—controller）結構，不過這些東西概念上基本是一樣的。在 Django 中：

* Models 代表資料，通常是用來與資料庫溝通。
* Templates 代表把東西呈現給使用者的媒介。
* Views 用來處理 models，以將其呈現於 templates 中，或者處理使用者送來的資料（以 HTTP POST 等方式），並存入 models。

在實務上，Django templates 的角色比較像 MVC 的 views，但是比起後者，templates 承擔的責任更少，只負責資料呈現，而幾乎不包含任何邏輯（除非是用來呈現的邏輯）。Django views 則比較位於 MVC 的 views 與 controllers 之間。但 MVC 中 controllers 的邏輯不全然包含於 Django views；Django 通常習慣把部分邏輯放在 models，並且提供了一些額外的工具，來簡化 views 需要承擔的責任。我們之後也會稍微介紹一下這些東西。但即使如此，Django views 仍然會像 MVC 的 controllers 一樣，負責連結 models、templates、以及 Django 提供的其他工具。

不論如何，在使用這類框架時，我們通常都是從設計 models 開始。所以首先來想想 lunch 這個專案應該包含哪些元件。我們（好啦，我）希望這個程式有兩個部分：

* 使用者註冊與登入。
* 列出與顯示店家資訊，包括名稱與菜單圖片。使用者可以自由新增、修改、刪除。
* 選取一家店，讓每個使用者可以填入自己想吃什麼。

我們可以使用 Django 內建的使用者認證功能處理第一部分，所以這先放著。第二與第三部分功能基本上是分開的（雖然第三部分會需要用到第二部分的功能），所以在 Django 中，我們會把它們各自放在不同的 **app** 裡面。如果你使用過其他 web 框架，可能會覺得這個名稱很怪——app 不是應該代表整個網站嗎？嗯，不管怎樣，反正在 Django 中，網站叫做 *project*，而組成網站的元件則是 *app*。習慣就好。每個 Django app 事實上也會是個完整的 Python module，所以可以獨立變成一個可安裝的 Python 函式庫。所以在 Django 中，很重視各 app 之間的獨立性。當然 app 可以 depend on 另一個 app，但兩個 apps 不應該互相需要對方；責任必須劃分清楚。不過這應該是很基本的設計概念吧。

現在開始來實作第二部分。Django 提供了一個指令，可以方便你建立 app：

```bash
pipenv run python manage.py startapp stores
```

這會建立一個叫 `stores` 的目錄，用來包裝我們的 app（其名稱就是 `stores`）。在 Django 中，通常習慣把 app 取名為它主要功能的 model 的複數形。這個 app 主要負責的是管理店家，所以我們會把主要的 model 取名為 `Store`。所以 app 名稱就是 stores 了。注意 Python 習慣把 module 取名為全小寫（可以使用底線），而既然 Django app 本身是 Python module，所以也應該遵從相同的命名規則。

我們還要讓 Django 知道這個 app 的存在。打開 `lunch/settings/base.py`，把 `stores` 這個 app 加入 `INSTALLED_APPS` 列表：

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'stores',
]
```

Django 並沒有硬性規定 app 的順序，不過一般除了有特殊理由（例如需要覆蓋內建的元件），都會把自己的 apps 排在最面。大致上的規則和 Python 的 import 習慣類似：先放內建，再來第三方套件，最後是自己的。

現在看看你的專案目錄：

```
lunch
├── lunch
│   ├── settings
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── local.py
│   ├── __init__.py
│   ├── urls.py
│   └── wsgi.py
├── stores
│   ├── migrations
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── manage.py
```

`stores` 裡面各項目的用途如下：

* `migrations` 存放 database migration，也就是資料庫結構改變的資料。這些檔案通常不會直接被執行，而是在你透過 Django 指令改變資料庫結構時，用來提示 Django 你的資料在某個時間點的結構。
* `admins.py` 設定 Django admin。
* `apps.py` 設定 app 的性質（例如在 admin 裡的名稱）。
* `models.py` 和 `views.py` 放 models 和 views 的程式。
* `tests.py` 放單元測試。

如果你不需要某些檔案，其實可以刪除它們；如果你有其他需求，也同樣可以另外新增其他檔案與目錄。不過我們首先會先使用預設產生的檔案。明天我們要來看看 `views.py`，為你的網站建立第一個（不是預設的）頁面。
