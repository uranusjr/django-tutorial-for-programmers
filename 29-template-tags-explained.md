今天我們來談談 Django 的 template tags 背後的原理。Django 在 `django.template` 子模組中實作了一個 [recursive descent parser](http://en.wikipedia.org/wiki/Recursive_descent_parser)，當你的 template 被讀入時，會經過這個 parser 處理成 [AST](http://zh.wikipedia.org/wiki/抽象語法樹)，接著再由一個 renderer 將這個 AST 輸出成字串。你寫的所有內容都會被轉化成下列其中之一：

1. 用 `{% ... %}` 語法寫出的元件代表一個 block 的開始或結束（或者一整個 block 本身）。Django 會根據該元件宣告時的定義，收集整個 block 中的資訊，轉為一個 *block token*。這是唯一一種內部可以有 child tokens 的元件。
2. 用 `{# ... #}` 寫出的元件會被轉為 *comment token*，代表註解。它會在 template 變成 HTML 時被捨棄。
3. 用 `{{ ... }}` 寫出的元件會被轉為 *variable token*。Django 會根據裡面的 variable name 從 context 中尋找它的值，再檢查後面有沒有接 filters（`|` 語法），如果有就進行額外的處理，然後輸出。
4. 其他所有輸入都會成為 *text token*，會直接被輸出。

其中 2. 和 4. 沒什麼好解釋的，我們先來看一個 variable token 的例子：

```
{{ foo }}
```

這會讓 Django 去 context 中尋找 `foo` 這個變數。如果你的 context 是用下面這個 `dict` 產生的（不論你是用 `render` 之類的函式，或直接用 `django.template.Context` 建構）：

```python
{
    'foo': object(),
    'bar': None,
}
```

那麼上面的 variable token 就會輸出像下面的內容：

```
<object object at 0x106647070>
```

注意 Django 會自動把所有東西都轉成字串。如果在 context 裡沒有對應的 key，則 Django 會**輸出空字串**，這和一般 Python 中如果找不到 key 會 raise KeyError 自爆的行為不太一樣，要注意。

如果 variable token 中包含 filter syntax，像這樣：

```
{{ foo|id|divide:2 }}
```

則 Django 會去 registry 找有沒有符合名稱的 filters，如果有就套用（否則會提示錯誤）。假設你的 filters 長這樣：

```python
from __future__ import division
from django.template import Library

register = Library()    # 產生與 Django template tag registry 溝通的 interface。

@register.filter(name='id')     # 把 filter 註冊進 registry。
def do_id(value):
    return id(value)
    
@register.filter
def divide(value, arg):
    return value / arg
```

那麼 Django 就會把上面的 token 解讀成這樣：

```python
divide(do_id(context['foo']))
```

注意上面有個重點：如果你不想或不能讓你的 filter 與 function 同名（例如上面的 `id` filter 會蓋掉內建的 `id` function），可以在 `filter` decorator 多加一個 `name` argument（並注意 Django 習慣在這種狀況使用 `do_` prefix）。另外，filter 的輸入值是**還沒被轉成字串**之前的值，所以我們可以直接在 `divide` 中用除法。但如果你的 filter 預期只會處理字串，則可以為你的 function 多加一個 decorator：

```python
from django.template.defaultfilters import stringfilter

@register.filter
@stringfilter
def cut(value, arg):
    return value.replace(arg, '')
```

這樣無論你輸入什麼變數，Django 都會自動先幫你把它轉成字串。所以即使你這樣用：

```
{{ 12345|cut:3 }}     {# 結果會是 1245 #}
```

也不會出錯，因為 `stringfilter` 會自動把 `12345` 和 `3` 轉成 `'12345'` 與 `'3'`。

Block tokens 可能有兩種型態。它可以是 self-contained，像這樣：

```
{% now '%Y-%m-%d' %}
```

或者是由一個 start tag、一個 end tag、以及之間的內容組成，例如：

```
{% upper %}     {# start tag #}
Hello!
{% encupper %}  {# end tag #}
```

不論是哪一種，其實在實作時都分成兩個部分：一個 entry function，以及一個 `Node` subclass。一個 self-contained tag 可以這樣實作：

```python
from django.template import Node, TemplateSyntaxError, Variable
from django.utils.timezone import now

class NowNode(Node):

    def __init__(self, format_string):
        super().__init__()
        self.format_string = format_string
        
    def render(self, context):
        format_string = Variable(self.format_string).resolve(context)
        return now().strftime(format_string)

@register.tag(name='now')
def do_now(parser, token_list):
    try:
        tag_name, format_string = token_list.split_contents()
    except ValueError:  # Not exactly two arguments.
        raise TemplateSyntaxError(
            'Template tag {name} takes exactly two arguments.'.format(
                name=tag_name
            )
        )
    return NowNode(format_string)
```

當 parser 遇到 `{% now '%Y-%m-%d' %}` 時，會呼叫 `do_now`，並把自己與 token list 傳入。我們可以自己處理它們，但這裡直接用內建的方法把他們拆開，並建立一個 node，讓 parser 把它存入 AST。當 renderer 遇到這個 node 時，就會呼叫它的 `render` method，並傳入當下的 context。我們可以用這個 context 來 resolve 先前得到的 token。在上面的例子中，因為 `'%Y-%m-%d'` 是 string literal，所以 resolve 出來仍然是 string literal，但如果他原本是變數名，`resolve` 就會去 context 中 lookup 對應值。接著我們就使用得到的參數，告訴 renderer 這個 node 的 render 結果。

如果 token 是由成對的 tags 組成，我們也可以自己進行額外的 parsing：

```python
@register.tag
def do_upper(parser, token_list):           # 遇到 {% upper %} tag 時進入。
    node_list = parser.parse(('endupper',)) # 繼續 parse，直到遇到 {% endupper %}。
    parser.delete_first_token()             # 跳過 {% endupper %} tag。
    return UpperNode(node_list)
    
class UpperNode(Node):
    # 略。
```

這個架構的彈性非常大，所以我們可以實作任何我們想要的功能，只要符合 Django template language 的語法即可。但在絕大多數情況中，我們其實只是簡單想把參數讀入，然後做件簡單的事情就回傳而已。所以 Django 提供了一些方便的 factory decorators，簡化一些常見的工作。例如上面的 `now` tag 其實可以簡化成下面這樣：

```python
@register.simple_tag(name='now')    # simple_tag 接受一些參數，並輸出一個字串。
def do_now(format_string):
    return now.strftime(format_string)
```

這會自動檢查參數數量（根據你的函式宣告）、在合適時刻 resolve variables、以及輸出結果。其他的類似 decorators 包含：

* `inclusion_tag`：可以自動幫你 render 一個 template 並輸出。
* `assignment_tag`：可以自動把 tag 結果存入某個變數（用 `as` syntax 指定變數名），並輸出空字串。

當你需要手動處理 context（而不僅只是需要 variable resolution）時，也可以在 decorator 上使用 `takes_context=True` 參數。這會讓 Django 在呼叫 function 時多傳入一個 `context` 參數，像這樣：

```python
@register.simple_tag(name='now', takes_context=True)
def do_now(context, format_string):
    timezone = context['timezone']
    return your_get_current_time_method(timezone, format_string)
```

篇幅也差不多了。Django templates 還有更多可以自訂的地方，詳情請參考[官方文件](https://docs.djangoproject.com/en/dev/howto/custom-template-tags/)。明天就是最後一篇了，yay！
