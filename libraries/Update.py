import requests
from bs4 import BeautifulSoup
import webbrowser
import wx
import threading
import time
import re

class UpdateChecker:
    def __init__(self, current_version=1.4):
        self.current_version = float(current_version)
        self.url = "https://sourceforge.net/projects/khervefitting/files/"
        self.download_url = "https://sourceforge.net/projects/khervefitting/files/latest/download"

    def check_latest_version(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            file_links = soup.find_all("a", {"title": re.compile(r"KherveFitting_.*\.exe")})
            version_pattern = re.compile(r"KherveFitting_(\d+\.\d+)_")
            versions = []

            for link in file_links:
                match = version_pattern.search(link.get('title', ''))
                if match:
                    versions.append(float(match.group(1)))

            if not versions:
                print("No version found.")
                return False, None

            latest_version = max(versions)
            print(f"Latest version found: {latest_version}")

            if latest_version > self.current_version:
                print(f"Update available: {latest_version}")
                return True, latest_version

            print("No update available.")
            return False, self.current_version

        except Exception as e:
            print(f"Error occurred: {e}")
            return None, None

    def download_latest_version(self):
        try:
            webbrowser.open(self.download_url)
        except Exception as e:
            print(f"Download failed: {e}")

    def check_update_delayed(self, window):
        def delayed_check():
            time.sleep(3)
            needs_update, latest_version = self.check_latest_version()
            if needs_update:
                wx.CallAfter(lambda: self.show_update_dialog(window, latest_version))

        thread = threading.Thread(target=delayed_check)
        thread.daemon = True
        thread.start()

    def show_update_dialog(self, window, latest_version):
        if wx.MessageBox(f"Version {latest_version} is available. Download now?",
                      "Update Available",
                      wx.YES_NO | wx.ICON_INFORMATION) == wx.YES:
            self.download_latest_version()