# libraries/PlotConfig.py
import matplotlib.widgets as widgets
import matplotlib.pyplot as plt


class PlotConfig:
    def __init__(self):
        self.plot_limits = {}
        self.original_limits = {}  # Store original limits for zoom out

    def update_plot_limits(self, window, sheet_name, x_min=None, x_max=None, y_min=None, y_max=None):
        if sheet_name not in self.plot_limits:
            self.plot_limits[sheet_name] = {}
            self.original_limits[sheet_name] = {}

        limits = self.plot_limits[sheet_name]
        original = self.original_limits[sheet_name]

        # Store original limits if not already stored
        if not original:
            x_values = window.Data['Core levels'][sheet_name]['B.E.']
            y_values = window.Data['Core levels'][sheet_name]['Raw Data']
            original['Xmin'] = min(x_values)
            original['Xmax'] = max(x_values)
            original['Ymin'] = min(y_values)
            original['Ymax'] = max(y_values) * 1.2  # Add 20% padding to the top

        # Update current limits
        if x_min is not None: limits['Xmin'] = x_min
        if x_max is not None: limits['Xmax'] = x_max
        if y_min is not None: limits['Ymin'] = y_min
        if y_max is not None: limits['Ymax'] = y_max

        # If any limit is not set, use the original values
        limits['Xmin'] = limits.get('Xmin', original['Xmin'])
        limits['Xmax'] = limits.get('Xmax', original['Xmax'])
        limits['Ymin'] = limits.get('Ymin', original['Ymin'])
        limits['Ymax'] = limits.get('Ymax', original['Ymax'])

    def reset_plot_limits(self, window, sheet_name):
        if sheet_name in self.original_limits:
            self.plot_limits[sheet_name] = self.original_limits[sheet_name].copy()
        else:
            self.update_plot_limits(window, sheet_name)

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

    # This def is also in PLotManager
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

    def update_after_drag(self, window, sheet_name):
        ax = window.ax
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()

        # Ensure x_min is always less than x_max (because of reversed x-axis)
        x_min, x_max = min(x_min, x_max), max(x_min, x_max)

        if sheet_name not in self.plot_limits:
            self.plot_limits[sheet_name] = {}

        limits = self.plot_limits[sheet_name]
        limits['Xmin'] = x_min
        limits['Xmax'] = x_max
        limits['Ymin'] = y_min
        limits['Ymax'] = y_max

        # Update the actual plot limits
        window.ax.set_xlim(x_max, x_min)  # Reverse X-axis
        window.ax.set_ylim(y_min, y_max)

        print(f"Updated limits after drag: Xmin={x_min:.2f}, Xmax={x_max:.2f}, Ymin={y_min:.2f}, Ymax={y_max:.2f}")



class CustomRectangleSelector(widgets.RectangleSelector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background = None

    def release(self, event):
        super().release(event)
        self.remove_rect()

    def remove_rect(self):
        if self.visible:
            self.visible = False
            self.ax.figure.canvas.draw_idle()

