# KherveFitting

## Introduction

KherveFitting is an open-source software developed by Dr. Gwilherm Kerherve at Imperial College London. This application is implemented in Python, leveraging wxPython for the graphical user interface, MatplotLib for data visualization, and NumPy for numerical computations and curve fitting algorithms. KherveFitting is distributed under the MIT License, allowing for broad use, modification, and distribution. When utilizing KherveFitting in academic or research contexts, appropriate citation is requested to acknowledge the software's contribution to your work.

## Keyboard Shortcuts

- **Tab:** Select next peak
- **Q:** Select previous peak
- **Minus (-):** Zoom out
- **Equal (=):** Zoom in
- **Left bracket [:** Decrease intensity
- **Right bracket ]:** Increase intensity
- **Up:** Select previous core level
- **Down:** Select next core level

## Opening Files

KherveFitting can open Excel files (.xlsx) and import/convert VAMAS files (.vms) into Excel format. For best results:

- Place raw data (X,Y) in Columns A and B, starting at row 0
- Use the row offset control in the horizontal toolbar if needed
- Save each core level in a separate sheet named after the core level (e.g., Si2p, Al2p, C1s, O1s)

When reopening a saved fitting, KherveFitting also looks for the corresponding .json file containing peak properties.

## Saving Files

KherveFitting offers three saving options:

1. Save corrected binding energy, background, envelope, residuals, and fitted peak data of the active core level to columns D onwards in the corresponding Excel sheet. Peak fitting properties for all core levels are saved in a JSON file.
2. Save the figure of the active core level to the corresponding Excel sheet and as a PNG file. The resolution (DPI) can be adjusted in the preference window.
3. Save all fitted core level data, including figures, to the Excel file. Peak fitting properties for all core levels are saved in a JSON file.

## Controlling Peaks

- Ensure the Peak Fitting tab in the Peak Fitting window is selected to move peaks
- Left-click and drag the cross to move a peak
- Shift + Left-click to adjust peak width
- Use the middle mouse scroll to change sheets or core levels

## Peak Fitting Window

### Background Tab

Five background types available: Linear, Shirley, Smart, Adaptive Smart, and Tougaard. Drag the red lines on the plot to set the background range.

- **Linear Background:** Y = mx + b
- **Shirley Background:** B(E) = k × ∫<sub>E</sub><sup>E<sub>max</sub></sup> I(E') dE'
- **Tougaard Background:** B(E) = λ(E) × ∫<sub>E</sub><sup>∞</sup> K(E' - E) × [f(E') - B(E')] dE'

Use high BE and low BE controls to apply offsets at range boundaries.

### Peak Fitting Tab

Fit single peaks or doublets. Doublet splitting values are stored in 'split.txt'. Intensity ratios for doublets: 0.5 for p-shell, 0.67 for d-shell, 0.75 for f-shell.

Available fitting models:

- **GL (Gaussian-Lorentzian product):** I(x) = H × [exp(-ln(2) × ((x-x<sub>0</sub>)/σ)<sup>2</sup>) × (1 / (1 + ((x-x<sub>0</sub>)/γ)<sup>2</sup>))]
- **SGL (Gaussian-Lorentzian sum):** I(x) = H × [m × exp(-ln(2) × ((x-x<sub>0</sub>)/σ)<sup>2</sup>) + (1-m) / (1 + ((x-x<sub>0</sub>)/γ)<sup>2</sup>)]
- **Pseudo-Voigt:** I(x) = H × [η × L(x) + (1-η) × G(x)]
- **Voigt:** I(x) = H × ∫<sub>-∞</sub><sup>∞</sup> G(x') × L(x-x') dx'

Where:
H is peak height
x<sub>0</sub> is peak center
σ is Gaussian width
γ is Lorentzian width
m and η are mixing parameters

## Peak Fitting Parameter Grid

Each peak uses two rows: values in the first row, constraints in the second.

Constraint shortcuts:
- 'a', 'b', 'c' → 'A*1', 'B*1', 'C*1' (follow peak A, B, or C)
- 'fi' → 'Fixed' (fix the value)
- '#0.5' → Constrain to ±0.5 eV of the peak position

## Binding Energy Correction

The BE correction button looks for a peak labeled 'C1s C-C' and calculates the difference from 284.8 eV. This correction is applied to all core levels. Fit all data before applying the BE correction.

## Plot Customization

Use the Preferences window to customize plot appearance, including:
- Colors for raw data, background, fitted peaks, and residuals
- Line styles (solid, dashed, dotted)
- Marker types for data points
- Font sizes and styles
- Axis labels and titles

## Toggling Display Elements

Use toggle buttons to show or hide various plot elements:
- Raw data points
- Background line
- Individual fitted peaks
- Overall envelope
- Residuals
- Legend

## Zooming and Navigation

Several tools are available for zooming and navigating the plot:
- Use the zoom in/out buttons or keyboard shortcuts
- Click and drag to create a zoom box
- Double-click to reset the view
- Use the pan tool to move around when zoomed in
- Adjust x and y axis limits manually in the plot settings

## Exporting Results

Export fitted peak parameters, areas, and atomic percentages to a summary table for further analysis. The export function provides:
- Peak positions, heights, and widths
- Integrated areas for each peak
- Relative sensitivity factors (RSF) used
- Calculated atomic percentages
- Options to export as CSV, Excel, or copy to clipboard

## Noise Analysis

Use the Noise Analysis tool to assess data quality and determine the signal-to-noise ratio of your spectra. Features include:
- Automatic noise level detection
- Signal-to-noise ratio calculation
- Noise histogram display
- Options for different noise reduction methods

## License

KherveFitting is distributed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

[Include contact information or links to project pages/repositories]

## Acknowledgements

[Include any acknowledgements or credits]