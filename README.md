# NoxeBrowser ![authoor](https://img.shields.io/badge/By:-R._iliya-green)

![GitHub stars](https://img.shields.io/github/stars/R-iliya/NoxeBrowser?style=flat&color=4A2BE3)
![GitHub forks](https://img.shields.io/github/forks/R-iliya/NoxeBrowser?style=flat&color=4A2BE3)
![GitHub issues](https://img.shields.io/github/issues/R-iliya/NoxeBrowser?style=flat&color=4A2BE3)
![GitHub pull requests](https://img.shields.io/github/issues-pr/R-iliya/NoxeBrowser?style=flat&color=4A2BE3)
![GitHub license](https://img.shields.io/github/license/R-iliya/NoxeBrowser?style=flat&color=4A2BE3)
![GitHub last commit](https://img.shields.io/github/last-commit/R-iliya/NoxeBrowser?style=flat&color=4A2BE3)


## NoxeBrowser is an advanced WebBrowser wrote in python

> # NoxeBrowser: built for speed, built for simplicity, built for you.

> “Simplicity is the soul of efficiency.”  
> – Austin Freeman

NoxeBrowser is wrote on python a fast paced modern language, achieving speed, performance and ease of use with PyQt5, functools, etc.
The code is also modelized and something around 1500 lines of code is cleanly put together, making everything way easier to contribute, which we're clearly looking forward to.


NoxeBrowser is aiming to make a clean and secure environment for any user; Developer, Housewife, Gamer, Artist etc.

Why NoxeBrowser Exists

In a world full of browsers that spy on you, nag you with ads, and feel like they were built in 2008, NoxeBrowser was born to fix that. Not just to browse, but to experience the web on your own terms.

We wanted a browser that doesn’t just load pages—it understands them, respects them, and respects you. A place where performance meets simplicity, and where clutter and distractions don’t have a seat at the table.

![Screenshot 1](https://github.com/R-iliya/NoxeBrowser/blob/main/Screenshot-Dark.png?raw=true)

NoxeBrowser isn’t about fancy gimmicks. It’s about clarity: clear code, clear UI, and a clear purpose. Every line of code, every feature, every tiny shortcut was designed to make your life easier, faster, and yes, even a little cooler.

We made it because the web should feel personal, not corporate. Because a browser should empower gamers, artists, developers, and everyone in between. Because your data should belong to you, not the algorithms watching your every click.

And most importantly? Because sometimes, you just want a browser that just works, without making you jump through hoops—or worse, begging for permission to exist online.

![Screenshot 2](https://github.com/R-iliya/NoxeBrowser/blob/main/Screenshot-Light.png?raw=true)

## Some key features:

#### Optimizations & Visuals
Browser tries to implement the best performance through many API's.

#### Fullscreen Support
Browser supports Fullscreen through the F11 shortcut for ease of use, Fullscreen Support is still under development for more advanced features.

#### DevTools Support
Browser supports DevTools through the F12 shortcut for debugging and inspections.

#### Wide Shortcut Support
Browser presents a variety of shortcuts for ease of access such as:
* "F12" Toggle DevTools
* "F11" Toggle Fullscreen
* "Ctrl+T" for add new tab
* "Ctrl+W" close current tab
* "Ctrl+R" refresh current tab
* "Ctrl+D" bookmark current tab
* "Ctrl+Shift+T" reopen last closed tab
* "Ctrl+Tab", "Ctrl+Shift+Tab", "Ctrl+L" etc.

#### Persistent Bookmarks
A bookmark system that can be enabled and disabled through settings and supports drag 'n dropping  links, saving the bookmarks through JS.

#### Persistent History
A history system that can be enabled and disabled through settings and supports a variety of options through right click such as "Delete All History", "Delete Last 30 Days", "Delete Last 7 Days" and last but not least, "Delete This Entry"

#### Persistent Settings
browser supports persistent setting options so you can toggle a menu to be open on every startup of the browser for quality of life.

#### Ad & Tracker Blocker
Browser blocks ad/tracker activities through network, and the blocklist includes 125 items.

#### Local Scheme For Pages
For hiding the unpleasant path to browser's local pages, browser presents a "local://" scheme.

#### Cache & Storage
For ease of access and faster page loads, browser presents a cache and a storage folder inside the browser directory.

#### Cache Cleanup
Whenever the "fp" file in cache reaches the size of 52.4 MB (Roughly aimed for 50MB) browser would clean it on startup.

#### Persistent Previous Tab Order
Browser saves the tab order of the previous session through a js and loads on next startup unless file corrupted.

#### Privacy Overrides
Through JS, browser injects parameters for privacy and quality of life such as (prefers-color-scheme: light) which implements auto dark mode for dark mode users (supported websites only) or (const adPatterns) which checks the network for ad patterns or if (isAdUrl(url)) that blocks WebSocket connections to known ad hosts and many more.

#### Dark Mode Support
For Windows users, browser checks if user is dark mode through the registry and yes, it would implement the Windows10+ immersive dark mode title bar And browser would auto dark mode the supported websites using JS.

For Linux users, browser checks if user is dark mode through the os.environ.get("GTK_THEME", "") method to implement dark mode for supported websites.

For MacOS users, browser checks if user is dark mode through a subprocess.run() and if yes, it'd implement dark mode for supported websites.

## Download Manager
Browser presents a clean download manager which is toggle able and persistent, cancel option and a load bar; Though Download manager is still under development for more advanced features.




