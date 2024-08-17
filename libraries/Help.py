import wx
import wx.html

def show_quick_help(parent):
    help_text = (
        "<body bgcolor='#FFFFE0'>"  # Light yellow
        "<h2><font color='#66CC66'>Quick Help</font></h2>"
        
        "<h3><font color='#006400'>Keyboard Shortcut</font></h3>"
        "<ul>"
            "<li><b>Tab:</b> Select next peak</li>"
            "<li><b>Q:</b> Select previous peak</li>"
        "</ul>"
        
        "<h3><font color='#006400'>Open File</font></h3>"
        "<p>KherveFitting can open Excel file (.xlsx) and import/convert vamas file (.vms) into an Excel file. It is "
        "best to have the raw datafile (X,Y) into Columns A and B starting at row 0. There is possibility to offset the row using the row "
        "ofsset control in the horizontal toolbar. Each core levels should be saved in different sheets named after "
        "the name of that core level, i.e. Si2p, Al2p, C1s, O1s... </p>"
        "<p>Once fitting has been created and saved, KherveFitting looks also for the .json file for the peaks "
        "properties.</p>"
        
        "<h3><font color='#006400'>Saving File</font></h3>"
        "<p> There are three saving options. </p>"
        
        "<h3><font color='#006400'>Controlling the Peaks</font></h3>"
        "<ul>"
            "<li>Peaks cannot be moved if the Peak Fitting tab in the Peak Fitting window is not selected.</li>"
            "<li>Press the left mouse button on the cross to drag the peak.</li>"
            "<li>Press Shift + Left mouse button to change the peak width.</li>"
            "<li>Keyboard Shortcuts:"
            "<ul>"
                "<li><b>Tab:</b> Select next peak</li>"
                "<li><b>Q:</b> Select previous peak</li>"
            "</ul>"
            "</li>"
            "<li>Use the middle mouse scroll to change the sheet or core level.</li>"
        "</ul>"
        "<h3><font color='#006400'>Binding Energy Correction</font></h3>"
        "<p>The Binding Energy correction button searches for a peak labeled C1s C-C in the current sheet.  It then "
        "calculates the difference between the actual position of C-C and 284.8 eV. This difference is entered into  "
        "the BE correction control. All core levels are subsequently corrected by this value. Ensure that you have  "
        "fitted all your data before applying the BE correction.</p>"
    )

    help_dialog = wx.Dialog(parent, title="Quick Help", size=(400, 600),
                            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    # help_dialog.SetBackgroundColour(wx.Colour(255, 255, 255))  # Light yellow
    html_window = wx.html.HtmlWindow(help_dialog)
    # html_window.SetBackgroundColour(wx.Colour(255, 255, 224))  # Light yellow
    html_window.SetPage(help_text)

    help_dialog.Show()
    help_dialog.Bind(wx.EVT_CLOSE, lambda evt: help_dialog.Destroy())