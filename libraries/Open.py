import wx
from Functions import open_xlsx_file

class ExcelDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        for file in filenames:
            if file.lower().endswith('.xlsx'):
                wx.CallAfter(open_xlsx_file, self.window, file)
                return True
        return False



def open_recent_file(window):
    if window.recent_file:
        from Functions import open_xlsx_file
        open_xlsx_file(window, window.recent_file)