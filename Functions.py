# FUNCTIONS.PY-------------------------------------------------------------------

# LIBRARIES----------------------------------------------------------------------
import wx
import wx.grid
from wx import DirDialog, MessageBox

import pandas as pd
import numpy as np
import lmfit
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from scipy.stats import linregress
from Save import save_data
from vamas import Vamas
from openpyxl import Workbook
from ConfigFile import *
from Save import *
from libraries.Sheet_Operations import on_sheet_selected
from libraries.Plot_Operations import plot_data, clear_and_replot, clear_plots


# -------------------------------------------------------------------------------

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


def clear_and_replot(window):
    sheet_name = window.sheet_combobox.GetValue()
    limits = window.plot_config.get_plot_limits(window, sheet_name)

    window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
    window.ax.set_ylim(limits['Ymin'], limits['Ymax'])
    if sheet_name not in window.Data['Core levels']:
        wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
        return

    core_level_data = window.Data['Core levels'][sheet_name]

    # Clear the plot
    window.ax.clear()
    window.ax.set_xlabel("Binding Energy (eV)")
    window.ax.set_ylabel("Intensity (CTS)")
    window.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    window.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

    # Plot the raw data
    x_values = np.array(core_level_data['B.E.'])
    y_values = np.array(core_level_data['Raw Data'])
    window.ax.scatter(x_values, y_values, facecolors='none', marker='o', s=10, edgecolors='black', label='Raw Data')

    # Get plot limits from PlotConfig
    if sheet_name not in window.plot_config.plot_limits:
        window.plot_config.update_plot_limits(window, sheet_name)
    limits = window.plot_config.plot_limits[sheet_name]

    # Set plot limits
    window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
    window.ax.set_ylim(limits['Ymin'], limits['Ymax'])

    # Plot the background if it exists
    if 'Bkg Y' in core_level_data['Background'] and len(core_level_data['Background']['Bkg Y']) > 0:
        window.ax.plot(x_values, core_level_data['Background']['Bkg Y'], color='grey', linestyle='--',
                       label='Background')

    # Replot all peaks and update indices
    num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows
    for i in range(num_peaks):
        row = i * 2
        position_str = window.peak_params_grid.GetCellValue(row, 2)
        height_str = window.peak_params_grid.GetCellValue(row, 3)

        # Check if the cells are not empty before converting to float
        if position_str and height_str:
            try:
                position = float(position_str)
                height = float(height_str)
                window.plot_peak(position, height, i)
            except ValueError:
                print(f"Warning: Invalid data for peak {i + 1}. Skipping this peak.")
        else:
            print(f"Warning: Empty data for peak {i + 1}. Skipping this peak.")

    # Update overall fit and residuals
    window.update_overall_fit_and_residuals()

    # Update the legend
    window.update_legend()

    # Draw the canvas
    window.canvas.draw_idle()


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
        clear_and_replot(window)

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
        window.ax.scatter(x_values, y_values, facecolors='none', marker='o', s=10, edgecolors='black', label='Raw Data')

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

        print(window.Data)

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
            window.Data['Core levels'][sheet_name]['Background']['Bkg Y'] = y_values.tolist()  # Store as list

        bg_min_energy = window.Data['Core levels'][sheet_name]['Background'].get('Bkg Low')
        bg_max_energy = window.Data['Core levels'][sheet_name]['Background'].get('Bkg High')

        if (bg_min_energy is not None
                and bg_max_energy is not None
                and bg_min_energy <= bg_max_energy
        ):
            bg_min_energy = float(bg_min_energy)
            bg_max_energy = float(bg_max_energy)

            mask = (x_values >= bg_min_energy) & (x_values <= bg_max_energy)

            x_values_filtered = x_values[mask]
            y_values_filtered = y_values[mask]

            if len(x_values_filtered) > 0 and len(y_values_filtered) > 0:
                method = window.background_method
                offset_h = float(window.offset_h)
                offset_l = float(window.offset_l)

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
                new_background[mask] = background_filtered
                window.Data['Core levels'][sheet_name]['Background']['Bkg Y'] = new_background.tolist()  # Store as list
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

            else:
                wx.MessageBox("No data points within the selected energy range.", "Warning",
                              wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("Invalid energy range selected.", "Warning", wx.OK | wx.ICON_INFORMATION)

        # Check if peak 1 exists and tick/untick it
        if window.peak_params_grid.GetNumberRows() > 0:
            # Call the method to clear and replot everything
            clear_and_replot(window)

            # Update the legend
            window.update_legend()

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

def calculate_shirley_background(x, y, start_offset, end_offset, max_iter=100, tol=1e-6, padding_factor=0.1):
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
    Config_item = edit_menu.Append(wx.NewId(), "Preference - TBD")

    ToggleFitting_item = view_menu.Append(wx.NewId(), "Toggle Peak Fitting")
    window.Bind(wx.EVT_MENU, lambda event: toggle_plot(window), ToggleFitting_item)

    ToggleLegend_item = view_menu.Append(wx.NewId(), "Toggle Legend")
    window.Bind(wx.EVT_MENU, lambda event: window.toggle_legend(), ToggleLegend_item)

    ToggleFit_item = view_menu.Append(wx.NewId(), "Toggle Fit Results")
    window.Bind(wx.EVT_MENU, lambda event: window.toggle_fitting_results(), ToggleFit_item)

    ToggleRes_item = view_menu.Append(wx.NewId(), "Toggle Residuals")
    window.Bind(wx.EVT_MENU, lambda event: window.toggle_residuals(), ToggleRes_item)

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
    toolbar.SetBackgroundColour(wx.Colour(200, 200, 200))
    toolbar.SetToolBitmapSize(wx.Size(25, 25))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "Icons")

    separators = []

    # File operations
    open_file_tool = toolbar.AddTool(wx.ID_ANY, 'Open File', wx.Bitmap(os.path.join(icon_path, "open-folder-64.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open File")
    refresh_folder_tool = toolbar.AddTool(wx.ID_ANY, 'Refresh Folder', wx.Bitmap(os.path.join(icon_path, "refresh-96.png"), wx.BITMAP_TYPE_PNG), shortHelp="Refresh Folder")
    save_tool = toolbar.AddTool(wx.ID_ANY, 'Save', wx.Bitmap(os.path.join(icon_path, "save-Excel2.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save the Fitted Results to Excel for this Core Level")
    save_plot_tool = toolbar.AddTool(wx.ID_ANY, 'Save Plot', wx.Bitmap(os.path.join(icon_path, "save-64.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save this Figure to Excel")

    toolbar.AddSeparator()

    # separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    # separators[-1].SetSize((2, 24))
    # toolbar.AddControl(separators[-1])

    # Sheet selection
    window.sheet_combobox = wx.ComboBox(toolbar, style=wx.CB_READONLY)
    window.sheet_combobox.SetToolTip("Select Sheet")
    toolbar.AddControl(window.sheet_combobox)

    window.skip_rows_spinbox = wx.SpinCtrl(toolbar, min=0, max=200, initial=0, size=(60, -1))
    window.skip_rows_spinbox.SetToolTip("Set the number of rows to skip in the sheet of the Excel file")
    toolbar.AddControl(window.skip_rows_spinbox)

    # separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    # separators[-1].SetSize((2, 24))
    # toolbar.AddControl(separators[-1])

    toolbar.AddSeparator()

    # Plot adjustment tools
    plot_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Plot',
                                wx.Bitmap(os.path.join(icon_path, "scatter-plot-60.png"),
                                wx.BITMAP_TYPE_PNG), shortHelp="Toggle between Raw Data and Fit")

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
    bkg_tool = toolbar.AddTool(wx.ID_ANY, 'Background', wx.Bitmap(os.path.join(icon_path, "BKG-64.png"), wx.BITMAP_TYPE_PNG),shortHelp="Calculate Area under Peak")
    # bkg_tool = toolbar.AddTool(wx.ID_ANY, 'Background', wx.Bitmap(wx.Bitmap(os.path.join(icon_path, "Plot_Area.ico")), wx.BITMAP_TYPE_PNG), shortHelp="Calculate Area under Peak")
    fitting_tool = toolbar.AddTool(wx.ID_ANY, 'Fitting', wx.Bitmap(os.path.join(icon_path, "STO-200.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open Fitting Window")
    noise_analysis_tool = toolbar.AddTool(wx.ID_ANY, 'Noise Analysis', wx.Bitmap(os.path.join(icon_path, "Noise.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open Noise Analysis Window")

    # separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    # separators[-1].SetSize((2, 24))
    # toolbar.AddControl(separators[-1])


    # Add a spacer to push the following items to the right
    toolbar.AddStretchableSpace()

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
    window.Bind(wx.EVT_TOOL, lambda event: refresh_sheets(window, on_sheet_selected), refresh_folder_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_plot(window), plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_background_window(), bkg_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_fitting_window(), fitting_tool)
    window.Bind(wx.EVT_TOOL, window.on_open_noise_analysis_window, noise_analysis_tool)
    # window.Bind(wx.EVT_TOOL, lambda event: window.resize_plot(), resize_plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.toggle_legend(), toggle_legend_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.toggle_fitting_results(), toggle_fit_results_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.toggle_residuals(), toggle_residuals_tool)
    window.sheet_combobox.Bind(wx.EVT_COMBOBOX, lambda event: on_sheet_selected(window, event))
    window.Bind(wx.EVT_TOOL, lambda event: on_save(window), save_tool)
    window.Bind(wx.EVT_TOOL, lambda event: on_save_plot(window), save_plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_Col_1(window), toggle_Col_1_tool)

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
                                     wx.Bitmap(os.path.join(icon_path, "ZoomIN.png"), wx.BITMAP_TYPE_PNG),
                                     shortHelp="Zoom In")

    # Add zoom out tool (previously resize_plot)
    zoom_out_tool = v_toolbar.AddTool(wx.ID_ANY, 'Zoom Out',
                                      wx.Bitmap(os.path.join(icon_path, "ZoomOUT2.png"), wx.BITMAP_TYPE_PNG),
                                      shortHelp="Zoom Out")

    # Add drag tool
    drag_tool = v_toolbar.AddTool(wx.ID_ANY, 'Drag',
                                  wx.Bitmap(os.path.join(icon_path, "drag-64.png"), wx.BITMAP_TYPE_PNG),
                                  shortHelp="Drag Plot")

    v_toolbar.AddSeparator()

    # BE adjustment tools
    high_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE +', wx.Bitmap(os.path.join(icon_path, "Right-Red.png"), wx.BITMAP_TYPE_PNG), shortHelp="Increase High BE")
    high_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE -', wx.Bitmap(os.path.join(icon_path, "Left-Red-100.png"), wx.BITMAP_TYPE_PNG), shortHelp="Decrease High BE")

    v_toolbar.AddSeparator()

    low_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE +', wx.Bitmap(os.path.join(icon_path, "Left-Blue-100.png"), wx.BITMAP_TYPE_PNG), shortHelp="Increase Low BE")
    low_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE -', wx.Bitmap(os.path.join(icon_path, "Right-Blue-100.png"), wx.BITMAP_TYPE_PNG), shortHelp="Decrease Low BE")

    # v_toolbar.AddSeparator()

    # # Add increment spin control
    # increment_label = wx.StaticText(v_toolbar, label="Increment:")
    # v_toolbar.AddControl(increment_label)
    # frame.be_increment_spin = wx.SpinCtrlDouble(v_toolbar, value='1.0', min=0.1, max=10.0, inc=0.1, size=(60, -1))
    # # v_toolbar.AddControl(frame.be_increment_spin)   #  DO NOT ADD YET


    v_toolbar.AddSeparator()

    # Intensity adjustment tools
    high_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int +', wx.Bitmap(os.path.join(icon_path, "Up-Red-100.png"), wx.BITMAP_TYPE_PNG), shortHelp="Increase High Intensity")
    high_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int -', wx.Bitmap(os.path.join(icon_path, "Down-Red-100.png"), wx.BITMAP_TYPE_PNG), shortHelp="Decrease High Intensity")

    v_toolbar.AddSeparator()

    low_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low Int +', wx.Bitmap(os.path.join(icon_path, "Up-Blue-100.png"), wx.BITMAP_TYPE_PNG), shortHelp="Increase Low Intensity")
    low_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low Int -', wx.Bitmap(os.path.join(icon_path, "Down-Blue-100.png"), wx.BITMAP_TYPE_PNG), shortHelp="Decrease Low Intensity")

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
        clear_and_replot(window)
    else:
        plot_data(window)
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

                # Update sheet names in the combobox
                window.sheet_combobox.Clear()
                window.sheet_combobox.AppendItems(sheet_names)

                # Set the first sheet as the selected one
                first_sheet = sheet_names[0]
                window.sheet_combobox.SetValue(first_sheet)

                # Use on_sheet_selected to update peak parameter grid and plot
                event = wx.CommandEvent(wx.EVT_COMBOBOX.typeId)
                event.SetString(first_sheet)
                on_sheet_selected(window,event)

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
        plot_data(window)

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

def toggle_Col_1(window):
    # List of columns to toggle
    columns1 = [9, 10, 11, 12, 13, 14]
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



def parse_constraints(constraint_str, current_value, peak_params_grid, peak_index, param_name):
    if constraint_str.lower() in ['f', 'fixed']:
        return current_value - 0.1, current_value + 0.1, False
    elif constraint_str.lower().startswith('p'):
        ref_peak_index = int(constraint_str[1:]) - 1
        num_peaks = peak_params_grid.GetNumberRows() // 2
        if 0 <= ref_peak_index < num_peaks:
            param_column = {'Position': 2, 'Height': 3, 'FWHM': 4, 'L/G': 5}.get(param_name)
            if param_column is not None:
                ref_value = float(peak_params_grid.GetCellValue(ref_peak_index * 2, param_column))
                return ref_value - 0.001, ref_value + 0.001, True
            else:
                raise ValueError(f"Invalid parameter name: {param_name}")
        else:
            raise ValueError(f"Invalid peak reference: {constraint_str}")
    else:
        try:
            min_val, max_val = map(float, constraint_str.split(','))
            return min_val, max_val, True
        except ValueError:
            raise ValueError(f"Invalid constraint format: {constraint_str}")

def gaussian(x, E, F, m):
    return np.exp(-4 * np.log(2) * (1 - m / 100) * ((x - E) / F)**2)

def lorentzian(x, E, F, m):             # E= position, F width, m : percent G like 40 / 100
    return 1 / (1 + 4 * m / 100 * ((x - E) / F)**2)

def gauss_lorentz(x, center , fwhm , fraction, amplitude):                   # x, E, F, m
    return amplitude * (
            gaussian(x, center, fwhm, fraction*100) * lorentzian(x, center, fwhm, fraction*100))

def S_gauss_lorentz(x, center , fwhm , fraction, amplitude):                   # x, E, F, m
    return amplitude * (
        (1-fraction)*gaussian(x, center, fwhm, 0) + fraction * lorentzian(x, center, fwhm, 100))


import numpy as np


def pseudo_voigt_2(x, center, amplitude, sigma, fraction):
    """
    Custom Pseudo-Voigt function.

    Parameters:
    x : array
        The x values
    center : float
        The peak center
    amplitude : float
        The peak height
    sigma : float
        The peak width (standard deviation for Gaussian component)
    fraction : float
        The fraction of Lorentzian component (0 to 1)

    Returns:
    array : The y values of the Pseudo-Voigt function
    """
    sigma2 = sigma ** 2
    gamma = sigma * np.sqrt(2 * np.log(2))

    gaussian = (1 - fraction) * np.exp(-((x - center) ** 2) / (2 * sigma2))
    lorentzian = fraction * (gamma ** 2 / ((x - center) ** 2 + gamma ** 2))

    return amplitude * (gaussian + lorentzian)


import numpy as np


def pseudo_voigt_1_2(x, center, amplitude, fwhm, fraction):
    """
    Custom Pseudo-Voigt function using FWHM.

    Parameters:
    x : array
        The x values
    center : float
        The peak center
    amplitude : float
        The peak height
    fwhm : float
        Full Width at Half Maximum of the peak
    fraction : float
        The fraction of Lorentzian component (0 to 1)

    Returns:
    array : The y values of the Pseudo-Voigt function
    """
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))  # Convert FWHM to sigma for Gaussian
    gamma = fwhm / 2  # Convert FWHM to gamma for Lorentzian

    z = (x - center) / sigma

    gaussian = (1 - fraction) * np.exp(-z ** 2 / 2) / (sigma * np.sqrt(2 * np.pi))
    lorentzian = fraction * gamma / (np.pi * (gamma ** 2 + (x - center) ** 2))

    return amplitude * (gaussian + lorentzian) * sigma * np.sqrt(2 * np.pi)

def pseudo_voigt_1(x, center, amplitude, fwhm, fraction):
    """
    Corrected Pseudo-Voigt function ensuring the amplitude parameter represents peak height.

    Parameters:
    x : array
        The x values
    center : float
        The peak center
    amplitude : float
        The peak height
    fwhm : float
        Full Width at Half Maximum of the peak
    fraction : float
        The fraction of Lorentzian component (0 to 1)

    Returns:
    array : The y values of the Pseudo-Voigt function
    """
    sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
    gamma = fwhm / 2

    z = (x - center) / sigma

    gaussian = (1 - fraction) * np.exp(-z ** 2 / 2) / (sigma * np.sqrt(2 * np.pi))
    lorentzian = fraction / (np.pi * gamma * (1 + ((x - center) / gamma) ** 2))

    return amplitude * (gaussian + lorentzian) / (gaussian.max() + lorentzian.max())


def calculate_r2(y_true, y_pred):
    """Calculate the coefficient of determination (R²)"""
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return 1 - (ss_res / ss_tot)


def calculate_chi_square(y_true, y_pred):
    """Calculate the chi-square value"""
    return np.sum((y_true - y_pred) ** 2 / y_pred)



import numpy as np
import lmfit

from matplotlib.ticker import ScalarFormatter
import matplotlib.pyplot as plt


def fit_peaks(window, peak_params_grid):
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
    print(f"Number of peaks: {num_peaks}")
    for i in range(num_peaks):
        row = i * 2
        print(f"Peak {i + 1}: Position={peak_params_grid.GetCellValue(row, 2)}, "
              f"Height={peak_params_grid.GetCellValue(row, 3)}, "
              f"FWHM={peak_params_grid.GetCellValue(row, 4)}, "
              f"L/G={peak_params_grid.GetCellValue(row, 5)}")

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

                sigma_min = fwhm_min / (2 * np.sqrt(2 * np.log(2))) if fwhm_vary else None
                sigma_max = fwhm_max / (2 * np.sqrt(2 * np.log(2))) if fwhm_vary else None
                gamma_min = lg_ratio_min * sigma_min if lg_ratio_vary else None
                gamma_max = lg_ratio_max * sigma_max if lg_ratio_vary else None

                prefix = f'peak{i}_'

                # Create the appropriate peak model based on the selected fitting method
                if model_choice == "Voigt":
                    peak_model = lmfit.models.VoigtModel(prefix=prefix)
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}sigma', value=sigma, min=sigma_min, max=sigma_max, vary=fwhm_vary)
                    params.add(f'{prefix}gamma', value=gamma, min=gamma_min, max=gamma_max, vary=lg_ratio_vary)
                elif model_choice == "Pseudo-Voigt":
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
                # elif model_choice == "Pseudo-Voigt":
                #     peak_model = lmfit.Model(pseudo_voigt_2, prefix=prefix)
                #     params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                #     params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                #     params.add(f'{prefix}sigma', value=sigma, min=sigma_min, max=sigma_max, vary=fwhm_vary)
                #     params.add(f'{prefix}fraction', value=lg_ratio, min=lg_ratio_min, max=lg_ratio_max,
                #                vary=lg_ratio_vary)
                # elif model_choice == "Pseudo-Voigt_3":
                #     peak_model = lmfit.Model(pseudo_voigt_1, prefix=prefix)
                #     params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                #     params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                #     params.add(f'{prefix}fwhm', value=fwhm, min=fwhm_min, max=fwhm_max, vary=fwhm_vary)
                #     params.add(f'{prefix}fraction', value=lg_ratio, min=lg_ratio_min, max=lg_ratio_max,
                #                vary=lg_ratio_vary)
                elif model_choice == "GL":
                    peak_model = lmfit.Model(gauss_lorentz, prefix=prefix)
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}fwhm', value=fwhm, min=fwhm_min, max=fwhm_max, vary=fwhm_vary)
                    params.add(f'{prefix}fraction', value=lg_ratio, min=lg_ratio_min, max=lg_ratio_max,
                               vary=lg_ratio_vary)
                elif model_choice == "SGL":
                    peak_model = lmfit.Model(S_gauss_lorentz, prefix=prefix)
                    params.add(f'{prefix}amplitude', value=height, min=height_min, max=height_max, vary=height_vary)
                    params.add(f'{prefix}center', value=center, min=center_min, max=center_max, vary=center_vary)
                    params.add(f'{prefix}fwhm', value=fwhm, min=fwhm_min, max=fwhm_max, vary=fwhm_vary)
                    params.add(f'{prefix}fraction', value=lg_ratio, min=lg_ratio_min, max=lg_ratio_max,
                               vary=lg_ratio_vary)

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

                if peak_label in existing_peaks:
                    center = result.params[f'{prefix}center'].value
                    if model_choice == "Voigt":
                        amplitude = result.params[f'{prefix}amplitude'].value
                        sigma = result.params[f'{prefix}sigma'].value
                        gamma = result.params[f'{prefix}gamma'].value
                        # Calculate height directly using the model
                        height = get_voigt_height(amplitude, sigma, gamma)
                        fwhm = voigt_fwhm(sigma, gamma)
                        fraction = gamma / (sigma * np.sqrt(2 * np.log(2)))
                    elif model_choice == "Pseudo-Voigt":
                        amplitude = result.params[f'{prefix}amplitude'].value
                        sigma = result.params[f'{prefix}sigma'].value
                        fraction = result.params[f'{prefix}fraction'].value
                        fwhm = sigma * 2.355
                        # Calculate height directly using the model
                        height = get_pseudo_voigt_height(amplitude, sigma, fraction)
                    else:
                        # For all other models, amplitude is treated as height
                        height = result.params[f'{prefix}amplitude'].value
                        fwhm = result.params[f'{prefix}fwhm'].value if f'{prefix}fwhm' in result.params else 2.355 * \
                                                                                                             result.params[
                                                                                                                 f'{prefix}sigma'].value
                        fraction = result.params[f'{prefix}fraction'].value if f'{prefix}fraction' in result.params else \
                        result.params[f'{prefix}gamma'].value / result.params[f'{prefix}sigma'].value

                    # Update peak_params_grid
                    peak_params_grid.SetCellValue(row, 2, f"{center:.2f}")
                    peak_params_grid.SetCellValue(row, 3, f"{height:.2f}")
                    peak_params_grid.SetCellValue(row, 4, f"{fwhm:.2f}")
                    peak_params_grid.SetCellValue(row, 5, f"{fraction:.2f}")

                    # Update existing peak in window.Data
                    existing_peaks[peak_label].update({
                        'Position': center,
                        'Height': height,
                        'FWHM': fwhm,
                        'L/G': fraction,
                        'Area': height * fwhm * (np.sqrt(2 * np.pi) / 2.355),
                        # Consistent area calculation for all models
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
                window.ax.scatter(x_values, y_values, facecolors='none', marker='o', s=10, edgecolors='black',
                                  label='Raw Data')
                window.ax.plot(x_values, background, 'gray', linestyle='--', label='Background')

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
                scaled_residuals = residuals * scaling_factor + 1.01 * max(y_values)
                residuals_line, = window.ax.plot(x_values, scaled_residuals, 'g', alpha=0.4, label='Residuals')

                # Plot individual peaks
                for i, (peak_model, color) in enumerate(zip(individual_peaks, colors)):
                    peak = np.zeros_like(y_values)
                    peak[mask] = peak_model.eval(result.params, x=x_values_filtered)
                    peak_name = peak_params_grid.GetCellValue(i * 2, 1)
                    # window.ax.fill_between(x_values, background, peak + background, facecolor=color,
                    #                        alpha=0.8, label=peak_name)
                    # window.ax.plot(x_values, peak + background, 'black', alpha=0.4)
                    window.ax.plot(x_values, peak + background)
                    window.ax.fill_between(x_values, background, peak + background,
                                              alpha=0.3, label=peak_name)

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
                fitting_results_text = window.ax.text(
                    0.02, 0.04,
                    f'Noise STD: {std_value_int} cts\nR²: {r_squared:.5f}\nChi²: {chi_square:.2f}\nRed. Chi²: {red_chi_square:.2f}\nIteration: {nfev_used}',
                    transform=window.ax.transAxes,
                    fontsize=9,
                    verticalalignment='bottom',
                    horizontalalignment='left',
                    visible=False,
                    bbox=dict(facecolor='white', edgecolor='grey', alpha=0.7),
                )

                window.fitting_results_text = fitting_results_text
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

import re

def format_sheet_name2(sheet_name):
    # Regular expression to separate element and electron shell
    match = re.match(r'([A-Z][a-z]*)(\d+[spdfg])', sheet_name)
    if match:
        element, shell = match.groups()
        return f"{element} {shell}"
    else:
        return sheet_name  # Return original if it doesn't match the expected format

import lmfit

def get_pseudo_voigt_height(amplitude, sigma, fraction):
    """
    Calculate the height of a Pseudo-Voigt profile directly using the lmfit model.
    """
    model = lmfit.models.PseudoVoigtModel()
    params = model.make_params(amplitude=amplitude, center=0, sigma=sigma, fraction=fraction)
    return model.eval(params, x=0)

def get_voigt_height(amplitude, sigma, gamma):
    """
    Calculate the height of a Voigt profile directly using the lmfit model.
    """
    model = lmfit.models.VoigtModel()
    params = model.make_params(amplitude=amplitude, center=0, sigma=sigma, gamma=gamma)
    return model.eval(params, x=0)


def voigt_fwhm(sigma, gamma):
    """
    Approximate the FWHM of a Voigt profile.

    This uses an approximation that is accurate to within a few percent.

    Parameters:
    sigma : float
        The sigma parameter of the Gaussian component
    gamma : float
        The gamma parameter of the Lorentzian component

    Returns:
    float : The approximate FWHM of the Voigt profile
    """
    fg = 2 * sigma * np.sqrt(2 * np.log(2))
    fl = 2 * gamma
    return 0.5346 * fl + np.sqrt(0.2166 * fl ** 2 + fg ** 2)

def pseudo_voigt_amplitude_to_height(amplitude, sigma, fraction):
    """
    Convert amplitude to height for a Pseudo-Voigt profile.

    Parameters:
    amplitude : float
        The amplitude of the Pseudo-Voigt profile
    sigma : float
        The sigma parameter of the profile (related to FWHM)
    fraction : float
        The fraction of Lorentzian component (0 to 1)

    Returns:
    float : The height of the Pseudo-Voigt profile
    """
    # Constants
    sqrt2pi = np.sqrt(2 * np.pi)
    sqrt2ln2 = np.sqrt(2 * np.log(2))

    # Gaussian component height
    gaussian_height = amplitude / (sigma * sqrt2pi)

    # Lorentzian component height
    lorentzian_height = 2 * amplitude / (np.pi * sigma * 2 * sqrt2ln2)

    # Combine using the fraction
    height = (1 - fraction) * gaussian_height + fraction * lorentzian_height

    return height


def pseudo_voigt_height_to_amplitude(height, sigma, fraction):
    """
    Convert height to amplitude for a Pseudo-Voigt profile.

    Parameters:
    height : float
        The height of the Pseudo-Voigt profile
    sigma : float
        The sigma parameter of the profile (related to FWHM)
    fraction : float
        The fraction of Lorentzian component (0 to 1)

    Returns:
    float : The amplitude of the Pseudo-Voigt profile
    """
    # Constants
    sqrt2pi = np.sqrt(2 * np.pi)
    sqrt2ln2 = np.sqrt(2 * np.log(2))

    # Gaussian component amplitude
    gaussian_amplitude = height * sigma * sqrt2pi

    # Lorentzian component amplitude
    lorentzian_amplitude = height * np.pi * sigma * 2 * sqrt2ln2 / 2

    # Combine using the fraction
    amplitude = (1 - fraction) * gaussian_amplitude + fraction * lorentzian_amplitude

    return amplitude

import numpy as np

def pseudo_voigt_2_height_to_amplitude(height, sigma, fraction):
    """
    Convert height to amplitude for Pseudo-Voigt_2 profile.
    """
    return height * (sigma * np.sqrt(2 * np.pi) * (1 - fraction) + np.pi * sigma * fraction)

def pseudo_voigt_2_amplitude_to_height(amplitude, sigma, fraction):
    """
    Convert amplitude to height for Pseudo-Voigt_2 profile.
    """
    return amplitude / (sigma * np.sqrt(2 * np.pi) * (1 - fraction) + np.pi * sigma * fraction)







