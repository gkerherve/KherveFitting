
import re
import wx
from Functions import fit_peaks, remove_peak
from libraries.Plot_Operations import PlotManager
from libraries.Open import load_library_data

from libraries.Save import save_state

class FittingWindow(wx.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU) | wx.STAY_ON_TOP)
        self.parent = parent  # Store reference to MainFrame


        self.SetTitle("Peak Fitting")
        self.SetSize((305, 520))  # Increased height to accommodate new elements
        self.SetMinSize((305, 520))
        self.SetMaxSize((305, 520))

        #305 480

        self.init_ui()

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.library_data = self.parent.library_data
        self.doublet_splittings = self.load_doublet_splittings(self.parent.library_data)

        # self.library_data = load_library_data()  # Load once when the window is created
        # self.doublet_splittings = self.load_doublet_splittings(self.library_data)
        # self.doublet_splittings = self.load_doublet_splittings("DS.lib")

    def init_ui(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))

        main_sizer = wx.BoxSizer(wx.VERTICAL)


        notebook = wx.Notebook(panel)
        self.init_background_tab(notebook)
        self.init_fitting_tab(notebook)

        main_sizer.Add(notebook, 1, wx.EXPAND,border=5)
        panel.SetSizer(main_sizer)

        notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)

        self.parent.background_tab_selected = True
        self.parent.peak_fitting_tab_selected = False
        self.parent.show_hide_vlines()
        self.parent.deselect_all_peaks()



    def init_background_tab(self, notebook):
        """Initialize the background tab in the notebook."""
        self.parent.background_method = "Multi-Regions Smart"
        self.parent.offset_h = 0
        self.parent.offset_l = 0


        self.background_panel = wx.Panel(notebook)
        background_sizer = wx.GridBagSizer(hgap=0, vgap=0)

        method_label = wx.StaticText(self.background_panel, label="Method:")
        self.method_combobox = wx.ComboBox(self.background_panel, choices=["Multi-Regions Smart", "Smart", "Shirley", "Linear"],
                                           style=wx.CB_READONLY)
        method_index = self.method_combobox.FindString(self.parent.background_method)
        self.method_combobox.SetSelection(method_index)
        self.method_combobox.Bind(wx.EVT_COMBOBOX, self.on_bkg_method_change)

        info_button = self.create_info_button(self.background_panel,
                                              self.get_background_description(self.parent.background_method))

        offset_h_label = wx.StaticText(self.background_panel, label="Offset (H):")
        self.offset_h_text = wx.TextCtrl(self.background_panel, value=str(self.parent.offset_h))
        self.offset_h_text.Bind(wx.EVT_TEXT, self.on_offset_h_change)

        offset_l_label = wx.StaticText(self.background_panel, label="Offset (L):")
        self.offset_l_text = wx.TextCtrl(self.background_panel, value=str(self.parent.offset_l))
        self.offset_l_text.Bind(wx.EVT_TEXT, self.on_offset_l_change)

        averaging_points_label = wx.StaticText(self.background_panel, label="Averaging Points:")
        self.averaging_points_text = wx.TextCtrl(self.background_panel, value="5")
        self.averaging_points_text.Bind(wx.EVT_TEXT, self.on_averaging_points_change)

        background_button = wx.Button(self.background_panel, label="Background")
        background_button.SetMinSize((125, 40))
        background_button.Bind(wx.EVT_BUTTON, self.on_background)

        clear_background_button = wx.Button(self.background_panel, label="Clear All")
        clear_background_button.SetMinSize((125, 40))
        clear_background_button.Bind(wx.EVT_BUTTON, self.on_clear_background)

        reset_vlines_button = wx.Button(self.background_panel, label="Reset \nVertical Lines")
        reset_vlines_button.SetMinSize((125, 40))
        reset_vlines_button.Bind(wx.EVT_BUTTON, self.on_reset_vlines)

        clear_background_only_button = wx.Button(self.background_panel, label="Clear\nBackground")
        clear_background_only_button.SetMinSize((125, 40))
        clear_background_only_button.Bind(wx.EVT_BUTTON, self.on_clear_background_only)

        # Layout Background Tab
        background_sizer.Add(method_label, pos=(0, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        background_sizer.Add(self.method_combobox, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=0)
        background_sizer.Add(info_button, pos=(1, 1), flag=wx.ALL, border=0)
        background_sizer.Add(offset_h_label, pos=(2, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        background_sizer.Add(self.offset_h_text, pos=(2, 1), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(offset_l_label, pos=(3, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        background_sizer.Add(self.offset_l_text, pos=(3, 1), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(averaging_points_label, pos=(4, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        background_sizer.Add(self.averaging_points_text, pos=(4, 1), flag=wx.ALL | wx.EXPAND, border=5)

        background_sizer.Add(reset_vlines_button, pos=(7, 1), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(clear_background_only_button, pos=(8, 1), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(background_button, pos=(9, 0), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(clear_background_button, pos=(9, 1), flag=wx.ALL | wx.EXPAND, border=5)

        self.background_panel.SetSizer(background_sizer)
        notebook.AddPage(self.background_panel, "Background")

    def init_fitting_tab(self, notebook):
        """Initialize the peak fitting tab in the notebook."""
        self.fitting_panel = wx.Panel(notebook)
        fitting_sizer = wx.GridBagSizer(hgap=0, vgap=0)


        self.model_combobox = CustomComboBox(self.fitting_panel, style=wx.CB_READONLY)

        # Set items and green items
        items = ["Preferred Models-----",
                 "GL (Area)",
                 "SGL (Area)",
                 "LA (Area, \u03c3/\u03b3, \u03b3)",
                 "Voigt (Area, L/G, \u03c3)",
                 "Area Based----------",
                 "GL (Area)",
                 "SGL (Area)",
                 "Voigt (Area, \u03c3, \u03b3)",
                 "Voigt (Area, L/G, \u03c3)",
                 "LA (Area, \u03c3, \u03b3)",
                 "LA (Area, \u03c3/\u03b3, \u03b3)",
                 "LA*G (Area, \u03c3/\u03b3, \u03b3)",
                 "Pseudo-Voigt (Area)",
                 "ExpGauss.(Area, \u03c3, \u03b3)",
                 "Height Based---------",
                 "GL (Height)",
                 "SGL (Height)",
                 "Under Test -----------"
                 ]


        green_items = ["Area Based----------", "Height Based---------", "Under Test -----------", "Preferred Models-----"]
        self.model_combobox.SetItems(items)
        self.model_combobox.SetGreenItems(green_items)

        # Set default selection to "GL (Area)"
        default_index = items.index("GL (Area)")
        self.model_combobox.SetSelection(default_index)
        self.model_combobox.SetValue("GL (Area)")
        self.parent.set_fitting_method("GL (Area)")



        # model_index = self.model_combobox.FindString(self.parent.selected_fitting_method)
        # self.model_combobox.SetSelection(model_index)
        self.model_combobox.Bind(wx.EVT_COMBOBOX, self.on_method_change)

        info_button = self.create_info_button(self.fitting_panel,
                                              self.get_fitting_description(self.parent.selected_fitting_method))

        self.optimization_method = wx.ComboBox(self.fitting_panel, choices=[
            "leastsq",
            "least_squares",
            # "differential_evolution",
            "nelder",
            # "lbfgsb",
            "powell",
            # "cg",
            # "newton",
            "cobyla",
            # "basinhopping",
            # "slsqp",
            # "tnc",
            # "trust-krylov",
            "trust-constr"
            # "dogleg",
            # "shgo",
            # "dual_annealing"
        ], style=wx.CB_READONLY)
        self.optimization_method.SetSelection(1)  # Default value

        self.max_iter_spin = wx.SpinCtrl(self.fitting_panel, value=str(self.parent.max_iterations), min=20, max=200)
        self.max_iter_spin.Bind(wx.EVT_SPINCTRL, self.on_max_iter_change)

        self.fit_iterations_spin = wx.SpinCtrl(self.fitting_panel, value="20", min=3, max=100)

        self.r_squared_label = wx.StaticText(self.fitting_panel, label="R²:")
        self.r_squared_text = wx.TextCtrl(self.fitting_panel, style=wx.TE_READONLY)


        # self.chi_squared_label = wx.StaticText(self.fitting_panel, label="Chi²:")
        # self.chi_squared_text = wx.TextCtrl(self.fitting_panel, style=wx.TE_READONLY)

        self.rsd_label = wx.StaticText(self.fitting_panel, label="RSD:")
        self.rsd_text = wx.TextCtrl(self.fitting_panel, style=wx.TE_READONLY)


        self.red_chi_squared_label = wx.StaticText(self.fitting_panel, label="Red. Chi²:")
        self.red_chi_squared_text = wx.TextCtrl(self.fitting_panel, style=wx.TE_READONLY)

        self.actual_iter_label = wx.StaticText(self.fitting_panel, label="Actual Iterations:")
        self.actual_iter_text = wx.TextCtrl(self.fitting_panel, style=wx.TE_READONLY)

        self.current_fit_label = wx.StaticText(self.fitting_panel, label="Current Fit:")
        self.current_fit_text = wx.TextCtrl(self.fitting_panel, style=wx.TE_READONLY)

        add_peak_button = wx.Button(self.fitting_panel, label="Add 1 Peak\nSinglet")
        add_peak_button.SetMinSize((125, 40))
        add_peak_button.Bind(wx.EVT_BUTTON, self.on_add_peak)

        add_doublet_button = wx.Button(self.fitting_panel, label="Add 2 Peaks\nDoublet")
        add_doublet_button.SetMinSize((125, 40))
        add_doublet_button.Bind(wx.EVT_BUTTON, self.on_add_doublet)

        remove_peak_button = wx.Button(self.fitting_panel, label="Remove Peak")
        remove_peak_button.SetMinSize((125, 40))
        remove_peak_button.Bind(wx.EVT_BUTTON, self.on_remove_peak)

        export_button = wx.Button(self.fitting_panel, label="Accept")
        export_button.SetMinSize((125, 40))
        export_button.Bind(wx.EVT_BUTTON, self.on_export_results)

        fit_button = wx.Button(self.fitting_panel, label="Fit \nOne Time")
        fit_button.SetMinSize((125, 40))
        fit_button.Bind(wx.EVT_BUTTON, self.on_fit_peaks)

        fit_multi_button = wx.Button(self.fitting_panel, label="Fit \nMultiple Times")
        fit_multi_button.SetMinSize((125, 40))
        fit_multi_button.Bind(wx.EVT_BUTTON, self.on_fit_multi)

        fitting_sizer.Add(wx.StaticText(self.fitting_panel, label="Fitting Model:"), pos=(0, 0),
                          flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.model_combobox, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=0)
        fitting_sizer.Add(info_button, pos=(1, 1), flag=wx.ALL, border=0)

        fitting_sizer.Add(wx.StaticText(self.fitting_panel, label="Optimization Method:"), pos=(2, 0),
                          flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.optimization_method, pos=(2, 1), flag=wx.ALL | wx.EXPAND, border=0)

        fitting_sizer.Add(wx.StaticText(self.fitting_panel, label="Convergence Limit:"), pos=(3, 0),
                          flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.max_iter_spin, pos=(3, 1), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(wx.StaticText(self.fitting_panel, label="Fit Iterations:"), pos=(4, 0),
                          flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.fit_iterations_spin, pos=(4, 1), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_sizer.Add(self.r_squared_label, pos=(5, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.r_squared_text, pos=(5, 1), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(self.rsd_label, pos=(6, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.rsd_text, pos=(6, 1), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(self.red_chi_squared_label, pos=(7, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.red_chi_squared_text, pos=(7, 1), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_sizer.Add(self.actual_iter_label, pos=(8, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.actual_iter_text, pos=(8, 1), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(self.current_fit_label, pos=(9, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.current_fit_text, pos=(9, 1), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_sizer.Add(add_peak_button, pos=(10, 0), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(add_doublet_button, pos=(10, 1), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_sizer.Add(remove_peak_button, pos=(11, 0), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(export_button, pos=(11, 1), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_sizer.Add(fit_button, pos=(12, 0), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(fit_multi_button, pos=(12, 1), flag=wx.ALL | wx.EXPAND, border=5)

        self.fitting_panel.SetSizer(fitting_sizer)
        notebook.AddPage(self.fitting_panel, "Peak Fitting")

    def get_optimization_method(self):
        selection = self.optimization_method.GetValue()
        return selection.split()[0]  # Get just the method name without description

    def on_method_change(self, event):
        new_method = self.model_combobox.GetValue()
        old_method = self.parent.selected_fitting_method
        self.parent.set_fitting_method(new_method)
        self.update_fitting_info_button()

    def on_max_iter_change(self, event):
        self.parent.set_max_iterations(self.max_iter_spin.GetValue())

    # def on_method_change(self, event):
    #     new_method = self.model_combobox.GetValue()
    #     self.parent.set_fitting_method(new_method)

    def on_bkg_method_change(self, event):
        new_method = self.method_combobox.GetValue()
        self.parent.set_background_method(new_method)
        self.update_background_info_button()

    def on_clear_background_only(self, event):
        self.parent.plot_manager.clear_background_only(self.parent)

    def on_averaging_points_change(self, event):
        try:
            self.parent.averaging_points = int(self.averaging_points_text.GetValue())
        except ValueError:
            pass

    def on_reset_vlines(self, event):
        self.parent.vline1 = None
        self.parent.vline2 = None
        self.parent.show_hide_vlines()
        self.parent.plot_manager.clear_and_replot(self.parent)


    def on_add_peak(self, event):
        self.parent.add_peak_params()

    def on_remove_peak(self, event):
        remove_peak(self.parent)

    def on_fit_multi(self, event):
        save_state(self.parent)
        iterations = self.fit_iterations_spin.GetValue()
        for i in range(1, iterations + 1):
            self.current_fit_text.SetValue(f"{i}/{iterations}")
            result = fit_peaks(self.parent, self.parent.peak_params_grid)
            if result:
                r_squared, rsd, red_chi_square = result
                self.update_fit_indicators(r_squared, rsd, red_chi_square)
                self.actual_iter_text.SetValue(str(self.parent.fit_results['nfev']))
            self.parent.clear_and_replot()
            wx.Yield()
        self.current_fit_text.SetValue("Complete")
        save_state(self.parent)

    def on_fit_peaks(self, event):
        save_state(self.parent)
        result = fit_peaks(self.parent, self.parent.peak_params_grid)
        if result:
            r_squared, rsd, red_chi_squared = result
            self.update_fit_indicators(r_squared, rsd, red_chi_squared)
        else:
            print("Fitting failed or was cancelled.")

    def update_fit_indicators(self, r_squared, rsd, red_chi_squared):
        self.r_squared_text.SetValue(f"{r_squared:.5f}")
        self.rsd_text.SetValue(f"{rsd:.5f}")
        self.red_chi_squared_text.SetValue(f"{red_chi_squared:.2f}")
        self.Layout()

    def on_export_results(self, event):
        self.parent.export_results()


    def load_doublet_splittings_OLD(self, library_data):
        splittings = {}
        for key, value in library_data.items():
            element, orbital = key
            if orbital.endswith(('p', 'd', 'f')):
                # splittings[f"{element}{orbital}"] = value['Al']['ds']  # Default to Al instrument
                splittings[f"{element}{orbital}"] = value['Al1486']['ds']  # Default to Al instrument
        return splittings

    def load_doublet_splittings(self, library_data):
        splittings = {}
        for key, value in library_data.items():
            element, orbital = key
            if orbital.endswith(('p', 'd', 'f')):
                try:
                    splittings[f"{element}{orbital}"] = value['C-Al1486']['ds']  # Must match Excel exactly
                except KeyError:
                    # print(f"Available instruments for {element}{orbital}: {list(value.keys())}")
                    # print(f"Full value data: {value}")
                    continue
        return splittings

    def get_doublet_splitting(self, element, orbital, instrument):
        # Try with the orbital as is
        key = (element, orbital)
        if key in self.library_data and instrument in self.library_data[key]:
            return self.library_data[key][instrument]['ds']

        # If not found, try prepending numbers to the orbital
        for num in range(1, 6):  # Trying 1d, 2d, 3d, 4d, 5d
            key = (element, f"{num}{orbital}")
            if key in self.library_data and instrument in self.library_data[key]:
                # return self.library_data[key][instrument]['ds']
                return self.library_data[key]['C-Al1486']['ds']

        # If still not found, return a default value or raise an error
        print(f"Warning: No doublet splitting found for {element} {orbital}")
        return 0.0  # or whatever default value makes sense for your application

    def on_add_doublet(self, event):
        sheet_name = self.parent.sheet_combobox.GetValue()
        first_word = sheet_name.split()[0]  # Get the first word of the sheet name
        orbital = re.search(r'[spdf]', first_word)

        if not orbital:
            wx.MessageBox("Invalid sheet name. Cannot determine orbital type. It needs to of the form Au4f and NOT Au 4f, Error",
                          wx.OK | wx.ICON_ERROR)
            return

        orbital = orbital.group()

        if orbital == 's':
            self.parent.add_peak_params()
        else:
            first_peak = self.parent.add_peak_params()
            second_peak = self.parent.add_peak_params()

            # Add this block here to copy fill type and hatch pattern
            self.parent.peak_fill_types[second_peak] = self.parent.peak_fill_types[first_peak]
            self.parent.peak_hatch_patterns[second_peak] = self.parent.peak_hatch_patterns[first_peak]
            self.hatch_density = 2

            # Set constraints for the second peak
            row1 = first_peak * 2
            row2 = second_peak * 2

            # L/G ratio constraint
            lg_constraint = f"{chr(65 + first_peak)}*1"
            self.parent.peak_params_grid.SetCellValue(row2 + 1, 5, lg_constraint)

            # FWHM constraint
            fwhm_constraint = f"{chr(65 + first_peak)}*1"
            self.parent.peak_params_grid.SetCellValue(row2 + 1, 4, fwhm_constraint)

            # Height constraint
            height_factor = {'p': 0.5, 'd': 0.667, 'f': 0.75}
            height_constraint = f"{chr(65 + first_peak)}*{height_factor[orbital]}#0.05"
            self.parent.peak_params_grid.SetCellValue(row2 + 1, 3, height_constraint)

            # Area constraint
            Area_factor = {'p': 0.5, 'd': 0.667, 'f': 0.75}
            area_constraint = f"{chr(65 + first_peak)}*{height_factor[orbital]}#0.05"
            self.parent.peak_params_grid.SetCellValue(row2 + 1, 6, area_constraint)

            # Position constraint
            # splitting = self.doublet_splittings.get(first_word, 0)
            element = re.match(r'([A-Z][a-z]*)', first_word).group(1)
            splitting = self.get_doublet_splitting(element, orbital, self.parent.current_instrument)

            position_constraint = f"{chr(65 + first_peak)}+{splitting}#0.2"
            self.parent.peak_params_grid.SetCellValue(row2 + 1, 2, position_constraint)

            # Sigma constraint
            sigma_constraint = f"{chr(65 + first_peak)}*1"
            self.parent.peak_params_grid.SetCellValue(row2 + 1, 7, sigma_constraint)

            # Gamma constraint
            gamma_constraint = f"{chr(65 + first_peak)}*1"
            self.parent.peak_params_grid.SetCellValue(row2 + 1, 8, gamma_constraint)

            # Skew constraint
            skew_constraint = f"{chr(65 + first_peak)}*1"
            self.parent.peak_params_grid.SetCellValue(row2 + 1, 9, skew_constraint)

            # Calculate peak numbers
            peak_number1 = first_peak + 1
            peak_number2 = second_peak + 1

            # Set peak names
            if orbital == 'p':
                peak1_name = f"{first_word}3/2 p{peak_number1}"
                peak2_name = f"{first_word}1/2 p{peak_number2}"
            elif orbital == 'd':
                peak1_name = f"{first_word}5/2 p{peak_number1}"
                peak2_name = f"{first_word}3/2 p{peak_number2}"
            elif orbital == 'f':
                peak1_name = f"{first_word}7/2 p{peak_number1}"
                peak2_name = f"{first_word}5/2 p{peak_number2}"

            self.parent.peak_params_grid.SetCellValue(row1, 1, peak1_name)
            self.parent.peak_params_grid.SetCellValue(row2, 1, peak2_name)

            # Position the second peak
            first_peak_position = float(self.parent.peak_params_grid.GetCellValue(row1, 2))
            second_peak_position = first_peak_position + splitting
            self.parent.peak_params_grid.SetCellValue(row2, 2, f"{second_peak_position:.2f}")

            # Update window.Data with new constraints and names
            if 'Fitting' in self.parent.Data['Core levels'][sheet_name] and 'Peaks' in \
                    self.parent.Data['Core levels'][sheet_name]['Fitting']:
                peaks = self.parent.Data['Core levels'][sheet_name]['Fitting']['Peaks']
                new_peaks = {}
                for i, (key, value) in enumerate(peaks.items()):
                    if i == first_peak:
                        new_peaks[peak1_name] = value
                        new_peaks[peak1_name]['Name'] = peak1_name
                    elif i == second_peak:
                        new_peaks[peak2_name] = value
                        new_peaks[peak2_name]['Name'] = peak2_name
                        new_peaks[peak2_name]['Position'] = second_peak_position
                        new_peaks[peak2_name]['Constraints'] = {
                            'Position': position_constraint,
                            'Height': height_constraint,
                            'FWHM': fwhm_constraint,
                            'L/G': lg_constraint,
                            'Area': area_constraint,
                            'Sigma': sigma_constraint,
                            'Gamma': gamma_constraint,
                            'Skew': skew_constraint
                        }
                    else:
                        new_peaks[key] = value
                self.parent.Data['Core levels'][sheet_name]['Fitting']['Peaks'] = new_peaks

        self.parent.clear_and_replot()

    def on_background(self, event):
        self.parent.plot_manager.plot_background(self.parent)
        save_state(self.parent)

    def on_clear_background(self, event):
        self.parent.plot_manager.clear_background(self.parent)
        save_state(self.parent)

    def on_offset_h_change(self, event):
        offset_h_value = self.offset_h_text.GetValue()
        self.parent.set_offset_h(offset_h_value)

    def on_offset_l_change(self, event):
        offset_l_value = self.offset_l_text.GetValue()
        self.parent.set_offset_l(offset_l_value)


    def get_background_description(self, method):
        descriptions = {
            "Multi-Regions Smart": "Same as the Smart background but not restricted to a single region",
            "Smart": "Single region Smart background estimation. It applies a Shirley background "
                     "when the intensity is going up and a linear background when the intensity is "
                     "going down. If the calculated background is above the data then the "
                     "background is set equal to the data.",
            "Shirley": "Iterative background calculation. Reliable for on positive background when "
            "the data contains symmetrical peak.",
            "Linear": "Simple linear background. Usually used on negative background"
        }
        return descriptions.get(method, "No description available")

    def get_fitting_description(self, model):
        descriptions = {
            "GL (Height)": "Gaussian-Lorentzian product function (height-based).\nEquation: I(x) = H * [exp(-ln(2) * ((x-x₀)/σ)²) * (1 / (1 + ((x-x₀)/γ)²))]",
            "SGL (Height)": "Sum of Gaussian and Lorentzian functions (height-based).\nEquation: I(x) = H * [m * exp(-ln(2) * ((x-x₀)/σ)²) + (1-m) / (1 + ((x-x₀)/γ)²)]",
            "GL (Area)": "Gaussian-Lorentzian product function (area-based).\nEquation: Similar to GL (Height), but normalized for area",
            "SGL (Area)": "Sum of Gaussian and Lorentzian functions (area-based).\nEquation: Similar to SGL (Height), but normalized for area",
            "Pseudo-Voigt (Area)": "Linear combination of Gaussian and Lorentzian.\nEquation: I(x) = A * [η * L(x) + (1-η) * G(x)]",
            "Voigt (Area, L/G, \u03c3)": "Convolution of Gaussian and Lorentzian.\nEquation: I(x) = A * ∫G(x')L(x-x')dx'",
            "Voigt (Area,\u03c3, \u03b3)": "Voigt function with separate Gaussian and Lorentzian widths.\nEquation: "
                                           "I(x) = A * ∫G(x', σ)L(x-x', γ)dx'",
            "ExpGauss.(Area, \u03c3, \u03b3)": "Gaussian shape model with asymmetric side. The asymmetry is modelled"
                                               "using an exponential decay as per equation: ",
            "LA (Area, \u03c3, \u03b3)": "Asymmetrical lorentzian similar to the model used in casa XPS",
            "LA (Area, \u03c3/\u03b3, \u03b3)": "Asymmetrical lorentzian with asymmetru controlled by the ratio "
                                                "between \u03c3 and \u03b3 similar to the model used in casa XPS",
            "LA*G (Area, \u03c3/\u03b3, \u03b3)": "Asymmetrical lorentzian convoluted with a gaussian peak of a certain width "
                                           "similar to the model used in casa XPS"

        }
        return descriptions.get(model, "No description available")


    def create_info_button(self, parent, tooltip):
        info_button = wx.Button(parent, label="?", size=(20, 20))
        info_button.SetToolTip(tooltip)
        # info_button.Bind(wx.EVT_ENTER_WINDOW, self.on_info_hover)
        info_button.Bind(wx.EVT_LEAVE_WINDOW, self.on_info_leave)
        return info_button

    def on_info_hover(self, event):
        button = event.GetEventObject()
        pos = button.ClientToScreen(button.GetPosition())
        self.show_info_popup(pos, button.GetToolTip().GetTip())

    def on_info_leave(self, event):
        if hasattr(self, 'info_popup'):
            self.info_popup.Destroy()

    def show_info_popup(self, pos, text):
        self.info_popup = wx.PopupWindow(self, wx.SIMPLE_BORDER)
        panel = wx.Panel(self.info_popup)
        st = wx.StaticText(panel, label=text, pos=(10, 10))
        sz = st.GetBestSize()
        self.info_popup.SetSize((sz.width + 20, sz.height + 20))
        panel.SetSize(self.info_popup.GetSize())
        self.info_popup.Position(pos, (0, 0))
        self.info_popup.Show()

    def update_background_info_button(self):
        for child in self.background_panel.GetChildren():
            if isinstance(child, wx.Button) and child.GetLabel() == "?":
                child.SetToolTip(self.get_background_description(self.parent.background_method))
                break

    def update_fitting_info_button(self):
        for child in self.fitting_panel.GetChildren():
            if isinstance(child, wx.Button) and child.GetLabel() == "?":
                child.SetToolTip(self.get_fitting_description(self.parent.selected_fitting_method))
                break

    def on_tab_change(self, event):
        selected_page = event.GetSelection()
        self.parent.background_tab_selected = (selected_page == 0)
        self.parent.peak_fitting_tab_selected = (selected_page == 1)
        self.parent.show_hide_vlines()

        if selected_page == 0:
            self.parent.enable_background_interaction()
        else:
            self.parent.disable_background_interaction()

        if not self.parent.peak_fitting_tab_selected:
            self.parent.deselect_all_peaks()

        event.Skip()

    def on_close(self, event):
        self.parent.background_tab_selected = False
        self.parent.peak_fitting_tab_selected = False
        self.parent.show_hide_vlines()
        self.parent.deselect_all_peaks()
        self.Destroy()



class CustomComboBox(wx.ComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.green_items = []

    def SetGreenItems(self, items):
        self.green_items = items

    def GetGreenItems(self):
        return self.green_items

    def OnDrawItem(self, dc, rect, item, flags):
        if flags & wx.CONTROL_SELECTED:
            dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
            dc.SetBrush(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT), wx.BRUSHSTYLE_SOLID))
        else:
            dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
            dc.SetBrush(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW), wx.BRUSHSTYLE_SOLID))

        dc.DrawRectangle(rect)
        text = self.GetString(item)
        if text in self.green_items:
            dc.SetTextForeground(wx.GREEN)
        dc.DrawText(text, rect.x + 3, rect.y + 2)

    def OnMeasureItem(self, item):
        return 24

    def OnSelect(self, event):
        selection = self.GetStringSelection()
        if selection in self.green_items:
            wx.CallAfter(self.SetSelection, self.GetSelection())
        else:
            event.Skip()