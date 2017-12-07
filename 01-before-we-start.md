2014 年 9 月 27 日，台北將舉行世界第三、亞洲第一場 [Django Girls](http://djangogirls.org/taipei) 工作坊。這個工作坊的目的，是希望能以一個簡單易用的網站開發框架——Django——帶領非程式專業的人們進入程式設計的領域。我們的主要目標是女性，因為程式設計領域目前的性別鴻溝仍然太大；我們相信，若能有更多來自不同背景的人加入這個行列，能夠為這個領域的所有人，不論是已經身在其中的老手，或者想要加入的新人，都能帶來好處。

為了達到推廣目的，Django Girls 花了很大的功夫降低非程式背景者從「一無所知」到「能夠開始寫程式」之間的門檻。我們花了很多精力，為參與會眾量身訂做教學，盡可能讓他們不會因為太早遇到挫折而退縮。

但身為程式人，我也有一些其他寫程式的朋友問我要如何入門 Django。Django Girls 適合嗎？完全不適合。我們也不會收你當學員。由於初衷是推廣，Django Girls 的教學再怎麼說還是淺嚐即止。如果你已經會寫程式，甚至已經知道 web framework 是怎麼回事，那麼用 Django Girls 的教學入門只是浪費大家的時間。

在未來一個月（希望）內，我會用一個完全不同的角度切入 Django。我會假設你已經：

* 會寫至少一種[高階程式語言](http://en.wikipedia.org/wiki/High-level_programming_language)（C 也算）。
* 有[物件導向](http://zh.wikipedia.org/zh-hant/面向对象程序设计)基礎。
* 知道關聯式資料庫是什麼東西。不需要你會什麼很厲害的 SQL，但至少要知道裡面資料怎麼存的。
* 懂[基本的 HTML](http://pydoing.blogspot.tw/2012/01/html-5-syntax.html)。
* 會一點點 Python——至少看完[這個系列](http://pydoing.blogspot.tw/2012/10/python-tutorial.html)的基礎篇。
* 最好在看的同時開始[惡補 CSS](http://zh-tw.learnlayout.com)，總是會用到。

總之，這個教學會非常硬派，而且不繞遠路，直攻 best practice。我不會讓你有任何機會建立壞習慣。

首先你可能需要安裝 Python。Django 2.0 起僅支援 Python 3.4 以上版本，所以請挑一個安裝。如果你已經裝好了，麻煩直接跳到下面。

## 安裝 Python

### Windows

我建議用我自己做的 [SNAFU](https://github.com/uranusjr/snafu/releases) 工具管理 Python。安裝方法很直覺：

* 下載安裝檔（注意你是 32-bit 還是 64-bit）後執行
* 打開一個 command prompt（我建議用 [cmder](http://cmder.net)，不過內建的 `cmd.exe` 也能用）
* `snafu install 3.6`（安裝目前最新的 Python 3.6；如果你看到這篇文章時有更新的，也可以改這個，後面有版本號的指令再改成對應值）
* 等它跑完

### macOS

建議用 [Homebrew](https://brew.sh/index_zh-tw.html)。安裝後執行 `brew install python3` 即可。

### 其他系統

應該你自己更知道該怎麼裝⋯⋯吧？通常會有個不錯的套件管理系統可以用。


## 安裝專案環境管理工具 Pipenv

除非你對 Django 只是玩玩而已，不然你應該會用它做超過一個網站。當你需要同時維護複數個網站時，就會遇到升級問題。當 Django 發新版本時，你也會想升級你網站使用的 Django 版本，以獲得最新的功能、更好的效能、以及更安全的修正。但如果你所有專案都共用一份 Django，那麼你要嘛是一次全升，要嘛就是要冒著有些網站可能壞掉的風險。為了解決這個問題，Python 提供了一個工具「虛擬環境」（virtual environment，簡稱 virtualenv 或 venv）。這個工具可以讓你把每個專案的 Python 環境分開，讓你可以分開處理它們的升級。[註 1]

```
pip3 install pipenv
```

> * 如果你用 SNAFU 管理 Python，在這之後請執行 `snafu use 3.6` 讓 `pipenv` 指令能被使用。

Pipenv 的運作方法是，當你使用它安裝一個套件時，不會直接安裝到系統 Python 環境，而是建立一個[虛擬環境](https://docs.python-guide.org/en/latest/dev/virtualenvs/)，把所有套件放到一個專案專用的位置。當我們為專案執行一個 Python 指令時，會使用 `pipenv run` 這個指令（例如 `pipenv run python` 執行 Python 直譯器）。Pipenv 會在執行這個指令時，同時設定相關的環境，使得每個專案可以有獨立、不互相干擾的環境。有興趣的人可以看看 [Pipenv 的文件](https://docs.pipenv.org)。


## 開始開發

首先來為我們的專案建立一個目錄。

```
mkdir lunch
cd lunch
```

我好像還沒解釋我們要做什麼專案。這會是一個決定今天午餐要吃什麼系統，包含一個可以讓使用者註冊、登入、增加新店家的介面，以及一個新增投票決定要吃什麼的介面。預計是這樣，如果之後有想到什麼可能會再加。

接著為這個專案安裝 Django：

```
pipenv install django~=2.0
```

Django 從 2.0 開始使用類似 sematic versioning 的版本模式，所以我們使用 `~=` 安裝「2.0 系列，API 相容」的版本。

這樣就設定完成啦。明天終於要寫程式了嗎？還沒。我們要先來聊聊 Django 究竟是怎麼運作的。

---

註 1：只有 Python 環境可以被分開。如果你的專案有用到系統函式庫以及其他語言（例如 C）函式庫，那麼還是會有問題。不過幸好其他語言有其他語言的玩法，例如 Windows 的 manifest 或 Linux 的函式庫命名規則等等。總之 Python 虛擬環境不處理這些。