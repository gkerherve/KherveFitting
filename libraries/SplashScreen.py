import wx
import wx.adv
import os
import sys
import time


class SplashScreen:
    def __init__(self, duration=3000, delay=2):
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        splash_image_path = os.path.join(application_path, "libraries","Images", "splash_600.png")

        self.splash = None
        self.delay = delay
        if os.path.exists(splash_image_path):
            bitmap = wx.Bitmap(splash_image_path)
            if bitmap.IsOk():
                self.splash = wx.adv.SplashScreen(
                    bitmap,
                    wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
                    duration,  # milliseconds
                    None,
                    -1
                )
            else:
                print(f"Failed to load bitmap: {splash_image_path}")
        else:
            print(f"Splash image not found: {splash_image_path}")

    def Show(self):
        if self.splash:
            self.splash.Show()
            time.sleep(self.delay)  # Add delay here

    def Destroy(self):
        if self.splash:
            self.splash.Destroy()


def show_splash(duration=3000, delay=2):
    splash = SplashScreen(duration, delay)
    splash.Show()
    return splash

# if __name__ == "__main__":
#     show_splash()