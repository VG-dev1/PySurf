from PyQt5.QtWidgets import QApplication,QMainWindow,QLineEdit,QPushButton,QVBoxLayout,QHBoxLayout,QWidget,QLabel,QTabWidget,QMenu,QAction
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl,Qt
from PyQt5.QtGui import QFont
import sys,os,json

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"]="--enable-gpu --ignore-gpu-blocklist"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"]="1"

shortcuts_file="shortcuts.json"
def load_shortcuts():
 if os.path.exists(shortcuts_file):
  with open(shortcuts_file,"r")as f:return json.load(f)
 return[("YouTube","https://www.youtube.com"),("Google","https://www.google.com")]
def save_shortcuts(data):
 with open(shortcuts_file,"w")as f:json.dump(data,f)

class ShortcutButton(QPushButton):
 def __init__(self,name,url,remove_callback,*args,**kwargs):
  super().__init__(name,*args,**kwargs)
  self.url=url
  self.remove_callback=remove_callback
 def contextMenuEvent(self,event):
  menu=QMenu(self)
  delete_action=QAction("Delete",self)
  delete_action.triggered.connect(lambda:self.remove_callback(self,self.url))
  menu.addAction(delete_action)
  menu.exec_(event.globalPos())

app=QApplication(sys.argv)
app.setFont(QFont("Arial"))
window=QMainWindow()
window.setWindowTitle("PySurf")
window.setGeometry(100,100,1200,800)

tabs=QTabWidget()
tabs.setTabsClosable(True)
def close_tab(index):tabs.removeTab(index)
tabs.tabCloseRequested.connect(close_tab)
new_tab_button=QPushButton("New Tab")

def open_site(url):
 browser=QWebEngineView()
 address_bar=QLineEdit()
 address_bar.setText(url)
 def navigate_to_url():
  new_url=address_bar.text()
  if not new_url.startswith("http"):new_url="https://"+new_url
  browser.load(QUrl(new_url))
 address_bar.returnPressed.connect(navigate_to_url)
 def update_address_bar(qurl):address_bar.setText(qurl.toString())
 browser.urlChanged.connect(update_address_bar)
 browser.load(QUrl(url))
 back_button=QPushButton("Back")
 forward_button=QPushButton("Forward")
 refresh_button=QPushButton("Refresh")
 back_button.clicked.connect(browser.back)
 forward_button.clicked.connect(browser.forward)
 refresh_button.clicked.connect(browser.reload)
 nav_layout=QHBoxLayout()
 nav_layout.addWidget(back_button)
 nav_layout.addWidget(forward_button)
 nav_layout.addWidget(refresh_button)
 nav_layout.addWidget(address_bar)
 browser_layout=QVBoxLayout()
 browser_layout.addLayout(nav_layout)
 browser_layout.addWidget(browser)
 browser_widget=QWidget()
 browser_widget.setLayout(browser_layout)
 tab_index=tabs.addTab(browser_widget,url)
 tabs.setCurrentIndex(tab_index)
 def update_tab_title():
  browser.page().runJavaScript("document.title",lambda title:tabs.setTabText(tab_index,title))
 browser.loadFinished.connect(update_tab_title)

def create_homepage():
 label=QLabel("PySurf Search")
 label.setFont(QFont("Arial",48))
 label.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
 entry=QLineEdit()
 entry.setPlaceholderText("Search for anything...")
 entry.setFont(QFont("Arial",18))
 search_button=QPushButton("Search")
 search_button.setFont(QFont("Arial",18))
 shortcuts_layout=QHBoxLayout()
 shortcuts=load_shortcuts()
 def remove_shortcut(btn,url):
  for i,(name,link)in enumerate(shortcuts):
   if link==url:
    del shortcuts[i]
    save_shortcuts(shortcuts)
    break
  btn.setParent(None)
 def add_shortcut():
  dialog=QWidget()
  dialog.setWindowTitle("Add Shortcut")
  dialog.setFixedSize(300,150)
  name_entry=QLineEdit()
  name_entry.setPlaceholderText("Name")
  url_entry=QLineEdit()
  url_entry.setPlaceholderText("URL (include https://)")
  ok_button=QPushButton("OK")
  def confirm():
   name=name_entry.text().strip()
   url=url_entry.text().strip()
   if name and url:
    shortcuts.append((name,url))
    save_shortcuts(shortcuts)
    btn=ShortcutButton(name,url,remove_shortcut)
    btn.clicked.connect(lambda checked,url=url:open_site(url))
    shortcuts_layout.addWidget(btn)
    dialog.close()
  ok_button.clicked.connect(confirm)
  layout=QVBoxLayout()
  layout.addWidget(name_entry)
  layout.addWidget(url_entry)
  layout.addWidget(ok_button)
  dialog.setLayout(layout)
  dialog.show()
 add_shortcut_button=QPushButton("Add Shortcut")
 add_shortcut_button.clicked.connect(add_shortcut)
 shortcuts_layout.addWidget(add_shortcut_button)
 for name,url in shortcuts:
  btn=ShortcutButton(name,url,remove_shortcut)
  btn.clicked.connect(lambda checked,url=url:open_site(url))
  shortcuts_layout.addWidget(btn)
 def search():
  query=entry.text()
  if query.strip()=="":return
  url="https://www.google.com/search?q="+query
  open_site(url)
 search_button.clicked.connect(search)
 homepage_layout=QVBoxLayout()
 homepage_layout.addWidget(label)
 homepage_layout.addWidget(entry)
 homepage_layout.addLayout(shortcuts_layout)
 homepage_layout.addWidget(search_button)
 homepage_widget=QWidget()
 homepage_widget.setLayout(homepage_layout)
 tabs.addTab(homepage_widget,"Home")
 tabs.setCurrentWidget(homepage_widget)

new_tab_button.clicked.connect(create_homepage)
main_layout=QVBoxLayout()
main_layout.addWidget(new_tab_button)
main_layout.addWidget(tabs)
main_widget=QWidget()
main_widget.setLayout(main_layout)
window.setCentralWidget(main_widget)
create_homepage()
window.show()
sys.exit(app.exec_())
