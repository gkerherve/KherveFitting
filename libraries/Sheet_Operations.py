# sheet_operations.py

import wx
import wx.grid

from libraries.Utilities import _clear_peak_params_grid

def on_sheet_selected(window, event):
    if isinstance(event, str):
        selected_sheet = event
    else:
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

                    # corrected_position = peak_data.get('Position', 0) + window.be_correction
                    # window.peak_params_grid.SetCellValue(row, 2, f"{corrected_position:.2f}")
                    # Use the position directly from peak_data, which is already corrected
                    window.peak_params_grid.SetCellValue(row, 2, f"{peak_data.get('Position', 'N/A'):.2f}")

                    window.peak_params_grid.SetCellValue(row, 3, f"{peak_data.get('Height', 'N/A')}")
                    window.peak_params_grid.SetCellValue(row, 4, f"{peak_data.get('FWHM', 'N/A')}")
                    window.peak_params_grid.SetCellValue(row, 5, f"{peak_data.get('L/G', 'N/A')}")
                    window.peak_params_grid.SetCellValue(row, 6, f"{peak_data.get('Area', 'N/A')}")
                    window.peak_params_grid.SetCellValue(row, 9, f"{peak_data.get('Fitting Model', 'N/A')}")
                    window.peak_params_grid.SetCellValue(row, 10, f"{peak_data.get('Bkg Type', 'N/A')}")
                    window.peak_params_grid.SetCellValue(row, 11, f"{peak_data.get('Bkg Low', 'N/A')}")
                    window.peak_params_grid.SetCellValue(row, 12, f"{peak_data.get('Bkg High', 'N/A')}")
                    window.peak_params_grid.SetCellValue(row, 13, f"{peak_data.get('Bkg Offset Low', 'N/A')}")
                    window.peak_params_grid.SetCellValue(row, 14, f"{peak_data.get('Bkg Offset High', 'N/A')}")

                    # Set constraints if available
                    if 'Constraints' in peak_data:
                        constraints = peak_data['Constraints']
                        window.peak_params_grid.SetCellValue(row + 1, 2, str(constraints.get('Position', 'N/A')))
                        window.peak_params_grid.SetCellValue(row + 1, 3, str(constraints.get('Height', 'N/A')))
                        window.peak_params_grid.SetCellValue(row + 1, 4, str(constraints.get('FWHM', 'N/A')))
                        window.peak_params_grid.SetCellValue(row + 1, 5, str(constraints.get('L/G', 'N/A')))

                    # Set background color for constraint rows
                    for col in range(window.peak_params_grid.GetNumberCols()+1):
                        # window.peak_params_grid.SetCellBackgroundColour(row + 1, col, wx.Colour(230, 230, 230))
                        window.peak_params_grid.SetCellBackgroundColour(row + 1, col-1, wx.Colour(28,204,170))

                # Update background information if available
                if 'Background' in core_level_data:
                    bg_data = core_level_data['Background']
                    window.bg_min_energy = bg_data.get('Bkg Low', None)
                    window.bg_max_energy = bg_data.get('Bkg High', None)
                    window.background_method = bg_data.get('Bkg Type', 'N/A')
                    window.offset_l = bg_data.get('Bkg Offset Low', 0)
                    window.offset_h = bg_data.get('Bkg Offset High', 0)

            else:
                # If no fitting data, ensure the grid is empty
                _clear_peak_params_grid(window)
        else:
            # If no data for this sheet, ensure the grid is empty
            _clear_peak_params_grid(window)

        # Refresh the grid display
        window.peak_params_grid.ForceRefresh()

        # Update the plot
        window.plot_manager.plot_data(window)  # Always plot raw data first
        if window.show_fit and window.peak_params_grid.GetNumberRows() > 0:
            window.clear_and_replot()  # Add fit and residuals if show_fit is True

        window.plot_config.update_plot_limits(window, selected_sheet)
        window.plot_manager.update_legend(window)

        print(f"Selected sheet: {selected_sheet}, Peak count: {window.peak_count}, Show fit: {window.show_fit}")

    # Update the combobox selection if a string was passed directly
    if isinstance(event, str):
        window.sheet_combobox.SetValue(selected_sheet)

