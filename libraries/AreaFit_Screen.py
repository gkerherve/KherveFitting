import wx
from libraries.Plot_Operations import PlotManager
from libraries.Save import save_state
import numpy as np

class BackgroundWindow(wx.Frame):
    def __init__(self, parent, *args, **kw):
        super(BackgroundWindow, self).__init__(parent, *args, **kw, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU) | wx.STAY_ON_TOP)
        self.parent = parent
        self.SetTitle("Measure Area between the range cursors")
        self.SetSize((270, 300))
        self.SetMinSize((270, 300))
        self.SetMaxSize((270, 300))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))

        # Create controls
        method_label = wx.StaticText(panel, label="Method:")
        self.method_combobox = wx.ComboBox(panel, choices=["Multi-Regions Smart", "Smart", "Shirley", "Linear"],
                                           style=wx.CB_READONLY)
        self.method_combobox.SetSelection(0)  # Default to Shirley

        offset_h_label = wx.StaticText(panel, label="Offset (H):")
        self.offset_h_text = wx.TextCtrl(panel, value="0")

        offset_l_label = wx.StaticText(panel, label="Offset (L):")
        self.offset_l_text = wx.TextCtrl(panel, value="0")

        self.offset_h_text.Bind(wx.EVT_TEXT, self.on_offset_changed)
        self.offset_l_text.Bind(wx.EVT_TEXT, self.on_offset_changed)

        background_button = wx.Button(panel, label="Background")
        background_button.SetMinSize((110, 40))
        background_button.Bind(wx.EVT_BUTTON, self.on_background)

        clear_background_button = wx.Button(panel, label="Clear Background")
        clear_background_button.SetMinSize((110, 40))
        clear_background_button.Bind(wx.EVT_BUTTON, self.on_clear_background)

        export_button = wx.Button(panel, label="Accept")
        export_button.SetMinSize((60, 40))
        export_button.Bind(wx.EVT_BUTTON, self.on_export_results)

        # Layout with a GridBagSizer
        sizer = wx.GridBagSizer(hgap=5, vgap=5)

        # First row: Method
        sizer.Add(method_label, pos=(0, 0), span=(1, 2), flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(self.method_combobox, pos=(1, 0), span=(1, 2), flag=wx.ALL | wx.EXPAND, border=5)

        # Second row: Offset (H) and Offset (L)
        sizer.Add(offset_h_label, pos=(2, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.offset_h_text, pos=(2, 1), flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(offset_l_label, pos=(3, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer.Add(self.offset_l_text, pos=(3, 1), flag=wx.ALL | wx.EXPAND, border=5)

        # Third row: Background and Clear Background buttons
        sizer.Add(background_button, pos=(4, 0), flag=wx.ALL | wx.EXPAND, border=5)
        sizer.Add(clear_background_button, pos=(4, 1), flag=wx.ALL | wx.EXPAND, border=5)

        # Fourth row: Export buttons
        sizer.Add(export_button, pos=(5, 0), flag=wx.ALL | wx.EXPAND, border=5)


        self.Bind(wx.EVT_CLOSE, self.on_close)

        panel.SetSizer(sizer)

    def on_close(self, event):
        self.parent.background_tab_selected = False
        self.Destroy()

    def on_background(self, event):
        try:
            # Define the background behavior here
            self.parent.plot_manager.plot_background(self.parent)

            # Calculate the area between data and background
            sheet_name = self.parent.sheet_combobox.GetValue()
            if sheet_name in self.parent.Data['Core levels']:
                core_level_data = self.parent.Data['Core levels'][sheet_name]
                x_values = np.array(core_level_data['B.E.'])
                y_values = np.array(core_level_data['Raw Data'])
                background = np.array(core_level_data['Background']['Bkg Y'])

                # Ensure the arrays have the same length
                min_length = min(len(x_values), len(y_values), len(background))
                x_values = x_values[:min_length]
                y_values = y_values[:min_length]
                background = background[:min_length]

                # Save background data
                self.parent.Data['Core levels'][sheet_name]['Background']['Bkg Y'] = background.tolist()

                # Calculate the area
                area = round(abs(np.trapz(y_values - background, x_values)), 2)

                # Find the peak position and height
                peak_index = np.argmax(y_values - background)
                peak_position = round(x_values[peak_index], 2)
                peak_height = round(y_values[peak_index] - background[peak_index], 2)

                # Use sheet_name as peak_name
                peak_name = sheet_name

                # Calculate FWHM for a Gaussian peak (L/G = 0)
                fwhm = round(2 * np.sqrt(2 * np.log(2)) * area / (peak_height * np.sqrt(2 * np.pi)), 2)

                # Default constraints
                position_constraint = "0,1e3"
                height_constraint = "1,1e7"
                fwhm_constraint = "0.3,3.5"
                lg_constraint = "0,0.5"
                sigma_constraint = "0.1,1"
                gamma_constraint = "0.1,1"

                # Update peak fitting parameter grid
                grid = self.parent.peak_params_grid
                grid.ClearGrid()
                if grid.GetNumberRows() > 0:
                    grid.DeleteRows(0, grid.GetNumberRows())
                grid.AppendRows(2)  # Add two rows for the new peak

                grid.SetCellValue(0, 0, "A")  # Set ID
                grid.SetCellValue(0, 1, peak_name)
                grid.SetCellValue(0, 2, f"{peak_position:.2f}")
                grid.SetCellValue(0, 3, f"{peak_height:.2f}")
                grid.SetCellValue(0, 4, f"{fwhm:.2f}")
                grid.SetCellValue(0, 5, "0.00")  # L/G
                grid.SetCellValue(0, 6, f"{area:.2f}")
                grid.SetCellValue(0, 7, "0.00")  # Sigma
                grid.SetCellValue(0, 8, "0.00")  # Gamma
                grid.SetCellValue(0, 13, "Unfitted")  # Fitting Model

                # Set constraints and color
                for col in range(grid.GetNumberCols()):
                    grid.SetCellBackgroundColour(1, col, wx.Colour(230, 230, 230))
                grid.SetCellValue(1, 2, position_constraint)
                grid.SetCellValue(1, 3, height_constraint)
                grid.SetCellValue(1, 4, fwhm_constraint)
                grid.SetCellValue(1, 5, lg_constraint)
                grid.SetCellValue(1, 7, sigma_constraint)
                grid.SetCellValue(1, 8, gamma_constraint)
                grid.SetCellValue(1, 9, skew_constraint)

                # Save peak data in window.Data
                if 'Fitting' not in self.parent.Data['Core levels'][sheet_name]:
                    self.parent.Data['Core levels'][sheet_name]['Fitting'] = {}
                if 'Peaks' not in self.parent.Data['Core levels'][sheet_name]['Fitting']:
                    self.parent.Data['Core levels'][sheet_name]['Fitting']['Peaks'] = {}

                self.parent.Data['Core levels'][sheet_name]['Fitting']['Peaks'][peak_name] = {
                    'Position': peak_position,
                    'Height': peak_height,
                    'FWHM': fwhm,
                    'L/G': 0.00,
                    'Area': area,
                    'Sigma': 0,
                    'Gamma': 0,
                    'Skew': 0,
                    'Fitting Model': "Unfitted",
                    'Constraints': {
                        'Position': position_constraint,
                        'Height': height_constraint,
                        'FWHM': fwhm_constraint,
                        'L/G': lg_constraint,
                        'Sigma': sigma_constraint,
                        'Gamma': gamma_constraint,
                        'skew': skew_constraint
                    }
                }

                # Fill the area between raw data and background
                fill = self.parent.ax.fill_between(x_values, background, y_values,
                                                   facecolor='lightgreen', alpha=0.5,
                                                   label=f'{peak_name}')

                # Update the legend
                self.parent.ax.legend()

                # Refresh the grid and plot
                self.parent.peak_params_grid.ForceRefresh()
                self.parent.canvas.draw_idle()

                # Print the results to the terminal
                print(f"Results for {sheet_name}:")
                print(f"Peak Name: {peak_name}")
                print(f"Peak Position: {peak_position:.2f} eV")
                print(f"Peak Height: {peak_height:.2f} counts")
                print(f"FWHM: {fwhm:.2f} eV")
                print(f"Area: {area:.2f}")

                save_state(self.parent)

        except Exception as e:
            print(f"Error calculating background: {str(e)}")

    def on_clear_background(self, event):
        # Define the clear background behavior here
        self.parent.plot_manager.clear_background(self.parent)
        save_state(self.parent)

    def on_export_results(self, event):
        self.parent.export_results()
        save_state(self.parent)

    def on_offset_changed(self, event):
        try:
            offset_h = float(self.offset_h_text.GetValue())
            offset_l = float(self.offset_l_text.GetValue())
            self.parent.set_offset_h(offset_h)
            self.parent.set_offset_l(offset_l)
            save_state(self.parent)
        except ValueError:
            print("Invalid offset value")
