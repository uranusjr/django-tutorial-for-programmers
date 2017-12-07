我們的 `stores` app 負責管理店家資訊，所以顯然我們需要有一個 `Store` model。這個 model 裡面要可以存店家名稱與菜單的圖片。菜單上的項目當然不止一個，所以它與店家之間是多對一關聯。我們知道，多對一需要一個 foreign key，所以我們還需要另一個 model，用來放菜單項目。它們之間的關聯會像下面這樣：

    ┌───────────────┐           ┌───────────────┐
    │     Store     │           │   MenuItem    │
    ├───────────────┤           ├───────────────┤
    │ name          │           │ name          │
    │ note          │ 1       n │ price         │
    │ menu_items    │ <──────── │ store         │
    └───────────────┘           └───────────────┘

`Store` 有兩個資料欄位，分別儲存店家名稱與其他資訊；`MenuItem` 也有兩個資料欄位，一個用來存圖片檔案位置，另一個則是圖片標題（用在 HTML `alt` tag）。`MenuItem` 另外有一個指向 `Store` 的 foreign key，叫做 `store`；這個 FK 在 `Store` 的 reverse attribute 則叫做 `menu_items`。

好了，現在我們要把上面的結構轉換為 Django model 定義。打開 `stores/models.py`，加入以下的內容（記得保留第一行的 `import`）：

```python
class Store(models.Model):

    name = models.CharField(
        max_length=20,
    )
    notes = models.TextField(
        blank=True, default='',
    )

    def __str__(self):
        return self.name


class MenuItem(models.Model):

    store = models.ForeignKey(
        to=Store, related_name='menuitem_set',
    )
    name = models.CharField(
        max_length=20,
    )
    price = models.IntegerField(
    )

    def __str__(self):
        return self.name

```

在 Django 中，一個 model 就是一個 class。所有的 Django models 都必須繼承 `django.db.models.Model`。我們在兩個 models 中依照上面的結構，加入合適的欄位。各欄位形態的意義如下：

* `CharField` 對應到資料庫的 `VARCHAR`。`max_length` 參數代表 `VARCHAR` 的長度。[註 1]
* `TextField` 對應到 `TEXT`。`blank=True` 代表本欄位可空白（注意不是可為 `NULL`！可為 `NULL` 的欄位是使用 `null=True`，我們這裡沒有用到）；`default` 代表如果你在建立 `Store` 物件時沒有輸入本欄位，預設會使用的值。
* `IntegerField` 對應到 `INTEGER`。
* `ForeignKey` 是 Django 專門用來管理 foreign key 的 model field。我們來詳細討論一下它的原理。

當你建立一個 model 時，Django 會自動幫它加入一個名為 `id` 的 `AutoField`——對應到資料庫的 `INTEGER`，加上 primary key（和 auto increment）屬性。[註 2] `ForeignKey` 同樣對應到 `INTEGER`，但當它被使用時，Django 會自動用裡面的值執行一個 `SELECT`，把該 ID 對應的物件取出來。`ForeignKey` 必須擁有兩個參數，指明這個 FK 指向的 model class，以及當一筆資料（store）被刪除時，要怎麼處理關聯它的資料（menu item）——在這裡我們指定 `CASCADE`，代表如果資料被刪除，**同時把所有必要的關聯一併刪掉**。[註 3]

你可能已經注意到，我們並沒有為 `Store` 的 `menuitem_set` 建立 attribute，但這裡 `related_name` 的值就是它。Django 會自動建立 foreign key 的 reverse relation，所以你不需要自行建立。

在 `ForeignKey` 的狀況中，Django 預設會用 model 的名稱後面加 `_set` 來當作 reverse relation 的名稱，所以 `MenuItem.store` 的預設 reverse relation key 會是 `Store.menuitem_set`。這和我們設定的值一模一樣，所以其實可以不設；不過如果狀況允許，我個人推薦盡量還是明確設定，因為 *explicit is better than implicit* 是 Python 的中心思想之一，而且這會讓你以後 trace 程式碼時更容易找到某個 reverse relation 的定義。

