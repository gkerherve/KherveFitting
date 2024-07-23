# sheet_operations.py

import wx
import wx.grid
from libraries.Plot_Operations import plot_data, clear_and_replot
from libraries.Utilities import _clear_peak_params_grid

def on_sheet_selected2(window, event):
    selected_sheet = window.sheet_combobox.GetValue()
    if selected_sheet:
        # Reinitialize peak count
        window.peak_count = 0

        window.remove_cross_from_peak()

        # Check if there's data for the selected sheet in window.Data
        if selected_sheet in window.Data['Core levels']:
            core_level_data = window.Data['Core levels'][selected_sheet]

            # Check if there's fitting data available
            if 'Fitting' in core_level_data and 'Peaks' in core_level_data['Fitting']:
                peaks = core_level_data['Fitting']['Peaks']

                # Update peak count
                window.peak_count = len(peaks)

                # Adjust the number of rows in the grid
                required_rows = window.peak_count * 2
                current_rows = window.peak_params_grid.GetNumberRows()

                if current_rows < required_rows:
                    window.peak_params_grid.AppendRows(required_rows - current_rows)
                elif current_rows > required_rows:
                    window.peak_params_grid.DeleteRows(required_rows, current_rows - required_rows)

                # Clear existing data in the peak_params_grid
                window.peak_params_grid.ClearGrid()

                # Populate the grid with peak data
                for i, (peak_label, peak_data) in enumerate(peaks.items()):
                    row = i * 2  # Each peak uses two rows

                    # Set peak data
                    window.peak_params_grid.SetCellValue(row, 0, chr(65 + i))  # A, B, C, etc.
                    window.peak_params_grid.SetCellValue(row, 1, peak_label)
                    window.peak_params_grid.SetCellValue(row, 2, f"{peak_data['Position']:.2f}")
                    window.peak_params_grid.SetCellValue(row, 3, f"{peak_data['Height']:.2f}")
                    window.peak_params_grid.SetCellValue(row, 4, f"{peak_data['FWHM']:.2f}")
                    window.peak_params_grid.SetCellValue(row, 5, f"{peak_data['L/G']:.2f}")

                    # Set constraints if available
                    if 'Constraints' in peak_data:
                        constraints = peak_data['Constraints']
                        window.peak_params_grid.SetCellValue(row + 1, 2, str(constraints.get('Position', '')))
                        window.peak_params_grid.SetCellValue(row + 1, 3, str(constraints.get('Height', '')))
                        window.peak_params_grid.SetCellValue(row + 1, 4, str(constraints.get('FWHM', '')))
                        window.peak_params_grid.SetCellValue(row + 1, 5, str(constraints.get('L/G', '')))


                        window.peak_params_grid.SetReadOnly(row + 1, 0)
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 0, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 1, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 2, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 3, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 4, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 5, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 6, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 7, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 8, wx.Colour(230, 230, 230))
            else:
                # If no fitting data, ensure the grid is empty
                _clear_peak_params_grid(window)
        else:
            # If no data for this sheet, ensure the grid is empty
            _clear_peak_params_grid(window)

        # Update the plot
        if window.peak_params_grid.GetNumberRows() > 0:
            # window.update_overall_fit_and_residuals()
            plot_data(window)
            clear_and_replot(window)
            window.plot_config.update_plot_limits(window, selected_sheet)
        else:
            plot_data(window)
            window.plot_config.update_plot_limits(window, selected_sheet)

        # Refresh the grid display
        window.peak_params_grid.ForceRefresh()

        print(f"Selected sheet: {selected_sheet}, Peak count: {window.peak_count}")
        pass

def on_sheet_selected(window, event):
    selected_sheet = window.sheet_combobox.GetValue()
    if selected_sheet:
        # Reinitialize peak count
        window.peak_count = 0

        window.remove_cross_from_peak()

        # Check if there's data for the selected sheet in window.Data
        if selected_sheet in window.Data['Core levels']:
            core_level_data = window.Data['Core levels'][selected_sheet]

            # Check if there's fitting data available
            if 'Fitting' in core_level_data and 'Peaks' in core_level_data['Fitting']:
                peaks = core_level_data['Fitting']['Peaks']

                # Update peak count
                window.peak_count = len(peaks)

                # Adjust the number of rows in the grid
                required_rows = window.peak_count * 2
                current_rows = window.peak_params_grid.GetNumberRows()

                if current_rows < required_rows:
                    window.peak_params_grid.AppendRows(required_rows - current_rows)
                elif current_rows > required_rows:
                    window.peak_params_grid.DeleteRows(required_rows, current_rows - required_rows)

                # Clear existing data in the peak_params_grid
                window.peak_params_grid.ClearGrid()

                # Populate the grid with peak data
                for i, (peak_label, peak_data) in enumerate(peaks.items()):
                    row = i * 2  # Each peak uses two rows

                    # Set peak data
                    window.peak_params_grid.SetCellValue(row, 0, chr(65 + i))  # A, B, C, etc.
                    window.peak_params_grid.SetCellValue(row, 1, peak_label)
                    window.peak_params_grid.SetCellValue(row, 2, f"{peak_data['Position']:.2f}")
                    window.peak_params_grid.SetCellValue(row, 3, f"{peak_data['Height']:.2f}")
                    window.peak_params_grid.SetCellValue(row, 4, f"{peak_data['FWHM']:.2f}")
                    window.peak_params_grid.SetCellValue(row, 5, f"{peak_data['L/G']:.2f}")

                    # Set constraints if available
                    if 'Constraints' in peak_data:
                        constraints = peak_data['Constraints']
                        window.peak_params_grid.SetCellValue(row + 1, 2, str(constraints.get('Position', '')))
                        window.peak_params_grid.SetCellValue(row + 1, 3, str(constraints.get('Height', '')))
                        window.peak_params_grid.SetCellValue(row + 1, 4, str(constraints.get('FWHM', '')))
                        window.peak_params_grid.SetCellValue(row + 1, 5, str(constraints.get('L/G', '')))

                        window.peak_params_grid.SetReadOnly(row + 1, 0)
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 0, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 1, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 2, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 3, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 4, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 5, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 6, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 7, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, 8, wx.Colour(230, 230, 230))
            else:
                # If no fitting data, ensure the grid is empty
                _clear_peak_params_grid(window)
        else:
            # If no data for this sheet, ensure the grid is empty
            _clear_peak_params_grid(window)

        # Update the plot
        plot_data(window)  # Always plot raw data first
        if window.show_fit and window.peak_params_grid.GetNumberRows() > 0:
            clear_and_replot(window)  # Add fit and residuals if show_fit is True

        window.plot_config.update_plot_limits(window, selected_sheet)

        # Refresh the grid display
        window.peak_params_grid.ForceRefresh()

        print(f"Selected sheet: {selected_sheet}, Peak count: {window.peak_count}, Show fit: {window.show_fit}")
