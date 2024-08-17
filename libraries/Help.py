import wx
import wx.html

def show_quick_help(parent):
    help_text = (
        "<h2><font color='red'>Quick Help</h2>"
        "<h3><font color='blue'>Keyboard Shortcuts</h3>"
        "<ul>"
        "<li><b>Tab:</b> Select next peak</li>"
        "<li><b>Q:</b> Select previous peak</li>"
        "</ul>"
        "<h3><font color='blue'>Mouse Controls</h3>"
        "<ul>"
        "<h5><li><b>With Peak Fitting window opened and the Peak Fitting is selected:</b></li></h5>"
        "<ul>"
        "<li><b>Left Click:</b> Select peak</li>"
        "<li><b>Shift + Left Click:</b> Adjust FWHM</li>"
        "</ul>"
        "<h5><li><b>On the Plot:</b></li></h5>"
        "<ul>"
        "<li><b>Scroll Middle Button:</b> Change Sheet</li>"
        "</ul>"
        "</ul>"
    )

    help_dialog = wx.Dialog(parent, title="Quick Help", size=(400, 600),
                            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    html_window = wx.html.HtmlWindow(help_dialog)
    html_window.SetPage(help_text)

    help_dialog.Show()
    help_dialog.Bind(wx.EVT_CLOSE, lambda evt: help_dialog.Destroy())