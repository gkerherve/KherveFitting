# FUNCTIONS.PY-------------------------------------------------------------------

# LIBRARIES----------------------------------------------------------------------
import wx
import wx.grid
from wx import DirDialog, MessageBox

import pandas as pd
import numpy as np
import lmfit
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from scipy.stats import linregress
from Save import save_data
from vamas import Vamas
from openpyxl import Workbook
from ConfigFile import *
from Save import refresh_sheets
# from libraries.Sheet_Operations import on_sheet_selected
from libraries.Plot_Operations import PlotManager
from libraries.Peak_Functions import PeakFunctions
# from libraries.Peak_Functions import gauss_lorentz, S_gauss_lorentz


# -------------------------------------------------------------------------------

def save_data_wrapper(window, data):
    from Save import save_data
    save_data(window, data)

def on_sheet_selected_wrapper(window, event):
    from libraries.Sheet_Operations import on_sheet_selected
    on_sheet_selected(window, event)

def load_rsf_data(file_path):
    rsf_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) == 2:
                core_level, rsf = parts
                rsf_dict[core_level] = float(rsf)
    return rsf_dict




from matplotlib.ticker import ScalarFormatter



def safe_delete_rows(grid, pos, num_rows):
    try:
        if pos >= 0 and num_rows > 0 and (pos + num_rows) <= grid.GetNumberRows():
            grid.DeleteRows(pos, num_rows)
        else:
            wx.MessageBox("Invalid row indices for deletion.", "Information", wx.OK | wx.ICON_INFORMATION)
    except Exception as e:
        # wx.MessageBox(f"Error deleting rows: {e}", "Error", wx.OK | wx.ICON_ERROR)
        print("Error")





def remove_peak(window):
    num_rows = window.peak_params_grid.GetNumberRows()
    if num_rows > 0:
        sheet_name = window.sheet_combobox.GetValue()

        # Remove the last two rows from the peak_params_grid
        if num_rows >= 2:
            safe_delete_rows(window.peak_params_grid, num_rows - 2, 2)
        elif num_rows == 1:
            safe_delete_rows(window.peak_params_grid, num_rows - 1, 1)
        else:
            wx.MessageBox("No rows to delete.", "Information", wx.OK | wx.ICON_INFORMATION)
            return

        # Decrease the peak count
        window.peak_count = num_rows // 2 - 1  # Update peak count based on remaining rows

        # Remove the last peak from window.Data
        if 'Fitting' in window.Data['Core levels'][sheet_name] and 'Peaks' in window.Data['Core levels'][sheet_name][
            'Fitting']:
            peaks = window.Data['Core levels'][sheet_name]['Fitting']['Peaks']
            if peaks:
                last_peak_key = f"p{window.peak_count + 1}"
                if last_peak_key in peaks:
                    del peaks[last_peak_key]
                else:
                    # If the key doesn't match the expected pattern, remove the last item
                    peaks.popitem()

        # Reset the selected peak index
        window.selected_peak_index = None

        # Call the method to clear and replot everything
        window.clear_and_replot()

        # Layout the updated panel
        window.panel.Layout()

        window.canvas.draw_idle()
    else:
        wx.MessageBox("No peaks to remove.", "Information", wx.OK | wx.ICON_INFORMATION)





def plot_noise(window):
    if window.noise_min_energy is not None and window.noise_max_energy is not None:
        mask = (window.x_values >= window.noise_min_energy) & (window.x_values <= window.noise_max_energy)
        x_values_filtered = window.x_values[mask]
        y_values_filtered = window.y_values[mask]

        if len(x_values_filtered) > 0 and len(y_values_filtered) > 0:
            # Fit a linear line to the noise data
            slope, intercept, r_value, p_value, std_err = linregress(x_values_filtered, y_values_filtered)
            linear_fit = slope * x_values_filtered + intercept
            noise_subtracted = y_values_filtered - linear_fit

            # Calculate the standard deviation
            std_value = np.std(noise_subtracted)
            window.noise_std_value = std_value  # Save noise STD value in window instance

            # Create the inset plot in the main window
            if hasattr(window, 'noise_inset_ax') and window.noise_inset_ax:
                window.noise_inset_ax.clear()
            else:
                window.noise_inset_ax = window.ax.inset_axes([0.05, 0.05, 0.2, 0.2])

            window.noise_inset_ax.hist(noise_subtracted, bins=15, histtype='bar', edgecolor='black')
            window.noise_inset_ax.tick_params(axis='both', which='major', labelsize=8)
            window.noise_inset_ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            window.noise_inset_ax.set_facecolor('none')

            # Hide top, right, and left borders, and the y-axis
            window.noise_inset_ax.spines['top'].set_visible(False)
            window.noise_inset_ax.spines['right'].set_visible(False)
            window.noise_inset_ax.spines['left'].set_visible(False)
            window.noise_inset_ax.yaxis.set_visible(False)

            # Add standard deviation text
            std_value_int = int(std_value)
            window.noise_inset_ax.text(0.5, 1.1, f'STD: {std_value_int} cts',
                                       transform=window.noise_inset_ax.transAxes,
                                       fontsize=8,
                                       verticalalignment='top',
                                       horizontalalignment='center')

            window.canvas.draw()

            # Return the data for the NoiseAnalysisWindow
            return x_values_filtered, y_values_filtered, linear_fit, noise_subtracted, std_value

    return None


def remove_noise_inset(window):
    if hasattr(window, 'noise_inset_ax') and window.noise_inset_ax:
        window.noise_inset_ax.clear()
        window.noise_inset_ax.remove()
        window.noise_inset_ax = None
        window.canvas.draw()

def clear_plot(window):
    window.ax.clear()
    window.canvas.draw()

    # Reinitialize the background to raw data
    window.background = None



def clear_background(window):
    sheet_name = window.sheet_combobox.GetValue()

    if sheet_name not in window.Data['Core levels']:
        wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
        return

    try:
        window.ax.clear()

        x_values = window.Data['Core levels'][sheet_name]['B.E.']
        y_values = window.Data['Core levels'][sheet_name]['Raw Data']

        # Plot the raw data with unfilled circle markers
        window.ax.scatter(x_values, y_values, facecolors='black', marker='o', s=15, edgecolors='black', label='Raw Data')

        # Update window.x_values and window.y_values
        window.x_values = np.array(x_values)
        window.y_values = np.array(y_values)

        # Initialize background to raw data
        window.Data['Core levels'][sheet_name]['Background']['Bkg X'] = x_values
        window.Data['Core levels'][sheet_name]['Background']['Bkg Y'] = y_values
        window.background = np.array(y_values)

        # Reset background parameters
        window.Data['Core levels'][sheet_name]['Background']['Bkg Type'] = ''
        window.Data['Core levels'][sheet_name]['Background']['Bkg Low'] = ''
        window.Data['Core levels'][sheet_name]['Background']['Bkg High'] = ''
        window.Data['Core levels'][sheet_name]['Background']['Bkg Offset Low'] = ''
        window.Data['Core levels'][sheet_name]['Background']['Bkg Offset High'] = ''

        # Set x-axis limits to reverse the direction and match the min and max of the data
        window.ax.set_xlim([max(window.x_values), min(window.x_values)])

        window.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        window.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        window.ax.legend(loc='upper left')

        # Hide the cross if it exists
        if hasattr(window, 'cross') and window.cross:
            window.cross.set_visible(False)

        # Switch to "None" ticked box and hide background lines
        window.vline1 = None
        window.vline2 = None
        window.vline3 = None
        window.vline4 = None
        window.show_hide_vlines()

        # Clear all peak data from the grid
        num_rows = window.peak_params_grid.GetNumberRows()
        if num_rows > 0:
            window.peak_params_grid.DeleteRows(0, num_rows)

        # Reset peak count and selected peak index
        window.peak_count = 0
        window.selected_peak_index = None

        # Clear fitting data from window.Data
        if 'Fitting' in window.Data['Core levels'][sheet_name]:
            window.Data['Core levels'][sheet_name]['Fitting'] = {}

        # Redraw the canvas
        window.canvas.draw_idle()

        # Layout the updated panel
        window.panel.Layout()

    except Exception as e:
        wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)


