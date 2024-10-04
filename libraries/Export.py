import wx
import numpy as np
import re
from libraries.Utilities import load_rsf_data
from libraries.Save import save_state


def export_results(window):
    """
    Export peak fitting results to the results grid and update window.Data.
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

    num_peaks = window.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows

    for i in range(num_peaks):
        row = i * 2  # Each peak uses two rows in the grid

        # Extract peak parameters
        peak_params = _extract_peak_parameters(window, row, rsf_dict)

        # Get the fitting model for this specific peak
        fitting_model = window.peak_params_grid.GetCellValue(row, 12)

        # Calculate area and related values
        area, normalized_area, rel_area = _calculate_peak_areas(window, peak_params, row)

        # Store peak data for atomic percent calculation
        peak_data.append((peak_params['name'], peak_params['position'], peak_params['height'],
                          peak_params['fwhm'], peak_params['lg_ratio'], area, peak_params['rsf'], normalized_area))

        # Update window.Data structure and get the peak_label
        peak_label = _update_data_structure(window, sheet_name, i, peak_params, area, rel_area, fitting_model)

        # Update or add to results grid
        if start_row + i >= current_rows:
            window.results_grid.AppendRows(1)

        _update_results_grid(window, start_row + i, peak_params, area, rel_area, fitting_model, peak_label)

    # After updating all rows, force a refresh and update checkboxes
    window.results_grid.ForceRefresh()
    window.update_checkboxes_from_data()

    # Bind events
    _bind_grid_events(window)

    # Calculate atomic percentages for checked elements
    window.update_atomic_percentages()

    # undo and redo
    save_state(window)



def _ensure_results_grid_columns(window):
    """Ensure that all necessary columns exist in the results grid."""
    if window.results_grid.GetNumberCols() < 11:
        window.results_grid.AppendCols(2)
        window.results_grid.SetColLabelValue(9, "Fitting Model")
        window.results_grid.SetColLabelValue(10, "Rel. Area")


def safe_float(value, default=0.0):
    try:
        return float(value) if value.strip() else default
    except (ValueError, AttributeError):
        return default

def _extract_peak_parameters(window, row, rsf_dict):
    peak_name = window.peak_params_grid.GetCellValue(row, 1)  # Label

    # Use regex to extract element and orbital information
    match = re.match(r'([A-Z][a-z]*)(\d+[spdf])(?:(\d+/\d+))?', peak_name)
    if match:
        element, orbital, suborbital = match.groups()
        core_level = element + orbital
    else:
        core_level = ''.join(filter(str.isalnum, peak_name.split()[0]))

    rsf = rsf_dict.get(core_level, 1.0)

    # Adjust RSF for doublets
    if suborbital:
        if orbital.endswith('p'):
            total_electrons = 6
            if suborbital == '3/2':
                rsf *= 4 / total_electrons
            elif suborbital == '1/2':
                rsf *= 2 / total_electrons
        elif orbital.endswith('d'):
            total_electrons = 10
            if suborbital == '5/2':
                rsf *= 6 / total_electrons
            elif suborbital == '3/2':
                rsf *= 4 / total_electrons
        elif orbital.endswith('f'):
            total_electrons = 14
            if suborbital == '7/2':
                rsf *= 8 / total_electrons
            elif suborbital == '5/2':
                rsf *= 6 / total_electrons

    return {
        'name': peak_name,
        'position': safe_float(window.peak_params_grid.GetCellValue(row, 2)),
        'height': safe_float(window.peak_params_grid.GetCellValue(row, 3)),
        'fwhm': safe_float(window.peak_params_grid.GetCellValue(row, 4)),
        'lg_ratio': safe_float(window.peak_params_grid.GetCellValue(row, 5)),
        'rsf': rsf,
        'area': safe_float(window.peak_params_grid.GetCellValue(row, 6)),
        'sigma': safe_float(window.peak_params_grid.GetCellValue(row, 7)),
        'gamma': safe_float(window.peak_params_grid.GetCellValue(row, 8)),
        'constraints': {
            'position': window.peak_params_grid.GetCellValue(row + 1, 2),
            'height': window.peak_params_grid.GetCellValue(row + 1, 3),
            'fwhm': window.peak_params_grid.GetCellValue(row + 1, 4),
            'lg_ratio': window.peak_params_grid.GetCellValue(row + 1, 5),
            'area': window.peak_params_grid.GetCellValue(row+1, 6),
            'sigma': window.peak_params_grid.GetCellValue(row+1, 7),
            'gamma': window.peak_params_grid.GetCellValue(row+1, 8)
        }
    }


def _calculate_peak_areas2(peak_params, fitting_model):
    """Calculate area, normalized area, and relative area for a peak."""
    height = peak_params['height']
    fwhm = peak_params['fwhm']

    if fitting_model == "Voigt (Area, L/G, \u03C3)":
        # Area calculation for Voigt profile
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        area = height * sigma * np.sqrt(2 * np.pi)
    elif fitting_model == "Pseudo-Voigt (Area)":
        # Area calculation for Pseudo-Voigt profile
        area = height * fwhm * np.pi / 2
    elif fitting_model == "LA (Area, \u03C3, \u03B3)":
        # For LA model, area is directly provided
        area = peak_params['area']
        # If area is not provided in peak_params, you can calculate it numerically:
        # if 'area' not in peak_params:
        #     sigma = peak_params['sigma']
        #     gamma = peak_params['gamma']
        #     x_range = np.linspace(peak_params['center'] - 5*fwhm, peak_params['center'] + 5*fwhm, 1000)
        #     y_values = PeakFunctions.LA(x_range, peak_params['center'], height, fwhm, sigma, gamma)
        #     area = np.trapz(y_values, x_range)
    elif fitting_model in ["GL (Height)", "SGL (Height)", "Unfitted"]:
        # Area calculation for Gaussian-Lorentzian profiles
        area = height * fwhm * np.sqrt(np.pi / (4 * np.log(2)))
    elif fitting_model in ["GL (Area)", "SGL (Area)"]:
        # For area-based models, area is already provided
        pass  # We don't need to calculate area as it's already given
    else:
        raise ValueError(f"Unknown fitting model: {fitting_model}")

    normalized_area = area / peak_params['rsf']
    rel_area = area / peak_params['rsf']

    return round(area, 2), round(normalized_area, 2), round(rel_area, 2)

def _calculate_peak_areas(window, peak_params, row):
    area = float(window.peak_params_grid.GetCellValue(row, 6))  # Assuming area is in column 6
    rsf = peak_params['rsf']
    normalized_area = area / rsf
    rel_area = normalized_area
    return round(area, 2), round(normalized_area, 2), round(rel_area, 2)

def _update_results_grid(window, row, peak_params, area, rel_area, fitting_model, peak_label):
    """Update a row in the results grid with peak data."""
    window.results_grid.SetCellValue(row, 0, f"{peak_params['name']}")  # Keep the original peak name
    window.results_grid.SetCellValue(row, 1, f"{peak_params['position']:.2f}")
    window.results_grid.SetCellValue(row, 2, f"{peak_params['height']:.2f}")
    window.results_grid.SetCellValue(row, 3, f"{peak_params['fwhm']:.2f}")
    window.results_grid.SetCellValue(row, 4, f"{peak_params['lg_ratio']:.2f}")
    window.results_grid.SetCellValue(row, 5, f"{area:.2f}")
    window.results_grid.SetCellValue(row, 6, "0.00")  # Initial atomic percentage

    checkbox_state = window.Data['Results']['Peak'][peak_label].get('Checkbox', '0')
    _set_checkbox(window, row, 7, checkbox_state)

    window.results_grid.SetCellValue(row, 8, f"{peak_params['rsf']:.2f}")
    window.results_grid.SetCellValue(row, 9, fitting_model)
    window.results_grid.SetCellValue(row, 10, f"{rel_area:.2f}")
    window.results_grid.SetCellValue(row, 11, "")  # Sigma
    window.results_grid.SetCellValue(row, 12, "")  # Gamma
    window.results_grid.SetCellValue(row, 13, f"{window.bg_min_energy:.2f}" if window.bg_min_energy is not None else "")
    window.results_grid.SetCellValue(row, 14, f"{window.bg_max_energy:.2f}" if window.bg_max_energy is not None else "")
    window.results_grid.SetCellValue(row, 15, window.sheet_combobox.GetValue())
    _set_constraints(window, row, peak_params['constraints'])

    # Force a refresh of the grid cell to ensure the checkbox is displayed correctly
    window.results_grid.RefreshAttr(row, 7)


def _set_checkbox(window, row, col, state='0'):
    """Set up a checkbox in the specified grid cell."""
    window.results_grid.SetCellRenderer(row, col, wx.grid.GridCellBoolRenderer())
    window.results_grid.SetCellEditor(row, col, wx.grid.GridCellBoolEditor())
    window.results_grid.SetCellValue(row, col, state)
    # window.results_grid.SetCellValue(row, col, '1' if state == '1' else '0')
    window.results_grid.ForceRefresh()

def _set_constraints(window, row, constraints):
    """Set constraint values in the results grid."""
    window.results_grid.SetCellValue(row, 16, constraints['position'])
    window.results_grid.SetCellValue(row, 17, constraints['height'])
    window.results_grid.SetCellValue(row, 18, constraints['fwhm'])
    window.results_grid.SetCellValue(row, 19, constraints['lg_ratio'])

def _update_data_structure(window, sheet_name, peak_index, peak_params, area, rel_area, fitting_model):
    """Update the window.Data structure with peak results."""
    results = window.Data['Results']['Peak']

    # Find the next available peak number
    existing_peaks = [int(key.split('_')[1]) for key in results.keys() if key.startswith('Peak_')]
    next_peak_number = max(existing_peaks + [-1]) + 1

    peak_label = f"Peak_{next_peak_number}"
    peak_name = peak_params['name']

    # Check if this peak already exists (by name and sheet)
    existing_peak = next((key for key, value in results.items()
                          if value['Name'] == peak_name and value['Sheetname'] == sheet_name), None)

    if existing_peak:
        peak_label = existing_peak

    peak_data = {
        'Label': peak_label,
        'Name': peak_name,
        'Position': peak_params['position'],
        'Height': peak_params['height'],
        'FWHM': peak_params['fwhm'],
        'L/G': peak_params['lg_ratio'],
        'Area': area,
        'at. %': results.get(peak_label, {}).get('at. %', 0.00),  # Preserve existing at. % if available
        'RSF': peak_params['rsf'],
        'Fitting Model': fitting_model,
        'Rel. Area': rel_area,
        'Sigma': peak_params['sigma'],
        'Gamma': peak_params['gamma'],
        'Bkg Low': window.bg_min_energy,
        'Bkg High': window.bg_max_energy,
        'Sheetname': sheet_name,
        'Pos. Constraint': peak_params['constraints']['position'],
        'Height Constraint': peak_params['constraints']['height'],
        'FWHM Constraint': peak_params['constraints']['fwhm'],
        'L/G Constraint': peak_params['constraints']['lg_ratio'],
        'Area Constraint': peak_params['constraints']['area'],
        'Sigma Constraint':peak_params['constraints']['sigma'],
        'Gamma Constraint':peak_params['constraints']['gamma'],
        'Checkbox': results.get(peak_label, {}).get('Checkbox', '0')  # Preserve existing checkbox state if available
    }

    window.Data['Results']['Peak'][peak_label] = peak_data
    return peak_label  # Return the peak label for reference


def _bind_grid_events(window):
    """Bind necessary events to the results grid."""
    window.results_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, window.on_cell_changed)