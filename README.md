# 🌊 PySurf – Your Minimalist Python Browser

**PySurf** is a sleek, lightweight web browser built with **Python** and **PyQt5**, designed for speed, simplicity, and customization. Open multiple tabs, save bookmarks and shortcuts, and surf the web your way—all in one clean interface.

---

## 🚀 Features

- 🔖 **Tabbed Browsing** – Open and switch between multiple sites seamlessly  
- 🏠 **Custom Homepage** – Google search + personal website shortcuts  
- 📌 **Quick Shortcuts and boomarks** – Add, remove, and organize your favorite sites easily   
- 🎨 **Clean, Minimal UI** – Modern design with Segoe UI font  
- 🛠️ **Customizable Settings** – Save preferences and startup options  
- 🌐 **Full Navigation Controls** – Back, forward, refresh for every tab
- 🛠️ **Downloads support** - Download files from the internet, and manage them easily in one window
- 🛠️ **Fullscreen support** - Full screen support on all websites, or by pressing F11 on your keyboard

---

## 🖥️ PySurf UI Overview



### 🔵 Main Window

- The main app window titled **"PySurf"**  
- Contains a **"New Tab"** button and a **tabbed browsing area**  
- Ready for quick browsing sessions

### 🔘 "New Tab" Button

- Opens a **fresh homepage tab**  
- Always visible for starting new sessions

### 🗂️ Tab Area (`QTabWidget`)

- Each tab shows either the **homepage** or a **web page**  
- Tabs include a **✕ button** to close them  

---

### 🏠 Homepage Tab

The heart of PySurf when opening a new tab:
<img width="1919" height="1032" alt="Snimka zaslona 2025-08-13 132010" src="https://github.com/user-attachments/assets/c3a13c4b-9dc1-45f6-b302-792bbfeedb3b" />

#### 🧭 Title Label

- Shows **"PySurf Search"** prominently  
- Establishes the browser’s identity  

#### 🔎 Search Bar

- Type your query into **"Search for anything..."**  
- Press **Enter** or the **Search button**  

#### 🔘 Search Button

- Opens Google search results in a **new tab**  

---

### 🔗 Shortcut Row

Quick-access buttons for your favorite sites:

#### ➕ Add Shortcut

- Opens a dialog to add:  
  - **Name** (e.g., Reddit)  
  - **URL** (must start with `https://`)  
  - Confirm with **OK**  

#### 🖱️ Delete Shortcut

- Right-click a shortcut button to remove it instantly  

---

### 🌐 Web Page Tab

Full browser experience when visiting a site:

#### ◀️▶️🔄 Navigation

- **Back**: Go to the previous page  
- **Forward**: Move ahead in history  
- **Refresh**: Reload the current page  

#### 🧭 Address Handling

- Tab titles update automatically with the page’s URL  

---

## ✨ Why PySurf?

- Lightweight browsing without unnecessary bloat  
- Easy to customize and navigate quickly  
- Built with **Python**, ideal for learners and developers  
