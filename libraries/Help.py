import wx
import wx.html


def show_quick_help(parent):
    help_text = (

        "<h2>Quick Help</h2>"
        "<h3>Keyboard Shortcuts:</h3>"
        "<ul>"
        "<li><b>Tab:</b> Select next peak</li>"
        "<li><b>Q:</b> Select previous peak</li>"
        "</ul>"
        "<h3>Mouse Controls </h3>"
        "<h5> Peak Fitting window opened and the Peak Fitting is selected:</h5>"
        "<ul>"
        "<li><b>Left Click:</b> Select peak</li>"
        "<li><b>Shift + Left Click:</b> Adjust FWHM</li>"
        "</ul>"
    )

    help_dialog = wx.Dialog(parent, title="Quick Help", size=(400, 600))
    html_window = wx.html.HtmlWindow(help_dialog)
    html_window.SetPage(help_text)
    help_dialog.ShowModal()
    help_dialog.Destroy()