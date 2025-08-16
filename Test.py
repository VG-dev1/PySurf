import sys
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from PyQt5.QtCore import QCoreApplication, QTimer

# Initialize a dummy application
app = QCoreApplication(sys.argv)

def test_download_queue():
    print("Running test...")
    try:
        profile = QWebEngineProfile.defaultProfile()
        queue = profile.downloadQueue()
        print("Success! downloadQueue() method exists.")
    except AttributeError as e:
        print(f"Error: {e}")
        print("downloadQueue() does NOT exist on your system.")
    finally:
        # Exit the application to terminate the script cleanly
        app.quit()

# Use a timer to run the test after the application's event loop starts
QTimer.singleShot(0, test_download_queue)

# Start the application's event loop
sys.exit(app.exec_())