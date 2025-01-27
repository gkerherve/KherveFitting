
# CONFIG FILE FOR XPS DATA ------------------------------------
# -------------------------------------------------------------
import pandas as pd
import wx

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
    if sheet_name.startswith('Sheet'):
        wx.MessageBox(f"Sheet names must be core level names (e.g., C1s, O1s).\nInvalid sheet name: '{sheet_name}'",
                      "Invalid Sheet Name", wx.OK | wx.ICON_WARNING)
        return data

    skip_rows = 0

    # Check headers in first row
    headers_df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1)

    # # Check if headers are missing or are numbers
    # if (headers_df.empty or
    #         pd.isna(headers_df.iloc[0, 0]) or
    #         pd.isna(headers_df.iloc[0, 1]) or
    #         isinstance(headers_df.iloc[0, 0], (int, float)) or
    #         isinstance(headers_df.iloc[0, 1], (int, float))):
    #     print(f'Header: {headers_df.iloc[0, 0]}')
    #     wx.MessageBox(
    #         f"Sheet '{sheet_name}' has invalid headers in row 1.\nColumn A should be labeled 'BE' or 'Binding Energy'\nColumn B should be labeled 'Raw Data' or 'Intensity'\nHeaders cannot be numbers.",
    #         "Invalid Headers", wx.OK | wx.ICON_WARNING)
    #     return data

    # Rest of the function remains the same
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)

    if df.empty or df.shape[1] < 2:
        wx.MessageBox(
            f"All sheets must be filled with data and named after their core level (e.g., C1s, O1s).\nSheet '{sheet_name}' is empty or has insufficient columns.",
            "Invalid Sheet", wx.OK | wx.ICON_WARNING)
        return data

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