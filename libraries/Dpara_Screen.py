import wx
import numpy as np
from libraries.Peak_Functions import OtherCalc


class DParameterWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="D-Parameter Measurement",
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX))
        self.parent = parent
        self.SetSize((400, 400))

        panel = wx.Panel(self)

        # Parameters Box
        param_box = wx.StaticBox(panel, label="Parameters")
        param_sizer = wx.StaticBoxSizer(param_box, wx.VERTICAL)

        # Smooth Width
        smooth_sizer = wx.BoxSizer(wx.HORIZONTAL)
        smooth_label = wx.StaticText(panel, label="Smooth Width")
        self.smooth_spin = wx.SpinCtrlDouble(panel, value="7.0", min=0.1, max=10.0, inc=0.1)
        smooth_sizer.Add(smooth_label, 0, wx.ALL | wx.CENTER, 5)
        smooth_sizer.Add(self.smooth_spin, 0, wx.ALL, 5)

        # Pre-Smooth Passes
        pre_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pre_label = wx.StaticText(panel, label="Pre-Smooth Passes")
        self.pre_spin = wx.SpinCtrl(panel, value="2", min=0, max=10)
        pre_sizer.Add(pre_label, 0, wx.ALL | wx.CENTER, 5)
        pre_sizer.Add(self.pre_spin, 0, wx.ALL, 5)

        # Differentiation Width
        diff_sizer = wx.BoxSizer(wx.HORIZONTAL)
        diff_label = wx.StaticText(panel, label="Differentiation Width eV")
        self.diff_spin = wx.SpinCtrlDouble(panel, value="1.0", min=0.1, max=10.0, inc=0.1)
        diff_sizer.Add(diff_label, 0, wx.ALL | wx.CENTER, 5)
        diff_sizer.Add(self.diff_spin, 0, wx.ALL, 5)

        # Post-Smooth Passes
        post_sizer = wx.BoxSizer(wx.HORIZONTAL)
        post_label = wx.StaticText(panel, label="Post-Smooth Passes")
        self.post_spin = wx.SpinCtrl(panel, value="1", min=0, max=10)
        post_sizer.Add(post_label, 0, wx.ALL | wx.CENTER, 5)
        post_sizer.Add(self.post_spin, 0, wx.ALL, 5)

        # Smooth Algorithm Box
        algo_box = wx.StaticBox(panel, label="Smooth Algorithm")
        algo_sizer = wx.StaticBoxSizer(algo_box, wx.VERTICAL)

        algorithms = ["Gaussian", "Savitsky-Golay", "Moving Average", "Wiener", "None"]
        self.algo_radio = wx.RadioBox(panel, choices=algorithms, style=wx.RA_VERTICAL)
        algo_sizer.Add(self.algo_radio, 0, wx.ALL, 5)

        # D-Parameter Value Box
        d_box = wx.StaticBox(panel, label="D-Parameter Value")
        d_sizer = wx.StaticBoxSizer(d_box, wx.HORIZONTAL)

        self.auto_calc = wx.CheckBox(panel, label="Auto-Calculate")
        self.d_value = wx.TextCtrl(panel, value="0")
        self.d_unit = wx.StaticText(panel, label="eV")

        d_sizer.Add(self.auto_calc, 0, wx.ALL, 5)
        d_sizer.Add(self.d_value, 0, wx.ALL, 5)
        d_sizer.Add(self.d_unit, 0, wx.ALL | wx.CENTER, 5)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        defaults_btn = wx.Button(panel, label="Defaults")
        calc_btn = wx.Button(panel, label="Calculate")
        ok_btn = wx.Button(panel, label="OK")
        cancel_btn = wx.Button(panel, label="Cancel")

        btn_sizer.Add(defaults_btn, 0, wx.ALL, 5)
        btn_sizer.Add(calc_btn, 0, wx.ALL, 5)
        btn_sizer.Add(ok_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)

        # Bind events
        calc_btn.Bind(wx.EVT_BUTTON, self.on_calculate)
        defaults_btn.Bind(wx.EVT_BUTTON, self.on_defaults)
        ok_btn.Bind(wx.EVT_BUTTON, self.on_ok)
        cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)

        # Main sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        param_sizer.Add(smooth_sizer, 0, wx.ALL, 5)
        param_sizer.Add(pre_sizer, 0, wx.ALL, 5)
        param_sizer.Add(diff_sizer, 0, wx.ALL, 5)
        param_sizer.Add(post_sizer, 0, wx.ALL, 5)

        h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        h_sizer.Add(param_sizer, 0, wx.ALL, 5)
        h_sizer.Add(algo_sizer, 0, wx.ALL, 5)

        main_sizer.Add(h_sizer, 0, wx.ALL, 5)
        main_sizer.Add(d_sizer, 0, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        panel.SetSizer(main_sizer)

    def on_calculate(self, event):
        x_values = self.parent.x_values
        y_values = self.parent.y_values
        sheet_name = self.parent.sheet_combobox.GetValue()

        # Clear previous derivative plots
        for line in self.parent.ax.lines:
            if line.get_label() == 'Derivative':
                line.remove()

        # Remove previous D-parameter rows if they exist
        for row in range(self.parent.peak_params_grid.GetNumberRows() - 1, -1, -1):
            if self.parent.peak_params_grid.GetCellValue(row, 13) == "D-parameter":
                self.parent.peak_params_grid.DeleteRows(row, 2)

        algorithm = self.algo_radio.GetString(self.algo_radio.GetSelection())
        normalized_deriv = OtherCalc.smooth_and_differentiate(
            x_values,
            y_values,
            self.smooth_spin.GetValue(),
            self.pre_spin.GetValue(),
            self.diff_spin.GetValue(),
            self.post_spin.GetValue(),
            algorithm
        )

        min_idx = np.argmin(normalized_deriv)
        max_idx = np.argmax(normalized_deriv)
        x_min = x_values[min_idx]
        x_max = x_values[max_idx]
        center = (x_max + x_min) / 2
        d_param = abs(x_max - x_min)

        # Update D-value display
        self.d_value.SetValue(f"{d_param:.2f}")

        # Add new rows
        row = self.parent.peak_params_grid.GetNumberRows()
        self.parent.peak_params_grid.AppendRows(2)

        # Update grid values
        self.parent.peak_params_grid.SetCellValue(row, 0, chr(65 + row // 2))
        self.parent.peak_params_grid.SetCellValue(row, 1, "D-parameter")
        self.parent.peak_params_grid.SetCellValue(row, 2, f"{center:.2f}")
        self.parent.peak_params_grid.SetCellValue(row, 4, f"{d_param:.2f}")
        self.parent.peak_params_grid.SetCellValue(row, 7, f"{self.pre_spin.GetValue():.2f}")
        self.parent.peak_params_grid.SetCellValue(row, 8, f"{self.post_spin.GetValue():.2f}")
        self.parent.peak_params_grid.SetCellValue(row, 9, f"{self.smooth_spin.GetValue():.2f}")
        self.parent.peak_params_grid.SetCellValue(row, 5, f"{self.diff_spin.GetValue():.2f}")
        self.parent.peak_params_grid.SetCellValue(row, 13, "D-parameter")

        # Update Data dictionary
        if 'Fitting' not in self.parent.Data['Core levels'][sheet_name]:
            self.parent.Data['Core levels'][sheet_name]['Fitting'] = {}
        if 'Peaks' not in self.parent.Data['Core levels'][sheet_name]['Fitting']:
            self.parent.Data['Core levels'][sheet_name]['Fitting']['Peaks'] = {}

        peak_data = {
            'Position': center,
            'FWHM': d_param,
            'Sigma': self.pre_spin.GetValue(),
            'Gamma': self.post_spin.GetValue(),
            'Skew': self.smooth_spin.GetValue(),
            'L/G': self.diff_spin.GetValue(),
            'Fitting Model': 'D-parameter',
            'Derivative': normalized_deriv.tolist()  # Store derivative for replotting
        }

        self.parent.Data['Core levels'][sheet_name]['Fitting']['Peaks']['D-parameter'] = peak_data

        # Update plot
        self.parent.ax.plot(x_values, normalized_deriv, '--', color='red', label='Derivative')
        self.parent.canvas.draw_idle()

    def on_defaults(self, event):
        self.smooth_spin.SetValue(7.0)
        self.pre_spin.SetValue(2)
        self.diff_spin.SetValue(1.0)
        self.post_spin.SetValue(1)
        self.algo_radio.SetSelection(0)

    def on_ok(self, event):
        self.Close()

    def on_cancel(self, event):
        self.Close()