要講的東西太多了，所以今天就不講新東西，來講講接下來要怎麼繼續。Django 在中文圈的知名度或許不高（實在不知道為什麼），但英文的資源還是很多，中文也有一些地方可以問。

首先當然是 Django 官方文件。這一個月來應該也看過一堆連結指向官網了，但你也可以直接前往 <https://docs.djangoproject.com/> 閱讀文件。不過 Django 官方文件豐富歸豐富，如果你要找某個特定的東西（某個函式，或甚至某個參數之類的），或者想要交叉參照很多部分，可能就不是很好用；官網本身就有個搜尋，不過我推薦可以善用 Google 的 `site:` 參數，找起來會更方便。

之前也提過另一個很方便的網站 <http://ccbv.co.uk>。這個網站有個很方便的地方，是可以直接看直接在看文件時，同時對照某個元件的 source code。或許你有時候還會覺得讀源碼比讀文件更方便（畢竟 Python 的可讀性實在太高）！CCBV 只提供 generic class-based views 的源碼，但如果你想看的其他部分，可以直接讀 [Django 在 GitHub 上的官方 repository](https://github.com/django/django/tree/master/django)。如果你希望離線看，也可以 clone 一份回來。不過要注意：不論線上還是 clone 回來的源碼，預設都是在 master branch 上；在你看這篇文章的同時，Django 仍然持續在開發，你在專案中使用的版本常常和 master branch 的內容有差異。所以你必須 checkout 到正確的 tag 才行。

在討論區方面，Django 算是比較 old-fashioned。你可以加入 [django-users mailing list](https://groups.google.com/forum/#!forum/django-users)，或者，如果你喜歡 IRC，可以上 <irc://chat.freenode.net> 的 #django channel，如果時間段對的話（美國上班時間到晚上）應該都頗容易迅速得到答案。不過 #django channel 需要[認證 nickname](http://epttformosa.conic.me/interaction/irc/ircreg) 才能進入，必須注意。這些地方當然都是講英文，不過 Django Community 的人基本上都還滿 nice
的（他們有認真在維護社群文化，不像 Linux 社群嗯…），所以不需要太擔心，勇敢問下去就對了！

如果你還是有點怕怕的，最近 Django Girls 也有一個 Gitter channel，或許是對初學者更友善的選擇。如果你已經有在用 Gitter，可以直接加入 **DjangoGirls/tutorial** 聊天室；或者也可以使用[這個連結](https://gitter.im/DjangoGirls/tutorial)。不過 Gitter 需要 GitHub 帳號才能登入喔！

在中文方面，目前最好的教學應該是 Django Girls Taipei 的[課前準備](http://djangogirlstaipei.herokuapp.com/tutorials/)與[官方教學](http://djangogirlstaipei.gitbooks.io/django-girls-taipei-tutorial/)。也有人[翻譯了 Django Girls 英文版教學](http://carolhsu.gitbooks.io/django-girls-tutorial-traditional-chiness/)（內容與 Django Girls Taipei 用的教學不同）；英文版 Django Girls 教學的內容比起台北版稍微多一些，對於單日 workshop 有點硬，但是如果你按自己的步調練習，仍然是十分優秀。

台灣目前沒什麼專門的 Django 討論區。PTT 的 Python 版是個選擇，但我可以理解不是所有人都願意用 BBS。Facebook 的 Python Taiwan 群組有不少討論，但因為 Facebook 留言的格式限制，其實不是很適合在那裡問程式。如果需要在網路上問問題，[python.tw maiing list](https://groups.google.com/forum/#!forum/pythontw) 比較好一些。或者，如果你住在台北，[Taipei.py](http://www.meetup.com/Taipei-py/) 的 Web Developer Meetup 可以遇見不少人，其中不乏 Django 專家。有更多 Django 專家也會出現在 Taipei.py 的例月聚會，但後者就不見得是 web 相關，會遇到誰就要碰點運氣。Python 社群在[新竹](http://www.meetup.com/pythonhug/)、[台中](http://www.meetup.com/Taichung-Python-Meetup/)、[花蓮](http://hualien.python.org.tw)、[台南](http://www.meetup.com/Tainan-py-Python-Tainan-User-Group/)、[高雄](http://kaohsiungpy.kktix.cc)也都有各自的聚會，可以關注他們的訊息。

> 更新：我們也有自己的 Gitter channel 了！你可以在 GitHub 專案首頁找到連結，或者直接[點這裡](https://gitter.im/uranusjr/django-tutorial-for-programmers)。

在獲取新資訊方面，Django 官方網站有一個 [weblog](https://www.djangoproject.com/weblog/) 可以追蹤。這裡會放出新版本的消息，以及一些比較大的 Django 社群動態。或者，官方網站也有一個 Django 的[新聞 aggregation 服務](https://www.djangoproject.com/community/)，可以看到來自整個網路的 Django 相關文章動態。如果你用 Twitter，也可以追蹤 [Django 的官方帳號](https://twitter.com/djangoproject)。除了文字動態方面，英文聽力不差的人可以試試 Elena Williams 的 [Django News Podcast](https://soundcloud.com/elena)。他會在節目中訪問許多 Django 相關的人物，除了可以讓你了解 Django 社群外，有時也是不錯的靈感來源。

你大概也知道要怎麼在網路上找到我；在台北的 Python 聚會也滿容易碰到我本人，所以如果有什麼關於這個教學的問題，也歡迎用任何方法提出（當然最好還是用 GitHub issue）。如果有什麼奇怪的問題想問，我也很樂意幫你解答——或者告訴你怎麼找到答案，或者幫你找到可以回答的人。就這樣吧，我們未來有緣再見。 ;)
