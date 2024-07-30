# plot_operations.py

import re
import wx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

import lmfit
# from libraries.Peak_Functions import gauss_lorentz, S_gauss_lorentz
from libraries.Peak_Functions import PeakFunctions


class PlotManager:
    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas
        self.cross = None
        self.fitting_results_text = None
        self.fitting_results_visible = False

    def plot_peak2(self, x_values, background, selected_fitting_method, peak_params, sheet_name):
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
            peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
            params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)
        elif selected_fitting_method == "SGL":
            peak_model = lmfit.Model(PeakFunctions.S_gauss_lorentz)
            params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)

        peak_y = peak_model.eval(params, x=x_values) + background

        peak_label = peak_params['label'] if 'label' in peak_params else f"{sheet_name} p{row // 2 + 1}"


        self.ax.plot(x_values, peak_y)
        self.ax.fill_between(x_values, background, peak_y, alpha=0.3, label=peak_label)

        self.canvas.draw_idle()

        return peak_y

    def plot_peak(self, x_values, background, peak_params, sheet_name):
        row = peak_params['row']
        fwhm = peak_params['fwhm']
        lg_ratio = peak_params['lg_ratio']
        x = peak_params['position']
        y = peak_params['height']
        peak_label = peak_params['label']

        # Get the fitting model for this specific peak
        fitting_model = peak_params.get('fitting_model', "GL")  # Default to GL if not specified

        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        gamma = lg_ratio * sigma
        bkg_y = background[np.argmin(np.abs(x_values - x))]

        if fitting_model == "Voigt":
            peak_model = lmfit.models.VoigtModel()
            amplitude = y / peak_model.eval(center=0, amplitude=1, sigma=sigma, gamma=gamma, x=0)
            params = peak_model.make_params(center=x, amplitude=amplitude, sigma=sigma, gamma=gamma)
        elif fitting_model == "Pseudo-Voigt":
            peak_model = lmfit.models.PseudoVoigtModel()
            amplitude = y / peak_model.eval(center=0, amplitude=1, sigma=sigma, fraction=lg_ratio, x=0)
            params = peak_model.make_params(center=x, amplitude=amplitude, sigma=sigma, fraction=lg_ratio)
        elif fitting_model == "GL":
            peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
            params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)
        elif fitting_model == "SGL":
            peak_model = lmfit.Model(PeakFunctions.S_gauss_lorentz)
            params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)

        peak_y = peak_model.eval(params, x=x_values) + background

        self.ax.plot(x_values, peak_y, alpha=0.5)
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

            self.ax.scatter(x_values, y_values, facecolors='black', marker='o', s=20, edgecolors='black',
                            label='Raw Data')

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
                window.plot_manager.add_cross_to_peak(window, window.selected_peak_index)

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

    def clear_and_replot(self, window):
        sheet_name = window.sheet_combobox.GetValue()
        limits = window.plot_config.get_plot_limits(window, sheet_name)

        if sheet_name not in window.Data['Core levels']:
            wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
            return

        core_level_data = window.Data['Core levels'][sheet_name]

        self.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
        self.ax.set_ylim(limits['Ymin'], limits['Ymax'])

        # Store existing sheet name text
        sheet_name_text = None
        for txt in self.ax.texts:
            if getattr(txt, 'sheet_name_text', False):
                sheet_name_text = txt
                break

        # Clear the plot
        self.ax.clear()
        self.ax.set_xlabel("Binding Energy (eV)")
        self.ax.set_ylabel("Intensity (CTS)")
        self.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        self.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        # Plot the raw data
        x_values = np.array(core_level_data['B.E.'])
        y_values = np.array(core_level_data['Raw Data'])

        # Get plot limits from PlotConfig
        if sheet_name not in window.plot_config.plot_limits:
            window.plot_config.update_plot_limits(window, sheet_name)
        limits = window.plot_config.plot_limits[sheet_name]

        # Set plot limits
        self.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
        self.ax.set_ylim(limits['Ymin'], limits['Ymax'])


        # Replot all peaks and update indices
        num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows
        for i in range(num_peaks):
            row = i * 2

            # Get all necessary values, with error checking
            try:
                position = float(window.peak_params_grid.GetCellValue(row, 2))
                height = float(window.peak_params_grid.GetCellValue(row, 3))
                fwhm = float(window.peak_params_grid.GetCellValue(row, 4))
                fraction = float(window.peak_params_grid.GetCellValue(row, 5))
                label = window.peak_params_grid.GetCellValue(row, 1)
                fitting_model = window.peak_params_grid.GetCellValue(row, 9)
            except ValueError:
                print(f"Warning: Invalid data for peak {i + 1}. Skipping this peak.")
                continue

            if fitting_model == "Unfitted":
                # For unfitted peaks, fill between background and raw data
                mask = (x_values >= position - fwhm / 2) & (x_values <= position + fwhm / 2)
                self.ax.fill_between(x_values, window.background, y_values,
                                     facecolor='lightgreen', alpha=0.5, label=label)
            else:
                # For fitted peaks, use the existing plot_peak method
                peak_params = {
                    'row': row,
                    'position': position,
                    'height': height,
                    'fwhm': fwhm,
                    'lg_ratio': fraction,
                    'label': label,
                    'fitting_model': fitting_model
                }
                self.plot_peak(window.x_values, window.background, peak_params, sheet_name)




        # Plot the background if it exists
        if 'Bkg Y' in core_level_data['Background'] and len(core_level_data['Background']['Bkg Y']) > 0:
            self.ax.plot(x_values, core_level_data['Background']['Bkg Y'], color='grey', linestyle='--',
                         label='Background', alpha=0.5)

        # Update overall fit and residuals
        if fitting_model == "Unfitted":
            pass
        else:
            window.update_overall_fit_and_residuals()

        self.ax.scatter(x_values, y_values, facecolors='black', marker='o', s=20, edgecolors='black', label='Raw Data')

        # Update the legend only if necessary
        if self.ax.get_legend() is None or len(self.ax.get_legend().texts) != len(self.ax.lines):
            self.update_legend(window)
        # else: self.update_legend(window)

        # Restore sheet name text or create new one if it doesn't exist
        if sheet_name_text is None:
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
        else:
            self.ax.add_artist(sheet_name_text)

        # Draw the canvas
        self.canvas.draw_idle()

    def update_peak_plot(self, window, x, y, remove_old_peaks=True):
        if window.x_values is None or window.background is None:
            print("Error: x_values or background is None. Cannot update peak plot.")
            return

        if x is None or y is None:
            print("Error: x or y is None. Cannot update peak plot.")
            return
        if len(window.x_values) != len(window.background):
            print(f"Warning: x_values and background have different lengths. "
                  f"x: {len(window.x_values)}, background: {len(window.background)}")

        if window.selected_peak_index is not None and 0 <= window.selected_peak_index < window.peak_params_grid.GetNumberRows() // 2:
            row = window.selected_peak_index * 2
            peak_label = window.peak_params_grid.GetCellValue(row, 1)  # Get the current label

            # Get peak parameters from the grid
            fwhm = float(window.peak_params_grid.GetCellValue(row, 4))
            lg_ratio = float(window.peak_params_grid.GetCellValue(row, 5))
            sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
            gamma = lg_ratio * sigma
            bkg_y = window.background[np.argmin(np.abs(window.x_values - x))]

            # Ensure height is not negative
            y = max(y, 0)

            # Create the selected peak using updated position and height
            if window.selected_fitting_method == "Voigt":
                peak_model = lmfit.models.VoigtModel()
                amplitude = y / peak_model.eval(center=0, amplitude=1, sigma=sigma, gamma=gamma, x=0)
                params = peak_model.make_params(center=x, amplitude=amplitude, sigma=sigma, gamma=gamma)
            elif window.selected_fitting_method == "Pseudo-Voigt":
                peak_model = lmfit.models.PseudoVoigtModel()
                amplitude = y / peak_model.eval(center=0, amplitude=1, sigma=sigma, fraction=lg_ratio, x=0)
                params = peak_model.make_params(center=x, amplitude=amplitude, sigma=sigma, fraction=lg_ratio)
            elif window.selected_fitting_method == "GL":
                peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
                params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)
            elif window.selected_fitting_method == "SGL":
                peak_model = lmfit.Model(PeakFunctions.S_gauss_lorentz)
                params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)
            else:  # Add GL which is the safe bet
                peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
                params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)

            peak_y = peak_model.eval(params, x=window.x_values) + window.background

            # Update overall fit and residuals
            window.update_overall_fit_and_residuals()

            peak_label = window.peak_params_grid.GetCellValue(row, 1)  # Get peak label from grid

            # Update the selected peak plot line
            for line in self.ax.get_lines():
                if line.get_label() == peak_label:
                    line.set_ydata(peak_y)
                    break
            else:
                self.ax.plot(window.x_values, peak_y, label=peak_label)

            # Remove previous squares
            for line in self.ax.get_lines():
                if 'Selected Peak Center' in line.get_label():
                    line.remove()

            # Plot the new red square at the top center of the selected peak
            self.ax.plot(x, y + bkg_y, 'bx', label=f'Selected Peak Center {window.selected_peak_index}', markersize=15,
                         markerfacecolor='none')

            # Update the grid with new values
            window.peak_params_grid.SetCellValue(row, 2, f"{x:.2f}")  # Position
            window.peak_params_grid.SetCellValue(row, 3, f"{y:.2f}")  # Height
            window.peak_params_grid.SetCellValue(row, 4, f"{fwhm:.2f}")  # FWHM
            window.peak_params_grid.SetCellValue(row, 5, f"{lg_ratio:.2f}")  # L/G ratio

            self.canvas.draw_idle()

    def update_overall_fit_and_residuals(self, window):
        # Calculate the overall fit as the sum of all peaks
        overall_fit = window.background.copy()
        num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows

        for i in range(num_peaks):
            row = i * 2  # Each peak uses two rows in the grid

            # Get cell values
            position_str = window.peak_params_grid.GetCellValue(row, 2)  # Position
            height_str = window.peak_params_grid.GetCellValue(row, 3)  # Height
            fwhm_str = window.peak_params_grid.GetCellValue(row, 4)  # FWHM
            lg_ratio_str = window.peak_params_grid.GetCellValue(row, 5)  # L/G
            fitting_model = window.peak_params_grid.GetCellValue(row, 9)  # Fitting Model

            # Check if any of the cells are empty
            if not all([position_str, height_str, fwhm_str, lg_ratio_str, fitting_model]):
                print(f"Warning: Incomplete data for peak {i + 1}. Skipping this peak.")
                continue

            try:
                peak_x = float(position_str)
                peak_y = float(height_str)
                fwhm = float(fwhm_str)
                lg_ratio = float(lg_ratio_str)
            except ValueError:
                print(f"Warning: Invalid data for peak {i + 1}. Skipping this peak.")
                continue

            sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
            gamma = lg_ratio * sigma
            bkg_y = window.background[np.argmin(np.abs(window.x_values - peak_x))]

            if fitting_model == "Voigt":
                peak_model = lmfit.models.VoigtModel()
                amplitude = peak_y / peak_model.eval(center=0, amplitude=1, sigma=sigma, gamma=gamma, x=0)
                params = peak_model.make_params(center=peak_x, amplitude=amplitude, sigma=sigma, gamma=gamma)
            elif fitting_model == "Pseudo-Voigt":
                peak_model = lmfit.models.PseudoVoigtModel()
                amplitude = peak_y / peak_model.eval(center=0, amplitude=1, sigma=sigma, fraction=lg_ratio, x=0)
                params = peak_model.make_params(center=peak_x, amplitude=amplitude, sigma=sigma, fraction=lg_ratio)
            elif fitting_model == "GL":
                peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
                params = peak_model.make_params(center=peak_x, fwhm=fwhm, fraction=lg_ratio, amplitude=peak_y)
            elif fitting_model == "SGL":
                peak_model = lmfit.Model(PeakFunctions.S_gauss_lorentz)
                params = peak_model.make_params(center=peak_x, fwhm=fwhm, fraction=lg_ratio, amplitude=peak_y)
            else:
                print(f"Warning: Unknown fitting model '{fitting_model}' for peak {i + 1}. Skipping this peak.")
                continue

            peak_fit = peak_model.eval(params, x=window.x_values)
            overall_fit += peak_fit

        # Calculate residuals
        residuals = window.y_values - overall_fit

        # Determine the scaling factor
        max_raw_data = max(window.y_values)
        desired_max_residual = 0.1 * max_raw_data
        actual_max_residual = max(abs(residuals))
        scaling_factor = desired_max_residual / actual_max_residual if actual_max_residual != 0 else 1

        # Scale residuals
        scaled_residuals = residuals * scaling_factor

        # Remove old overall fit and residuals, keep background lines
        for line in self.ax.get_lines():
            if line.get_label() in ['Overall Fit', 'Residuals']:
                line.remove()

        # Plot the new overall fit and residuals
        self.ax.plot(window.x_values, overall_fit, 'b-', alpha=0.3, label='Overall Fit')
        self.ax.plot(window.x_values, scaled_residuals + 1.05 * max(window.y_values), 'g-', alpha=0.4,
                     label='Residuals')

        # Update the Y-axis label
        self.ax.set_ylabel(f'Intensity (CTS), residual x {scaling_factor:.2f}')

        self.canvas.draw_idle()

    def update_peak_fwhm(self, window, x):
        if window.initial_fwhm is not None and window.initial_x is not None:
            row = window.selected_peak_index * 2
            peak_center = float(window.peak_params_grid.GetCellValue(row, 2))
            peak_label = window.peak_params_grid.GetCellValue(row, 1)

            delta_x = x - window.initial_x
            new_fwhm = max(window.initial_fwhm + delta_x * 1, 0.3)  # Ensure minimum FWHM of 0.3 eV

            window.peak_params_grid.SetCellValue(row, 4, f"{new_fwhm:.2f}")

            # Update FWHM in window.Data
            sheet_name = window.sheet_combobox.GetValue()
            if sheet_name in window.Data['Core levels'] and 'Fitting' in window.Data['Core levels'][
                sheet_name] and 'Peaks' in window.Data['Core levels'][sheet_name]['Fitting']:
                peaks = window.Data['Core levels'][sheet_name]['Fitting']['Peaks']
                if peak_label in peaks:
                    peaks[peak_label]['FWHM'] = new_fwhm

            position = float(window.peak_params_grid.GetCellValue(row, 2))
            height = float(window.peak_params_grid.GetCellValue(row, 3))

            self.update_peak_plot(window, position, height, remove_old_peaks=False)

    def add_cross_to_peak(self, window, index):
        try:
            row = index * 2  # Each peak uses two rows in the grid
            peak_x = float(window.peak_params_grid.GetCellValue(row, 2))  # Position
            peak_y = float(window.peak_params_grid.GetCellValue(row, 3))  # Height

            # Find the closest background value
            closest_index = np.argmin(np.abs(window.x_values - peak_x))
            bkg_y = window.background[closest_index]

            # Add background to peak height
            peak_y += bkg_y

            # Remove existing cross if it exists
            if self.cross:
                self.cross.remove()

            # Plot new cross
            self.cross, = self.ax.plot(peak_x, peak_y, 'bx', markersize=15, markerfacecolor='none', picker=5)

            # Connect event handlers
            self.canvas.mpl_disconnect('motion_notify_event')  # Disconnect existing handlers
            self.canvas.mpl_disconnect('button_release_event')
            self.motion_notify_id = self.canvas.mpl_connect('motion_notify_event', window.on_cross_drag)
            self.button_release_id = self.canvas.mpl_connect('button_release_event', window.on_cross_release)

            # Redraw canvas
            self.canvas.draw_idle()

        except ValueError as e:
            print(f"Error adding cross to peak: {e}")
            # You might want to show an error message to the user here
        except Exception as e:
            print(f"Unexpected error adding cross to peak: {e}")
            # You might want to show an error message to the user here

    def toggle_residuals(self):
        for line in self.ax.get_lines():
            if line.get_label().startswith('Residuals'):
                line.set_visible(not line.get_visible())
        self.canvas.draw_idle()

    def toggle_fitting_results(self):
        if self.fitting_results_text:
            self.fitting_results_visible = not self.fitting_results_visible
            self.fitting_results_text.set_visible(self.fitting_results_visible)
            self.canvas.draw_idle()

    def set_fitting_results_text(self, text):
        # Method to set or update the fitting results text
        if self.fitting_results_text:
            self.fitting_results_text.remove()
        self.fitting_results_text = self.ax.text(
            0.02, 0.04, text,
            transform=self.ax.transAxes,
            fontsize=9,
            verticalalignment='bottom',
            horizontalalignment='left',
            bbox=dict(facecolor='white', edgecolor='grey', alpha=0.7),
        )
        self.fitting_results_text.set_visible(self.fitting_results_visible)

    def toggle_legend(self):
        legend = self.ax.get_legend()
        if legend:
            legend.set_visible(not legend.get_visible())
        self.canvas.draw_idle()

    def update_legend(self, window):
        # Retrieve the current handles and labels
        handles, labels = self.ax.get_legend_handles_labels()

        # Define the desired order of legend entries
        legend_order = ["Raw Data", "Background", "Overall Fit", "Residuals"]

        # Collect peak labels
        num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows
        peak_labels = [window.peak_params_grid.GetCellValue(i * 2, 1) for i in range(num_peaks)]

        # Ensure peaks are added to the end of the order
        legend_order += peak_labels

        # Create a list of (handle, label) tuples in the desired order
        ordered_handles_labels = []
        for l in legend_order:
            matching_labels = [label for label in labels if label == l or label.startswith(l)]
            for match in matching_labels:
                index = labels.index(match)
                ordered_handles_labels.append((handles[index], match))

        # Update the legend
        self.ax.legend([h for h, l in ordered_handles_labels], [l for h, l in ordered_handles_labels])
        self.ax.legend(loc='upper left')
        self.canvas.draw_idle()

    # Used by the defs above
    @staticmethod
    def format_sheet_name(sheet_name):
        import re
        match = re.match(r'([A-Z][a-z]*)(\d+[spdfg])', sheet_name)
        if match:
            element, shell = match.groups()
            return f"{element} {shell}"
        else:
            return sheet_name

    def update_plots_be_correction(self, window, delta_correction):
        sheet_name = window.sheet_combobox.GetValue()
        limits = window.plot_config.get_plot_limits(window, sheet_name)

        # Update x-axis limits
        limits['Xmin'] += delta_correction
        limits['Xmax'] += delta_correction

        # Update plot
        window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
        window.canvas.draw_idle()







