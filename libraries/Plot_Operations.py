# plot_operations.py

import re
import wx
import os
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.ticker import ScalarFormatter
from itertools import cycle
from PIL import Image, ImageDraw, ImageFont

import matplotlib.colors as mcolors

from scipy.ndimage import gaussian_filter

import lmfit
# from libraries.Peak_Functions import gauss_lorentz, S_gauss_lorentz
from libraries.Peak_Functions import PeakFunctions


class PlotManager:
    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas
        self.cross = None
        self.peak_fill_enabled = True
        self.fitting_results_text = None
        self.fitting_results_visible = False

        # init for preference window
        self.plot_style = "scatter"
        self.scatter_size = 20
        self.line_width = 1
        self.line_alpha = 0.7
        self.scatter_color = "#000000"
        self.line_color = "#000000"
        self.scatter_marker = "o"

        self.background_color = "#808080"
        self.background_alpha = 0.5
        self.background_linestyle = "--"
        self.envelope_color = "#0000FF"
        self.envelope_alpha = 0.6
        self.envelope_linestyle = "-"
        self.residual_color = "#00FF00"
        self.residual_alpha = 0.4
        self.residual_linestyle = "-"
        self.raw_data_linestyle = "-"

        self.peak_colors = []
        self.peak_alpha = 0.3

        self.energy_scale = 'BE'

    def toggle_energy_scale(self, window):
        window.energy_scale = 'KE' if window.energy_scale == 'BE' else 'BE'
        self.clear_and_replot(window)

    def load_and_process_image(self, blur_sigma=4):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "Images", "SplashScreen4.png")

        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return None

        # Load the PNG image
        img = Image.open(image_path) #.convert('L')  # Convert to grayscale

        # Convert to numpy array
        img_array = np.array(img)

        # Apply Gaussian blur
        blurred_img =  gaussian_filter(img_array, sigma=blur_sigma)

        # return blurred_img
        return img_array

    def plot_initial_logo(self):
        img_array = self.load_and_process_image()
        if img_array is None:
            return

        # Clear the current axis
        self.ax.clear()

        # Display the image
        self.ax.imshow(img_array, aspect='auto', alpha = 0.07, extent=[1350, 0, 0, 1000000])
        self.ax.set_xlabel('Binding Energy (eV)')
        self.ax.set_ylabel('Intensity (CPS)')

        # Set axis limits
        self.ax.set_xlim(1350, 0)
        self.ax.set_ylim(0, 1000000)

        # Enable scientific notation for the Y-axis
        self.ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

        # Draw the canvas
        self.canvas.draw()

    def plot_initial_logo2(self):
        fig = self.plot_logo()
        self.ax.clear()
        self.ax.imshow(fig.axes[0].images[0].get_array(), cmap='hot', alpha = 0.3, aspect='auto', extent=[1350, 0,
                                                                                                          10000,
                                                                                                      0])
        self.ax.set_xlabel('Binding Energy (eV)')
        self.ax.set_ylabel('Intensity (CPS)')
        plt.close(fig)  # Close the figure to free memory
        self.canvas.draw()

    def plot_initial_logo2(self):
        width, height = 300, 100
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("calibrib.ttf", 40)  # Calibri Bold
        except IOError:
            font = ImageFont.load_default()

        # Define a gradient color
        gradient = np.linspace(0, 1, width)
        color_func = mcolors.LinearSegmentedColormap.from_list("", ["#66CC66", "#006400"])

        # Draw text with gradient color
        for i, letter in enumerate("KherveFitting"):
            x = 10 + i * 20  # Adjust spacing as needed
            color = tuple(int(c * 255) for c in color_func(gradient[i * 20 % width])[:3])
            draw.text((x, 25), letter, font=font, fill=color)

        data = np.array(image)
        self.ax.clear()
        self.ax.imshow(data, aspect='auto', extent=[1350, 0, 10000, 0])
        self.ax.set_xlabel('Binding Energy (eV)')
        self.ax.set_ylabel('Intensity (CPS)')
        self.canvas.draw()

    def plot_peak(self, x_values, background, peak_params, sheet_name,window, color=None, alpha=0.3):
        row = peak_params['row']
        fwhm = peak_params['fwhm']
        lg_ratio = peak_params['lg_ratio']
        x = peak_params['position']
        y = peak_params['height']
        peak_label = peak_params['label']
        try:
            tail_M = float(peak_params.get('Tail M', 0))
            tail_E = float(peak_params.get('Tail E', 0))
        except ValueError:
            tail_M = 0.0
            tail_E = 0.0


        # Format the peak label for matplotlib
        formatted_label = re.sub(r'(\d+/\d+)', r'$_{\1}$', peak_label)

        # Get the fitting model for this specific peak
        fitting_model = peak_params.get('fitting_model', "GL")  # Default to GL if not specified

        sigma = fwhm / 2.355
        # sigma = fwhm / 2
        gamma = lg_ratio/100 * sigma
        bkg_y = background[np.argmin(np.abs(x_values - x))]
        if fitting_model == "Unfitted":
            # We've already handled this in clear_and_replot, so just return
            return
        elif fitting_model == "Voigt":
            peak_model = lmfit.models.VoigtModel()
            amplitude = y / peak_model.eval(center=0, amplitude=1, sigma=sigma, gamma=gamma, x=0)
            params = peak_model.make_params(center=x, amplitude=amplitude, sigma=sigma, gamma=gamma)
        elif fitting_model == "Pseudo-Voigt":
            sigma = fwhm / 2
            peak_model = lmfit.models.PseudoVoigtModel()
            amplitude = y / peak_model.eval(center=0, amplitude=1, sigma=sigma, fraction=lg_ratio/100, x=0)
            params = peak_model.make_params(center=x, amplitude=amplitude, sigma=sigma, fraction=lg_ratio/100)
        elif fitting_model == "GL2":
            peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
            params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)
        elif fitting_model == "GL":
            peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
            params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y, tail_mix=tail_M,
                                            tail_exp=tail_E)
        elif fitting_model == "SGL":
            peak_model = lmfit.Model(PeakFunctions.S_gauss_lorentz)
            params = peak_model.make_params(center=x, fwhm=fwhm, fraction=lg_ratio, amplitude=y)

        peak_y = peak_model.eval(params, x=x_values) + background

        if color is None:
            color = self.peak_colors[len(self.ax.lines) % len(self.peak_colors)]
        if alpha is None:
            alpha = self.peak_alpha

        line_alpha = min(alpha +0.1, 1)
        if self.peak_fill_enabled:
            label = peak_label
            if window.energy_scale == 'KE':
                self.ax.fill_between(window.photons - x_values, background, peak_y, color=color, alpha=alpha,
                                     interpolate=True, edgecolor='none', label=peak_label)
            else:
                self.ax.fill_between(x_values, background, peak_y, color=color, alpha=alpha, interpolate=True,
                                     edgecolor='none', label=peak_label)
            # self.ax.plot(x_values, peak_y, color=color, alpha=line_alpha)
        else:
            if self.energy_scale == 'KE':
                self.ax.plot(window.photons - x_values, peak_y, color=color, alpha=line_alpha, label=peak_label)
            else:
                self.ax.plot(x_values, peak_y, color=color, alpha=line_alpha, label=peak_label)

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

            x_values = np.array(x_values)  # Ensure x_values is a numpy array

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
            if window.energy_scale == 'KE':
                X_MIN = window.photons-limits['Xmax']
                X_MAX = window.photons-limits['Xmin']
                self.ax.set_xlim(min(X_MIN, X_MAX),max(X_MIN, X_MAX))  # Reverse X-axis
            else:
                self.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis

            self.ax.set_ylim(limits['Ymin'], limits['Ymax'])

            self.ax.set_ylabel("Intensity (CPS)")
            x_label = "Kinetic Energy (eV)" if window.energy_scale == 'KE' else "Binding Energy (eV)"
            self.ax.set_xlabel(x_label)
            # self.ax.set_xlabel("Binding Energy (eV)")

            self.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
            self.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

            if "survey" in sheet_name.lower() or "wide" in sheet_name.lower():
                if window.energy_scale == 'KE':
                    self.ax.plot(window.photons- x_values, y_values, c=self.line_color, linewidth=self.line_width,
                                 alpha=self.line_alpha, linestyle=self.raw_data_linestyle)  # , label='Raw Data')
                else:
                    self.ax.plot(x_values, y_values, c=self.line_color, linewidth=self.line_width,
                             alpha=self.line_alpha, linestyle=self.raw_data_linestyle) #, label='Raw Data')
            elif self.plot_style == "scatter":
                if window.energy_scale == 'KE':
                    self.ax.scatter(window.photons-x_values, y_values, c=self.scatter_color, s=self.scatter_size,
                                marker=self.scatter_marker, label='Raw Data')
                else:
                    self.ax.scatter(x_values, y_values, c=self.scatter_color, s=self.scatter_size,
                                marker=self.scatter_marker, label='Raw Data')
            else:
                if window.energy_scale == 'KE':
                    self.ax.plot(window.photons -x_values, y_values, c=self.line_color, linewidth=self.line_width,
                             alpha=self.line_alpha, linestyle=self.raw_data_linestyle, label='Raw Data')
                else:
                    self.ax.plot(x_values, y_values, c=self.line_color, linewidth=self.line_width,
                                 alpha=self.line_alpha, linestyle=self.raw_data_linestyle, label='Raw Data')


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

            if "survey" in sheet_name.lower() or "wide" in sheet_name.lower():
                pass
            else:
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
        """
        Clears the current plot and redraws all elements for the selected sheet.

        This function performs the following key operations:
        1. Retrieves the current sheet name and plot limits.
        2. Clears the existing plot and updates axis labels and formatting.
        3. Plots raw data according to the selected energy scale (BE or KE).
        4. Identifies and plots doublet peaks with appropriate coloring.
        5. Plots fitted peaks using stored parameters, handling different fitting models.
        6. Plots the background if available.
        7. Updates overall fit and residuals for fitted data.
        8. Handles special cases for survey/wide scans.
        9. Updates the plot legend and restores or creates sheet name text.
        10. Adjusts plot limits and spine widths for better visibility.
        11. Redraws the canvas to reflect all changes.

        The function adapts its behavior based on the sheet type (e.g., survey vs. core level),
        energy scale, and fitting status of peaks. It ensures that all visual elements
        are correctly positioned and formatted according to the current application state.
        """

        sheet_name = window.sheet_combobox.GetValue()
        limits = window.plot_config.get_plot_limits(window, sheet_name)
        cst_unfit = ""

        if sheet_name not in window.Data['Core levels']:
            wx.MessageBox(f"No data available for sheet: {sheet_name}", "Error", wx.OK | wx.ICON_ERROR)
            return

        core_level_data = window.Data['Core levels'][sheet_name]

        if window.energy_scale == 'KE':
            self.ax.set_xlim(window.photons - limits['Xmax'], window.photons - limits['Xmin'])  # Reverse X-axis
        else:
            self.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis

        # self.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
        self.ax.set_ylim(limits['Ymin'], limits['Ymax'])

        # Store existing sheet name text
        sheet_name_text = None
        for txt in self.ax.texts:
            if getattr(txt, 'sheet_name_text', False):
                sheet_name_text = txt
                break

        # Clear the plot
        self.ax.clear()
        x_label = "Kinetic Energy (eV)" if window.energy_scale == 'KE' else "Binding Energy (eV)"
        self.ax.set_xlabel(x_label)
        # self.ax.set_xlabel("Binding Energy (eV)")
        self.ax.set_ylabel("Intensity (CPS)")
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

        if window.energy_scale == 'KE':
            X_MIN = window.photons - limits['Xmax']
            X_MAX = window.photons - limits['Xmin']
            self.ax.set_xlim(min(X_MIN, X_MAX), max(X_MIN, X_MAX))  # Reverse X-axis
            # self.ax.set_xlim(window.photons - limits['Xmax'],window.photons - limits['Xmin'])  # Reverse X-axis

        self.ax.set_ylim(limits['Ymin'], limits['Ymax'])

        # Create a color cycle
        colors = plt.cm.tab10(np.linspace(0, 1, 10))
        color_cycle = cycle(colors)

        # Replot all peaks and update indices
        num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows

        # First, identify all doublets
        doublets = []
        for i in range(0, num_peaks - 1):
            current_label = window.peak_params_grid.GetCellValue(i * 2, 1)
            next_label = window.peak_params_grid.GetCellValue((i + 1) * 2, 1)
            if self.is_part_of_doublet(current_label, next_label):
                doublets.extend([i, i + 1])

        for i in range(num_peaks):
            row = i * 2

            # Get all necessary values, with error checking
            try:
                position = float(window.peak_params_grid.GetCellValue(row, 2))
                height = float(window.peak_params_grid.GetCellValue(row, 3))
                fwhm = float(window.peak_params_grid.GetCellValue(row, 4))
                fraction = float(window.peak_params_grid.GetCellValue(row, 5))
                tail_e = float(window.peak_params_grid.GetCellValue(row, 7))
                tail_m = float(window.peak_params_grid.GetCellValue(row, 8))
                label = window.peak_params_grid.GetCellValue(row, 1)
                fitting_model = window.peak_params_grid.GetCellValue(row, 12)
            except ValueError:
                print(f"Warning: Invalid data for peak {i + 1}. Skipping this peak.")
                continue

            if fitting_model == "Unfitted":
                # For unfitted peaks, fill between background and raw data
                cst_unfit = "Unfitted"
                if window.energy_scale == 'KE':
                    self.ax.fill_between(window.photons - x_values, window.background, y_values,
                                     facecolor='lightgreen', alpha=0.5, label=label)
                else:
                    self.ax.fill_between(x_values, window.background, y_values,
                                         facecolor='lightgreen', alpha=0.5, label=label)
            else:
                if i in doublets:
                    if doublets.index(i) % 2 == 0:  # First peak of the doublet
                        color = self.peak_colors[i % len(self.peak_colors)]
                        alpha = self.peak_alpha
                    else:  # Second peak of the doublet
                        # Use the same color as the first peak of the doublet, but with lower alpha
                        color = self.peak_colors[(i - 1) % len(self.peak_colors)]
                        alpha = self.peak_alpha * 0.8  # Reduce alpha for the second peak
                else:
                    color = self.peak_colors[i % len(self.peak_colors)]
                    alpha = self.peak_alpha

                # For fitted peaks, use the existing plot_peak method
                peak_params = {
                    'row': row,
                    'position': position,
                    'height': height,
                    'fwhm': fwhm,
                    'lg_ratio': fraction,
                    'Tail M': tail_m,
                    'Tail E': tail_e,
                    'label': label,
                    'fitting_model': fitting_model
                }
                if window.energy_scale == 'KE':
                    self.plot_peak(window.x_values, window.background, peak_params, sheet_name, window,
                                                color=color, alpha=alpha)
                else:
                    self.plot_peak(window.x_values, window.background, peak_params, sheet_name, window, color=color,
                                   alpha=alpha)


        # Plot the background if it exists
        if 'Bkg Y' in core_level_data['Background'] and len(core_level_data['Background']['Bkg Y']) > 0:
            if "survey" in sheet_name.lower() or "wide" in sheet_name.lower():
                pass
            else:
                if window.energy_scale == 'KE':
                    self.ax.plot(window.photons - x_values, core_level_data['Background']['Bkg Y'],
                                 color=self.background_color,
                            linestyle=self.background_linestyle, alpha=self.background_alpha, label='Background')
                else:
                    self.ax.plot(x_values, core_level_data['Background']['Bkg Y'], color=self.background_color,
                                 linestyle=self.background_linestyle, alpha=self.background_alpha, label='Background')
        # Update overall fit and residuals
        if cst_unfit == "Unfitted" or any(x in sheet_name.lower() for x in ["survey", "wide"]):
            pass
        else:
            window.update_overall_fit_and_residuals()

        # When plotting raw data
        if "survey" in sheet_name.lower() or "wide" in sheet_name.lower():
            if window.energy_scale == 'KE':
                self.ax.plot(window.photons - x_values, y_values, c=self.line_color, linewidth=self.line_width,
                         alpha=self.line_alpha, linestyle=self.raw_data_linestyle) #, label='Raw Data')
            else:
                self.ax.plot(x_values, y_values, c=self.line_color, linewidth=self.line_width,
                         alpha=self.line_alpha, linestyle=self.raw_data_linestyle) #, label='Raw Data')
        elif self.plot_style == "scatter":
            if window.energy_scale == 'KE':
                self.ax.scatter(window.photons - x_values, y_values, c=self.scatter_color, s=self.scatter_size,
                            marker=self.scatter_marker, label='Raw Data')
            else:
                self.ax.scatter(x_values, y_values, c=self.scatter_color, s=self.scatter_size,
                                marker=self.scatter_marker, label='Raw Data')
        else:
            self.ax.plot(x_values, y_values, c=self.line_color, linewidth=self.line_width,
                         alpha=self.line_alpha, linestyle=self.raw_data_linestyle, label='Raw Data')

        # Assuming 'ax' is your axes object
        for spine in self.ax.spines.values():
            spine.set_linewidth(1)  # Adjust this value to increase or decrease thickness

        # Update the legend only if necessary
        if "survey" in sheet_name.lower() or "wide" in sheet_name.lower():
            pass
        else:
            self.ax.legend(loc='upper left')

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
        # window.update_checkbox_visuals()


    def is_part_of_doublet(self, current_label, next_label):
        """
        Determines if two adjacent peaks form a doublet based on their labels.
        Checks for matching core levels and appropriate spin-orbit components.
        """
        current_parts = current_label.split()
        next_parts = next_label.split()

        if len(current_parts) < 1 or len(next_parts) < 1:
            return False

        # Extract core level without spin-orbit component
        def extract_core_level(label):
            match = re.match(r'([A-Za-z]+\d+[spdf])', label)
            return match.group(1) if match else label

        current_core_level = extract_core_level(current_parts[0])
        next_core_level = extract_core_level(next_parts[0])

        if current_core_level != next_core_level:
            return False

        orbital = re.search(r'\d([spdf])', current_core_level)
        if not orbital:
            return False

        orbital = orbital.group(1)

        # Check for spin-orbit components in either the first or second part of the label
        def has_component(parts, component):
            return any(component in part for part in parts)

        if orbital == 'p':
            return ((has_component(current_parts, '3/2') and has_component(next_parts, '1/2')))  # or \
            # (has_component(current_parts, '1/2') and has_component(next_parts, '3/2')))
        elif orbital == 'd':
            return ((has_component(current_parts, '5/2') and has_component(next_parts, '3/2'))) # or \
                # (has_component(current_parts, '3/2') and has_component(next_parts, '5/2'))
        elif orbital == 'f':
            return ((has_component(current_parts, '7/2') and has_component(next_parts, '5/2'))) # or \
                # (has_component(current_parts, '5/2') and has_component(next_parts, '7/2'))

        return False

    def update_peak_plot(self, window, x, y, remove_old_peaks=True):
        """
        Updates the plot for a selected peak when its position or height is changed.
        Recalculates the peak shape based on the current fitting model and parameters.
        """
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
            gamma = lg_ratio/100 * sigma
            bkg_y = window.background[np.argmin(np.abs(window.x_values - x))]

            tail_e = float(window.peak_params_grid.GetCellValue(row, 7))
            tail_m = float(window.peak_params_grid.GetCellValue(row, 8))

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
            elif window.selected_fitting_method == "GLT":
                peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
                params = peak_model.make_params(center=x, amplitude=y, sigma=sigma, gamma=gamma, tail_mix=tail_m,
                                                tail_exp=tail_e)
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
                print("I AM NOT SURE WHAT THIS DO")
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
        """
        Recalculates and updates the overall fit and residuals for all peaks.
        Handles different fitting models for each peak and scales residuals for better visibility.
        """
        # Calculate the overall fit as the sum of all peaks
        overall_fit = window.background.astype(float).copy()
        num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows

        for i in range(num_peaks):
            row = i * 2  # Each peak uses two rows in the grid

            # Get cell values
            position_str = window.peak_params_grid.GetCellValue(row, 2)  # Position
            height_str = window.peak_params_grid.GetCellValue(row, 3)  # Height
            fwhm_str = window.peak_params_grid.GetCellValue(row, 4)  # FWHM
            lg_ratio_str = window.peak_params_grid.GetCellValue(row, 5)  # L/G
            tail_e = window.peak_params_grid.GetCellValue(row, 7)
            tail_m = window.peak_params_grid.GetCellValue(row, 7)
            fitting_model = window.peak_params_grid.GetCellValue(row, 12)  # Fitting Model

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
            gamma = lg_ratio/100 * sigma
            bkg_y = window.background[np.argmin(np.abs(window.x_values - peak_x))]

            if fitting_model == "Voigt":
                peak_model = lmfit.models.VoigtModel()
                amplitude = peak_y / peak_model.eval(center=0, amplitude=1, sigma=sigma, gamma=gamma, x=0)
                params = peak_model.make_params(center=peak_x, amplitude=amplitude, sigma=sigma, gamma=gamma)
            elif fitting_model == "Pseudo-Voigt":
                sigma = fwhm / 2
                peak_model = lmfit.models.PseudoVoigtModel()
                amplitude = peak_y / peak_model.eval(center=0, amplitude=1, sigma=sigma, fraction=lg_ratio/100, x=0)
                params = peak_model.make_params(center=peak_x, amplitude=amplitude, sigma=sigma, fraction=lg_ratio/100)
            elif fitting_model == "GL":
                peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
                params = peak_model.make_params(center=peak_x, fwhm=fwhm, fraction=lg_ratio, amplitude=peak_y, tail_mix=tail_m, tail_exp=tail_e)
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


        # Create a masked array where 0 values are masked
        masked_residuals = ma.masked_where(np.isclose(scaled_residuals, 0, atol=5e-1), scaled_residuals)

        # Remove old overall fit and residuals, keep background lines
        for line in self.ax.get_lines():
            if line.get_label() in ['Overall Fit', 'Residuals']:
                line.remove()

        # Plot the new overall fit and residuals
        if window.energy_scale == 'KE':
            self.ax.plot(window.photons - window.x_values, overall_fit, color=self.envelope_color,
                    linestyle=self.envelope_linestyle, alpha=self.envelope_alpha, label='Overall Fit')

            self.ax.plot(window.photons - window.x_values, masked_residuals + 1.05 * max(window.y_values),
                     color=self.residual_color, linestyle=self.residual_linestyle,
                     alpha=self.residual_alpha, label='Residuals')
        else:
            self.ax.plot(window.x_values, overall_fit, color=self.envelope_color,
                    linestyle=self.envelope_linestyle, alpha=self.envelope_alpha, label='Overall Fit')

            self.ax.plot(window.x_values, masked_residuals + 1.05 * max(window.y_values),
                     color=self.residual_color, linestyle=self.residual_linestyle,
                     alpha=self.residual_alpha, label='Residuals')

        # Update the Y-axis label
        self.ax.set_ylabel(f'Intensity (CPS), residual x {scaling_factor:.2f}')

        self.canvas.draw_idle()

        return residuals

    def update_peak_fwhm(self, window, x):
        if window.initial_fwhm is not None and window.initial_x is not None:
            row = window.selected_peak_index * 2
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

            # Clear and replot
            window.clear_and_replot()

            # Add the cross back
            window.plot_manager.add_cross_to_peak(window, window.selected_peak_index)

            # Redraw the canvas
            window.canvas.draw_idle()

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
            self.cross, = self.ax.plot(peak_x, peak_y, 'bx', markersize=15, markerfacecolor='none', picker=5,
                                       linewidth=3)

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

    def update_legend2(self, window):
        # Retrieve the current handles and labels
        handles, labels = self.ax.get_legend_handles_labels()

        # Define the desired order of legend entries
        legend_order = ["Raw Data", "Background", "Overall Fit", "Residuals"]
        legend_order2 = ["Raw Data", "Background", "Overall Fit", "Residuals"]

        # Collect peak labels
        num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows
        peak_labels = [window.peak_params_grid.GetCellValue(i * 2, 1) for i in range(num_peaks)]
        formatted_peak_labels = [re.sub(r'(\d+/\d+)', r'$_{\1}$', label) for label in peak_labels]

        # Filter peak labels to only include those with a second word
        filtered_peak_labels = []
        for label in formatted_peak_labels:
            # Remove LaTeX formatting temporarily for splitting
            clean_label = re.sub(r'\$.*?\$', '', label)
            split_label = clean_label.split()
            print(f"Clean label: {clean_label}, Split label: {split_label}")
            if len(split_label) > 1:
                # Check if the second part is not empty
                if split_label[1].strip():
                    filtered_peak_labels.append(label)
            else:
                # Optionally, you can add logging or print a message for skipped labels
                print(f"Skipping label '{label}' from legend as it doesn't have a second word")

        # Ensure filtered peaks are added to the end of the order
        legend_order += peak_labels
        legend_order2 += filtered_peak_labels

        # Update the legend with the ordered items from legend_order
        if legend_order:
            # Find handles for each label in legend_order
            ordered_handles = []
            for l in legend_order:
                for index, label in enumerate(labels):
                    if label == l or label.startswith(l) or l.startswith(label):
                        ordered_handles.append(handles[index])
                        break
                else:
                    pass
                    # print(f"Warning: No handle found for label '{l}'")

            # Create the legend with the ordered labels and handles
            self.ax.legend(ordered_handles, legend_order2, loc='upper left')
        else:
            self.ax.legend().remove()
        self.canvas.draw_idle()

    def update_legend(self, window):
        # Retrieve the current handles and labels
        handles, labels = self.ax.get_legend_handles_labels()

        # Define the desired order of legend entries
        legend_order = ["Raw Data", "Background", "Overall Fit", "Residuals"]

        # Collect peak labels
        num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows
        peak_labels = [window.peak_params_grid.GetCellValue(i * 2, 1) for i in range(num_peaks)]
        formatted_peak_labels = [re.sub(r'(\d+/\d+)', r'$_{\1}$', label) for label in peak_labels]

        # Filter peak labels to only include those with a second word
        filtered_peak_labels = []
        filtered_formatted_labels = []
        for label, formatted_label in zip(peak_labels, formatted_peak_labels):
            split_label = label.split()
            if len(split_label) > 1:
                # Check if the second part is not empty
                if split_label[1].strip():
                    filtered_peak_labels.append(label)
                    filtered_formatted_labels.append(formatted_label)
            else:
                # print(f"Skipping label '{formatted_label}' from legend as it doesn't have a second word")
                pass

        # Ensure filtered peaks are added to the end of the order
        legend_order += filtered_peak_labels
        formatted_legend_order = legend_order[:4] + filtered_formatted_labels

        # Update the legend with the ordered items from legend_order
        if legend_order:
            # Find handles for each label in legend_order
            ordered_handles = []
            for l in legend_order:
                for index, label in enumerate(labels):
                    if label == l:
                        ordered_handles.append(handles[index])
                        break
                else:
                    pass

            # Create the legend with the ordered labels and handles
            self.ax.legend(ordered_handles, formatted_legend_order, loc='upper left')
        else:
            self.ax.legend().remove()
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

    def update_plot_style(self, style, scatter_size, line_width, line_alpha, scatter_color, line_color, scatter_marker,
                          background_color, background_alpha, background_linestyle,
                          envelope_color, envelope_alpha, envelope_linestyle,
                          residual_color, residual_alpha, residual_linestyle,
                          raw_data_linestyle, peak_colors, peak_alpha):
        self.plot_style = style
        self.scatter_size = scatter_size
        self.line_width = line_width
        self.line_alpha = line_alpha
        self.scatter_color = scatter_color
        self.line_color = line_color
        self.scatter_marker = scatter_marker
        self.background_color = background_color
        self.background_alpha = background_alpha
        self.background_linestyle = background_linestyle
        self.envelope_color = envelope_color
        self.envelope_alpha = envelope_alpha
        self.envelope_linestyle = envelope_linestyle
        self.residual_color = residual_color
        self.residual_alpha = residual_alpha
        self.residual_linestyle = residual_linestyle
        self.raw_data_linestyle = raw_data_linestyle
        self.peak_colors = peak_colors
        self.peak_alpha = peak_alpha

    def toggle_peak_fill(self):
        self.peak_fill_enabled = not self.peak_fill_enabled
        return self.peak_fill_enabled  # Return the new state

