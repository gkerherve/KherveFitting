# libraries/PlotConfig.py

class PlotConfig:
    def __init__(self):
        self.plot_limits = {}

    def update_plot_limits(self, window, sheet_name=None):
        if sheet_name is None:
            sheet_name = window.sheet_combobox.GetValue()

        if sheet_name in window.Data['Core levels']:
            x_values = window.Data['Core levels'][sheet_name]['B.E.']
            y_values = window.Data['Core levels'][sheet_name]['Raw Data']

            self.plot_limits[sheet_name] = {
                'Xmin': min(x_values),
                'Xmax': max(x_values),
                'Ymin': min(y_values),
                'Ymax': max(y_values) * 1.1  # Add 10% padding to the top
            }

    def adjust_plot_limits(self, window, axis, direction):
        sheet_name = window.sheet_combobox.GetValue()
        if sheet_name not in self.plot_limits:
            self.update_plot_limits(window, sheet_name)

        limits = self.plot_limits[sheet_name]

        if axis in ['high_be', 'low_be']:
            increment = 0.2  # Fixed BE increment of 0.2 eV
            if axis == 'high_be':
                if direction == 'increase':
                    limits['Xmax'] -= increment
                elif direction == 'decrease':
                    limits['Xmax'] += increment
            elif axis == 'low_be':
                if direction == 'increase':
                    limits['Xmin'] += increment
                elif direction == 'decrease':
                    limits['Xmin'] -= increment
        elif axis in ['high_int', 'low_int']:
            max_intensity = max(window.y_values)
            if axis == 'high_int':
                increment = 0.05 * max_intensity
                if direction == 'increase':
                    limits['Ymax'] += increment
                elif direction == 'decrease':
                    limits['Ymax'] = max(limits['Ymax'] - increment, limits['Ymin'])
            elif axis == 'low_int':
                increment = 0.02 * max_intensity
                if direction == 'increase':
                    limits['Ymin'] = min(limits['Ymin'] + increment, limits['Ymax'])
                elif direction == 'decrease':
                    limits['Ymin'] = max(limits['Ymin'] - increment, 0)

        window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
        window.ax.set_ylim(limits['Ymin'], limits['Ymax'])
        window.canvas.draw_idle()

    def resize_plot(self, window):
        sheet_name = window.sheet_combobox.GetValue()
        if sheet_name not in self.plot_limits:
            self.update_plot_limits(window, sheet_name)

        limits = self.plot_limits[sheet_name]
        window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
        window.ax.set_ylim(limits['Ymin'], limits['Ymax'])
        window.canvas.draw_idle()

    def get_plot_limits(self, window, sheet_name=None):
        if sheet_name is None:
            sheet_name = window.sheet_combobox.GetValue()

        if sheet_name not in self.plot_limits:
            self.update_plot_limits(window, sheet_name)

        return self.plot_limits[sheet_name]


    def adjust_limit(self, window, limit_type, increment):
        sheet_name = window.sheet_combobox.GetValue()
        if sheet_name not in self.plot_limits:
            self.update_plot_limits(window, sheet_name)

        limits = self.plot_limits[sheet_name]

        if limit_type in ['Xmin', 'Xmax']:
            limits[limit_type] += increment
        elif limit_type == 'Ymax':
            limits[limit_type] = max(limits[limit_type] + increment, limits['Ymin'])
        elif limit_type == 'Ymin':
            limits[limit_type] = max(limits[limit_type] + increment, 0)

        window.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
        window.ax.set_ylim(limits['Ymin'], limits['Ymax'])
        window.canvas.draw_idle()

    def get_increment(self, window, limit_type):
        sheet_name = window.sheet_combobox.GetValue()
        limits = self.plot_limits[sheet_name]
        if limit_type in ['Xmin', 'Xmax']:
            return 0.2  # Fixed BE increment of 0.2 eV
        else:  # Ymin or Ymax
            return 0.05 * (limits['Ymax'] - limits['Ymin'])