def plot_background(window):
    sheet_name = window.sheet_combobox.GetValue()
    if sheet_name not in window.Data['Core levels']:
        wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
        return

    try:
        x_values = np.array(window.Data['Core levels'][sheet_name]['B.E.'], dtype=float)
        y_values = np.array(window.Data['Core levels'][sheet_name]['Raw Data'], dtype=float)

        # Remove previous background lines
        lines_to_remove = [line for line in window.ax.lines if line.get_label().startswith("Background")]
        for line in lines_to_remove:
            line.remove()

        # Initialize full-size background array with raw data if not already present
        if 'Bkg Y' not in window.Data['Core levels'][sheet_name]['Background'] or not \
                window.Data['Core levels'][sheet_name]['Background']['Bkg Y']:
            window.Data['Core levels'][sheet_name]['Background']['Bkg Y'] = y_values.tolist()

        method = window.background_method
        offset_h = float(window.offset_h)
        offset_l = float(window.offset_l)

        if method == "Adaptive Smart":
            bg_min_energy = min(x_values)
            bg_max_energy = max(x_values)
            window.Data['Core levels'][sheet_name]['Background']['Bkg Low'] = bg_min_energy
            window.Data['Core levels'][sheet_name]['Background']['Bkg High'] = bg_max_energy

            # Get the current positions of vlines for the adaptive range
            if window.vline1 is not None and window.vline2 is not None:
                vline1_x = window.vline1.get_xdata()[0]
                vline2_x = window.vline2.get_xdata()[0]
                adaptive_range = (min(vline1_x, vline2_x), max(vline1_x, vline2_x))
            else:
                adaptive_range = (bg_min_energy, bg_max_energy)

            # Use the existing background as the starting point
            current_background = np.array(window.Data['Core levels'][sheet_name]['Background']['Bkg Y'])

            background_filtered = calculate_adaptive_smart_background(
                x_values, y_values, adaptive_range, current_background, offset_h, offset_l
            )
            label = 'Background (Adaptive Smart)'
        else:
            bg_min_energy = window.Data['Core levels'][sheet_name]['Background'].get('Bkg Low')
            bg_max_energy = window.Data['Core levels'][sheet_name]['Background'].get('Bkg High')

            if bg_min_energy is None or bg_max_energy is None or bg_min_energy > bg_max_energy:
                wx.MessageBox("Invalid energy range selected.", "Warning", wx.OK | wx.ICON_INFORMATION)
                return

            mask = (x_values >= bg_min_energy) & (x_values <= bg_max_energy)
            x_values_filtered = x_values[mask]
            y_values_filtered = y_values[mask]

            if method == "Shirley":
                background_filtered = calculate_shirley_background(x_values_filtered, y_values_filtered,
                                                                   offset_h, offset_l)
                label = 'Background (Shirley)'
            elif method == "Linear":
                background_filtered = calculate_linear_background(x_values_filtered, y_values_filtered,
                                                                  offset_h, offset_l)
                label = 'Background (Linear)'
            elif method == "Smart":
                background_filtered = calculate_smart_background(x_values_filtered, y_values_filtered,
                                                                 offset_h, offset_l)
                label = 'Background (Smart)'
            else:
                raise ValueError(f"Unknown background method: {method}")

        # Create a new background array
        new_background = np.array(window.Data['Core levels'][sheet_name]['Background']['Bkg Y'])
        if method == "Adaptive Smart":
            new_background = background_filtered
        else:
            new_background[mask] = background_filtered

        window.Data['Core levels'][sheet_name]['Background']['Bkg Y'] = new_background.tolist()
        window.background = new_background

        # Update the background information in the data dictionary
        window.Data['Core levels'][sheet_name]['Background']['Bkg Type'] = method
        window.Data['Core levels'][sheet_name]['Background']['Bkg Low'] = bg_min_energy
        window.Data['Core levels'][sheet_name]['Background']['Bkg High'] = bg_max_energy
        window.Data['Core levels'][sheet_name]['Background']['Bkg Offset Low'] = offset_l
        window.Data['Core levels'][sheet_name]['Background']['Bkg Offset High'] = offset_h
        window.Data['Core levels'][sheet_name]['Background']['Bkg X'] = x_values.tolist()

        # Plot the full background
        window.ax.plot(x_values, window.background, color='grey', linestyle='--', label=label)

        # Check if peak 1 exists and tick/untick it
        if window.peak_params_grid.GetNumberRows() > 0:
            # Call the method to clear and replot everything
            window.clear_and_replot()

            # Update the legend
            window.plot_manager.update_legend(window)

        window.ax.legend(loc='upper left')
        window.canvas.draw()

    except Exception as e:
        print("Error in plot_background:", str(e))
        import traceback
        traceback.print_exc()
        wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)

def calculate_linear_background(x, y, start_offset, end_offset):
    y_start = y[0] + start_offset
    y_end = y[-1] + end_offset
    return np.linspace(y_start, y_end, len(y))

def calculate_smart_background(x, y, offset_h, offset_l):
    # Calculate both backgrounds
    shirley_bg = calculate_shirley_background(x, y, offset_h, offset_l)
    linear_bg = calculate_linear_background(x, y, offset_h, offset_l)

    # Choose the background type based on first and last y-values
    if y[0] > y[-1]:
        background = shirley_bg
    else:
        background = linear_bg

    # Ensure background does not exceed raw data
    background = np.minimum(background, y)

    return background

from scipy.signal import savgol_filter

def calculate_smart2_background(x, y, threshold=0.01):
    # Calculate the derivative
    dy = np.gradient(y, x)

    threshold = 0.001*(max(y)-min(y))


    # Smooth the derivative (optional, but often helpful)
    dy_smooth = savgol_filter(dy, window_length=30, polyorder=3)

    # Initialize the background array
    background = np.zeros_like(y)

    # Determine flat regions (where derivative is close to zero)
    flat_mask = np.abs(dy_smooth) < threshold
    # flat_mask = np.abs(dy) < threshold

    # Set background to raw data in flat regions
    background[flat_mask] = y[flat_mask]

    # For non-flat regions, decide between linear and Shirley
    for i in range(1, len(y)):
        if not flat_mask[i]:
            if y[i] < y[i - 1]:  # Data going down
                # Linear interpolation
                background[i] = background[i - 1] + (y[i] - y[i - 1])
            else:  # Data going up
                # Use Shirley method (simplified for this example)
                A = np.trapz(y[:i + 1] - background[:i + 1], x[:i + 1])
                B = np.trapz(y[i:] - background[i:], x[i:])
                background[i] = y[-1] + (y[0] - y[-1]) * B / (A + B)

    # return dy_smooth + 1.1*max(y)
    return background


def calculate_adaptive_smart_background(x, y, x_range, previous_background, offset_h, offset_l):
    # Ensure previous_background is numpy array
    previous_background = np.array(previous_background)

    # Create mask for the selected range
    mask = (x >= x_range[0]) & (x <= x_range[1])

    # Calculate new background for selected range
    new_background = np.copy(previous_background)
    x_selected = x[mask]
    y_selected = y[mask]

    # Determine if we should use Shirley or Linear in the selected range
    if y_selected[0] > y_selected[-1]:
        new_background[mask] = calculate_shirley_background(x_selected, y_selected, offset_h, offset_l)
    else:
        new_background[mask] = calculate_linear_background(x_selected, y_selected, offset_h, offset_l)

    return new_background

def calculate_shirley_background(x, y, start_offset, end_offset, max_iter=100, tol=1e-6, padding_factor=0.01):
    x = np.asarray(x)
    y = np.asarray(y)

    # Padding
    x_min, x_max = x[0], x[-1]
    padding_width = padding_factor * (x_max - x_min)
    x_padded = np.concatenate([[x_min - padding_width], x, [x_max + padding_width]])
    y_padded = np.concatenate([[y[0] + start_offset], y, [y[-1] + end_offset]])

    background = np.zeros_like(y_padded)
    I0, Iend = y_padded[0], y_padded[-1]

    for iteration in range(max_iter):
        prev_background = background.copy()
        for i in range(1, len(y_padded) - 1):  # Use len(y_padded) here
            A1 = np.trapz(y_padded[:i] - background[:i], x_padded[:i])  # Use padded arrays
            A2 = np.trapz(y_padded[i:] - background[i:], x_padded[i:])  # Use padded arrays
            background[i] = Iend + (I0 - Iend) * A2 / (A1 + A2)
        if np.all(np.abs(background - prev_background) < tol):
            break

    return background[1:-1]  # Remove padding before returning


# NOT SURE IF IT IS USED
# def open_file(window):
#     with DirDialog(window, "Open directory", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dlg:
#         if dlg.ShowModal() == wx.ID_OK:
#             path = dlg.GetPath()
#             window.entry.SetValue(path)
#             populate_listbox(window)

# NOT SURE IF IT IS USED
# def populate_listbox(window):
#     """Populates the file listbox with Excel files from the selected directory."""
#     window.file_listbox.Clear()  # Use Clear() to empty the ListBox in wxPython
#     directory = window.entry.GetValue()  # Use GetValue() for wx.TextCtrl
#     if os.path.isdir(directory):
#         for filename in os.listdir(directory):
#             if filename.endswith(".xlsx") or filename.endswith(".xls"):
#                 window.file_listbox.Append(filename)  # Use Append() to add items in wxPython
#     else:
#         wx.MessageBox("Error", "Invalid directory path", style=wx.OK | wx.ICON_ERROR)
#
#     # Bind selection event to update the sheet names
#     window.file_listbox.Bind(wx.EVT_LISTBOX, lambda event: update_sheet_names(window))






def update_sheet_names(window):
    if window.selected_files:
        file_path = window.selected_files[0]
        try:
            sheet_names = pd.ExcelFile(file_path).sheet_names
            window.sheet_combobox.Set(sheet_names)
            if sheet_names:
                window.sheet_combobox.SetSelection(0)  # Set the first sheet as selected
        except Exception as e:
            wx.MessageBox(f"Error reading sheet names: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    else:
        wx.MessageBox("No files selected.", "Information", wx.OK | wx.ICON_INFORMATION)


# I do not think it is necessary
def rename_sheet(window, new_sheet_name):
    selected_indices = window.file_listbox.GetSelections()
    sheet_name = window.sheet_combobox.GetValue()

    if selected_indices:
        for i in selected_indices:
            filename = window.file_listbox.GetString(i)
            file_path = os.path.join(window.entry.GetValue(), filename)

            try:
                with pd.ExcelFile(file_path, engine='openpyxl') as xls:
                    df = pd.read_excel(xls, sheet_name=sheet_name, engine='openpyxl')
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        for sheet in xls.sheet_names:
                            if sheet == sheet_name:
                                df.to_excel(writer, sheet_name=new_sheet_name, index=False)
                            else:
                                pd.read_excel(xls, sheet_name=sheet, engine='openpyxl').to_excel(writer, sheet_name=sheet, index=False)
            except Exception as e:
                wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)

