# libraries/utilities.py
import wx


def _clear_peak_params_grid(window):
    num_rows = window.peak_params_grid.GetNumberRows()
    if num_rows > 0:
        window.peak_params_grid.DeleteRows(0, num_rows)
    window.peak_count = 0  # Reset peak count when clearing the grid


def copy_cell(grid):
    print("Copy cell function called")
    print(f"Grid has focus: {grid.HasFocus()}")
    print(f"Selected cells: {grid.GetSelectedCells()}")

    if grid.HasFocus():
        if grid.GetSelectedCells():
            print("CTL C has focus")
            row, col = grid.GetSelectedCells()[0]
            data = grid.GetCellValue(row, col)
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(data))
                wx.TheClipboard.Close()
        else:
            print("No cells selected")
    else:
        print("Grid does not have focus")

def paste_cell(grid):
    if grid.HasFocus() and wx.TheClipboard.Open():
        if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
            data = wx.TextDataObject()
            wx.TheClipboard.GetData(data)
            if grid.GetSelectedCells():
                row, col = grid.GetSelectedCells()[0]
                grid.SetCellValue(row, col, data.GetText())
        wx.TheClipboard.Close()
