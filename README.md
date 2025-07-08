# PySurf

PySurf is a lightweight custom web browser built using Python and PyQt5. It supports multiple tabs, homepage search, website shortcuts, and a simple, clean interface.

---

## 🚀 Features

- 🔖 **Tabbed browsing** with back, forward, and refresh controls  
- 🏠 **Custom homepage** with Google search  
- 📌 **Add/delete website shortcuts** from the homepage  
- 🎨 **Clean UI** with global Arial font  

---

## 🖼️ PySurf UI Components Explained

---

### 🔵 Main Window

- The overall app window titled **"PySurf"**.  
- Contains the **"New Tab"** button at the top and a **tabbed browsing area** below it.

---

### 🔘 "New Tab" Button

- Located above the tabs.  
- When clicked, opens a **new homepage tab**.  
- Always visible for easy access to start new sessions.

---

### 🗂️ Tab Area (`QTabWidget`)

- Where all your browser content lives.  
- Each tab can contain either:
    - A **homepage layout**.  
    - A **web page** opened from a search or shortcut.  
- Tabs include a **✕ (close button)** to close them.

---

### 🏠 Homepage Tab

Every time a "New Tab" is opened, it loads this homepage, which contains:

#### 🧭 1. Title Label

- Displays **"PySurf Search"** in a large, centered font.  
- Gives your browser its identity.

#### 🔎 2. Search Bar

- A text input field labeled **"Search for anything..."**  
- Users type in a query here.

#### 🔘 3. Search Button

- Triggers a **Google search** with the typed query.  
- Opens results in a **new tab**.

---

### 🔗 Shortcut Row

- Horizontal row of buttons representing **quick-access websites**.  
- Starts with built-in shortcuts like **YouTube** and **Google**.

#### ➕ "Add Shortcut" Button

- Opens a **dialog box** to add a custom shortcut.  
- Dialog has:
    - A field for **name** (e.g., "Reddit")  
    - A field for **URL** (must include `https://`)  
    - An **OK** button to confirm.

#### 🖱️ Right-Click to Delete Shortcut

- Every shortcut button supports **right-clicking**.  
- A **context menu** appears with the option **"Delete"**.  
- Clicking "Delete" **removes the shortcut** from the homepage.

---

### 🌐 Web Page Tab

When a site is opened (via search or shortcut), it loads into a full browser tab with:

#### ◀️▶️🔄 Navigation Buttons

- **Back**: Takes you to the previous page.  
- **Forward**: Moves ahead in browsing history.  
- **Refresh**: Reloads the current page.

#### 🧭 Address Area (implicitly handled)

- The current page’s **URL updates the tab’s title** dynamically.

---