def create_menu(window):
    menubar = wx.MenuBar()
    file_menu = wx.Menu()
    edit_menu = wx.Menu()
    view_menu = wx.Menu()
    tools_menu = wx.Menu()
    help_menu = wx.Menu()

    open_item = file_menu.Append(wx.ID_OPEN, "Open Excel File")
    window.Bind(wx.EVT_MENU, lambda event: open_xlsx_file(window), open_item)

    open_vamas_item = file_menu.Append(wx.NewId(), "Open/Convert Vamas file to Excel")
    window.Bind(wx.EVT_MENU, lambda event: open_vamas_file(window), open_vamas_item)

    save_Excel_item = file_menu.Append(wx.ID_SAVE, "Save Data to Excel")
    window.Bind(wx.EVT_MENU, lambda event: on_save(window), save_Excel_item)

    save_plot_item = file_menu.Append(wx.NewId(), "Save plot to Excel")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot(window), save_plot_item)

    save_Table_item = file_menu.Append(wx.NewId(), "Save Table - TBD")

    save_all_item = file_menu.Append(wx.NewId(), "Save all - TBD")

    file_menu.AppendSeparator()
    exit_item = file_menu.Append(wx.ID_EXIT, "Exit")
    window.Bind(wx.EVT_MENU, lambda event: on_exit(window, event), exit_item)  # Bind the on_exit function

    Undo_item = edit_menu.Append(wx.NewId(), "Undo Fit - TBD")
    Redo_item = edit_menu.Append(wx.NewId(), "Redo Fit - TBD")
    edit_menu.AppendSeparator()

    preferences_item = edit_menu.Append(wx.ID_PREFERENCES, "Preferences")
    window.Bind(wx.EVT_MENU, window.on_preferences, preferences_item)

    ToggleFitting_item = view_menu.Append(wx.NewId(), "Toggle Peak Fitting")
    window.Bind(wx.EVT_MENU, lambda event: toggle_plot(window), ToggleFitting_item)

    ToggleLegend_item = view_menu.Append(wx.NewId(), "Toggle Legend")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_legend(), ToggleLegend_item)

    ToggleFit_item = view_menu.Append(wx.NewId(), "Toggle Fit Results")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_fitting_results(), ToggleFit_item)

    ToggleRes_item = view_menu.Append(wx.NewId(), "Toggle Residuals")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_residuals(), ToggleRes_item)

    Area_item = tools_menu.Append(wx.NewId(), "Calculate Area")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_background_window(), Area_item)

    Fitting_item = tools_menu.Append(wx.NewId(), "Peak Fitting")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_fitting_window(), Fitting_item)

    Noise_item = tools_menu.Append(wx.NewId(), "Noise Analysis")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_noise_analysis_window, Noise_item)

    Manual_item = help_menu.Append(wx.NewId(), "Manual - TBD")

    menubar.Append(file_menu, "&File")
    menubar.Append(edit_menu, "&Edit")
    menubar.Append(view_menu, "&View")
    menubar.Append(tools_menu, "&Tools")
    menubar.Append(help_menu, "&Help")
    window.SetMenuBar(menubar)


def create_horizontal_toolbar(window):
    toolbar = window.CreateToolBar()
    toolbar.SetBackgroundColour(wx.Colour(220, 220, 220))
    toolbar.SetToolBitmapSize(wx.Size(25, 25))

    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # icon_path = os.path.join(current_dir, "Icons")
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, use the bundle's directory
        application_path = sys._MEIPASS
    else:
        # If the application is run as a script, use the script's directory
        application_path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(application_path, "Icons")



    separators = []

    # File operations
    open_file_tool = toolbar.AddTool(wx.ID_ANY, 'Open File', wx.Bitmap(os.path.join(icon_path, "open-folder-64-green.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open File")
    refresh_folder_tool = toolbar.AddTool(wx.ID_ANY, 'Refresh Folder', wx.Bitmap(os.path.join(icon_path, "refresh-96g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Refresh Folder")
    save_tool = toolbar.AddTool(wx.ID_ANY, 'Save', wx.Bitmap(os.path.join(icon_path, "save-Excel-64.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save the Fitted Results to Excel for this Core Level")
    save_plot_tool = toolbar.AddTool(wx.ID_ANY, 'Save Plot', wx.Bitmap(os.path.join(icon_path, "save-64.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save this Figure to Excel")

    save_all_tool = toolbar.AddTool(wx.ID_ANY, 'Save All Sheets',
                                    wx.Bitmap(os.path.join(icon_path, "save-Multi-64.png"), wx.BITMAP_TYPE_PNG),
                                    shortHelp="Save all sheets with plots")

    toolbar.AddSeparator()

    # separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    # separators[-1].SetSize((2, 24))
    # toolbar.AddControl(separators[-1])

    window.skip_rows_spinbox = wx.SpinCtrl(toolbar, min=0, max=200, initial=0, size=(60, -1))
    window.skip_rows_spinbox.SetToolTip("Set the number of rows to skip in the sheet of the Excel file")
    toolbar.AddControl(window.skip_rows_spinbox)

    # Sheet selection
    window.sheet_combobox = wx.ComboBox(toolbar, style=wx.CB_READONLY)
    window.sheet_combobox.SetToolTip("Select Sheet")
    toolbar.AddControl(window.sheet_combobox)



    # separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    # separators[-1].SetSize((2, 24))
    # toolbar.AddControl(separators[-1])

    toolbar.AddSeparator()

    separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    separators[-1].SetSize((2, 24))
    toolbar.AddControl(separators[-1])

    toolbar.AddSeparator()


    # Add BE correction spinbox
    window.be_correction_spinbox = wx.SpinCtrlDouble(toolbar, value='0.00', min=-20.00, max=20.00, inc=0.01, size=(70, -1))
    window.be_correction_spinbox.SetDigits(2)
    window.be_correction_spinbox.SetToolTip("BE Correction")
    toolbar.AddControl(window.be_correction_spinbox)

    # Add Auto BE button
    auto_be_button = toolbar.AddTool(wx.ID_ANY, 'Auto BE',
                                     wx.Bitmap(os.path.join(icon_path, "BEcorrect-64.png"), wx.BITMAP_TYPE_PNG),
                                     shortHelp="Automatic binding energy correction")

    toolbar.AddSeparator()

    separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    separators[-1].SetSize((2, 24))
    toolbar.AddControl(separators[-1])

    toolbar.AddSeparator()

    # Plot adjustment tools
    plot_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Plot',
                                wx.Bitmap(os.path.join(icon_path, "scatter-plot-60.png"),
                                wx.BITMAP_TYPE_PNG), shortHelp="Toggle between Raw Data and Fit")

    toggle_peak_fill_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Peak Fill',
                                            wx.Bitmap(os.path.join(icon_path, "STO-64.png"), wx.BITMAP_TYPE_PNG),
                                            shortHelp="Toggle Peak Fill")

    # resize_plot_tool = toolbar.AddTool(wx.ID_ANY, 'Resize Plot', wx.Bitmap(os.path.join(icon_path, "ResPlot-100.png"), wx.BITMAP_TYPE_PNG), shortHelp="Resize Plot")
    toggle_legend_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Legend',
                                         wx.Bitmap(os.path.join(icon_path, "Legend-100.png"), wx.BITMAP_TYPE_PNG),
                                         shortHelp="Toggle Legend")
    toggle_fit_results_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Fit Results',
                                              wx.Bitmap(os.path.join(icon_path, "ToggleFit-100.png"),
                                                        wx.BITMAP_TYPE_PNG), shortHelp="Toggle Fit Results")
    toggle_residuals_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Residuals',
                                            wx.Bitmap(os.path.join(icon_path, "Res-100.png"), wx.BITMAP_TYPE_PNG),
                                            shortHelp="Toggle Residuals")

    toolbar.AddSeparator()

    separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    separators[-1].SetSize((2, 24))
    toolbar.AddControl(separators[-1])

    toolbar.AddSeparator()

    # Analysis tools
    bkg_tool = toolbar.AddTool(wx.ID_ANY, 'Background', wx.Bitmap(os.path.join(icon_path, "BKG-64.png"), wx.BITMAP_TYPE_PNG),shortHelp="Calculate Area between the range cursor")
    # bkg_tool = toolbar.AddTool(wx.ID_ANY, 'Background', wx.Bitmap(wx.Bitmap(os.path.join(icon_path, "Plot_Area.ico")), wx.BITMAP_TYPE_PNG), shortHelp="Calculate Area under Peak")
    fitting_tool = toolbar.AddTool(wx.ID_ANY, 'Fitting', wx.Bitmap(os.path.join(icon_path, "C1s.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open Fitting Window")
    noise_analysis_tool = toolbar.AddTool(wx.ID_ANY, 'Noise Analysis', wx.Bitmap(os.path.join(icon_path, "Noise.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open Noise Analysis Window")

    # separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    # separators[-1].SetSize((2, 24))
    # toolbar.AddControl(separators[-1])


    # Add a spacer to push the following items to the right
    toolbar.AddStretchableSpace()

    # Add export button
    export_tool = toolbar.AddTool(wx.ID_ANY, 'Export Results',
                                  wx.Bitmap(os.path.join(icon_path, "Export-64g.png"), wx.BITMAP_TYPE_PNG),
                                  shortHelp="Export to Results Grid")

    # Hide columns in Peak Fitting Parameters
    toggle_Col_1_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Residuals',
                                            wx.Bitmap(os.path.join(icon_path, "HideColumn.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Columns Peak Fitting Parameters")

    # Add toggle button for the right panel
    window.toggle_right_panel_tool = window.add_toggle_tool(toolbar, "Toggle Right Panel",
                                                            wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR))


    # Bind the toggle event
    window.Bind(wx.EVT_TOOL, window.on_toggle_right_panel, window.toggle_right_panel_tool)

    toolbar.Realize()

    # Bind events (keeping the same bindings as before, except for BE adjustment tools)
    window.Bind(wx.EVT_TOOL, lambda event: open_xlsx_file(window), open_file_tool)
    window.Bind(wx.EVT_TOOL, lambda event: refresh_sheets(window, on_sheet_selected_wrapper), refresh_folder_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_plot(window), plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_background_window(), bkg_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_fitting_window(), fitting_tool)
    window.Bind(wx.EVT_TOOL, window.on_open_noise_analysis_window, noise_analysis_tool)
    # window.Bind(wx.EVT_TOOL, lambda event: window.resize_plot(), resize_plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_legend(), toggle_legend_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_fitting_results(), toggle_fit_results_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_residuals(), toggle_residuals_tool)
    window.sheet_combobox.Bind(wx.EVT_COMBOBOX, lambda event: on_sheet_selected_wrapper(window, event))
    window.Bind(wx.EVT_TOOL, lambda event: on_save(window), save_tool)
    window.Bind(wx.EVT_TOOL, lambda event: on_save_plot(window), save_plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: on_save_all_sheets(window,event), save_all_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_Col_1(window), toggle_Col_1_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.export_results(), export_tool)
    window.be_correction_spinbox.Bind(wx.EVT_SPINCTRLDOUBLE, window.on_be_correction_change)
    window.Bind(wx.EVT_TOOL, window.on_auto_be, auto_be_button)
    window.Bind(wx.EVT_TOOL, window.on_toggle_peak_fill, toggle_peak_fill_tool)

    return toolbar

def create_vertical_toolbar(parent, frame):
    v_toolbar = wx.ToolBar(parent, style=wx.TB_VERTICAL | wx.TB_FLAT)
    v_toolbar.SetBackgroundColour(wx.Colour(220, 220, 220))
    v_toolbar.SetToolBitmapSize(wx.Size(25, 25))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "Icons")


    # Add zoom tool
    # Add zoom in tool
    zoom_in_tool = v_toolbar.AddTool(wx.ID_ANY, 'Zoom In',
                                     wx.Bitmap(os.path.join(icon_path, "ZoomIN-64.png"), wx.BITMAP_TYPE_PNG),
                                     shortHelp="Zoom In")

    # Add zoom out tool (previously resize_plot)
    zoom_out_tool = v_toolbar.AddTool(wx.ID_ANY, 'Zoom Out',
                                      wx.Bitmap(os.path.join(icon_path, "ZoomOUT.png"), wx.BITMAP_TYPE_PNG),
                                      shortHelp="Zoom Out")

    # Add drag tool
    drag_tool = v_toolbar.AddTool(wx.ID_ANY, 'Drag',
                                  wx.Bitmap(os.path.join(icon_path, "drag-64.png"), wx.BITMAP_TYPE_PNG),
                                  shortHelp="Drag Plot")

    v_toolbar.AddSeparator()

    # BE adjustment tools
    high_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE +', wx.Bitmap(os.path.join(icon_path, "Right-Red-64g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Increase High BE")
    high_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE -', wx.Bitmap(os.path.join(icon_path, "Left-Red-64g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Decrease High BE")

    v_toolbar.AddSeparator()

    low_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE +', wx.Bitmap(os.path.join(icon_path, "Left-Blue-64g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Increase Low BE")
    low_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE -', wx.Bitmap(os.path.join(icon_path, "Right-Blue-64g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Decrease Low BE")

    # v_toolbar.AddSeparator()

    # # Add increment spin control
    # increment_label = wx.StaticText(v_toolbar, label="Increment:")
    # v_toolbar.AddControl(increment_label)
    # frame.be_increment_spin = wx.SpinCtrlDouble(v_toolbar, value='1.0', min=0.1, max=10.0, inc=0.1, size=(60, -1))
    # # v_toolbar.AddControl(frame.be_increment_spin)   #  DO NOT ADD YET


    v_toolbar.AddSeparator()

    # Intensity adjustment tools
    high_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int +', wx.Bitmap(os.path.join(icon_path, "Up-Red-64g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Increase High Intensity")
    high_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int -', wx.Bitmap(os.path.join(icon_path, "Down-Red-64g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Decrease High Intensity")

    v_toolbar.AddSeparator()

    low_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low Int +', wx.Bitmap(os.path.join(icon_path, "Up-Blue-64g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Increase Low Intensity")
    low_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY,
                                              'Low Int -',
                                              wx.Bitmap(os.path.join(icon_path, "Down-Blue-64g.png"),
                                              wx.BITMAP_TYPE_PNG),
                                              shortHelp="Decrease Low Intensity")

    v_toolbar.AddSeparator()

    # resize_plot_tool = v_toolbar.AddTool(wx.ID_ANY, 'Resize Plot',
    #                                    wx.Bitmap(os.path.join(icon_path, "ZoomOUT.png"), wx.BITMAP_TYPE_PNG),
    #                                    shortHelp="Resize Plot")



    v_toolbar.Realize()

    # Bind events to the frame
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_be', 'increase'), high_be_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_be', 'decrease'), high_be_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_be', 'increase'), low_be_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_be', 'decrease'), low_be_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_int', 'increase'), high_int_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_int', 'decrease'), high_int_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_int', 'increase'), low_int_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_int', 'decrease'), low_int_decrease_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_zoom_in_tool, zoom_in_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_zoom_out, zoom_out_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_drag_tool, drag_tool)


    return v_toolbar

