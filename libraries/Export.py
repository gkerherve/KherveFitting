import wx
import numpy as np
from Functions import load_rsf_data


def export_results(window):
    """
    Export peak fitting results to the results grid and update window.Data.

    This function processes the peak parameters from the peak_params_grid,
    calculates areas and other relevant values, and exports them to the
    results_grid. It also updates the window.Data structure with the
    exported results.

    Parameters:
    window : The main application window containing all necessary attributes and methods.

    Returns:
    None

    Side effects:
    - Modifies window.results_grid
    - Updates window.Data['Results']
    - Binds events to window.results_grid
    """
    # Load RSF data
    rsf_dict = load_rsf_data("RSF.txt")

    current_rows = window.results_grid.GetNumberRows()
    start_row = current_rows  # Preserve existing data

    # Ensure necessary columns exist in the results grid
    _ensure_results_grid_columns(window)

    # Initialize variables for atomic percent calculations
    peak_data = []

    sheet_name = window.sheet_combobox.GetValue()

    # Clear existing results
    window.Data['Results']['Peak'] = {}

    num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows

    for i in range(num_peaks):
        row = i * 2  # Each peak uses two rows in the grid

        # Extract peak parameters
        peak_params = _extract_peak_parameters(window, row, rsf_dict)

        # Get the fitting model for this specific peak
        fitting_model = window.peak_params_grid.GetCellValue(row, 11)  # Assuming column 9 is the Fitting Model

        # Calculate area and related values
        area, normalized_area, rel_area = _calculate_peak_areas(peak_params, fitting_model)

        # Store peak data for atomic percent calculation
        peak_data.append((peak_params['name'], peak_params['position'], peak_params['height'],
                          peak_params['fwhm'], peak_params['lg_ratio'], area, peak_params['rsf'], normalized_area))

        # Update results grid
        _update_results_grid(window, start_row + i, peak_params, area, rel_area, fitting_model)

        # Update window.Data structure
        _update_data_structure(window, sheet_name, i, peak_params, area, rel_area, fitting_model)

    window.results_grid.ForceRefresh()  # Refresh the grid to update the new cells

    # Bind events
    _bind_grid_events(window)

    # Calculate atomic percentages for checked elements
    window.update_atomic_percentages()


def _ensure_results_grid_columns(window):
    """Ensure that all necessary columns exist in the results grid."""
    if window.results_grid.GetNumberCols() < 11:
        window.results_grid.AppendCols(2)
        window.results_grid.SetColLabelValue(9, "Fitting Model")
        window.results_grid.SetColLabelValue(10, "Rel. Area")


def _extract_peak_parameters(window, row, rsf_dict):
    """Extract peak parameters from the peak_params_grid."""
    peak_name = window.peak_params_grid.GetCellValue(row, 1)  # Label
    core_level = ''.join(filter(str.isalnum, peak_name.split()[0]))

    # Remove spin-orbit coupling designation for RSF lookup
    base_core_level = core_level.rstrip('1234567890/')

    rsf = rsf_dict.get(base_core_level, 1.0)

    # Adjust RSF for doublets
    if '3d5/2' in peak_name:
        rsf *= 6 / 10
    elif '3d3/2' in peak_name:
        rsf *= 4 / 10
    elif '2p3/2' in peak_name:
        rsf *= 4 / 6
    elif '2p1/2' in peak_name:
        rsf *= 2 / 6
    elif '4f7/2' in peak_name:
        rsf *= 8 / 14
    elif '4f5/2' in peak_name:
        rsf *= 6 / 14

    return {
        'name': peak_name,
        'position': float(window.peak_params_grid.GetCellValue(row, 2)),
        'height': float(window.peak_params_grid.GetCellValue(row, 3)),
        'fwhm': float(window.peak_params_grid.GetCellValue(row, 4)),
        'lg_ratio': float(window.peak_params_grid.GetCellValue(row, 5)),
        'rsf': rsf_dict.get(core_level, 1.0),
        'constraints': {
            'position': window.peak_params_grid.GetCellValue(row + 1, 2),
            'height': window.peak_params_grid.GetCellValue(row + 1, 3),
            'fwhm': window.peak_params_grid.GetCellValue(row + 1, 4),
            'lg_ratio': window.peak_params_grid.GetCellValue(row + 1, 5)
        }
    }


