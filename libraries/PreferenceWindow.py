import wx
import json


class PreferenceWindow(wx.Frame):
    def __init__(self, parent):
        # super().__init__(parent, title="Preferences")
        super().__init__(parent, style=wx.DEFAULT_FRAME_STYLE & ~(
                wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU) | wx.STAY_ON_TOP)
        self.parent = parent

        self.SetTitle("Preferences")
        self.SetSize((220, 380))  # Increased height to accommodate new elements
        self.SetMinSize((220, 380))
        self.SetMaxSize((220, 380))

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

        # Line width (for line)
        self.line_width_label = wx.StaticText(panel, label="Line Width:")
        self.line_width_spin = wx.SpinCtrl(panel, value="1", min=1, max=10)
        self.line_width_spin.SetMinSize((100, -1))
        sizer.Add(self.line_width_label, pos=(5, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_width_spin, pos=(5, 1), flag=wx.ALL, border=5)

        # Line alpha (for line)
        self.line_alpha_label = wx.StaticText(panel, label="Line Alpha:")
        self.line_alpha_spin = wx.SpinCtrlDouble(panel, value="0.7", min=0, max=1, inc=0.1)
        self.line_alpha_spin.SetMinSize((100, -1))
        sizer.Add(self.line_alpha_label, pos=(6, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_alpha_spin, pos=(6, 1), flag=wx.ALL, border=5)

        # Line color
        line_color_label = wx.StaticText(panel, label="Line Color:")
        self.line_color_picker = wx.ColourPickerCtrl(panel)
        self.line_color_picker.SetMinSize((100, -1))
        sizer.Add(line_color_label, pos=(7, 0), flag=wx.ALL, border=5)
        sizer.Add(self.line_color_picker, pos=(7, 1), flag=wx.ALL, border=5)

        # Save button
        save_button = wx.Button(panel, label="Save")
        save_button.SetMinSize((190, 40))
        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        sizer.Add(save_button, pos=(8, 0), span=(1, 2), flag=wx.ALL | wx.ALIGN_CENTER, border=5)



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


    def OnSave(self, event):
        self.parent.plot_style = "scatter" if self.plot_style.GetSelection() == 0 else "line"
        self.parent.scatter_size = self.point_size_spin.GetValue()
        self.parent.scatter_marker = self.marker_choice.GetString(self.marker_choice.GetSelection())
        self.parent.scatter_color = self.scatter_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.line_width = self.line_width_spin.GetValue()
        self.parent.line_alpha = self.line_alpha_spin.GetValue()
        self.parent.line_color = self.line_color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)


        self.parent.save_config()
        self.parent.update_plot_preferences()
        self.Close()