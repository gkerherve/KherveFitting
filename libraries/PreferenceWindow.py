import wx
import json


class PreferenceWindow(wx.Frame):
    def __init__(self, parent):
        # super().__init__(parent, title="Preferences")
        super().__init__(parent, style=wx.DEFAULT_FRAME_STYLE & ~(
                wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU) | wx.STAY_ON_TOP)
        self.parent = parent

        self.SetTitle("Preferences")
        self.SetSize((600, 650))
        self.SetMinSize((600, 650))
        self.SetMaxSize((600, 650))

        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(2, 2)

        # Plot style
        plot_style_label = wx.StaticText(panel, label="Plot Style:")
        self.plot_style = wx.Choice(panel, choices=["Scatter", "Line"])
        self.plot_style.SetMinSize((100,30))
        sizer.Add(plot_style_label, pos=(0, 0), flag=wx.ALL, border=5)
        sizer.Add(self.plot_style, pos=(0, 1), flag=wx.ALL, border=5)

        # Point size (for scatter)
        self.point_size_label = wx.StaticText(panel, label="Scatter Size:")
        self.point_size_spin = wx.SpinCtrl(panel, value="20", min=1, max=50)
        self.point_size_spin.SetMinSize((100,-1))
        sizer.Add(self.point_size_label, pos=(1, 0), flag=wx.ALL, border=5)
        sizer.Add(self.point_size_spin, pos=(1, 1), flag=wx.ALL, border=5)

        # Scatter marker
        marker_label = wx.StaticText(panel, label="Scatter Marker:")
        self.marker_choice = wx.Choice(panel, choices=["o", "s", "^", "D", "*"])
        self.marker_choice.SetMinSize((100, -1))
        sizer.Add(marker_label, pos=(2, 0), flag=wx.ALL, border=5)
        sizer.Add(self.marker_choice, pos=(2, 1), flag=wx.ALL, border=5)

        # Scatter color
        scatter_color_label = wx.StaticText(panel, label="Scatter Color:")
        self.scatter_color_picker = wx.ColourPickerCtrl(panel)
        self.scatter_color_picker.SetMinSize((100, -1))
        sizer.Add(scatter_color_label, pos=(3, 0), flag=wx.ALL, border=5)
        sizer.Add(self.scatter_color_picker, pos=(3, 1), flag=wx.ALL, border=5)

        # Raw data linestyle
        self.raw_data_linestyle_label = wx.StaticText(panel, label="Raw Data Line:")
        self.raw_data_linestyle = wx.Choice(panel, choices=["-", "--", "-.", ":"])
        self.raw_data_linestyle.SetMinSize((100, -1))
        sizer.Add(self.raw_data_linestyle_label, pos=(5, 0), flag=wx.ALL, border=5)
        sizer.Add(self.raw_data_linestyle, pos=(5, 1), flag=wx.ALL, border=5)

        # Line width (for line)
        self.line_width_label = wx.StaticText(panel, label="Line Width:")
        self.line_width_spin = wx.SpinCtrl(panel, value="1", min=1, max=10)
        self.line_width_spin.SetMinSize((100, -1))
        sizer.Add(self.line_width_label, pos=(6, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_width_spin, pos=(6, 1), flag=wx.ALL, border=5)

        # Line alpha (for line)
        self.line_alpha_label = wx.StaticText(panel, label="Line Alpha:")
        self.line_alpha_spin = wx.SpinCtrlDouble(panel, value="0.7", min=0, max=1, inc=0.1)
        self.line_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.line_alpha_label, pos=(7, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_alpha_spin, pos=(7, 1), flag=wx.ALL, border=5)

        # Line color
        line_color_label = wx.StaticText(panel, label="Line Color:")
        self.line_color_picker = wx.ColourPickerCtrl(panel)
        self.line_color_picker.SetMinSize((100, -1))
        sizer.Add(line_color_label, pos=(8, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_color_picker, pos=(8, 1), flag=wx.ALL, border=5)

        # Residual options
        residual_label = wx.StaticText(panel, label="Residual:")
        self.residual_color_picker = wx.ColourPickerCtrl(panel)
        self.residual_color_picker.SetMinSize((100, -1))
        sizer.Add(residual_label, pos=(10, 0), flag=wx.ALL, border=5)
        sizer.Add(self.residual_color_picker, pos=(10, 1), flag=wx.ALL, border=5)

        self.residual_alpha_label = wx.StaticText(panel, label="Residual Alpha:")
        self.residual_alpha_spin = wx.SpinCtrlDouble(panel, value="0.4", min=0, max=1, inc=0.1)
        self.residual_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.residual_alpha_label, pos=(11, 0), flag=wx.ALL, border=5)
        sizer.Add(self.residual_alpha_spin, pos=(11, 1), flag=wx.ALL, border=5)

        self.residual_linestyle_label = wx.StaticText(panel, label="Residual Line:")
        self.residual_linestyle = wx.Choice(panel, choices=["-", "--", "-.", ":"])
        self.residual_linestyle.SetMinSize((100, -1))
        sizer.Add(self.residual_linestyle_label, pos=(12, 0), flag=wx.ALL, border=5)
        sizer.Add(self.residual_linestyle, pos=(12, 1), flag=wx.ALL, border=5)

        # Save button (moved to the bottom)
        save_button = wx.Button(panel, label="Save")
        save_button.SetMinSize((190, 40))
        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        sizer.Add(save_button, pos=(13, 0), span=(13, 2), flag=wx.ALL | wx.ALIGN_CENTER, border=5)


        # Background options
        self.background_linestyle_label = wx.StaticText(panel, label="Background Line:")
        self.background_linestyle = wx.Choice(panel, choices=["-", "--", "-.", ":"])
        self.background_linestyle.SetMinSize((100, -1))
        sizer.Add(self.background_linestyle_label, pos=(0, 4), flag=wx.ALL, border=5)
        sizer.Add(self.background_linestyle, pos=(0, 5), flag=wx.ALL, border=5)

        self.background_alpha_label = wx.StaticText(panel, label="Background Alpha:")
        self.background_alpha_spin = wx.SpinCtrlDouble(panel, value="0.5", min=0, max=1, inc=0.1)
        self.background_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.background_alpha_label, pos=(1, 4), flag=wx.ALL, border=5)
        sizer.Add(self.background_alpha_spin, pos=(1, 5), flag=wx.ALL, border=5)

        background_label = wx.StaticText(panel, label="Background:")
        self.background_color_picker = wx.ColourPickerCtrl(panel)
        self.background_color_picker.SetMinSize((100, -1))
        sizer.Add(background_label, pos=(2, 4), flag=wx.ALL, border=5)
        sizer.Add(self.background_color_picker, pos=(2, 5), flag=wx.ALL, border=5)

        # Envelope options
        self.envelope_linestyle_label = wx.StaticText(panel, label="Envelope Line:")
        self.envelope_linestyle = wx.Choice(panel, choices=["-", "--", "-.", ":"])
        self.envelope_linestyle.SetMinSize((100, -1))
        sizer.Add(self.envelope_linestyle_label, pos=(4, 4), flag=wx.ALL, border=5)
        sizer.Add(self.envelope_linestyle, pos=(4, 5), flag=wx.ALL, border=5)

        self.envelope_alpha_label = wx.StaticText(panel, label="Envelope Alpha:")
        self.envelope_alpha_spin = wx.SpinCtrlDouble(panel, value="0.6", min=0, max=1, inc=0.1)
        self.envelope_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.envelope_alpha_label, pos=(5, 4), flag=wx.ALL, border=5)
        sizer.Add(self.envelope_alpha_spin, pos=(5, 5), flag=wx.ALL, border=5)

        envelope_label = wx.StaticText(panel, label="Envelope:")
        self.envelope_color_picker = wx.ColourPickerCtrl(panel)
        self.envelope_color_picker.SetMinSize((100, -1))
        sizer.Add(envelope_label, pos=(6, 4), flag=wx.ALL, border=5)
        sizer.Add(self.envelope_color_picker, pos=(6, 5), flag=wx.ALL, border=5)


        # Peak colors
        peak_color_label = wx.StaticText(panel, label="Peak Colors:")
        sizer.Add(peak_color_label, pos=(0, 7), flag=wx.ALL, border=5)

        self.peak_colors = []
        for i in range(15):
            color_picker = wx.ColourPickerCtrl(panel)
            color_picker.SetMinSize((30, 30))
            sizer.Add(color_picker, pos=(i + 1, 7), flag=wx.ALL, border=2)
            self.peak_colors.append(color_picker)

        # Peak alpha
        self.peak_alpha_label = wx.StaticText(panel, label="Peak Alpha:")
        self.peak_alpha_spin = wx.SpinCtrlDouble(panel, value="0.3", min=0, max=1, inc=0.1)
        self.peak_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.peak_alpha_label, pos=(16, 7), flag=wx.ALL, border=5)
        sizer.Add(self.peak_alpha_spin, pos=(17, 7), flag=wx.ALL, border=5)



        panel.SetSizer(sizer)
        self.Centre()

        # Load current settings
        self.LoadSettings()

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

        for i, color_picker in enumerate(self.peak_colors):
            if i < len(self.parent.peak_colors):
                color_picker.SetColour(self.parent.peak_colors[i])

        self.peak_alpha_spin.SetValue(self.parent.peak_alpha)


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

        self.parent.peak_colors = [color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
                                   for color_picker in self.peak_colors]
        self.parent.peak_alpha = self.peak_alpha_spin.GetValue()


        self.parent.save_config()
        self.parent.update_plot_preferences()
        self.Close()