def create_statusbar(window):
    # Create a status bar
    window.CreateStatusBar(2)
    window.SetStatusWidths([-1, 200])
    window.SetStatusText("Working Directory: "+window.Working_directory,0)
    window.SetStatusText("BE: 0 eV, I: 0 CTS" ,1)

def update_statusbar(window, message):
    window.SetStatusText("Working Directory: "+message)

def on_exit(window, event):
    """Handles the Exit menu item."""
    window.Close()



def toggle_plot(window):
    window.show_fit = not window.show_fit
    sheet_name = window.sheet_combobox.GetValue()
    if window.show_fit:
        window.clear_and_replot()
    else:
        window.plot_manager.plot_data(window)
    window.canvas.draw_idle()

import json
from ConfigFile import Init_Measurement_Data, add_core_level_Data

def open_xlsx_file(window):
    print("Starting open_xlsx_file function")
    with wx.FileDialog(window, "Open XLSX file", wildcard="Excel files (*.xlsx)|*.xlsx",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
        if dlg.ShowModal() == wx.ID_OK:
            file_path = dlg.GetPath()
            window.SetStatusText(f"Selected File: {file_path}", 0)

            try:
                # Clear the results grid
                window.results_grid.ClearGrid()
                if window.results_grid.GetNumberRows() > 0:
                    window.results_grid.DeleteRows(0, window.results_grid.GetNumberRows())

                # Look for corresponding .json file
                json_file = os.path.splitext(file_path)[0] + '.json'
                if os.path.exists(json_file):
                    print(f"Found corresponding .json file: {json_file}")
                    with open(json_file, 'r') as f:
                        loaded_data = json.load(f)

                    # Convert data structure without changing types
                    window.Data = convert_from_serializable(loaded_data)

                    print("Loaded data from .json file")

                    # Populate the results grid
                    populate_results_grid(window)
                else:
                    print("No corresponding .json file found. Initializing new data.")
                    # Initialize the measurement data
                    window.Data = Init_Measurement_Data(window)

                # Read the Excel file
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                print(f"Number of sheets: {len(sheet_names)}")

                # Update file path
                window.Data['FilePath'] = file_path

                # If we didn't load from json, populate the data from Excel
                if 'Core levels' not in window.Data or not window.Data['Core levels']:
                    window.Data['Number of Core levels'] = 0
                    for sheet_name in sheet_names:
                        window.Data = add_core_level_Data(window.Data, window, file_path, sheet_name)

                print(f"Final number of core levels: {window.Data['Number of Core levels']}")

                # Load BE correction
                window.load_be_correction()

                # Update sheet names in the combobox
                window.sheet_combobox.Clear()
                window.sheet_combobox.AppendItems(sheet_names)

                # Set the first sheet as the selected one
                first_sheet = sheet_names[0]
                window.sheet_combobox.SetValue(first_sheet)

                # Use on_sheet_selected to update peak parameter grid and plot
                event = wx.CommandEvent(wx.EVT_COMBOBOX.typeId)
                event.SetString(first_sheet)
                window.plot_config.plot_limits.clear()
                on_sheet_selected_wrapper(window,event)

                print("open_xlsx_file function completed successfully")
            except Exception as e:
                print(f"Error in open_xlsx_file: {str(e)}")
                import traceback
                traceback.print_exc()
                wx.MessageBox(f"Error reading file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

def populate_results_grid(window):
    if 'Results' in window.Data and 'Peak' in window.Data['Results']:
        results = window.Data['Results']['Peak']

        # Clear existing data in the grid
        window.results_grid.ClearGrid()

        # Resize the grid if necessary
        num_rows = len(results)
        num_cols = 20  # Based on your Export.py structure
        if window.results_grid.GetNumberRows() < num_rows:
            window.results_grid.AppendRows(num_rows - window.results_grid.GetNumberRows())
        if window.results_grid.GetNumberCols() < num_cols:
            window.results_grid.AppendCols(num_cols - window.results_grid.GetNumberCols())

        # Set column labels
        column_labels = ["Peak", "Position", "Height", "FWHM", "L/G", "Area", "at. %", " ", "RSF", "Fitting Model",
                         "Rel. Area", "Tail E", "Tail M", "Bkg Low", "Bkg High", "Sheetname",
                         "Pos. Constraint", "Height Constraint", "FWHM Constraint", "L/G Constraint"]
        for col, label in enumerate(column_labels):
            window.results_grid.SetColLabelValue(col, label)

        # Populate the grid
        for row, (peak_label, peak_data) in enumerate(results.items()):
            window.results_grid.SetCellValue(row, 0, peak_data['Name'])
            window.results_grid.SetCellValue(row, 1, str(peak_data['Position']))
            window.results_grid.SetCellValue(row, 2, str(peak_data['Height']))
            window.results_grid.SetCellValue(row, 3, str(peak_data['FWHM']))
            window.results_grid.SetCellValue(row, 4, str(peak_data['L/G']))
            window.results_grid.SetCellValue(row, 5, f"{peak_data['Area']:.2f}")
            window.results_grid.SetCellValue(row, 6, f"{peak_data['at. %']:.2f}")

            # Set up checkbox
            window.results_grid.SetCellRenderer(row, 7, wx.grid.GridCellBoolRenderer())
            window.results_grid.SetCellEditor(row, 7, wx.grid.GridCellBoolEditor())
            window.results_grid.SetCellValue(row, 7, '0')  # Initialize as unchecked

            window.results_grid.SetCellValue(row, 8, f"{peak_data['RSF']:.2f}")
            window.results_grid.SetCellValue(row, 9, peak_data['Fitting Model'])
            window.results_grid.SetCellValue(row, 10, f"{peak_data['Rel. Area']:.2f}")
            window.results_grid.SetCellValue(row, 11, peak_data['Tail E'])
            window.results_grid.SetCellValue(row, 12, peak_data['Tail M'])
            window.results_grid.SetCellValue(row, 13, str(peak_data['Bkg Low']))
            window.results_grid.SetCellValue(row, 14, str(peak_data['Bkg High']))
            window.results_grid.SetCellValue(row, 15, peak_data['Sheetname'])
            window.results_grid.SetCellValue(row, 16, peak_data['Pos. Constraint'])
            window.results_grid.SetCellValue(row, 17, peak_data['Height Constraint'])
            window.results_grid.SetCellValue(row, 18, peak_data['FWHM Constraint'])
            window.results_grid.SetCellValue(row, 19, peak_data['L/G Constraint'])

        # Bind events
        window.results_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, window.on_checkbox_update)
        window.results_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, window.on_cell_changed)

        # Refresh the grid
        window.results_grid.ForceRefresh()
        print("Results grid populated from window.Data")
    else:
        print("No results data found in window.Data")

    # Calculate atomic percentages for checked elements
    window.update_atomic_percentages()



