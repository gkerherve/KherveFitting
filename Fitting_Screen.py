

import wx
from Functions import fit_peaks, remove_peak, plot_background, clear_background

class FittingWindow(wx.Frame):
    def __init__(self, parent, *args, **kw):
        super().__init__(parent, *args, **kw, style=wx.DEFAULT_FRAME_STYLE & ~(
                wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU) | wx.STAY_ON_TOP)
        self.parent = parent  # Store reference to MainFrame

        self.SetTitle("Peak Fitting")
        self.SetSize((270, 400))  # Increased height to accommodate new elements
        self.SetMinSize((270, 400))
        self.SetMaxSize((270, 400))

        self.init_ui()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def init_ui(self):
        """Initialize the user interface components."""
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))

        notebook = wx.Notebook(panel)

        self.init_background_tab(notebook)
        self.init_fitting_tab(notebook)

        # Set notebook as the main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(main_sizer)

        # Bind the tab change event
        notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)

        # Set initial state (background tab is selected by default)
        self.parent.background_tab_selected = True
        self.parent.peak_fitting_tab_selected = False
        self.parent.show_hide_vlines()
        self.parent.deselect_all_peaks()

    def init_background_tab(self, notebook):
        """Initialize the background tab in the notebook."""
        background_panel = wx.Panel(notebook)
        background_sizer = wx.GridBagSizer(hgap=0, vgap=0)

        method_label = wx.StaticText(background_panel, label="Method:")
        self.method_combobox = wx.ComboBox(background_panel, choices=["Shirley", "Linear", "Smart"],
                                           style=wx.CB_READONLY)
        method_index = self.method_combobox.FindString(self.parent.background_method)
        self.method_combobox.SetSelection(method_index)
        self.method_combobox.Bind(wx.EVT_COMBOBOX, self.on_bkg_method_change)

        offset_h_label = wx.StaticText(background_panel, label="Offset (H):")
        self.offset_h_text = wx.TextCtrl(background_panel, value=str(self.parent.offset_h))
        self.offset_h_text.Bind(wx.EVT_TEXT, self.on_offset_h_change)

        offset_l_label = wx.StaticText(background_panel, label="Offset (L):")
        self.offset_l_text = wx.TextCtrl(background_panel, value=str(self.parent.offset_l))
        self.offset_l_text.Bind(wx.EVT_TEXT, self.on_offset_l_change)

        background_button = wx.Button(background_panel, label="Background")
        background_button.SetMinSize((110, 40))
        background_button.Bind(wx.EVT_BUTTON, self.on_background)

        clear_background_button = wx.Button(background_panel, label="Clear Background")
        clear_background_button.SetMinSize((110, 40))
        clear_background_button.Bind(wx.EVT_BUTTON, self.on_clear_background)

        # Layout Background Tab
        background_sizer.Add(method_label, pos=(0, 0), span=(1, 2), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(self.method_combobox, pos=(1, 0), span=(1, 2), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(offset_h_label, pos=(2, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        background_sizer.Add(self.offset_h_text, pos=(2, 1), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(offset_l_label, pos=(3, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        background_sizer.Add(self.offset_l_text, pos=(3, 1), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(background_button, pos=(4, 0), flag=wx.ALL | wx.EXPAND, border=5)
        background_sizer.Add(clear_background_button, pos=(4, 1), flag=wx.ALL | wx.EXPAND, border=5)

        background_panel.SetSizer(background_sizer)
        notebook.AddPage(background_panel, "Background")

    def init_fitting_tab(self, notebook):
        """Initialize the peak fitting tab in the notebook."""
        fitting_panel = wx.Panel(notebook)
        fitting_sizer = wx.GridBagSizer(hgap=0, vgap=0)

        # self.model_combobox = wx.ComboBox(fitting_panel, choices=["Pseudo-Voigt", "Pseudo-Voigt_2", "Pseudo-Voigt_3", "GL", "SGL", "Voigt"], style=wx.CB_READONLY)
        self.model_combobox = wx.ComboBox(fitting_panel,
                                          choices=["Pseudo-Voigt", "GL", "SGL",
                                                   "Voigt"], style=wx.CB_READONLY)
        model_index = self.model_combobox.FindString(self.parent.selected_fitting_method)
        self.model_combobox.SetSelection(model_index)
        self.model_combobox.Bind(wx.EVT_COMBOBOX, self.on_method_change)

        self.max_iter_spin = wx.SpinCtrl(fitting_panel, value=str(self.parent.max_iterations), min=1, max=10000)
        self.max_iter_spin.Bind(wx.EVT_SPINCTRL, self.on_max_iter_change)

        self.r_squared_label = wx.StaticText(fitting_panel, label="R²:")
        self.r_squared_text = wx.TextCtrl(fitting_panel, style=wx.TE_READONLY)
        self.chi_squared_label = wx.StaticText(fitting_panel, label="Chi²:")
        self.chi_squared_text = wx.TextCtrl(fitting_panel, style=wx.TE_READONLY)
        self.red_chi_squared_label = wx.StaticText(fitting_panel, label="Red. Chi²:")
        self.red_chi_squared_text = wx.TextCtrl(fitting_panel, style=wx.TE_READONLY)

        add_peak_button = wx.Button(fitting_panel, label="Add Peak")
        add_peak_button.SetMinSize((60, 40))
        add_peak_button.Bind(wx.EVT_BUTTON, self.on_add_peak)

        remove_peak_button = wx.Button(fitting_panel, label="Remove Peak")
        remove_peak_button.SetMinSize((60, 40))
        remove_peak_button.Bind(wx.EVT_BUTTON, self.on_remove_peak)

        fit_button = wx.Button(fitting_panel, label="Fit")
        fit_button.SetMinSize((110, 40))
        fit_button.Bind(wx.EVT_BUTTON, self.on_fit_peaks)

        stop_button = wx.Button(fitting_panel, label="Stop")
        stop_button.SetMinSize((60, 40))
        stop_button.Bind(wx.EVT_BUTTON, self.on_stop)

        export_button = wx.Button(fitting_panel, label="Export")
        export_button.SetMinSize((60, 40))
        export_button.Bind(wx.EVT_BUTTON, self.on_export_results)

        # Layout Peak Fitting Tab
        fitting_sizer.Add(wx.StaticText(fitting_panel, label="Fitting Model:"), pos=(0, 0),
                          flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.model_combobox, pos=(0, 1), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(wx.StaticText(fitting_panel, label="Max Iteration:"), pos=(1, 0),
                          flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.max_iter_spin, pos=(1, 1), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_sizer.Add(self.r_squared_label, pos=(2, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.r_squared_text, pos=(2, 1), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(self.chi_squared_label, pos=(3, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.chi_squared_text, pos=(3, 1), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(self.red_chi_squared_label, pos=(4, 0), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)
        fitting_sizer.Add(self.red_chi_squared_text, pos=(4, 1), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_sizer.Add(add_peak_button, pos=(5, 0), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(remove_peak_button, pos=(5, 1), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_sizer.Add(fit_button, pos=(6, 0), flag=wx.ALL | wx.EXPAND, border=5)
        fitting_sizer.Add(stop_button, pos=(6, 1), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_sizer.Add(export_button, pos=(7, 0), span=(1, 2), flag=wx.ALL | wx.EXPAND, border=5)

        fitting_panel.SetSizer(fitting_sizer)
        notebook.AddPage(fitting_panel, "Peak Fitting")

    def on_max_iter_change(self, event):
        self.parent.set_max_iterations(self.max_iter_spin.GetValue())

    def on_method_change(self, event):
        new_method = self.model_combobox.GetValue()
        self.parent.set_fitting_method(new_method)

    def on_bkg_method_change(self, event):
        new_method = self.method_combobox.GetValue()
        self.parent.set_background_method(new_method)

    def on_add_peak(self, event):
        self.parent.add_peak_params()

    def on_remove_peak(self, event):
        remove_peak(self.parent)

    def on_fit_peaks(self, event):
        result = fit_peaks(self.parent, self.parent.peak_params_grid)
        if result:
            r_squared, chi_squared, red_chi_squared = result
            self.update_fit_indicators(r_squared, chi_squared, red_chi_squared)
        else:
            print("Fitting failed or was cancelled.")

    def update_fit_indicators(self, r_squared, chi_squared, red_chi_squared):
        self.r_squared_text.SetValue(f"{r_squared:.5f}")
        self.chi_squared_text.SetValue(f"{chi_squared:.2f}")
        self.red_chi_squared_text.SetValue(f"{red_chi_squared:.2f}")
        self.Layout()

    def on_export_results(self, event):
        self.parent.export_results()

    def on_stop(self, event):
        # Define the stop behavior here
        pass

    def on_background(self, event):
        plot_background(self.parent)

    def on_clear_background(self, event):
        clear_background(self.parent)

    def on_offset_h_change(self, event):
        offset_h_value = self.offset_h_text.GetValue()
        self.parent.set_offset_h(offset_h_value)

    def on_offset_l_change(self, event):
        offset_l_value = self.offset_l_text.GetValue()
        self.parent.set_offset_l(offset_l_value)

    def on_tab_change(self, event):
        selected_page = event.GetSelection()
        self.parent.background_tab_selected = (selected_page == 0)  # Assuming background is the first tab
        self.parent.peak_fitting_tab_selected = (selected_page == 1)
        self.parent.show_hide_vlines()

        # If switching to background tab, ensure vLines can be created
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
