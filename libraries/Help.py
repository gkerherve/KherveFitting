import wx
import wx.html
import os
import sys

def show_quick_help(parent):
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, use the bundle's directory
        application_path = sys._MEIPASS
    else:
        # If the application is run as a script, use the script's directory
        application_path = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(application_path, "Images")

    help_text = (
        "<body bgcolor='#FFFFE0'>"
        "<h2><font color='#66CC66'>Quick Help</font></h2>"

        "<h3><font color='#006400'>Keyboard Shortcuts</font></h3>"
        "<ul>"
        "<li><b>Tab:</b> Select next peak</li>"
        "<li><b>Q:</b> Select previous peak</li>"
        "<li><b>Minus (-):</b> Zoom out</li>"
        "<li><b>Equal (=):</b> Zoom in</li>"
        "<li><b>Left bracket [:</b> Decrease intensity</li>"
        "<li><b>Right bracket ]:</b> Increase intensity</li>"
        "<li><b>Up:</b> Select previous core level</li>"
        "<li><b>Down:</b> Select next core level</li>"
        "</ul>"

        "<h3><font color='#006400'>Opening Files</font></h3>"
        "<p>KherveFitting can open Excel files (.xlsx) and import/convert VAMAS files (.vms) into Excel format. For best results:"
        "<ul>"
        "<li>Place raw data (X,Y) in Columns A and B, starting at row 0</li>"
        "<li>Use the row offset control in the horizontal toolbar if needed</li>"
        "<li>Save each core level in a separate sheet named after the core level (e.g., Si2p, Al2p, C1s, O1s)</li>"
        "</ul>"
        "</p>"
        "<p>When reopening a saved fitting, KherveFitting also looks for the corresponding .json file containing peak properties.</p>"

        "<h3><font color='#006400'>Saving Files</font></h3>"
        "<p>KherveFitting offers three saving options:</p>"
        "<ol>"
        "<li>Save corrected binding energy, background, envelope, residuals, and fitted peak data of the active core level to columns D onwards in the corresponding Excel sheet. Peak fitting properties for all core levels are saved in a JSON file.</li>"
        "<li>Save the figure of the active core level to the corresponding Excel sheet and as a PNG file. The resolution (DPI) can be adjusted in the preference window.</li>"
        "<li>Save all fitted core level data, including figures, to the Excel file. Peak fitting properties for all core levels are saved in a JSON file.</li>"
        "</ol>"

        "<h3><font color='#006400'>Controlling Peaks</font></h3>"
        "<ul>"
        "<li>Ensure the Peak Fitting tab in the Peak Fitting window is selected to move peaks</li>"
        "<li>Left-click and drag the cross to move a peak</li>"
        "<li>Shift + Left-click to adjust peak width</li>"
        "<li>Use the middle mouse scroll to change sheets or core levels</li>"
        "</ul>"

        "<h3><font color='#006400'>Peak Fitting Window</font></h3>"
        "<h4>Background Tab</h4>"
        "<p>Four background types available: Linear, Shirley, Smart, and Adaptive Smart. Drag the red lines on the plot to set the background range.</p>"
        "<ul>"
        "<li><b>Smart Background:</b> Uses linear if intensity decreases, Shirley if it increases</li>"
        "<li><b>Adaptive Smart Background:</b> Starts equal to raw data, can be adapted within selected ranges</li>"
        "</ul>"
        "<p>Use high BE and low BE controls to apply offsets at range boundaries.</p>"

        "<h4>Peak Fitting Tab</h4>"
        "<p>Fit single peaks or doublets. Doublet splitting values are stored in 'split.txt'. Intensity ratios for doublets: 0.5 for p-shell, 0.67 for d-shell, 0.75 for f-shell.</p>"
        "<p>Available fitting models: GL (Gaussian-Lorentzian product), SGL (Gaussian-Lorentzian sum), Pseudo-Voigt, and Voigt.</p>"

        "<h3><font color='#006400'>Peak Fitting Parameter Grid</font></h3>"
        "<p>Each peak uses two rows: values in the first row, constraints in the second.</p>"
        "<p>Constraint shortcuts:</p>"
        "<ul>"
        "<li>'a' or 'b' or 'c' → 'A*1' or 'B*1' or 'C*1' (follow peak A, B, or C)</li>"
        "<li>'fi' → 'Fixed' (fix the value)</li>"
        "<li>'#0.5' → Constrain to ±0.5 eV of the peak position</li>"
        "</ul>"

        "<h3><font color='#006400'>Binding Energy Correction</font></h3>"
        f"<img src='{os.path.join(image_path, 'BEcorrections.png')}' alt='BE Correction icon'>"
        "<p>The BE correction button looks for a peak labeled 'C1s C-C' and calculates the difference from 284.8 eV. This correction is applied to all core levels. Fit all data before applying the BE correction.</p>"

        "<h3><font color='#006400'>Plot Customization</font></h3>"
        "<p>Use the Preferences window to customize plot appearance, including colors, line styles, and marker types.</p>"

        "<h3><font color='#006400'>Exporting Results</font></h3>"
        "<p>Export fitted peak parameters, areas, and atomic percentages to a summary table for further analysis.</p>"

        "<h3><font color='#006400'>Noise Analysis</font></h3>"
        "<p>Use the Noise Analysis tool to assess data quality and determine the signal-to-noise ratio of your spectra.</p>"

        "</body>"
    )


    help_dialog = wx.Dialog(parent, title="Quick Help", size=(400, 600),
                            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
    # help_dialog.SetBackgroundColour(wx.Colour(255, 255, 255))  # Light yellow
    html_window = wx.html.HtmlWindow(help_dialog)
    # html_window.SetBackgroundColour(wx.Colour(255, 255, 224))  # Light yellow
    html_window.SetPage(help_text)

    help_dialog.Show()
    help_dialog.Bind(wx.EVT_CLOSE, lambda evt: help_dialog.Destroy())

    '''
    image_path = os.path.join(application_path, "Images")
    
    '''