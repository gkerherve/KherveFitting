import wx

class PreferenceWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Preferences")
        self.parent = parent
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        # Plot style
        plot_style_label = wx.StaticText(panel, label="Plot Style:")
        self.plot_style = wx.Choice(panel, choices=["Scatter", "Line"])
        sizer.Add(plot_style_label, pos=(0, 0), flag=wx.ALL, border=5)
        sizer.Add(self.plot_style, pos=(0, 1), flag=wx.ALL, border=5)

        # Point/Line size
        size_label = wx.StaticText(panel, label="Size:")
        self.size_spin = wx.SpinCtrl(panel, value="1", min=1, max=10)
        sizer.Add(size_label, pos=(1, 0), flag=wx.ALL, border=5)
        sizer.Add(self.size_spin, pos=(1, 1), flag=wx.ALL, border=5)

        # Color
        color_label = wx.StaticText(panel, label="Color:")
        self.color_picker = wx.ColourPickerCtrl(panel)
        sizer.Add(color_label, pos=(2, 0), flag=wx.ALL, border=5)
        sizer.Add(self.color_picker, pos=(2, 1), flag=wx.ALL, border=5)

        # Save button
        save_button = wx.Button(panel, label="Save")
        save_button.Bind(wx.EVT_BUTTON, self.OnSave)
        sizer.Add(save_button, pos=(3, 0), span=(1, 2), flag=wx.ALL|wx.ALIGN_CENTER, border=5)

        panel.SetSizer(sizer)
        self.Centre()

    def OnSave(self, event):
        # Save preferences and update main window
        self.parent.plot_style = "scatter" if self.plot_style.GetSelection() == 0 else "line"
        self.parent.plot_size = self.size_spin.GetValue()
        self.parent.plot_color = self.color_picker.GetColour().GetAsString(wx.C2S_HTML_SYNTAX)
        self.parent.update_plot_preferences()
        self.Close()