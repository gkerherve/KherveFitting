# plot_operations.py

import re
import wx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

import lmfit
from libraries.Peak_Functions import gauss_lorentz, S_gauss_lorentz


class PlotManager:
    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas

    def plot_peak(self, x_values, background, selected_fitting_method, peak_params, sheet_name):
        row = peak_params['row']
        fwhm = peak_params['fwhm']
        lg_ratio = peak_params['lg_ratio']
        x = peak_params['position']
        y = peak_params['height']

        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        gamma = lg_ratio * sigma
        bkg_y = background[np.argmin(np.abs(x_values - x))]

        if selected_fitting_method == "Voigt":
            peak_model = lmfit.models.VoigtModel()
            amplitude = y / peak_model.eval(center=0, amplitude=1, sigma=sigma, gamma=gamma, x=0)
            params = peak_model.make_params(center=x, amplitude=amplitude, sigma=sigma, gamma=gamma)
        elif selected_fitting_method == "Pseudo-Voigt":
            peak_model = lmfit.models.PseudoVoigtModel()
            amplitude = y / peak_model.eval(center=0, amplitude=1, sigma=sigma, fraction=lg_ratio, x=0)
            params = peak_model.make_params(center=x, amplitude=amplitude, sigma=sigma, fraction=lg_ratio)
        elif selected_fitting_method == "GL":
            peak_model = lmfit.Model(gauss_lorentz)
            params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)
        elif selected_fitting_method == "SGL":
            peak_model = lmfit.Model(S_gauss_lorentz)
            params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)

        peak_y = peak_model.eval(params, x=x_values) + background

        peak_label = f"{sheet_name} p{row // 2 + 1}"

        self.ax.plot(x_values, peak_y)
        self.ax.fill_between(x_values, background, peak_y, alpha=0.3, label=peak_label)

        self.canvas.draw_idle()

        return peak_y

    def plot_data(self, window):
        if 'Core levels' not in window.Data or not window.Data['Core levels']:
            wx.MessageBox("No data available to plot.", "Error", wx.OK | wx.ICON_ERROR)
            return

        sheet_name = window.sheet_combobox.GetValue()
        limits = window.plot_config.get_plot_limits(window, sheet_name)
        if sheet_name not in window.Data['Core levels']:
            wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
            return

        try:
            self.ax.clear()

            x_values = window.Data['Core levels'][sheet_name]['B.E.']
            y_values = window.Data['Core levels'][sheet_name]['Raw Data']

            self.ax.scatter(x_values, y_values, facecolors='none', marker='o', s=10, edgecolors='black',
                            label='Raw Data')

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
            self.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
            self.ax.set_ylim(limits['Ymin'], limits['Ymax'])

            self.ax.set_ylabel("Intensity (CTS)")
            self.ax.set_xlabel("Binding Energy (eV)")

            self.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            self.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

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
            for line in self.ax.lines:
                if line.get_label() in ['Envelope', 'Residuals', 'Background']:
                    line.remove()

            for collection in self.ax.collections:
                if collection.get_label().startswith(window.sheet_combobox.GetValue()):
                    collection.remove()

            self.ax.legend(loc='upper left')

            # Check if a peak is selected and add cross
            if window.selected_peak_index is not None:
                window.add_cross_to_peak(window.selected_peak_index)

            # Remove any existing sheet name text
            for txt in self.ax.texts:
                if getattr(txt, 'sheet_name_text', False):
                    txt.remove()

            # Format and add sheet name text
            formatted_sheet_name = self.format_sheet_name(sheet_name)
            sheet_name_text = self.ax.text(
                0.98, 0.98,  # Position (top-right corner)
                formatted_sheet_name,
                transform=self.ax.transAxes,
                fontsize=15,
                fontweight='bold',
                verticalalignment='top',
                horizontalalignment='right',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7),
            )
            sheet_name_text.sheet_name_text = True  # Mark this text object

            self.canvas.draw()  # Update the plot

        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)

    @staticmethod
    def format_sheet_name(sheet_name):
        import re
        match = re.match(r'([A-Z][a-z]*)(\d+[spdfg])', sheet_name)
        if match:
            element, shell = match.groups()
            return f"{element} {shell}"
        else:
            return sheet_name








def clear_plots(window):
    # Remove all lines
    while window.ax.lines:
        window.ax.lines.pop(0).remove()

    # Remove all scatter plots and other collections
    for collection in window.ax.collections[:]:
        collection.remove()

    # Remove all patches (like filled areas)
    for patch in window.ax.patches[:]:
        patch.remove()

    # Clear the legend
    if window.ax.get_legend():
        window.ax.get_legend().remove()

    # Clear texts (except for the sheet name text)
    for text in window.ax.texts[:]:
        if not getattr(text, 'sheet_name_text', False):
            text.remove()

    # Clear images
    for im in window.ax.images[:]:
        im.remove()

    # Reset the axis limits
    window.ax.relim()
    window.ax.autoscale_view()

def clear_and_replot(window):
    sheet_name = window.sheet_combobox.GetValue()
    limits = window.plot_config.get_plot_limits(window, sheet_name)


    if sheet_name not in window.Data['Core levels']:
        wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
        return

    core_level_data = window.Data['Core levels'][sheet_name]

    # Clear existing plots
    # clear_plots(window)

    window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
    window.ax.set_ylim(limits['Ymin'], limits['Ymax'])

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

    # Update the legend only if necessary
    if window.ax.get_legend() is None or len(window.ax.get_legend().texts) != len(window.ax.lines):
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


@staticmethod
def format_sheet_name(sheet_name):
    import re
    match = re.match(r'([A-Z][a-z]*)(\d+[spdfg])', sheet_name)
    if match:
        element, shell = match.groups()
        return f"{element} {shell}"
    else:
        return sheet_name


