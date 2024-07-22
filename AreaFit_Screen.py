import wx
from Functions import plot_background, clear_background
import numpy as np

class BackgroundWindow(wx.Frame):
    def __init__(self, parent, *args, **kw):
        super(BackgroundWindow, self).__init__(parent, *args, **kw, style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.SYSTEM_MENU) | wx.STAY_ON_TOP)
        self.parent = parent
        self.SetTitle("Background Settings")
        self.SetSize((250, 300))
        self.SetMinSize((250, 300))
        self.SetMaxSize((250, 300))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(255, 255, 255))

        # Create controls
        method_label = wx.StaticText(panel, label="Method:")
        self.method_combobox = wx.ComboBox(panel, choices=["Shirley", "Linear", "Smart"], style=wx.CB_READONLY)
        self.method_combobox.SetSelection(0)  # Default to Shirley

        offset_h_label = wx.StaticText(panel, label="Offset (H):")
        self.offset_h_text = wx.TextCtrl(panel, value="0")

        offset_l_label = wx.StaticText(panel, label="Offset (L):")
        self.offset_l_text = wx.TextCtrl(panel, value="0")

        self.offset_h_text.Bind(wx.EVT_TEXT, self.on_offset_changed)
        self.offset_l_text.Bind(wx.EVT_TEXT, self.on_offset_changed)

        background_button = wx.Button(panel, label="Background")
        background_button.Bind(wx.EVT_BUTTON, self.on_background)

        clear_background_button = wx.Button(panel, label="Clear Background")
        clear_background_button.Bind(wx.EVT_BUTTON, self.on_clear_background)

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

        self.Bind(wx.EVT_CLOSE, self.on_close)

        panel.SetSizer(sizer)

    def on_close(self, event):
        self.parent.background_tab_selected = False
        self.Destroy()

    def on_clear_background(self, event):
        # Define the clear background behavior here
        clear_background(self)

    def on_background(self, event):
        try:
            # Define the background behavior here
            plot_background(self.parent)

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

                # Calculate the area
                area = np.trapz(y_values - background, x_values)

                # Print the result to the terminal
                print(f"Area between data and background for {sheet_name}: {area:.2f}")
        except Exception as e:
            print(f"Error calculating background: {str(e)}")

    def on_clear_background(self, event):
        # Define the clear background behavior here
        clear_background(self)

    def on_offset_changed(self, event):
        try:
            offset_h = float(self.offset_h_text.GetValue())
            offset_l = float(self.offset_l_text.GetValue())
            self.parent.set_offset_h(offset_h)
            self.parent.set_offset_l(offset_l)
        except ValueError:
            print("Invalid offset value")
