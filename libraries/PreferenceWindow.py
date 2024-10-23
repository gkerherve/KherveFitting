import wx
import json


class PreferenceWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, style=wx.DEFAULT_FRAME_STYLE & ~(
                wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU) | wx.STAY_ON_TOP)
        self.parent = parent

        self.SetTitle("Preferences")
        self.SetSize((490, 680))
        self.SetMinSize((490, 680))
        self.SetMaxSize((490, 680))

        panel = wx.Panel(self)

        # Create notebook
        self.notebook = wx.Notebook(panel)

        # Create tabs
        self.plot_tab = wx.Panel(self.notebook)
        self.instrument_tab = wx.Panel(self.notebook)

        # Add tabs to notebook
        self.notebook.AddPage(self.plot_tab, "Plot")
        self.notebook.AddPage(self.instrument_tab, "Instrument")

        # Set up sizer for the main panel
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.temp_peak_colors = self.parent.peak_colors.copy()

        self.InitUI()
        self.init_instrument_tab()
        self.LoadSettings()

    def init_instrument_tab(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        instruments = list(set(instr for data in self.parent.library_data.values() for instr in data.keys()))
        self.instrument_combo = wx.ComboBox(self.instrument_tab, choices=instruments, style=wx.CB_READONLY)
        self.instrument_combo.Bind(wx.EVT_COMBOBOX, self.on_instrument_change)

        sizer.Add(wx.StaticText(self.instrument_tab, label="Instrument:"), 0, wx.ALL, 5)
        sizer.Add(self.instrument_combo, 0, wx.ALL | wx.EXPAND, 5)

        self.instrument_tab.SetSizer(sizer)

    def on_instrument_change(self, event):
        selected_instrument = self.instrument_combo.GetValue()
        self.parent.update_instrument(selected_instrument)

    def InitUI(self):
        # panel = wx.Panel(self)
        sizer = wx.GridBagSizer(2, 2)
        # self.plot_tab.SetSizer(sizer)

        # Plot style
        plot_style_label = wx.StaticText(self.plot_tab, label="Plot Style:")
        self.plot_style = wx.Choice(self.plot_tab, choices=["Scatter", "Line"])
        self.plot_style.SetMinSize((100,30))
        sizer.Add(plot_style_label, pos=(0, 0), flag=wx.ALL, border=5)
        sizer.Add(self.plot_style, pos=(0, 1), flag=wx.ALL, border=5)

        # Point size (for scatter)
        self.point_size_label = wx.StaticText(self.plot_tab, label="Scatter Size:")
        self.point_size_spin = wx.SpinCtrl(self.plot_tab, value="20", min=1, max=50)
        self.point_size_spin.SetMinSize((100,-1))
        sizer.Add(self.point_size_label, pos=(1, 0), flag=wx.ALL, border=5)
        sizer.Add(self.point_size_spin, pos=(1, 1), flag=wx.ALL, border=5)

        # Scatter marker
        marker_label = wx.StaticText(self.plot_tab, label="Scatter Marker:")
        self.marker_choice = wx.Choice(self.plot_tab, choices=["o", "s", "^", "D", "*"])
        self.marker_choice.SetMinSize((100, -1))
        sizer.Add(marker_label, pos=(2, 0), flag=wx.ALL, border=5)
        sizer.Add(self.marker_choice, pos=(2, 1), flag=wx.ALL, border=5)

        # Scatter color
        scatter_color_label = wx.StaticText(self.plot_tab, label="Scatter Color:")
        self.scatter_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.scatter_color_picker.SetMinSize((100, -1))
        sizer.Add(scatter_color_label, pos=(3, 0), flag=wx.ALL, border=5)
        sizer.Add(self.scatter_color_picker, pos=(3, 1), flag=wx.ALL, border=5)

        # Raw data linestyle
        self.raw_data_linestyle_label = wx.StaticText(self.plot_tab, label="Raw Data Line:")
        self.raw_data_linestyle = wx.Choice(self.plot_tab, choices=["-", "--", "-.", ":"])
        self.raw_data_linestyle.SetMinSize((100, -1))
        sizer.Add(self.raw_data_linestyle_label, pos=(5, 0), flag=wx.ALL, border=5)
        sizer.Add(self.raw_data_linestyle, pos=(5, 1), flag=wx.ALL, border=5)

        # Line width (for line)
        self.line_width_label = wx.StaticText(self.plot_tab, label="Line Width:")
        self.line_width_spin = wx.SpinCtrl(self.plot_tab, value="1", min=1, max=10)
        self.line_width_spin.SetMinSize((100, -1))
        sizer.Add(self.line_width_label, pos=(6, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_width_spin, pos=(6, 1), flag=wx.ALL, border=5)

        # Line alpha (for line)
        self.line_alpha_label = wx.StaticText(self.plot_tab, label="Line Alpha:")
        self.line_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.7", min=0, max=1, inc=0.1)
        self.line_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.line_alpha_label, pos=(7, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_alpha_spin, pos=(7, 1), flag=wx.ALL, border=5)

        # Line color
        line_color_label = wx.StaticText(self.plot_tab, label="Line Color:")
        self.line_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.line_color_picker.SetMinSize((100, -1))
        sizer.Add(line_color_label, pos=(8, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_color_picker, pos=(8, 1), flag=wx.ALL, border=5)

        # Residual options
        self.residual_linestyle_label = wx.StaticText(self.plot_tab, label="Residual Line:")
        self.residual_linestyle = wx.Choice(self.plot_tab, choices=["-", "--", "-.", ":"])
        self.residual_linestyle.SetMinSize((100, -1))
        sizer.Add(self.residual_linestyle_label, pos=(10, 0), flag=wx.ALL, border=5)
        sizer.Add(self.residual_linestyle, pos=(10, 1), flag=wx.ALL, border=5)



        self.residual_alpha_label = wx.StaticText(self.plot_tab, label="Residual Alpha:")
        self.residual_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.4", min=0, max=1, inc=0.1)
        self.residual_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.residual_alpha_label, pos=(11, 0), flag=wx.ALL, border=5)
        sizer.Add(self.residual_alpha_spin, pos=(11, 1), flag=wx.ALL, border=5)

        residual_label = wx.StaticText(self.plot_tab, label="Residual:")
        self.residual_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.residual_color_picker.SetMinSize((100, -1))
        sizer.Add(residual_label, pos=(12, 0), flag=wx.ALL, border=5)
        sizer.Add(self.residual_color_picker, pos=(12, 1), flag=wx.ALL, border=5)

        # Background options
        self.background_linestyle_label = wx.StaticText(self.plot_tab, label="Background Line:")
        self.background_linestyle = wx.Choice(self.plot_tab, choices=["-", "--", "-.", ":"])
        self.background_linestyle.SetMinSize((100, -1))
        sizer.Add(self.background_linestyle_label, pos=(0, 4), flag=wx.ALL, border=5)
        sizer.Add(self.background_linestyle, pos=(0, 5), flag=wx.ALL, border=5)

        self.background_alpha_label = wx.StaticText(self.plot_tab, label="Background Alpha:")
        self.background_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.5", min=0, max=1, inc=0.1)
        self.background_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.background_alpha_label, pos=(1, 4), flag=wx.ALL, border=5)
        sizer.Add(self.background_alpha_spin, pos=(1, 5), flag=wx.ALL, border=5)

        background_label = wx.StaticText(self.plot_tab, label="Background:")
        self.background_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.background_color_picker.SetMinSize((100, -1))
        sizer.Add(background_label, pos=(2, 4), flag=wx.ALL, border=5)
        sizer.Add(self.background_color_picker, pos=(2, 5), flag=wx.ALL, border=5)

        # Envelope options
        self.envelope_linestyle_label = wx.StaticText(self.plot_tab, label="Envelope Line:")
        self.envelope_linestyle = wx.Choice(self.plot_tab, choices=["-", "--", "-.", ":"])
        self.envelope_linestyle.SetMinSize((100, -1))
        sizer.Add(self.envelope_linestyle_label, pos=(4, 4), flag=wx.ALL, border=5)
        sizer.Add(self.envelope_linestyle, pos=(4, 5), flag=wx.ALL, border=5)

        self.envelope_alpha_label = wx.StaticText(self.plot_tab, label="Envelope Alpha:")
        self.envelope_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.6", min=0, max=1, inc=0.1)
        self.envelope_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.envelope_alpha_label, pos=(5, 4), flag=wx.ALL, border=5)
        sizer.Add(self.envelope_alpha_spin, pos=(5, 5), flag=wx.ALL, border=5)

        envelope_label = wx.StaticText(self.plot_tab, label="Envelope:")
        self.envelope_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.envelope_color_picker.SetMinSize((100, -1))
        sizer.Add(envelope_label, pos=(6, 4), flag=wx.ALL, border=5)
        sizer.Add(self.envelope_color_picker, pos=(6, 5), flag=wx.ALL, border=5)

        # Peak number selection
        self.peak_number_spin_label = wx.StaticText(self.plot_tab, label="Peak Number:")
        self.peak_number_spin = wx.SpinCtrl(self.plot_tab, min=1, max=15, initial=1)
        self.peak_number_spin.SetMinSize((100, -1))
        sizer.Add(self.peak_number_spin_label, pos=(8, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_number_spin, pos=(8, 5), flag=wx.ALL, border=5)

        # Peak fill type
        peak_fill_type_label = wx.StaticText(self.plot_tab, label="Peak Fill Type:")
        self.peak_fill_type_combo = wx.ComboBox(self.plot_tab, choices=["Solid Fill", "Hatch"], style=wx.CB_READONLY)
        self.peak_fill_type_combo.SetMinSize((100, -1))
        sizer.Add(peak_fill_type_label, pos=(9, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_fill_type_combo, pos=(9, 5), flag=wx.ALL, border=5)

        # Peak hatch pattern
        peak_hatch_label = wx.StaticText(self.plot_tab, label="Hatch Pattern:")
        self.peak_hatch_combo = wx.ComboBox(self.plot_tab,
                                            choices=["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"],
                                            style=wx.CB_READONLY)
        self.peak_hatch_combo.SetMinSize((100, -1))
        sizer.Add(peak_hatch_label, pos=(10, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_hatch_combo, pos=(10, 5), flag=wx.ALL, border=5)

        hatch_density_label = wx.StaticText(self.plot_tab, label="Hatch Density:")
        self.hatch_density_spin = wx.SpinCtrl(self.plot_tab, value="2", min=1, max=5)
        self.hatch_density_spin.SetMinSize((100, -1))
        sizer.Add(hatch_density_label, pos=(11, 4), flag=wx.ALL, border=5)
        sizer.Add(self.hatch_density_spin, pos=(11, 5), flag=wx.ALL, border=5)

        self.peak_fill_type_combo.Bind(wx.EVT_COMBOBOX, self.OnFillTypeChange)
        self.peak_hatch_combo.Bind(wx.EVT_COMBOBOX, self.OnHatchChange)


        # Peak color selection
        peak_color_label = wx.StaticText(self.plot_tab, label="Peak Color:")
        self.peak_color_picker = wx.ColourPickerCtrl(self.plot_tab)
        self.peak_color_picker.SetMinSize((100, -1))
        sizer.Add(peak_color_label, pos=(12, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_color_picker, pos=(12, 5), flag=wx.ALL, border=5)

        # Peak alpha
        self.peak_alpha_label = wx.StaticText(self.plot_tab, label="Peak Alpha:")
        self.peak_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.3", min=0, max=1, inc=0.1)
        self.peak_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.peak_alpha_label, pos=(13, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_alpha_spin, pos=(13, 5), flag=wx.ALL, border=5)

        # Peak line style
        peak_line_style_label = wx.StaticText(self.plot_tab, label="Peak Line Style:")
        self.peak_line_style_combo = wx.ComboBox(self.plot_tab,
                                                 choices=["No Line", "Black", "Same Color", "Grey", "Yellow"],
                                                 style=wx.CB_READONLY)
        self.peak_line_style_combo.SetMinSize((100, -1))
        sizer.Add(peak_line_style_label, pos=(14, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_line_style_combo, pos=(14, 5), flag=wx.ALL, border=5)

        # Peak line thickness
        self.peak_line_thickness_label = wx.StaticText(self.plot_tab, label="Peak Line Thickness:")
        self.peak_line_thickness_spin = wx.SpinCtrl(self.plot_tab, value="1", min=1, max=5)
        self.peak_line_thickness_spin.SetMinSize((100, -1))
        sizer.Add(self.peak_line_thickness_label, pos=(15, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_line_thickness_spin, pos=(15, 5), flag=wx.ALL, border=5)

        # Peak line alpha
        self.peak_line_alpha_label = wx.StaticText(self.plot_tab, label="Peak Line Alpha:")
        self.peak_line_alpha_spin = wx.SpinCtrlDouble(self.plot_tab, value="0.7", min=0, max=1, inc=0.1)
        self.peak_line_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.peak_line_alpha_label, pos=(16, 4), flag=wx.ALL, border=5)
        sizer.Add(self.peak_line_alpha_spin, pos=(16, 5), flag=wx.ALL, border=5)


        # Peak line pattern
        # peak_line_pattern_label = wx.StaticText(self.plot_tab, label="Peak Line Pattern:")
        # self.peak_line_pattern_combo = wx.ComboBox(self.plot_tab, choices=["-", "--", "-.", ":"],
        # style=wx.CB_READONLY)
        # sizer.Add(peak_line_pattern_label, pos=(12, 4), flag=wx.ALL, border=5)
        # sizer.Add(self.peak_line_pattern_combo, pos=(12, 5), flag=wx.ALL, border=5)

        # Save button (moved to the bottom)
        save_button = wx.Button(self.plot_tab, label="Save")
        save_button.SetMinSize((190, 40))
        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        sizer.Add(save_button, pos=(15, 0), span=(2, 2), flag=wx.ALL | wx.ALIGN_CENTER, border=5)

        # Bind the spin control to update the color picker
        self.peak_number_spin.Bind(wx.EVT_SPINCTRL, self.OnPeakNumberChange)
        self.peak_color_picker.Bind(wx.EVT_COLOURPICKER_CHANGED, self.OnColorChange)

        self.plot_tab.SetSizer(sizer)
        self.Centre()

        # Load current settings
        # self.LoadSettings()

    def LoadSettings(self):
        self.plot_style.SetSelection(0 if self.parent.plot_style == "scatter" else 1)
        self.point_size_spin.SetValue(self.parent.scatter_size)
        self.marker_choice.SetSelection(["o", "s", "^", "D", "*"].index(self.parent.scatter_marker))
        self.scatter_color_picker.SetColour(self.parent.scatter_color)
        self.line_width_spin.SetValue(self.parent.line_width)
        self.line_alpha_spin.SetValue(self.parent.line_alpha)
        self.line_color_picker.SetColour(self.parent.line_color)

        self.background_color_picker.SetColour(self.parent.background_color)
        self.background_alpha_spin.SetValue(self.parent.background_alpha)
        self.background_linestyle.SetSelection(["", "-", "--", "-.", ":"].index(self.parent.background_linestyle))
        self.envelope_color_picker.SetColour(self.parent.envelope_color)
        self.envelope_alpha_spin.SetValue(self.parent.envelope_alpha)
        self.envelope_linestyle.SetSelection(["", "-", "--", "-.", ":"].index(self.parent.envelope_linestyle))
        self.residual_color_picker.SetColour(self.parent.residual_color)
        self.residual_alpha_spin.SetValue(self.parent.residual_alpha)
        self.residual_linestyle.SetSelection(["", "-", "--", "-.", ":"].index(self.parent.residual_linestyle))
        self.raw_data_linestyle.SetSelection(["", "-", "--", "-.", ":"].index(self.parent.raw_data_linestyle))

        self.peak_line_style_combo.SetValue(self.parent.peak_line_style)
        self.peak_line_alpha_spin.SetValue(self.parent.peak_line_alpha)
        self.peak_line_thickness_spin.SetValue(self.parent.peak_line_thickness)
        # self.peak_line_pattern_combo.SetValue(self.parent.peak_line_pattern)
        self.hatch_density_spin.SetValue(self.parent.hatch_density)


        # Load the first peak color
        self.temp_peak_colors = self.parent.peak_colors.copy()
        if self.parent.peak_colors:
            self.peak_color_picker.SetColour(self.parent.peak_colors[0])

        self.peak_alpha_spin.SetValue(self.parent.peak_alpha)

        current_peak = self.peak_number_spin.GetValue() - 1
        self.peak_fill_type_combo.SetValue(self.parent.peak_fill_types[current_peak])
        self.peak_hatch_combo.SetValue(self.parent.peak_hatch_patterns[current_peak])

        if hasattr(self.parent, 'current_instrument'):
            self.instrument_combo.SetValue(self.parent.current_instrument)

    # def OnPeakNumberChange2(self, event):
    #     current_peak = self.peak_number_spin.GetValue() - 1
    #     # Save the current color before changing
    #     self.temp_peak_colors[current_peak] = self.peak_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
    #
    #     # Change to the new peak color
    #     new_peak = event.GetPosition() - 1
    #     if new_peak < len(self.temp_peak_colors):
    #         self.peak_color_picker.SetColour(self.temp_peak_colors[new_peak])
    #     else:
    #         # If it's a new peak, set a default color
    #         self.peak_color_picker.SetColour(wx.Colour(128, 128, 128))  # Gray as default

    def OnPeakNumberChange(self, event):
        current_peak = event.GetPosition() - 1
        if current_peak < len(self.temp_peak_colors):
            color = wx.Colour(self.temp_peak_colors[current_peak])
        else:
            color = wx.Colour(128, 128, 128)
            self.temp_peak_colors.append(color.GetAsString(wx.C2S_HTML_SYNTAX))

        self.peak_color_picker.SetColour(color)

        # Update fill type and hatch pattern for current peak
        self.peak_fill_type_combo.SetValue(self.parent.peak_fill_types[current_peak])
        self.peak_hatch_combo.SetValue(self.parent.peak_hatch_patterns[current_peak])

    def OnFillTypeChange(self, event):
        current_peak = self.peak_number_spin.GetValue() - 1
        new_value = self.peak_fill_type_combo.GetValue()
        self.parent.peak_fill_types[current_peak] = new_value

    def OnHatchChange(self, event):
        current_peak = self.peak_number_spin.GetValue() - 1
        new_value = self.peak_hatch_combo.GetValue()
        self.parent.peak_hatch_patterns[current_peak] = new_value

    def OnColorChange(self, event):
        current_peak = self.peak_number_spin.GetValue() - 1
        new_color = event.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        if current_peak < len(self.temp_peak_colors):
            self.temp_peak_colors[current_peak] = new_color

            # Update hatch pattern based on peak number
            hatch_patterns = ["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]
            self.peak_hatch_combo.SetValue(hatch_patterns[current_peak % len(hatch_patterns)])
        else:
            self.temp_peak_colors.append(new_color)

    def update_plot(self):
        self.parent.update_plot_preferences()
        self.parent.clear_and_replot()

    def OnSave(self, event):
        self.parent.plot_style = "scatter" if self.plot_style.GetSelection() == 0 else "line"
        self.parent.scatter_size = self.point_size_spin.GetValue()
        self.parent.scatter_marker = self.marker_choice.GetString(self.marker_choice.GetSelection())
        self.parent.scatter_color = self.scatter_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.line_width = self.line_width_spin.GetValue()
        self.parent.line_alpha = self.line_alpha_spin.GetValue()
        self.parent.line_color = self.line_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)

        self.parent.background_color = self.background_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.background_alpha = self.background_alpha_spin.GetValue()
        self.parent.background_linestyle = ["", "-", "--", "-.", ":"][self.background_linestyle.GetSelection()]

        self.parent.envelope_color = self.envelope_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.envelope_alpha = self.envelope_alpha_spin.GetValue()
        self.parent.envelope_linestyle = ["", "-", "--", "-.", ":"][self.envelope_linestyle.GetSelection()]

        self.parent.residual_color = self.residual_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.residual_alpha = self.residual_alpha_spin.GetValue()
        self.parent.residual_linestyle = ["", "-", "--", "-.", ":"][self.residual_linestyle.GetSelection()]

        self.parent.raw_data_linestyle = ["", "-", "--", "-.", ":"][self.raw_data_linestyle.GetSelection()]

        self.parent.peak_line_style = self.peak_line_style_combo.GetValue()
        self.parent.peak_line_alpha = self.peak_line_alpha_spin.GetValue()
        self.parent.peak_line_thickness = self.peak_line_thickness_spin.GetValue()
        # self.parent.peak_line_pattern = self.peak_line_pattern_combo.GetValue()

        # Save the current color of the selected peak
        current_peak = self.peak_number_spin.GetValue() - 1
        self.temp_peak_colors[current_peak] = self.peak_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)

        # Update parent's peak_colors with temp_peak_colors
        self.parent.peak_colors = self.temp_peak_colors.copy()

        self.parent.peak_alpha = self.peak_alpha_spin.GetValue()

        self.parent.current_instrument = self.instrument_combo.GetValue()

        current_peak = self.peak_number_spin.GetValue() - 1
        self.parent.peak_fill_types[current_peak] = self.peak_fill_type_combo.GetValue()
        self.parent.peak_hatch_patterns[current_peak] = self.peak_hatch_combo.GetValue()
        self.parent.hatch_density = self.hatch_density_spin.GetValue()

        # Save the configuration
        self.parent.save_config()

        # Update the plot preferences
        self.parent.update_plot_preferences()

        # Close the preference window
        self.Close()

