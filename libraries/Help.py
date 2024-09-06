import wx
import wx.html
import os
import sys



def on_about(self, event):
    info = wx.adv.AboutDialogInfo()
    info.SetName("KherveFitting")
    info.SetVersion("1.0")
    info.SetDescription("An open-source XPS peak fitting software developed by Dr. Gwilherm Kerherve at Imperial College London.")
    info.SetCopyright("(C) 2024 Gwilherm Kerherve")
    info.SetWebSite("https://www.imperial.ac.uk/people/g.kerherve")
    info.AddDeveloper("Dr. Gwilherm Kerherve / g.kerherve@imperial.ac.uk\n William Skinner")
    wx.adv.AboutBox(info)

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
        
        "<p>KherveFitting is an open-source software developed by Dr. Gwilherm Kerherve at Imperial College London. "
        "This application is implemented in Python, using wxPython for the graphical user interface, MatplotLib for "
        "data visualization, NumPy and lmfit for numerical computations and curve fitting algorithms, "
        "Panda for manipulating Excel files. KherveFitting is distributed under the BSD-3 License, allowing for broad "
        "use, modification, and distribution. When using KherveFitting in academic or research contexts, appropriate "
        "citation would be appreciated to acknowledge the software's contribution to your work.</p>"

        "<h3><font color='#006400'>Keyboard Shortcuts</font></h3>"        
        "<ul>"
        "<li><b>Tab:</b> Select next peak</li>"
        "<li><b>Q:</b> Select previous peak</li>"
        "<li><b>Ctrl+Minus (-):</b> Zoom out</li>"
        "<li><b>Ctrl+Equal (=):</b> Zoom in</li>"
        "<li><b>Ctrl+Left bracket [:</b> Select previous core level</li>"
        "<li><b>Ctrl+Right bracket ]:</b> Select next core level</li>"
        "<li><b>Ctrl+Up:</b> Increase intensity</li>"
        "<li><b>Ctrl+Down:</b> Decrease intensity</li>"
        "<li><b>Ctrl+Up:</b> Increase intensity</p></li>"        
        "<li><b>Ctrl+Left:</b> Move plot to High BE</p></li>"  
        "<li><b>Ctrl+Right:</b> Move plot to Low BE</p></li>"  
        "<li><b>SHIFT+Left:</b> Decrease High BE</p></li>"  
        "<li><b>SHIFT+Right:</b> Increase High BE</p></li>"  
        "<li><b>Ctrl+Z:</b> Undo up to 30 events</p></li>"  
        "<li><b>Ctrl+Y:</b> Redo</p></li>"  
        "<li><b>Ctrl+S:</b> Save. Only works on the grid and not on the figure canvas</p></li>"  
        "<li><b>Ctrl+P:</b> Open peak fitting window</p></li>"  
        "<li><b>Ctrl+A:</b> Open Area window</p></li>"  
        "<li><b>Ctrl+K:</b> Show Keyboard shortcut</p></li>"  
        "<h3><font color='#006400'>Opening Files</font></h3>"        
        
        "<p>KherveFitting can open Excel files (.xlsx) and import/convert VAMAS files (.vms), AVG files and Avantage "
        "files  into Excel format.  For best results: "
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

def show_shortcuts(parent):
    shortcuts_html = """
    <html>
    <body style="font-size: 10px; line-height: 1;">
    <h3 style="margin-bottom: 1px;">Keyboard Shortcuts</h3>
    <div style="margin-top: 0;">
    <p style="margin: 2px 0;"><b>Tab:</b> Select next peak</p>
    <p style="margin: 2px 0;"><b>Q:</b> Select previous peak</p>
    <p style="margin: 2px 0;"><b>Ctrl+Minus (-):</b> Zoom out</p>
    <p style="margin: 2px 0;"><b>Ctrl+Equal (=):</b> Zoom in</p>
    <p style="margin: 2px 0;"><b>Ctrl+Left bracket [:</b> Select previous core level</p>
    <p style="margin: 2px 0;"><b>Ctrl+Right bracket ]:</b> Select next core level</p>
    <p style="margin: 2px 0;"><b>Ctrl+Up:</b> Increase intensity</p>
    <p style="margin: 2px 0;"><b>Ctrl+Down:</b> Decrease intensity</p>
    <p style="margin: 2px 0;"><b>Ctrl+Left:</b> Move plot to High BE</p>
    <p style="margin: 2px 0;"><b>Ctrl+Right:</b> Move plot to Low BE</p>
    <p style="margin: 2px 0;"><b>SHIFT+Left:</b> Decrease High BE</p>
    <p style="margin: 2px 0;"><b>SHIFT+Right:</b> Increase High BE</p>
    <p style="margin: 2px 0;"><b>Ctrl+Z:</b> Undo up to 30 events</p>
    <p style="margin: 2px 0;"><b>Ctrl+Y:</b> Redo</p>
    <p style="margin: 2px 0;"><b>Ctrl+S:</b> Save. Only works on the grid and not on the figure canvas</p>
    <p style="margin: 2px 0;"><b>Ctrl+P:</b> Open peak fitting window</p>
    <p style="margin: 2px 0;"><b>Ctrl+A:</b> Open Area window</p>
    <p style="margin: 2px 0;"><b>Ctrl+K:</b> Show Keyboard shortcut</p>
    </div>
    </body>
    </html>
    """

    dlg = wx.Dialog(parent, title="List of Shortcuts", size=(400, 680), style=wx.DEFAULT_DIALOG_STYLE |
                                                                              wx.RESIZE_BORDER)
    html_win = wx.html.HtmlWindow(dlg)
    html_win.SetPage(shortcuts_html)

    # btn = wx.Button(dlg, wx.ID_OK, "Close")
    # btn.Bind(wx.EVT_BUTTON, lambda event: dlg.EndModal(wx.ID_OK))

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(html_win, 1, wx.EXPAND | wx.ALL, 1)
    # sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.ALL, 5)

    dlg.SetSizer(sizer)
    # dlg.ShowModal()
    dlg.Show()