def _calculate_peak_areas(peak_params, fitting_model):
    """Calculate area, normalized area, and relative area for a peak."""
    height = peak_params['height']
    fwhm = peak_params['fwhm']

    if fitting_model == "Voigt":
        # Area calculation for Voigt profile
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        area = height * sigma * np.sqrt(2 * np.pi)
    elif fitting_model == "Pseudo-Voigt":
        # Area calculation for Pseudo-Voigt profile
        area = height * fwhm * np.pi / 2
    elif fitting_model in ["GL", "SGL", "Unfitted"]:
        # Area calculation for Gaussian-Lorentzian profiles
        area = height * fwhm * np.sqrt(np.pi / (4 * np.log(2)))
    else:
        raise ValueError(f"Unknown fitting model: {fitting_model}")

    normalized_area = area / peak_params['rsf']
    rel_area = area / peak_params['rsf']

    return round(area, 2), round(normalized_area, 2), round(rel_area, 2)


def _update_results_grid(window, row, peak_params, area, rel_area, fitting_model):
    """Update a row in the results grid with peak data."""
    window.results_grid.AppendRows(1)
    window.results_grid.SetCellValue(row, 0, peak_params['name'])
    window.results_grid.SetCellValue(row, 1, f"{peak_params['position']:.2f}")
    window.results_grid.SetCellValue(row, 2, f"{peak_params['height']:.2f}")
    window.results_grid.SetCellValue(row, 3, f"{peak_params['fwhm']:.2f}")
    window.results_grid.SetCellValue(row, 4, f"{peak_params['lg_ratio']:.2f}")
    window.results_grid.SetCellValue(row, 5, f"{area:.2f}")
    window.results_grid.SetCellValue(row, 6, "0.00")  # Initial atomic percentage
    _set_checkbox(window, row, 7)
    window.results_grid.SetCellValue(row, 8, f"{peak_params['rsf']:.2f}")
    window.results_grid.SetCellValue(row, 9, fitting_model)
    window.results_grid.SetCellValue(row, 10, f"{rel_area:.2f}")
    window.results_grid.SetCellValue(row, 11, "")  # Tail E
    window.results_grid.SetCellValue(row, 12, "")  # Tail M
    window.results_grid.SetCellValue(row, 13, f"{window.bg_min_energy:.2f}" if window.bg_min_energy is not None else "")
    window.results_grid.SetCellValue(row, 14, f"{window.bg_max_energy:.2f}" if window.bg_max_energy is not None else "")
    window.results_grid.SetCellValue(row, 15, window.sheet_combobox.GetValue())
    _set_constraints(window, row, peak_params['constraints'])


def _set_checkbox(window, row, col):
    """Set up a checkbox in the specified grid cell."""
    window.results_grid.SetCellRenderer(row, col, wx.grid.GridCellBoolRenderer())
    window.results_grid.SetCellEditor(row, col, wx.grid.GridCellBoolEditor())
    window.results_grid.SetCellValue(row, col, '0')  # Initialize checkbox as unchecked


def _set_constraints(window, row, constraints):
    """Set constraint values in the results grid."""
    window.results_grid.SetCellValue(row, 16, constraints['position'])
    window.results_grid.SetCellValue(row, 17, constraints['height'])
    window.results_grid.SetCellValue(row, 18, constraints['fwhm'])
    window.results_grid.SetCellValue(row, 19, constraints['lg_ratio'])


def _update_data_structure(window, sheet_name, peak_index, peak_params, area, rel_area, fitting_model):
    """Update the window.Data structure with peak results."""
    peak_data = {
        'Label': chr(65 + peak_index),  # A, B, C, ...
        'Name': peak_params['name'],
        'Position': peak_params['position'],
        'Height': peak_params['height'],
        'FWHM': peak_params['fwhm'],
        'L/G': peak_params['lg_ratio'],
        'Area': area,
        'at. %': 0.00,  # Initial atomic percentage
        'RSF': peak_params['rsf'],
        'Fitting Model': fitting_model,
        'Rel. Area': rel_area,
        'Tail E': "",
        'Tail M': "",
        'Bkg Low': window.bg_min_energy,
        'Bkg High': window.bg_max_energy,
        'Sheetname': sheet_name,
        'Pos. Constraint': peak_params['constraints']['position'],
        'Height Constraint': peak_params['constraints']['height'],
        'FWHM Constraint': peak_params['constraints']['fwhm'],
        'L/G Constraint': peak_params['constraints']['lg_ratio']
    }
    window.Data['Results']['Peak'][chr(65 + peak_index)] = peak_data


def _bind_grid_events(window):
    """Bind necessary events to the results grid."""
    window.results_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, window.on_checkbox_update)
    window.results_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, window.on_cell_changed)