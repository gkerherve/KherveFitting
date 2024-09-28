
# CONFIG FILE FOR XPS DATA ------------------------------------
# -------------------------------------------------------------
import pandas as pd

def Init_Measurement_Data2(window):
    Data = {
        'FilePath': '',
        'Number of Core levels': 1,
        'Core levels':{
            'Name': '',
            'B.E.': [],
            'Raw Data': [],
            'Background': {
                'Bkg Type': 'Shirley',
                'Bkg Low': 0,
                'Bkg High': 1200,
                'Bkg Offset Low': 0,
                'Bkg Offset High': 0,
                'Bkg x array': [],
                'Bkg y array': []
            },
            'Fitting': {
                'Peak': {
                    'Label':'A',
                    'Position': 529,
                    'Height': 1e3,
                    'FWHM': 1.3,
                    'L/G': 0.3,
                    'Area': '',
                    'at. %': '',
                    'RSF': 1.0,
                    'Fitting Model': 'GL',
                    'Rel. Area': 0,
                    'Sigma': 0.2,
                    'Gamma': 0.3,
                    'Pos. Constraint': '1,1.1e3',
                    'Height Constraint': '1,1e7',
                    'FWHM Constraint': '0.2,3.5',
                    'L/G Constraint': '0.1,0.5',
                    'Area Constraint':'1,1e7',
                    'Sigma Constraint': '0.01:2',
                    'Gamma Constraint': '0.01:1'
                }
            }
        },
        'Results': {
            'Peak': {
                'Label': 'A',
                'Position': 529,
                'Height': 1e3,
                'FWHM': 1.3,
                'L/G': 0.3,
                'Area': '',
                'at. %': '',
                'RSF': 1.0,
                'Fitting Model': 'GL',
                'Rel. Area': 0,
                'Sigma': 0.2,
                'Gamma': 0.3,
                'Pos. Constraint': '0,1e3',
                'Height Constraint': '0,1e7',
                'FWHM Constraint': '0.2,3.5',
                'L/G Constraint': '0.1,0.5',
                'Area Constraint': '1,1e7',
                'Sigma Constraint': '0.01:2',
                'Gamma Constraint': '0.01:1'
            }
        }


    }
    return(Data)

def Init_Measurement_Data(window):
    Data = {
        'FilePath': '',
        'Number of Core levels': 0,
        'Core levels':{
        },
        'Results': {
            'Peak': {
            }
        }
    }
    return(Data)




def add_core_level_Data(data, window, file_path, sheet_name):
    """
    Extracts X and Y data from the given Excel file and adds it to the core level in the data dictionary.
    The sheet_name corresponds to the core level label.
    Uses the window.skip_rows_spinbox value to determine how many rows to skip.
    """
    # Get the number of rows to skip from the spinbox
    skip_rows = window.skip_rows_spinbox.GetValue()

    # Read the specified sheet from the Excel file, skipping the specified number of rows
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)

    # Ensure we have at least two columns
    if df.shape[1] < 2:
        raise ValueError(f"Sheet '{sheet_name}' does not have enough columns after skipping {skip_rows} rows.")

    x_values = df.iloc[:, 0].tolist()
    y_values = df.iloc[:, 1].tolist()

    core_level = {
        'Name': sheet_name,
        'B.E.': df.iloc[:, 0].tolist(),
        'Raw Data': df.iloc[:, 1].tolist(),
        'Background': {
            'Bkg Type': '',
            'Bkg Low': '',
            'Bkg High': '',
            'Bkg Offset Low': '',
            'Bkg Offset High': '',
            'Bkg X': df.iloc[:, 0].tolist(),
            'Bkg Y': df.iloc[:, 1].tolist()
        },
        'Fitting': {}
    }

    data['Core levels'][sheet_name] = core_level
    data['Number of Core levels'] += 1

    print(f"Added core level: {sheet_name}. Total core levels: {data['Number of Core levels']}")
    print(f"Skipped {skip_rows} rows. Data starts from row {skip_rows + 1}")

    return data




def add_peak_to_core_level_Data(data, core_name, peak_data):
    if core_name in data['Core levels']:
        fitting = data['Core levels'][core_name]['Fitting']
        fitting.update(peak_data)
    else:
        print(f"Core level {core_name} does not exist.")