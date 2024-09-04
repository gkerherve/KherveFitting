import wx
import os
import json
import openpyxl
import wx

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

def import_avantage_file(window):
    # Open file dialog to select the Avantage Excel file
    with wx.FileDialog(window, "Open Avantage Excel file", wildcard="Excel files (*.xlsx)|*.xlsx",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return

        file_path = fileDialog.GetPath()

    # Load the selected workbook
    wb = openpyxl.load_workbook(file_path)

    # List to keep track of sheets to be removed
    sheets_to_remove = []

    # Iterate through all sheets in the workbook
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]

        if "Survey" in sheet_name or "Scan" in sheet_name:
            # Process Survey or Scan sheets
            if "Survey" in sheet_name or "survey" in sheet_name:
                new_name = "Survey XPS"
            else:
                new_name = sheet_name.split()[0]

            wb.create_sheet(new_name)
            new_sheet = wb[new_name]
            new_sheet['A1'] = "Binding Energy"
            new_sheet['B1'] = "Raw Data"
            # Copy data starting from row 17, skipping column B
            for row in sheet.iter_rows(min_row=17, values_only=True):
                new_sheet.append([row[0]] + list(row[2:]))
            sheets_to_remove.append(sheet_name)

            # Remove data from columns C to X
            for col in new_sheet.iter_cols(min_col=3, max_col=24):
                for cell in col:
                    cell.value = None

        else:
            # Mark other sheets for removal
            sheets_to_remove.append(sheet_name)

    # Remove the original sheets
    for sheet_name in sheets_to_remove:
        del wb[sheet_name]

    # Save the modified workbook with a new name
    new_file_path = os.path.splitext(file_path)[0] + "_Kfitting.xlsx"
    wb.save(new_file_path)

    # Open the newly created file using the existing open_xlsx_file function
    from Functions import open_xlsx_file
    open_xlsx_file(window, new_file_path)