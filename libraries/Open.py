import wx
import os
import json

class ExcelDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        from Functions import open_xlsx_file
        for file in filenames:
            if file.lower().endswith('.xlsx'):
                wx.CallAfter(open_xlsx_file, self.window, file)
                return True
        return False



def update_recent_files(window, file_path):
    if file_path in window.recent_files:
        window.recent_files.remove(file_path)
    window.recent_files.insert(0, file_path)
    window.recent_files = window.recent_files[:window.max_recent_files]
    update_recent_files_menu(window)
    save_recent_files_to_config(window)


def update_recent_files_menu(window):
    if hasattr(window, 'recent_files_menu'):
        from Functions import open_xlsx_file
        # Remove all existing menu items
        for item in window.recent_files_menu.GetMenuItems():
            window.recent_files_menu.DestroyItem(item)

        # Add new menu items for recent files
        for i, file_path in enumerate(window.recent_files):
            item = window.recent_files_menu.Append(wx.ID_ANY, os.path.basename(file_path))
            window.Bind(wx.EVT_MENU, lambda evt, fp=file_path: open_xlsx_file(window, fp), item)

def save_recent_files_to_config(window):
    config = window.load_config()
    config['recent_files'] = window.recent_files
    window.save_config(config)

def load_recent_files_from_config(window):
    config = window.load_config()
    window.recent_files = config.get('recent_files', [])
    update_recent_files_menu(window)

def update_recent_files(window, file_path):
    if file_path in window.recent_files:
        window.recent_files.remove(file_path)
    window.recent_files.insert(0, file_path)
    window.recent_files = window.recent_files[:window.max_recent_files]
    update_recent_files_menu(window)
    window.save_config()  # Call save_config directly on the window object