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
        "<h2><font color='#66CC66'>KherveFitting Help</font></h2>"
        
        "<p>KherveFitting is an open-source software developed by Dr. Gwilherm Kerherve at Imperial College London. This application is implemented in Python, leveraging wxPython for the graphical user interface, MatplotLib for data visualization, and NumPy for numerical computations and curve fitting algorithms. KherveFitting is distributed under the MIT License, allowing for broad use, modification, and distribution. When utilizing KherveFitting in academic or research contexts, appropriate citation is requested to acknowledge the software's contribution to your work.</p>"

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
        f"<img src='{os.path.join(image_path, 'file_saving.png')}' alt='File Saving'>"
        "<p>KherveFitting offers three saving options:</p>"
        "<ol>"
        "<li>Save corrected binding energy, background, envelope, residuals, and fitted peak data of the active core level to columns D onwards in the corresponding Excel sheet. Peak fitting properties for all core levels are saved in a JSON file.</li>"
        "<li>Save the figure of the active core level to the corresponding Excel sheet and as a PNG file. The resolution (DPI) can be adjusted in the preference window.</li>"
        "<li>Save all fitted core level data, including figures, to the Excel file. Peak fitting properties for all core levels are saved in a JSON file.</li>"
        "</ol>"

        "<h3><font color='#006400'>Controlling Peaks</font></h3>"
        f"<img src='{os.path.join(image_path, 'peak_control.png')}' alt='Peak Control'>"
        "<ul>"
        "<li>Ensure the Peak Fitting tab in the Peak Fitting window is selected to move peaks</li>"
        "<li>Left-click and drag the cross to move a peak</li>"
        "<li>Shift + Left-click to adjust peak width</li>"
        "<li>Use the middle mouse scroll to change sheets or core levels</li>"
        "</ul>"

        "<h3><font color='#006400'>Peak Fitting Window</font></h3>"
        f"<img src='{os.path.join(image_path, 'peak_fitting_window.png')}' alt='Peak Fitting Window'>"
        "<h4>Background Tab</h4>"
        "<p>Five background types available: Linear, Shirley, Smart, Adaptive Smart, and Tougaard. Drag the red lines on the plot to set the background range.</p>"
        "<ul>"
        "<li><b>Linear Background:</b><br>"
        "<pre>Y = mx + b</pre>"
        "where m is the slope and b is the y-intercept</li>"
        "<li><b>Shirley Background:</b><br>"
        "<pre>B(E) = k × ∫<sub>E</sub><sup>E<sub>max</sub></sup> I(E') dE'</pre>"
        "where k is a constant and I(E') is the spectrum intensity</li>"
        "<li><b>Tougaard Background:</b><br>"
        "<pre>B(E) = λ(E) × ∫<sub>E</sub><sup>∞</sup> K(E' - E) × [f(E') - B(E')] dE'</pre>"
        "where λ(E) is the inelastic mean free path and K(E) is the loss function</li>"
        "</ul>"
        "<p>Use high BE and low BE controls to apply offsets at range boundaries.</p>"

        "<h4>Peak Fitting Tab</h4>"
        "<p>Fit single peaks or doublets. Doublet splitting values are stored in 'split.txt'. Intensity ratios for doublets: 0.5 for p-shell, 0.67 for d-shell, 0.75 for f-shell.</p>"
        "<p>Available fitting models:</p>"
        "<ul>"
        "<li><b>GL (Gaussian-Lorentzian product):</b><br>"
        "<pre>I(x) = H × [exp(-ln(2) × ((x-x<sub>0</sub>)/σ)<sup>2</sup>) × (1 / (1 + ((x-x<sub>0</sub>)/γ)<sup>2</sup>))]</pre></li>"
        "<li><b>SGL (Gaussian-Lorentzian sum):</b><br>"
        "<pre>I(x) = H × [m × exp(-ln(2) × ((x-x<sub>0</sub>)/σ)<sup>2</sup>) + (1-m) / (1 + ((x-x<sub>0</sub>)/γ)<sup>2</sup>)]</pre></li>"
        "<li><b>Pseudo-Voigt:</b><br>"
        "<pre>I(x) = H × [η × L(x) + (1-η) × G(x)]</pre>"
        "where L(x) is Lorentzian and G(x) is Gaussian</li>"
        "<li><b>Voigt:</b><br>"
        "<pre>I(x) = H × ∫<sub>-∞</sub><sup>∞</sup> G(x') × L(x-x') dx'</pre>"
        "convolution of Gaussian and Lorentzian</li>"
        "</ul>"
        "<p>Where:<br>"
        "H is peak height<br>"
        "x<sub>0</sub> is peak center<br>"
        "σ is Gaussian width<br>"
        "γ is Lorentzian width<br>"
        "m and η are mixing parameters</p>"
    
        "<h3><font color='#006400'>Peak Fitting Parameter Grid</font></h3>"
        f"<img src='{os.path.join(image_path, 'parameter_grid.png')}' alt='Parameter Grid'>"
        "<p>Each peak uses two rows: values in the first row, constraints in the second.</p>"
        "<p>Constraint shortcuts:</p>"
        "<ul>"
        "<li>'a', 'b', 'c' → 'A*1', 'B*1', 'C*1' (follow peak A, B, or C)</li>"
        "<li>'fi' → 'Fixed' (fix the value)</li>"
        "<li>'#0.5' → Constrain to ±0.5 eV of the peak position</li>"
        "</ul>"

        "<h3><font color='#006400'>Binding Energy Correction</font></h3>"
        f"<img src='{os.path.join(image_path, 'BEcorrections.png')}' alt='BE Correction icon'>"
        "<p>The BE correction button looks for a peak labeled 'C1s C-C' and calculates the difference from 284.8 eV. This correction is applied to all core levels. Fit all data before applying the BE correction.</p>"

        "<h3><font color='#006400'>Plot Customization</font></h3>"
        f"<img src='{os.path.join(image_path, 'plot_customization.png')}' alt='Plot Customization'>"
        "<p>Use the Preferences window to customize plot appearance, including:</p>"
        "<ul>"
        "<li>Colors for raw data, background, fitted peaks, and residuals</li>"
        "<li>Line styles (solid, dashed, dotted)</li>"
        "<li>Marker types for data points</li>"
        "<li>Font sizes and styles</li>"
        "<li>Axis labels and titles</li>"
        "</ul>"

        "<h3><font color='#006400'>Toggling Display Elements</font></h3>"
        f"<img src='{os.path.join(image_path, 'toggle_elements.png')}' alt='Toggle Elements'>"
        "<p>Use toggle buttons to show or hide various plot elements:</p>"
        "<ul>"
        "<li>Raw data points</li>"
        "<li>Background line</li>"
        "<li>Individual fitted peaks</li>"
        "<li>Overall envelope</li>"
        "<li>Residuals</li>"
        "<li>Legend</li>"
        "</ul>"

        "<h3><font color='#006400'>Zooming and Navigation</font></h3>"
        f"<img src='{os.path.join(image_path, 'zoom_navigation.png')}' alt='Zoom and Navigation'>"
        "<p>Several tools are available for zooming and navigating the plot:</p>"
        "<ul>"
        "<li>Use the zoom in/out buttons or keyboard shortcuts</li>"
        "<li>Click and drag to create a zoom box</li>"
        "<li>Double-click to reset the view</li>"
        "<li>Use the pan tool to move around when zoomed in</li>"
        "<li>Adjust x and y axis limits manually in the plot settings</li>"
        "</ul>"

        "<h3><font color='#006400'>Exporting Results</font></h3>"
        f"<img src='{os.path.join(image_path, 'export_results.png')}' alt='Export Results'>"
        "<p>Export fitted peak parameters, areas, and atomic percentages to a summary table for further analysis. The export function provides:"
        "<ul>"
        "<li>Peak positions, heights, and widths</li>"
        "<li>Integrated areas for each peak</li>"
        "<li>Relative sensitivity factors (RSF) used</li>"
        "<li>Calculated atomic percentages</li>"
        "<li>Options to export as CSV, Excel, or copy to clipboard</li>"
        "</ul>"
        "</p>"

        "<h3><font color='#006400'>Noise Analysis</font></h3>"
        f"<img src='{os.path.join(image_path, 'noise_analysis.png')}' alt='Noise Analysis'>"
        "<p>Use the Noise Analysis tool to assess data quality and determine the signal-to-noise ratio of your spectra. Features include:"
        "<ul>"
        "<li>Automatic noise level detection</li>"
        "<li>Signal-to-noise ratio calculation</li>"
        "<li>Noise histogram display</li>"
        "<li>Options for different noise reduction methods</li>"
        "</ul>"
        "</p>"

        "</body>"
    )


    help_dialog = wx.Dialog(parent, title="Quick Help", size=(650, 650),
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