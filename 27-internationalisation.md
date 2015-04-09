今天來討論怎麼實作多國語系。這個主題可以分為兩部份：

1. 讓一個網站用多種語言顯示內容（國際化）。
2. 判斷使用者的地區與使用語言，以選擇顯示語言與格式。

在 Django 中，國際化的步驟如下：

1. 在程式中標記字串，讓 Gettext 知道哪些字串需要翻譯。
2. 用 `manage.py makemessages` 把需要翻譯的字串抽出來，做成 `po` 檔。
3. 修改 `po` 檔，在其中加入合適的翻譯。
4. 用 `manage.py compilemessages` 把 `po` 檔編譯成 `mo` 檔。
5. 當某個 request 用到被翻譯的字串時，Django 會自動 lookup 對應的翻譯來使用。

由於 Django 使用 GNU Gettext 編譯翻譯檔（第四步），所以需要 GNU Gettext toolset。在 Linux 上這不是問題，但如果你用 [OS X](https://github.com/Homebrew/homebrew/issues/8461) 或 [Windows](https://docs.djangoproject.com/en/dev/topics/i18n/translation/#gettext-on-windows)，就需要自行安裝 Gettext，並把它們加入 PATH。（前面的連結中有相關說明。）[註 1]

我們來把店家相關的名稱翻成中文。新增下面的檔案：

```python
# stores/apps.py

from django.apps.config import AppConfig
from django.utils.translation import ugettext_lazy as _

class StoresAppConfig(AppConfig):
    name = 'stores'
    verbose_name = _('Stores')
```

在 Python 程式中使用 `ugettext`，就可以把字串標記為需要翻譯；我們這裡使用 lazy 版本，因為我們要在 runtime 才能知道 `Stores` 要被翻譯成什麼語言。

我們要實際指定這個 config，Django 才知道要使用它：

```python
# stores/__init__.py

default_app_config = 'stores.apps.StoresAppConfig'
```

如法炮製，把 models 也翻譯一下：

```python
# stores/models.py

from django.utils.translation import ugettext_lazy as _


class Store(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name='owned_stores',
        verbose_name=_('owner'),
    )
    name = models.CharField(
        max_length=20, verbose_name=_('name'),
    )
    notes = models.TextField(
        blank=True, default='', verbose_name=_('notes'),
    )

    class Meta:
        verbose_name = _('Store')
        verbose_name_plural = _('Stores')

    # ...

class MenuItem(models.Model):
    store = models.ForeignKey(
        'Store', related_name='menu_items', verbose_name=_('store'),
    )
    name = models.CharField(
        max_length=20, verbose_name=_('name'),
    )
    price = models.IntegerField(
        verbose_name=_('price'),
    )

    class Meta:
        verbose_name = _('Menu item')
        verbose_name_plural = _('Menu items')

    # ...
```

欄位的名稱同樣是用 `verbose_name` 屬性。這個字串會在 model 被製作成 form 時被拿來當標籤使用。Model 本身的名稱則要用 `Meta` 裡面的屬性設定，其中 `verbose_name_plural` 代表複數的翻譯。如果不指定這個，Django 預設會在需要複數時直接在單數詞後面加 s（或 es）；在英文裡這通常還 OK，但中文看起來就不對了，所以必須指定這個選項。

記得，有改 models 就要跑 migration，所以：

```bash
python manage.py makemigrations stores
python manage.py migrate stores
```

接著我們把 `stores` app 裡的翻譯整理成中文翻譯檔（`po` 檔）。首先建立 `stores/locale` 目錄：

```bash
mkdir stores/locale
```

然後要求 Django 產生 `po` 檔：

```bash
cd stores
python ../manage.py makemessages -l zh_Hant
```

注意一定要進去 `stores` 目錄才能正常執行，而且必須要用 `../manage.py`，因為這個檔案在外面那層！上面的指令會讓 Django 產生一個 `zh_Hant`（繁體中文）的翻譯檔。我們打開它，來編輯看看。

翻譯的項目會類似下面這樣子：

```
#: apps.py:7 models.py:22
msgid "Store"
msgstr ""
```

第一行的註解代表這個詞出現在哪裡，`msgid` 與 `msgstr` 分別代表會被輸入 ugettext（也就是程式裡面使用的值）、以及 ugettext 應該為這個語系輸出的翻譯。把你想要的翻譯填到雙引號中即可，像這樣：

```
#: apps.py:7 models.py:22
msgid "Store"
msgstr "店家"
```

修改完之後，仍然在 `stores` 目錄中把 `po` 編譯成 `mo`：

```bash
python ../manage.py compilemessages
```

把 server 跑起來，進入 admin 看看。你的「Store」model 標題應該會變成中文「店家」。[註 2]

我們目前是讓 Django 偵測我們的預設語言，但有時候我們可能也會想手動切換，看到其他的語言。Django 可以使用 session、cookie 與 HTTP header 中的 Accept-Languages 來判斷應該使用什麼語言。[註 3] 如果要實作多國語言，必須確認設定裡有以下內容：

1. `USE_I18N` 是 `True`。
2. `MIDDLEWARE_CLASSES` 中有 `'django.middleware.locale.LocaleMiddleware'`，且位於 `SessionMiddleware` 與 `CommonMiddleware` 之間。
3. `TEMPLATES` 的 `context_processors` 列表中包含 `'django.template.context_processors.i18n'`。

有這些資料之後，我們就可以實作一個 form 來切換語言：

```python
# lunch/settings/base.py

# 設定我們要使用的語言。
LANGUAGES = (
    ('en-us', 'English (United States)',),
    ('zh-hant', '中文（繁體）')
)
```

```html
{# base/templates/base.html #}

{# 在 navbar 裡 #}
<form class="navbar-form navbar-right" action="{% url 'set_language' %}" method="post">
  {% csrf_token %}
  <select name="language" class="form-control language-switch">
    {% for code, name in LANGUAGES %}
      <option value="{{ code }}"{% if LANGUAGE_CODE == code %} selected{% endif %}>{{ name }}</option>
    {% endfor %}
  </select>
</form>
```

上面 form 的 action 指向 `set_language`。這是 Django 內建的切換語言用 form view，接受一個 `language` 參數，包含我們要用的 language code（另外它還可以接受 `next`，用途應該不用解釋——不過我們這裡不用，預設會重導向回目前頁面，這是我們要的行為沒錯）。這個 widget 的內容可以用 for 產生，而且我們把符合當下語言（可以用 `LANGUAGE_CODE` 得知）的選項選起來。

用點 JavaScript 讓表單直接在 widget 選擇改變時送出，而不用按 submit：

```javascript
// base/static/base/js/base.js

$('.language-switch').change(function () {
  $(this).parent('form').submit();
});
```

最後，記得把內建語言切換頁加入 URL conf：

```python
# lunch/urls.py

urlpatterns = [
    # ...
    url(r'^i18n/', include('django.conf.urls.i18n')),
)
```

在頁面上按按看這個 widget，應該會感受到一個頁面重新整理。如果你再去看 admin，應該就可以看到語言改變。

你也可以繼續修改其他部分，讓使用者可以切換網頁語言。在 Python 中，你可以使用 `ugettext` 與 `ugettext_lazy`，在 template 中則可以使用 `trans` tag（記得必須 `{% load i18n %}`，我超常忘記），例如像這樣：

```html
{% load i18n %}
<button type="submit">{% trans 'Submit' %}</button>
```

這些函式還有許多變體，例如可以根據一個額外參數切換單複數的 `ungettext` 系列，以及字串 format 的用法，例如：

```python
text = ungettext(
    'I have {count} apple', 'I have {count} apples', count,
).format(count=count)
```

就會根據 `count` 的值，顯示例如 *I have 1 apple* 或 *I have 5 apples* 等翻譯！不過這就讓你自己發掘吧，如果有什麼不懂的，就參考[官方文件](https://docs.djangoproject.com/en/1.7/topics/i18n/translation/)。

---

註 1：更好的方法是使用一個 staging server 加上 post-commit hooks 來自動編譯，不過設 staging server 有時候實在是 overkill。

註 2：如果你的 Accept-Languages header 沒有中文——如果你把系統語言設成其他語言，就會發生這種狀況，那麼就還是會看到英文，因為 Django 會根據它來判斷。不過先別急，馬上教你怎麼複寫。

註 3：Django 另外提供了用網址分辨（例如 `/zh/store/` 是中文，`/en/store/` 是英文），以及如果一切設定都無法決定，可以在設定檔寫死的做法，不過這裡不討論。
