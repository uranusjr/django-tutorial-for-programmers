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

開始寫這篇之前還真的一點準備也沒有，所以或許之後的教學會很亂。說真的我也不確定題材能不能寫滿 30 篇。或者反過來，30 篇寫得完嗎？我也不知道。但希望這個系列能夠成為未來完整教學的基礎。萬事起頭難嘛。

總之，這個教學會非常硬派，而且不繞遠路，直攻 best practice。我不會讓你有任何機會建立壞習慣。

首先我們要安裝 Django。不過在那之前，你可能需要先安裝 Python。本教學會使用 Python 3.4，所以請安裝它。不接受 Python 2。沒有商量餘地。

如果你沒有 Python 3，可以參考 [Django Girls 的教學](http://djangogirlstaipei.herokuapp.com/tutorials/installation/)來安裝。如果你用某種沒提到的作業系統，請直接問我。反正把 Python 3.4 裝起來就對了。

接著我們要安裝 Django。不過等等。除非你對 Django 只是玩玩而已，不然你應該會用它做超過一個網站。當你需要同時維護複數個網站時，就會遇到升級問題。當 Django 發新版本時，你也會想升級你網站使用的 Django 版本，以獲得最新的功能、更好的效能、以及更安全的修正。但如果你所有專案都共用一份 Django，那麼你要嘛是一次全升，要嘛就是要冒著有些網站可能壞掉的風險。為了解決這個問題，Python 提供了一個工具「虛擬環境」（virtual environment，簡稱 virtualenv 或 venv）。這個工具可以讓你把每個專案的 Python 環境分開，讓你可以分開處理它們的升級。[註 1]

所以首先來為我們的專案建立一個目錄。

```
mkdir lunch
cd lunch
```

我好像還沒解釋我們要做什麼專案。這會是一個決定今天午餐要吃什麼系統，包含一個可以讓使用者註冊、登入、增加新店家的介面，以及一個新增投票決定要吃什麼的介面。預計是這樣，如果之後有想到什麼可能會再加。

總之，接著我們就來建立虛擬環境。注意請使用 Python 3：[註 2]

```
python3 -m venv venv/lunch
```

這應該會在 `lunch` 目錄下建立一個 `venv` 目錄，裡面有一個 `lunch` 目錄，裡面包含著一個虛擬環境。

接著我們要進入這個虛擬環境：

```
source venv/lunch/bin/activate
```

Windows 使用者請執行

```
venv/lunch/Scripts/activate.bat
```

如果成功的話，你的 command prompt 前面應該會多出 `(lunch)` 的字樣，代表已經進入這個虛擬環境。

如果未來你想退出這個虛擬環境，可以輸入 `deactivate`。要再次進入的話，就再執行一次前面的 `activate` 指令。

> 如果上面遇到任何問題，可以先試著參考[官方文件](https://docs.python.org/dev/library/venv.html)。

接著我們可以安裝 Django 了：

```
pip install django
```

結束。

明天終於要寫程式了嗎？還沒。我們要先來聊聊 Django 究竟是怎麼運作的。

---

註 1：只有 Python 環境可以被分開。如果你的專案有用到系統函式庫以及其他語言（例如 C）函式庫，那麼還是會有問題。不過幸好其他語言有其他語言的玩法，例如 Windows 的 manifest 或 Linux 的函式庫命名規則等等。總之 Python 虛擬環境不處理這些。

註 2：如果你用 Windows，要用 `python` 才能正確抓到路徑。如果還是抓不到，請使用完整路徑，例如 `C:\Python34\python.exe -m venv venv/lunch`。