def convert_from_serializable(obj):
    if isinstance(obj, list):
        return [convert_from_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_from_serializable(v) for k, v in obj.items()}
    else:
        return obj


import wx
import os
import shutil
import pandas as pd
from vamas import Vamas
from openpyxl import Workbook



def open_vamas_file(window):
    with wx.FileDialog(window, "Open VAMAS file", wildcard="VAMAS files (*.vms)|*.vms",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return

        original_vamas_path = fileDialog.GetPath()

    try:
        if not os.path.exists(original_vamas_path):
            raise FileNotFoundError(f"The file {original_vamas_path} does not exist.")

        vamas_filename = os.path.basename(original_vamas_path)
        destination_path = os.path.join(os.getcwd(), vamas_filename)
        shutil.copy2(original_vamas_path, destination_path)

        vamas_data = Vamas(vamas_filename)

        wb = Workbook()
        wb.remove(wb.active)

        for block in vamas_data.blocks:
            sheet_name = f"{block.species_label}".replace("/", "_")
            ws = wb.create_sheet(title=sheet_name)

            num_points = block.num_y_values
            x_start = block.x_start
            x_step = block.x_step
            x_values = [x_start + i * x_step for i in range(num_points)]
            y_values = block.corresponding_variables[0].y_values

            if block.x_label == "Kinetic Energy":
                x_values = [window.photons - x - window.workfunction for x in x_values]
                x_label = "Binding Energy"
            else:
                x_label = block.x_label

            ws.append([x_label, "Intensity"])
            for x, y in zip(x_values, y_values):
                ws.append([x, y])

        excel_filename = os.path.splitext(vamas_filename)[0] + ".xlsx"
        excel_path = os.path.join(os.path.dirname(original_vamas_path), excel_filename)
        wb.save(excel_path)

        os.remove(destination_path)

        # Update window.Data with the new Excel file
        window.Data = Init_Measurement_Data(window)
        window.Data['FilePath'] = excel_path

        # Open the Excel file and populate window.Data
        open_xlsx_file_vamas(window, excel_path)

    except FileNotFoundError as e:
        wx.MessageBox(f"File not found: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    except Exception as e:
        wx.MessageBox(f"Error processing VAMAS file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

def open_xlsx_file_vamas(window, file_path):
    try:
        window.SetStatusText(f"Selected File: {file_path}", 0)

        # Initialize the measurement data
        window.Data = Init_Measurement_Data(window)
        window.Data['FilePath'] = file_path

        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names

        # Update number of core levels (sheets)
        window.Data['Number of Core levels'] = 0  # Initialize to 0, we'll increment in add_core_level_Data

        # Add core level data for each sheet
        for sheet_name in sheet_names:
            window.Data = add_core_level_Data(window.Data, window, file_path, sheet_name)

        print(f"Final number of core levels: {window.Data['Number of Core levels']}")

        # Update sheet names in the combobox
        window.sheet_combobox.Clear()
        window.sheet_combobox.AppendItems(sheet_names)
        window.sheet_combobox.SetValue(sheet_names[0])  # Set first sheet as default

        # Update other necessary GUI elements or data structures
        update_sheet_names(window)

        # Plot the data for the first sheet
        window.plot_manager.plot_data(window)

    except Exception as e:
        print(f"Error in open_xlsx_file_vamas: {str(e)}")
        import traceback
        traceback.print_exc()
        wx.MessageBox(f"Error reading Excel file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)

def on_save_plot(window):
    print("on_save plot function called")
    from Save import save_plot_to_excel
    save_plot_to_excel(window)


def on_save(window):
    print("on_save function called")
    from Save import save_data
    data = window.get_data_for_save()
    save_data(window,data)
    # save_data(window, data)

def on_save_all_sheets(window, event):
    from Save import save_all_sheets_with_plots
    save_all_sheets_with_plots(window)

def toggle_Col_1(window):
    # List of columns to toggle
    columns1 = [11, 12, 13, 14, 15,16]
    columns2 = [8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]


    # Check if the first column in the list is hidden or shown
    if window.peak_params_grid.IsColShown(columns1[0]):
        for col in columns1:
            window.peak_params_grid.HideCol(col)
        for col in columns2:
            window.results_grid.HideCol(col)
    else:
        for col in columns1:
            window.peak_params_grid.ShowCol(col)
        for col in columns2:
            window.results_grid.ShowCol(col)

    # print(window.Data)




def calculate_r2(y_true, y_pred):
    """Calculate the coefficient of determination (R²)"""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)


def calculate_chi_square(y_true, y_pred):
    """Calculate the chi-square value"""
    return np.sum((y_true - y_pred) ** 2 / y_pred)



from matplotlib.ticker import ScalarFormatter
import matplotlib.pyplot as plt


def fit_peaks2(window, peak_params_grid):
    """
    Perform peak fitting on the spectral data and update the plot and window.Data.
    """
    # Check if peak parameters are defined
    if peak_params_grid is None or peak_params_grid.GetNumberRows() == 0:
        wx.MessageBox("No peak parameters defined. Please add at least one peak before fitting.", "Error",
                      wx.OK | wx.ICON_ERROR)
        return None

    sheet_name = window.sheet_combobox.GetValue()

    if sheet_name not in window.plot_config.plot_limits:
        window.plot_config.update_plot_limits(window, sheet_name)
    limits = window.plot_config.plot_limits[sheet_name]


    if sheet_name not in window.Data['Core levels']:
        wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
        return None

    # Extract data for the selected core level
    core_level_data = window.Data['Core levels'][sheet_name]
    x_values = np.array(core_level_data['B.E.'])
    y_values = np.array(core_level_data['Raw Data'])
    background = np.array(core_level_data['Background']['Bkg Y'])

    # Log peak information for debugging
    num_peaks = peak_params_grid.GetNumberRows() // 2

    # Get background energy range
    bg_min_energy = core_level_data['Background'].get('Bkg Low')
    bg_max_energy = core_level_data['Background'].get('Bkg High')

    if bg_min_energy is not None and bg_max_energy is not None and bg_min_energy <= bg_max_energy:
        # Create mask for the selected energy range
        mask = (x_values >= bg_min_energy) & (x_values <= bg_max_energy)
        x_values_filtered = x_values[mask]
        y_values_filtered = y_values[mask]
        background_filtered = background[mask]

        if len(x_values_filtered) > 0 and len(y_values_filtered) > 0:
            # Subtract background from the data
            y_values_subtracted = y_values_filtered - background_filtered

            model_choice = window.selected_fitting_method
            max_nfev = window.max_iterations

            model = None
            params = lmfit.Parameters()

            individual_peaks = []

            # Set up the model and parameters for each peak
            for i in range(num_peaks):
                row = i * 2
                center = float(peak_params_grid.GetCellValue(row, 2))
                height = float(peak_params_grid.GetCellValue(row, 3))
                fwhm = float(peak_params_grid.GetCellValue(row, 4))
                lg_ratio = float(peak_params_grid.GetCellValue(row, 5))
                peak_model_choice = peak_params_grid.GetCellValue(row, 11)  # Assuming column 11 is the Fitting Model
                sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
                gamma = lg_ratio * sigma

                # Parse constraints for each parameter
                center_min, center_max, center_vary = parse_constraints(peak_params_grid.GetCellValue(row + 1, 2),
                                                                        center, peak_params_grid, i, "Position")
                height_min, height_max, height_vary = parse_constraints(peak_params_grid.GetCellValue(row + 1, 3),
                                                                        height, peak_params_grid, i, "Height")
                fwhm_min, fwhm_max, fwhm_vary = parse_constraints(peak_params_grid.GetCellValue(row + 1, 4),
                                                                  fwhm, peak_params_grid, i, "FWHM")
                lg_ratio_min, lg_ratio_max, lg_ratio_vary = parse_constraints(peak_params_grid.GetCellValue(row + 1, 5),
                                                                              lg_ratio, peak_params_grid, i, "L/G")


                # Evaluate constraints
                center_min = evaluate_constraint(center_min, peak_params_grid, 'center', center)
                center_max = evaluate_constraint(center_max, peak_params_grid, 'center', center)
                height_min = evaluate_constraint(height_min, peak_params_grid, 'height', height)
                height_max = evaluate_constraint(height_max, peak_params_grid, 'height', height)
                fwhm_min = evaluate_constraint(fwhm_min, peak_params_grid, 'fwhm', fwhm)
                fwhm_max = evaluate_constraint(fwhm_max, peak_params_grid, 'fwhm', fwhm)
                lg_ratio_min = evaluate_constraint(lg_ratio_min, peak_params_grid, 'lg_ratio', lg_ratio)
                lg_ratio_max = evaluate_constraint(lg_ratio_max, peak_params_grid, 'lg_ratio', lg_ratio)


                sigma_min = fwhm_min / (2 * np.sqrt(2 * np.log(2))) if fwhm_min is not None else None
                sigma_max = fwhm_max / (2 * np.sqrt(2 * np.log(2))) if fwhm_max is not None else None
                gamma_min = lg_ratio_min * sigma_min if lg_ratio_min is not None and sigma_min is not None else None
                gamma_max = lg_ratio_max * sigma_max if lg_ratio_max is not None and sigma_max is not None else None

                prefix = f'peak{i}_'

                # Create the appropriate peak model based on the selected fitting method
                if peak_model_choice == "Voigt":
                    peak_model = lmfit.models.VoigtModel(prefix=prefix)
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}sigma', value=sigma, min=sigma_min, max=sigma_max, vary=fwhm_vary)
                    params.add(f'{prefix}gamma', value=gamma, min=gamma_min, max=gamma_max, vary=lg_ratio_vary)
                elif peak_model_choice == "Pseudo-Voigt":
                    peak_model = lmfit.models.PseudoVoigtModel(prefix=prefix)
                    sigma = fwhm / 2.355
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}amplitude', value=height * sigma * np.sqrt(2 * np.pi), min=0)
                    params.add(f'{prefix}sigma', value=sigma, min=fwhm_min / 2.355 if fwhm_min else None,
                               max=fwhm_max / 2.355 if fwhm_max else None, vary=fwhm_vary)
                    params.add(f'{prefix}fraction', value=lg_ratio, min=0, max=1, vary=lg_ratio_vary)
                elif peak_model_choice == "Pseudo-Voigt2":
                    peak_model = lmfit.models.PseudoVoigtModel(prefix=prefix)
                    sigma = fwhm / 2.355
                    # Use the current height as initial guess, let the model handle the conversion
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}sigma', value=sigma,
                               min=fwhm_min / 2.355 if fwhm_min is not None else None,
                               max=fwhm_max / 2.355 if fwhm_max is not None else None,
                               vary=fwhm_vary)
                    params.add(f'{prefix}fraction', value=lg_ratio, min=lg_ratio_min, max=lg_ratio_max,
                               vary=lg_ratio_vary)
                elif peak_model_choice == "GL":
                    peak_model = lmfit.Model(PeakFunctions.gauss_lorentz, prefix=prefix)
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}fwhm', value=fwhm, min=fwhm_min, max=fwhm_max, vary=fwhm_vary)
                    params.add(f'{prefix}fraction', value=lg_ratio, min=lg_ratio_min, max=lg_ratio_max,
                               vary=lg_ratio_vary)
                elif peak_model_choice == "SGL":
                    peak_model = lmfit.Model(PeakFunctions.S_gauss_lorentz, prefix=prefix)
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}fwhm', value=fwhm, min=fwhm_min, max=fwhm_max, vary=fwhm_vary)
                    params.add(f'{prefix}fraction', value=lg_ratio, min=lg_ratio_min, max=lg_ratio_max,
                               vary=lg_ratio_vary)
                else:
                    raise ValueError(f"Unknown fitting model: {peak_model_choice} for peak {i}")

                # Add the peak model to the overall model
                if model is None:
                    model = peak_model
                else:
                    model += peak_model

                individual_peaks.append(peak_model)

            # Perform the fit
            result = model.fit(y_values_subtracted, params, x=x_values_filtered, max_nfev=max_nfev)

            # Calculate goodness-of-fit metrics
            residuals = y_values_subtracted - result.best_fit
            ss_res = np.sum(residuals ** 2)
            ss_tot = np.sum((y_values_subtracted - np.mean(y_values_subtracted)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            window.r_squared = r_squared
            chi_square = result.chisqr
            red_chi_square = result.redchi

            # Update peak parameters in the grid with fit results and update window.Data
            if 'Fitting' not in window.Data['Core levels'][sheet_name]:
                window.Data['Core levels'][sheet_name]['Fitting'] = {}
            if 'Peaks' not in window.Data['Core levels'][sheet_name]['Fitting']:
                window.Data['Core levels'][sheet_name]['Fitting']['Peaks'] = {}

            existing_peaks = window.Data['Core levels'][sheet_name]['Fitting']['Peaks']

            # After the fit, update peak parameters
            for i in range(num_peaks):
                row = i * 2
                prefix = f'peak{i}_'
                peak_label = peak_params_grid.GetCellValue(row, 1)
                peak_model_choice = peak_params_grid.GetCellValue(row, 11)

                if peak_label in existing_peaks:
                    center = result.params[f'{prefix}center'].value
                    if peak_model_choice == "Voigt":
                        amplitude = result.params[f'{prefix}amplitude'].value
                        sigma = result.params[f'{prefix}sigma'].value
                        gamma = result.params[f'{prefix}gamma'].value
                        height = PeakFunctions.get_voigt_height(amplitude, sigma, gamma)
                        fwhm = PeakFunctions.voigt_fwhm(sigma, gamma)
                        fraction = gamma / (sigma * np.sqrt(2 * np.log(2)))
                        area = amplitude * (sigma * np.sqrt(2 * np.pi))
                    elif peak_model_choice == "Pseudo-Voigt":
                        amplitude = result.params[f'{prefix}amplitude'].value
                        sigma = result.params[f'{prefix}sigma'].value
                        fraction = result.params[f'{prefix}fraction'].value
                        fwhm = sigma * 2.355
                        height = PeakFunctions.get_pseudo_voigt_height(amplitude, sigma, fraction)
                        area = amplitude  # Area for Pseudo-Voigt (amplitude is already the area)
                    elif peak_model_choice in ["GL", "SGL"]:
                        height = result.params[f'{prefix}amplitude'].value
                        fwhm = result.params[f'{prefix}fwhm'].value
                        fraction = result.params[f'{prefix}fraction'].value
                        area = height * fwhm * np.sqrt(np.pi / (4 * np.log(2)))  # Area for GL and SGL
                    else:
                        raise ValueError(f"Unknown fitting model: {peak_model_choice} for peak {peak_label}")

                    # Round the values
                    center = round(float(center), 2)
                    height = round(float(height), 2)
                    fwhm = round(float(fwhm), 2)
                    fraction = round(float(fraction), 2)
                    area = round(float(area), 2)

                    # Update peak_params_grid
                    peak_params_grid.SetCellValue(row, 2, f"{center:.2f}")
                    peak_params_grid.SetCellValue(row, 3, f"{height:.2f}")
                    peak_params_grid.SetCellValue(row, 4, f"{fwhm:.2f}")
                    peak_params_grid.SetCellValue(row, 5, f"{fraction:.2f}")
                    peak_params_grid.SetCellValue(row, 6, f"{area:.2f}")  # Assuming column 6 is for Area

                    # Update existing peak in window.Data
                    existing_peaks[peak_label].update({
                        'Position': center,
                        'Height': height,
                        'FWHM': fwhm,
                        'L/G': fraction,
                        'Area': area,
                        'Fitting Model': peak_model_choice
                    })
                else:
                    print(f"Warning: Peak {peak_label} not found in existing data. Skipping update for this peak.")

            # Update the fitting model for the sheet
            window.Data['Core levels'][sheet_name]['Fitting']['Model'] = model_choice

            print(f"Updated peaks: {list(existing_peaks.keys())}")

            # Generate color palette for peaks
            colors = plt.cm.Set1(np.linspace(0, 1, len(individual_peaks)))

            try:
                # Store existing sheet name text
                sheet_name_text = None
                for txt in window.ax.texts:
                    if getattr(txt, 'sheet_name_text', False):
                        sheet_name_text = txt
                        break

                # Plotting
                window.ax.clear()



                # Plot envelope
                fitted_peak = y_values.copy()
                fitted_peak[mask] = result.best_fit + background_filtered
                window.ax.plot(x_values, fitted_peak, 'b', alpha=0.6, label='Envelope')

                # Scale and plot residuals
                residuals = np.zeros_like(y_values)
                residuals[mask] = y_values_subtracted - result.best_fit
                max_raw_data = max(y_values)
                desired_max_residual = 0.1 * max_raw_data
                actual_max_residual = max(abs(residuals))
                scaling_factor = desired_max_residual / actual_max_residual if actual_max_residual != 0 else 1
                scaled_residuals = residuals * scaling_factor + 1.05 * max(y_values)
                residuals_line, = window.ax.plot(x_values, scaled_residuals, 'g', alpha=0.4, label='Residuals')

                # Plot individual peaks
                for i, (peak_model, color) in enumerate(zip(individual_peaks, colors)):
                    peak = np.zeros_like(y_values)
                    peak[mask] = peak_model.eval(result.params, x=x_values_filtered)
                    peak_name = peak_params_grid.GetCellValue(i * 2, 1)
                    # window.ax.fill_between(x_values, background, peak + background, facecolor=color,
                    #                        alpha=0.8, label=peak_name)
                    # window.ax.plot(x_values, peak + background, 'black', alpha=0.4)
                    window.ax.plot(x_values, peak + background, alpha = 0.5)
                    window.ax.fill_between(x_values, background, peak + background,
                                              alpha=0.3, label=peak_name)

                window.ax.plot(x_values, background, 'gray', linestyle='--', label='Background',alpha=0.7)

                window.ax.scatter(x_values, y_values, facecolors='black', marker='o', s=20, edgecolors='black',
                                  label='Raw Data')

                # Set plot labels and formatting
                window.ax.legend(loc='upper left')
                window.ax.set_ylabel(f"Intensity (CTS), residual x {scaling_factor:.2f}")
                window.ax.set_xlabel("Binding Energy (eV)")
                window.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
                window.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

                # Use the stored limits from PlotConfig
                window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
                window.ax.set_ylim(limits['Ymin'], limits['Ymax'])

                # Add text annotations with fit results
                std_value_int = int(window.noise_std_value) if hasattr(window, 'noise_std_value') else "N/A"
                nfev_used = result.nfev

                window.plot_manager.set_fitting_results_text(f'Noise STD: {std_value_int}'
                                                             f' cts\nR²: {r_squared:.5f}\nChi²: {chi_square:.2f}\nRed. Chi²: {red_chi_square:.2f}\nIteration: {nfev_used}')
                window.residuals_line = residuals_line

                # Restore or add sheet name text
                if sheet_name_text is None:
                    formatted_sheet_name = format_sheet_name2(sheet_name)
                    sheet_name_text = window.ax.text(
                        0.98, 0.98,  # Position (top-right corner)
                        formatted_sheet_name,
                        transform=window.ax.transAxes,
                        fontsize=15,
                        fontweight='bold',
                        verticalalignment='top',
                        horizontalalignment='right',
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
                    )
                    sheet_name_text.sheet_name_text = True  # Mark this text object
                else:
                    window.ax.add_artist(sheet_name_text)

                window.canvas.draw()

                # Reset vertical lines
                window.vline1 = None
                window.vline2 = None
                window.vline3 = None
                window.vline4 = None

                window.update_ratios()

                return r_squared, chi_square, red_chi_square

            except Exception as e:
                print(f"Error in fit_peaks: {str(e)}")
                import traceback
                traceback.print_exc()
                wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)

        else:
            raise ValueError("No data points found in the specified energy range for background subtraction")

    else:
        raise ValueError("Invalid background energy range")

def fit_peaks(window, peak_params_grid):
    """
    Perform peak fitting on the spectral data and update the peak parameters.
    """
    if peak_params_grid is None or peak_params_grid.GetNumberRows() == 0:
        wx.MessageBox("No peak parameters defined. Please add at least one peak before fitting.", "Error",
                      wx.OK | wx.ICON_ERROR)
        return None

    sheet_name = window.sheet_combobox.GetValue()

    if sheet_name not in window.plot_config.plot_limits:
        window.plot_config.update_plot_limits(window, sheet_name)
    limits = window.plot_config.plot_limits[sheet_name]

    if sheet_name not in window.Data['Core levels']:
        wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
        return None

    core_level_data = window.Data['Core levels'][sheet_name]
    x_values = np.array(core_level_data['B.E.'])
    y_values = np.array(core_level_data['Raw Data'])
    background = np.array(core_level_data['Background']['Bkg Y'])

    num_peaks = peak_params_grid.GetNumberRows() // 2

    bg_min_energy = core_level_data['Background'].get('Bkg Low')
    bg_max_energy = core_level_data['Background'].get('Bkg High')

    if bg_min_energy is not None and bg_max_energy is not None and bg_min_energy <= bg_max_energy:
        mask = (x_values >= bg_min_energy) & (x_values <= bg_max_energy)
        x_values_filtered = x_values[mask]
        y_values_filtered = y_values[mask]
        background_filtered = background[mask]

        if len(x_values_filtered) > 0 and len(y_values_filtered) > 0:
            y_values_subtracted = y_values_filtered - background_filtered

            model_choice = window.selected_fitting_method
            max_nfev = window.max_iterations

            model = None
            params = lmfit.Parameters()

            individual_peaks = []

            for i in range(num_peaks):
                row = i * 2
                prefix = f'peak{i}_'  # Define the prefix here

                center = float(peak_params_grid.GetCellValue(row, 2))
                height = float(peak_params_grid.GetCellValue(row, 3))
                fwhm = float(peak_params_grid.GetCellValue(row, 4))
                lg_ratio = float(peak_params_grid.GetCellValue(row, 5))
                peak_model_choice = peak_params_grid.GetCellValue(row, 11)

                tail_m = float(peak_params_grid.GetCellValue(row, 7))
                tail_e = float(peak_params_grid.GetCellValue(row, 8))

                # Add tail parameters to the model
                params.add(f'{prefix}tail_mix', value=tail_m, min=0, max=1)
                params.add(f'{prefix}tail_exp', value=tail_e, min=0)

                sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
                gamma = lg_ratio * sigma

                center_min, center_max, center_vary = parse_constraints(peak_params_grid.GetCellValue(row + 1, 2),
                                                                        center, peak_params_grid, i, "Position")
                height_min, height_max, height_vary = parse_constraints(peak_params_grid.GetCellValue(row + 1, 3),
                                                                        height, peak_params_grid, i, "Height")
                fwhm_min, fwhm_max, fwhm_vary = parse_constraints(peak_params_grid.GetCellValue(row + 1, 4),
                                                                  fwhm, peak_params_grid, i, "FWHM")
                lg_ratio_min, lg_ratio_max, lg_ratio_vary = parse_constraints(peak_params_grid.GetCellValue(row + 1, 5),
                                                                              lg_ratio, peak_params_grid, i, "L/G")

                center_min = evaluate_constraint(center_min, peak_params_grid, 'center', center)
                center_max = evaluate_constraint(center_max, peak_params_grid, 'center', center)
                height_min = evaluate_constraint(height_min, peak_params_grid, 'height', height)
                height_max = evaluate_constraint(height_max, peak_params_grid, 'height', height)
                fwhm_min = evaluate_constraint(fwhm_min, peak_params_grid, 'fwhm', fwhm)
                fwhm_max = evaluate_constraint(fwhm_max, peak_params_grid, 'fwhm', fwhm)
                lg_ratio_min = evaluate_constraint(lg_ratio_min, peak_params_grid, 'lg_ratio', lg_ratio)
                lg_ratio_max = evaluate_constraint(lg_ratio_max, peak_params_grid, 'lg_ratio', lg_ratio)

                sigma_min = fwhm_min / (2 * np.sqrt(2 * np.log(2))) if fwhm_min is not None else None
                sigma_max = fwhm_max / (2 * np.sqrt(2 * np.log(2))) if fwhm_max is not None else None
                gamma_min = lg_ratio_min * sigma_min if lg_ratio_min is not None and sigma_min is not None else None
                gamma_max = lg_ratio_max * sigma_max if lg_ratio_max is not None and sigma_max is not None else None

                prefix = f'peak{i}_'

                if peak_model_choice == "Voigt":
                    peak_model = lmfit.models.VoigtModel(prefix=prefix)
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}sigma', value=sigma, min=sigma_min, max=sigma_max, vary=fwhm_vary)
                    params.add(f'{prefix}gamma', value=gamma, min=gamma_min, max=gamma_max, vary=lg_ratio_vary)
                elif peak_model_choice == "Pseudo-Voigt":
                    peak_model = lmfit.models.PseudoVoigtModel(prefix=prefix)
                    sigma = fwhm / 2.355
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}amplitude', value=height * sigma * np.sqrt(2 * np.pi), min=0)
                    params.add(f'{prefix}sigma', value=sigma, min=fwhm_min / 2.355 if fwhm_min else None,
                               max=fwhm_max / 2.355 if fwhm_max else None, vary=fwhm_vary)
                    params.add(f'{prefix}fraction', value=lg_ratio, min=0, max=1, vary=lg_ratio_vary)
                elif peak_model_choice == "GL":
                    peak_model = lmfit.Model(PeakFunctions.gauss_lorentz, prefix=prefix)
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}fwhm', value=fwhm, min=fwhm_min, max=fwhm_max, vary=fwhm_vary)
                    params.add(f'{prefix}fraction', value=lg_ratio, min=lg_ratio_min, max=lg_ratio_max,
                               vary=lg_ratio_vary)
                elif peak_model_choice == "SGL":
                    peak_model = lmfit.Model(PeakFunctions.S_gauss_lorentz, prefix=prefix)
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}fwhm', value=fwhm, min=fwhm_min, max=fwhm_max, vary=fwhm_vary)
                    params.add(f'{prefix}fraction', value=lg_ratio, min=lg_ratio_min, max=lg_ratio_max,
                               vary=lg_ratio_vary)
                else:
                    raise ValueError(f"Unknown fitting model: {peak_model_choice} for peak {i}")

                if model is None:
                    model = peak_model
                else:
                    model += peak_model

                individual_peaks.append(peak_model)

            result = model.fit(y_values_subtracted, params, x=x_values_filtered, max_nfev=max_nfev)

            residuals = y_values_subtracted - result.best_fit
            ss_res = np.sum(residuals ** 2)
            ss_tot = np.sum((y_values_subtracted - np.mean(y_values_subtracted)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            window.r_squared = r_squared
            chi_square = result.chisqr
            red_chi_square = result.redchi

            if 'Fitting' not in window.Data['Core levels'][sheet_name]:
                window.Data['Core levels'][sheet_name]['Fitting'] = {}
            if 'Peaks' not in window.Data['Core levels'][sheet_name]['Fitting']:
                window.Data['Core levels'][sheet_name]['Fitting']['Peaks'] = {}

            existing_peaks = window.Data['Core levels'][sheet_name]['Fitting']['Peaks']

            for i in range(num_peaks):
                row = i * 2
                prefix = f'peak{i}_'
                peak_label = peak_params_grid.GetCellValue(row, 1)
                peak_model_choice = peak_params_grid.GetCellValue(row, 11)

                if peak_label in existing_peaks:
                    center = result.params[f'{prefix}center'].value
                    if peak_model_choice == "Voigt":
                        amplitude = result.params[f'{prefix}amplitude'].value
                        sigma = result.params[f'{prefix}sigma'].value
                        gamma = result.params[f'{prefix}gamma'].value
                        height = PeakFunctions.get_voigt_height(amplitude, sigma, gamma)
                        fwhm = PeakFunctions.voigt_fwhm(sigma, gamma)
                        fraction = gamma / (sigma * np.sqrt(2 * np.log(2)))
                        area = amplitude * (sigma * np.sqrt(2 * np.pi))
                    elif peak_model_choice == "Pseudo-Voigt":
                        amplitude = result.params[f'{prefix}amplitude'].value
                        sigma = result.params[f'{prefix}sigma'].value
                        fraction = result.params[f'{prefix}fraction'].value
                        fwhm = sigma * 2.355
                        height = PeakFunctions.get_pseudo_voigt_height(amplitude, sigma, fraction)
                        area = amplitude
                    elif peak_model_choice in ["GL", "SGL"]:
                        height = result.params[f'{prefix}amplitude'].value
                        fwhm = result.params[f'{prefix}fwhm'].value
                        fraction = result.params[f'{prefix}fraction'].value
                        area = height * fwhm * np.sqrt(np.pi / (4 * np.log(2)))
                    else:
                        raise ValueError(f"Unknown fitting model: {peak_model_choice} for peak {peak_label}")

                    center = round(float(center), 2)
                    height = round(float(height), 2)
                    fwhm = round(float(fwhm), 2)
                    fraction = round(float(fraction), 2)
                    area = round(float(area), 2)

                    peak_params_grid.SetCellValue(row, 2, f"{center:.2f}")
                    peak_params_grid.SetCellValue(row, 3, f"{height:.2f}")
                    peak_params_grid.SetCellValue(row, 4, f"{fwhm:.2f}")
                    peak_params_grid.SetCellValue(row, 5, f"{fraction:.2f}")
                    peak_params_grid.SetCellValue(row, 6, f"{area:.2f}")

                    existing_peaks[peak_label].update({
                        'Position': center,
                        'Height': height,
                        'FWHM': fwhm,
                        'L/G': fraction,
                        'Area': area,
                        'Fitting Model': peak_model_choice
                    })
                else:
                    print(f"Warning: Peak {peak_label} not found in existing data. Skipping update for this peak.")

            window.Data['Core levels'][sheet_name]['Fitting']['Model'] = model_choice

            window.fit_results = {
                'result': result,
                'r_squared': r_squared,
                'chi_square': chi_square,
                'red_chi_square': red_chi_square,
                'nfev': result.nfev,
                'fitted_peak': y_values.copy(),
                'mask': mask,
                'background_filtered': background_filtered,
                'y_values_subtracted': y_values_subtracted
            }
            window.fit_results['fitted_peak'][mask] = result.best_fit + background_filtered

            # Add text annotations with fit results
            std_value_int = int(window.noise_std_value) if hasattr(window, 'noise_std_value') else "N/A"

            window.update_ratios()
            window.clear_and_replot()

            # Fitting results --- THIS NEEDS TO BE SET AFTER CLEAR & REPLOT TO WORK
            window.plot_manager.set_fitting_results_text(f'Noise STD: {std_value_int}'
                                                         f' cts\nR²: {r_squared:.5f}\nChi²: {chi_square:.2f}\nRed. Chi²: {red_chi_square:.2f}\nIteration: {result.nfev}')

            return r_squared, chi_square, red_chi_square

        else:
            raise ValueError("No data points found in the specified energy range for background subtraction")

    else:
        raise ValueError("Invalid background energy range")


def get_peak_value(peak_params_grid, peak_name, param_name):
    for i in range(peak_params_grid.GetNumberRows()):
        if peak_params_grid.GetCellValue(i, 0) == peak_name:
            if param_name == 'center':
                return float(peak_params_grid.GetCellValue(i, 2))
            elif param_name == 'height':
                return float(peak_params_grid.GetCellValue(i, 3))
            elif param_name == 'fwhm':
                return float(peak_params_grid.GetCellValue(i, 4))
            elif param_name == 'lg_ratio':
                return float(peak_params_grid.GetCellValue(i, 5))
    return None


import re

def parse_constraints(constraint_str, current_value, peak_params_grid, peak_index, param_name):
    constraint_str = constraint_str.strip()
    small_error = 0.05

    # Pattern to match A+1.5#0.5 format
    pattern = r'^([A-P])([+*])(\d+\.?\d*)#([\d\.]+)$'
    match = re.match(pattern, constraint_str)

    # Pattern for A+2 or A*2 format
    pattern_simple = r'^([A-P])([+*])(\d+\.?\d*)$'
    match_simple = re.match(pattern_simple, constraint_str)

    if constraint_str in ['Fixed']:
        small_error3=0.001
        return current_value - small_error3, current_value +small_error3, False
    elif match:
        ref_peak, operator, value, delta = match.groups()
        value = float(value)
        delta = float(delta)
        if operator == '+':
            return f"{ref_peak}+{value - delta}", f"{ref_peak}+{value + delta}", True
        elif operator == '*':
            return f"{ref_peak}*{value - delta}", f"{ref_peak}*{value + delta}", True

    elif match_simple:
        ref_peak, operator, value = match_simple.groups()
        value = float(value)
        if operator == '+':
            return f"{ref_peak}+{value - small_error}", f"{ref_peak}+{value + small_error}", True
        elif operator == '*':
            small_error2 = 0.0001
            return f"{ref_peak}*{value - small_error2}", f"{ref_peak}*{value + small_error2}", True

    # If it's a simple number or range
    if ',' in constraint_str:
        min_val, max_val = map(float, constraint_str.split(','))
        return min_val, max_val, True
    if ':' in constraint_str:
        min_val, max_val = map(float, constraint_str.split(','))
        return min_val, max_val, True


    try:
        value = float(constraint_str)
        return value - 0.1, value + 0.1, True
    except ValueError:
        pass

    # If we can't parse it, return the current value with a small range
    return current_value - 0.1, current_value + 0.1, True


def evaluate_constraint(constraint, peak_params_grid, param_name, current_value):
    if isinstance(constraint, (int, float)):
        return constraint
    if constraint is None:
        return None

    # Handle the case A+1.5 or A*1.5
    match = re.match(r'([A-J])([+*])(-?\d+\.?\d*)', constraint)
    if match:
        peak, op, value = match.groups()
        peak_value = get_peak_value(peak_params_grid, peak, param_name)
        if peak_value is not None:
            value = float(value)
            if op == '+':
                return peak_value + value
            elif op == '*':
                return peak_value * value

    # Handle simple numeric constraints
    try:
        return float(constraint)
    except ValueError:
        return current_value


def format_sheet_name2(sheet_name):
    # Regular expression to separate element and electron shell
    match = re.match(r'([A-Z][a-z]*)(\d+[spdfg])', sheet_name)
    if match:
        element, shell = match.groups()
        return f"{element} {shell}"
    else:
        return sheet_name  # Return original if it doesn't match the expected format










