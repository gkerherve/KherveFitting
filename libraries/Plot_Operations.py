# plot_operations.py

import wx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter



def plot_data(window):
    if 'Core levels' not in window.Data or not window.Data['Core levels']:
        wx.MessageBox("No data available to plot.", "Error", wx.OK | wx.ICON_ERROR)
        return

    sheet_name = window.sheet_combobox.GetValue()
    limits = window.plot_config.get_plot_limits(window, sheet_name)
    if sheet_name not in window.Data['Core levels']:
        wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
        return

    try:
        window.ax.clear()

        x_values = window.Data['Core levels'][sheet_name]['B.E.']
        y_values = window.Data['Core levels'][sheet_name]['Raw Data']

        window.ax.scatter(x_values, y_values, facecolors='none', marker='o', s=10, edgecolors='black', label='Raw Data')

        # Update window.x_values and window.y_values
        window.x_values = np.array(x_values)
        window.y_values = np.array(y_values)

        # Initialize background to raw data if not already present
        if 'Bkg Y' not in window.Data['Core levels'][sheet_name]['Background'] or not \
        window.Data['Core levels'][sheet_name]['Background']['Bkg Y']:
            window.Data['Core levels'][sheet_name]['Background']['Bkg Y'] = window.y_values.tolist()
        window.background = np.array(window.Data['Core levels'][sheet_name]['Background']['Bkg Y'])

        # Initialize Bkg X if not already present
        if 'Bkg X' not in window.Data['Core levels'][sheet_name]['Background'] or not \
        window.Data['Core levels'][sheet_name]['Background']['Bkg X']:
            window.Data['Core levels'][sheet_name]['Background']['Bkg X'] = window.x_values.tolist()

        # Set x-axis limits to reverse the direction and match the min and max of the data
        window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
        window.ax.set_ylim(limits['Ymin'], limits['Ymax'])

        window.ax.set_ylabel("Intensity (CTS)")
        window.ax.set_xlabel("Binding Energy (eV)")

        window.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        window.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        # Hide the cross if it exists
        if hasattr(window, 'cross') and window.cross:
            window.cross.remove()

        # Switch to "None" ticked box and hide background lines
        window.vline1 = None
        window.vline2 = None
        window.vline3 = None
        window.vline4 = None
        window.show_hide_vlines()

        # Remove any existing fit or residual lines
        for line in window.ax.lines:
            if line.get_label() in ['Envelope', 'Residuals', 'Background']:
                line.remove()

        for collection in window.ax.collections:
            if collection.get_label().startswith(window.sheet_combobox.GetValue()):
                collection.remove()

        window.ax.legend(loc='upper left')

        # Check if a peak is selected and add cross
        if window.selected_peak_index is not None:
            window.add_cross_to_peak(window.selected_peak_index)

        # Remove any existing sheet name text
        for txt in window.ax.texts:
            if getattr(txt, 'sheet_name_text', False):
                txt.remove()

        # Format and add sheet name text
        formatted_sheet_name = format_sheet_name(sheet_name)
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

        window.canvas.draw()  # Update the plot

    except Exception as e:
        wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
    pass

def clear_and_replot(window):
    sheet_name = window.sheet_combobox.GetValue()
    limits = window.plot_config.get_plot_limits(window, sheet_name)

    window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
    window.ax.set_ylim(limits['Ymin'], limits['Ymax'])
    if sheet_name not in window.Data['Core levels']:
        wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
        return

    core_level_data = window.Data['Core levels'][sheet_name]

    # Store existing sheet name text
    sheet_name_text = None
    for txt in window.ax.texts:
        if getattr(txt, 'sheet_name_text', False):
            sheet_name_text = txt
            break

    # Clear the plot
    window.ax.clear()
    window.ax.set_xlabel("Binding Energy (eV)")
    window.ax.set_ylabel("Intensity (CTS)")
    window.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    window.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

    # Plot the raw data
    x_values = np.array(core_level_data['B.E.'])
    y_values = np.array(core_level_data['Raw Data'])


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

    window.ax.scatter(x_values, y_values, facecolors='none', marker='o', s=10, edgecolors='black', label='Raw Data')

    # Update overall fit and residuals
    window.update_overall_fit_and_residuals()

    # Update the legend
    window.update_legend()

    # Restore sheet name text or create new one if it doesn't exist
    if sheet_name_text is None:
        formatted_sheet_name = format_sheet_name(sheet_name)
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

    # Draw the canvas
    window.canvas.draw_idle()

import re

def format_sheet_name(sheet_name):
    # Regular expression to separate element and electron shell
    match = re.match(r'([A-Z][a-z]*)(\d+[spdfg])', sheet_name)
    if match:
        element, shell = match.groups()
        # return f"{element} $\\mathbf{{\\it{{{shell}}}}}$"
        return f"{element} "+shell
    else:
        return sheet_name  # Return original if it doesn't match the expected format