我們另外在兩個 models 都各加上了一個 [`__str__`](https://docs.python.org/3/reference/datamodel.html#object.__str__) 函式。這是 Python 用來把物件轉換成 `str` 的 hook；因為做網站時，常常需要把東西變成字串，所以這會很方便。

現在程式已經可以認得這兩種 models 了。但如果要儲存它們，還需要在資料庫裡建立對應的 tables。確保資料庫與程式中的定義同步，是件很麻煩的工作；幸好，Django 提供了一個自動同步資料表的工具，可以協助我們完成這個工作。

在 console 執行以下指令：

```bash
pipenv run python manage.py makemigrations stores
```

這告訴 Django 我們更新了 `stores` 中的 models。這個指令應該會輸出下面的內容：

```
Loading .env environment variables…
Migrations for 'stores':
  stores/migrations/0001_initial.py
    - Create model MenuItem
    - Create model Store
    - Add field store to menuitem
```

這代表 Django 已經偵測到你新增了 `MenuItem` 與 `Store` 兩個 models，以及它們之間的關聯。這些資訊被放在 `0001_initial.py` 中。這個檔案會被放在 `store/migrations` 目錄裡。檢查看看！

我們昨天提到，每個 Django app 都可以包含 `migrations` 目錄，用來存放 database migration 記錄。這些記錄是用來告訴 Django，這個 app 中的 models 在某個時間點長什麼樣子。你可以自己寫（同樣要放在 `migrations` 目錄裡），但是在大多數的情況下，只要用 `makemigrations` 這個指令，Django 就可以自動偵測。Django 自動產生的檔案會以以個四位數字開頭，後面接一個底線，然後是 Django 偵測到**這個記錄與前一個記錄間相異處的描述**。

接著我們要實際執行這個檔案，讓資料庫發生改變：

```bash
pipenv run python manage.py migrate stores
```

輸出：

```
Loading .env environment variables…
Operations to perform:
  Apply all migrations: stores
Running migrations:
  Applying stores.0001_initial... OK
```

Django 偵測到剛剛的 `0001_initial` 尚未與資料庫同步，並成功執行它。所以現在資料庫裡會多出兩個 tables。

不信？證明給你看。輸入以下的指令：

```bash
python manage.py dbshell
```

這會你連上 Django 目前設定的資料庫（就是你在 `DATABASES` 裡面設定的那個）。列出目前的資料庫看看（SQLite：`.tables`、PostgreSQL：`\d`、MySQL：`SHOW TABLES;`；這裡以 SQLite 為例）：

```
sqlite> .tables
auth_group                  django_admin_log
auth_group_permissions      django_content_type
auth_permission             django_migrations
auth_user                   django_session
auth_user_groups            stores_menuitem
auth_user_user_permissions  stores_store
```

其中 `stores_store` 和 `stores_menuitem` 就是我們剛剛建立的 models！

不過其他的是什麼？這些是 Django 預設啟用功能所需要的資料。還記得我們剛建立 project 時有執行一次 `migrate` 嗎？這就是用來 migrate Django 內建的資料。那時我們後面沒有加 app name，所以會 migrate **所有** apps。

在這些資料表中，`auth` 開頭的是用來管理使用者註冊與權限——所以我們之前才會先跳過使用者認證，因為 Django 內建就有。其他還有一些內部用的資料，這裡先略過。不過我們特別來看一下 `django_migrations`：

```
sqlite> select * from django_migrations;
1|contenttypes|0001_initial|2017-12-07 10:13:56.444638
2|auth|0001_initial|2017-12-07 10:13:56.466164
3|admin|0001_initial|2017-12-07 10:13:56.483577
4|admin|0002_logentry_remove_auto_add|2017-12-07 10:13:56.502065
5|contenttypes|0002_remove_content_type_name|2017-12-07 10:13:56.547797
6|auth|0002_alter_permission_name_max_length|2017-12-07 10:13:56.558823
7|auth|0003_alter_user_email_max_length|2017-12-07 10:13:56.572393
8|auth|0004_alter_user_username_opts|2017-12-07 10:13:56.588283
9|auth|0005_alter_user_last_login_null|2017-12-07 10:13:56.602905
10|auth|0006_require_contenttypes_0002|2017-12-07 10:13:56.607146
11|auth|0007_alter_validators_add_error_messages|2017-12-07 10:13:56.622861
12|auth|0008_alter_user_username_max_length|2017-12-07 10:13:56.642080
13|auth|0009_alter_user_last_name_max_length|2017-12-07 10:13:56.659138
14|sessions|0001_initial|2017-12-07 10:13:56.665113
15|stores|0001_initial|2017-12-07 11:20:01.623780
```

這就是 Django 用來記錄 migration 的表！這裡記錄了目前各 app 被 migrate 到哪個階段，以及進行的時間。這個表格搭配 `migrations` 裡面的資料，就能讓 Django 偵測 models 的修改，幫我們產生合適的 migration record，並對資料庫進行合適的設定。

呼！這篇好像有點長。明天我們會實際使用這些 models 看看。

對了，剛剛那個資料庫介面可以用 control-d 退出。


更多關於 Django model 欄位的資訊，請參照[官網文件](https://docs.djangoproject.com/en/2.0/ref/models/fields/)。

---

註 1：SQLite 沒有固定長度字串型別，所以 `CharField` 其實是對應到 `TEXT`。不過 Django 會在程式內部檢查輸入長度，所以 `max_length` 還是會有用（除非你手動直接把值插入資料庫）。

註 2：這個行為可以被覆寫，不過我們這裡不管。

註 3：其他可能的值包括 `PROTECT`、`SET_NULL`、`SET_DEFAULT`、`SET()`、`NO_NOTHING`。請參照[官方文件](https://docs.djangoproject.com/en/2.0/ref/models/fields/#django.db.models.ForeignKey.on_delete)了解各種值的差異與用法。