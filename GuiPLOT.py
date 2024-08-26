# GuiPLOT------------------------------------------------------------------------
# Fitting program create with chatGPT 4o-----------------------------------------

import matplotlib
import matplotlib.widgets as widgets
# LIBRARIES----------------------------------------------------------------------
import wx.grid
import wx.adv
matplotlib.use('WXAgg')  # Use WXAgg backend for wxPython compatibility
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.ticker import ScalarFormatter
# from Functions import *
import lmfit
from libraries.Fitting_Screen import *
from libraries.AreaFit_Screen import *
from libraries.Save import *
from libraries.NoiseAnalysis import NoiseAnalysisWindow
from libraries.ConfigFile import *
from libraries.Export import export_results
from libraries.PlotConfig import PlotConfig
from libraries.Plot_Operations import PlotManager
from libraries.Peak_Functions import PeakFunctions
# from libraries.Peak_Functions import gauss_lorentz, S_gauss_lorentz
from Functions import create_menu, create_statusbar, create_horizontal_toolbar, create_vertical_toolbar
from Functions import toggle_Col_1, update_sheet_names, rename_sheet
from libraries.PreferenceWindow import PreferenceWindow
from libraries.Sheet_Operations import on_sheet_selected
from libraries.Sheet_Operations import CheckboxRenderer
from libraries.SplashScreen import show_splash

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(1600, 700))
        self.SetMinSize((800, 600))
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(255, 255, 255))  # Set background color to white

        # Center the window on the screen
        self.Centre()

        self.Data = Init_Measurement_Data(self)


        # Initial folder path
        self.Working_directory =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")

        self.selected_files = []     # Initialize selected_files variable
        self.selected_indices = []  # Initialize selected_indices variable

        # BKG selected
        self.background_tab_selected = False
        self.peak_fitting_tab_selected = False
        self.fitting_window = None

        self.noise_analysis_window = None
        self.noise_tab_selected = False

        # New attribute to track plot state for showing fit or not
        self.show_fit = True

        # For FWHM calculation
        self.selected_peak_index = 0
        self.initial_fwhm = None
        self.initial_x = None

        self.peak_params = []  # Initialize
        self.peak_count = 0  # To keep track of the number of peaks

        # Dictionary for the X and Y limits
        self.plot_config = PlotConfig()

        self.is_right_panel_hidden = False

        # X axis correction from KE to BE
        self.photons = 1486.67
        self.workfunction = 0

        # Initialize variables for vertical lines and background energy
        self.vline1 = None
        self.vline2 = None
        self.active_vline = None
        self.vline_drag_threshold = 5  # pixels


        self.vline3 = None  # For noise range
        self.vline4 = None  # For noise range
        self.some_threshold = 0.1
        self.bg_min_energy = None
        self.bg_max_energy = None
        self.noise_min_energy = None
        self.noise_max_energy = None

        # Initial max iteration value
        self.max_iterations = 50
        # Initial fitting method
        self.selected_fitting_method = "GL"

        # self.fitting_results_visible = False

        self.background_method = "Shirley"
        self.offset_h = 0
        self.offset_l = 0

        # Initial background method
        self.selected_bkg_method  = "Shirley"


        # Zoom initialisation variables
        self.zoom_mode = False
        self.zoom_rect = None

        # Drag button initialisation
        self.drag_mode = False
        self.drag_tool = None


        # Initialize attributes for background and noise data
        self.background = None
        self.noise_data = None

        self.x_values = None  # To store x values for noise plotting
        self.y_values = None  # To store y values for noise plotting

        # initialise peak fill or not
        self.peak_fill_enabled = True

        # Initialize right_frame to None before creating widgets
        self.right_frame = None
        self.figure = plt.figure()
        self.ax = self.figure.add_subplot(111)  # Create the Matplotlib axes
        self.ax.set_xlabel("Binding Energy (eV)")  # Set x-axis label
        self.ax.set_ylabel("Intensity (CTS)")  # Set y-axis label
        self.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        self.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))

        self.moving_vline = None  # Initialize moving_vline attribute
        self.selected_peak_index = None  # Add this attribute to track selected peak index

        self.be_correction = 0.00

        # Number of column to remove from the excel file
        self.num_fitted_columns = 15

        # Initialize plot preference attributes with default values
        self.plot_style = "scatter"
        self.scatter_size = 20
        self.line_width = 1
        self.line_alpha = 0.7
        self.scatter_color = "#000000"
        self.line_color = "#000000"
        self.scatter_marker = "o"
        self.background_color = "#808080"
        self.background_alpha = 0.5
        self.background_linestyle = "--"
        self.envelope_color = "#0000FF"
        self.envelope_alpha = 0.6
        self.envelope_linestyle = "-"
        self.residual_color = "#00FF00"
        self.residual_alpha = 0.4
        self.residual_linestyle = "-"
        self.raw_data_linestyle = "-"

        self.peak_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF",
                            "#00FFFF", "#800000", "#008000", "#000080", "#808000",
                            "#800080", "#008080", "#C0C0C0", "#808080", "#9B30FF"]
        self.peak_alpha = 0.3


        self.create_widgets()
        create_menu(self)


        create_statusbar(self)


        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.canvas.mpl_connect('scroll_event', self.on_mouse_wheel)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press_global)
        # self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)
        # self.add_cross_to_peak(self.selected_peak_index)

        self.peak_params_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_peak_params_cell_changed)
        self.peak_params_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self.on_peak_params_cell_changed)
        # self.peak_params_grid.Bind(wx.EVT_KEY_DOWN, self.on_grid_key)


    def create_widgets(self):
        # Main sizer
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create the vertical toolbar as a child of the panel
        self.v_toolbar = create_vertical_toolbar(self.panel, self)

        # Content sizer (everything except vertical toolbar)
        content_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Create a splitter window
        self.splitter = wx.SplitterWindow(self.panel, style=wx.SP_LIVE_UPDATE)

        # Right frame for the plot
        self.right_frame = wx.Panel(self.splitter)
        self.right_frame.SetBackgroundColour(wx.Colour(255, 255, 255))
        right_frame_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create the FigureCanvas
        self.canvas = FigureCanvas(self.right_frame, -1, self.figure)
        # self.canvas.mpl_connect("button_press_event", self.on_click)
        plt.tight_layout()
        right_frame_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 0)

        # Initialize plot_manager after self.ax and self.canvas are created
        self.plot_manager = PlotManager(self.ax, self.canvas)

        # Load config if exists
        self.load_config()

        # Update plot manager with loaded or default values
        self.update_plot_preferences()

        # Create a single NavigationToolbar (hidden by default)
        self.navigation_toolbar = NavigationToolbar(self.canvas)
        self.navigation_toolbar.Hide()

        self.right_frame.SetSizer(right_frame_sizer)

        # Create a panel for grids
        grids_panel = wx.Panel(self.splitter)
        grids_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create a frame box for peak fitting parameters
        peak_params_frame_box = wx.StaticBox(grids_panel, label="Peak Fitting Parameters")
        peak_params_sizer = wx.StaticBoxSizer(peak_params_frame_box, wx.VERTICAL)

        self.peak_params_frame = wx.Panel(peak_params_frame_box)
        self.peak_params_frame.SetBackgroundColour(wx.Colour(255, 255, 255))
        peak_params_sizer_inner = wx.BoxSizer(wx.VERTICAL)

        # Initialize the Fit_grid for peak parameters
        self.peak_params_grid = wx.grid.Grid(self.peak_params_frame)
        self.peak_params_grid.CreateGrid(0, 18)
        self.peak_params_grid.SetColLabelValue(0, "ID")
        self.peak_params_grid.SetColLabelValue(1, "Label")
        self.peak_params_grid.SetColLabelValue(2, "Position")
        self.peak_params_grid.SetColLabelValue(3, "Height")
        self.peak_params_grid.SetColLabelValue(4, "FWHM")
        self.peak_params_grid.SetColLabelValue(5, "L/G")
        self.peak_params_grid.SetColLabelValue(6, "Area")
        self.peak_params_grid.SetColLabelValue(7, "Tail E")
        self.peak_params_grid.SetColLabelValue(8, "Tail M")
        self.peak_params_grid.SetColLabelValue(9, "I ratio")
        self.peak_params_grid.SetColLabelValue(10, "A ratio")
        self.peak_params_grid.SetColLabelValue(11, "Split")
        self.peak_params_grid.SetColLabelValue(12, "Fitting Model")
        self.peak_params_grid.SetColLabelValue(13, "Bkg Type")
        self.peak_params_grid.SetColLabelValue(14, "Bkg Low")
        self.peak_params_grid.SetColLabelValue(15, "Bkg High")
        self.peak_params_grid.SetColLabelValue(16, "Bkg Offset Low")
        self.peak_params_grid.SetColLabelValue(17, "Bkg Offset High")

        # Set grid properties
        self.peak_params_grid.SetDefaultRowSize(25)
        self.peak_params_grid.SetDefaultColSize(60)
        self.peak_params_grid.SetLabelBackgroundColour(wx.Colour(255, 255, 255))
        self.peak_params_grid.SetDefaultCellBackgroundColour(self.peak_params_grid.GetLabelBackgroundColour())
        self.peak_params_grid.SetRowLabelSize(25)
        self.peak_params_grid.SetColLabelSize(20)

        # Adjust individual column sizes
        self.peak_params_grid.SetColSize(0, 20)
        self.peak_params_grid.SetColSize(1, 90)
        self.peak_params_grid.SetColSize(2, 80)
        self.peak_params_grid.SetColSize(3, 80)
        self.peak_params_grid.SetColSize(4, 80)
        self.peak_params_grid.SetColSize(5, 50)
        self.peak_params_grid.SetColSize(7, 50)
        self.peak_params_grid.SetColSize(8, 50)
        self.peak_params_grid.SetColSize(12, 100)
        self.peak_params_grid.SetColSize(16, 100)
        self.peak_params_grid.SetColSize(17, 100)

        peak_params_sizer_inner.Add(self.peak_params_grid, 1, wx.EXPAND | wx.ALL, 5)
        self.peak_params_frame.SetSizer(peak_params_sizer_inner)
        peak_params_sizer.Add(self.peak_params_frame, 1, wx.EXPAND | wx.ALL, 5)

        grids_sizer.Add(peak_params_sizer, 1, wx.EXPAND | wx.ALL, 5)

        # Results frame
        results_frame_box = wx.StaticBox(grids_panel, label="Results")
        results_sizer = wx.StaticBoxSizer(results_frame_box, wx.VERTICAL)

        self.results_frame = wx.Panel(results_frame_box)
        results_sizer_inner = wx.BoxSizer(wx.VERTICAL)

        # Create the results Grid
        self.results_grid = wx.grid.Grid(self.results_frame)
        self.results_grid.CreateGrid(0, 23)

        # Set column labels and properties for results grid
        column_labels = ["Peak", "Position", "Height", "FWHM", "L/G", "Area", "at. %", " ", "RSF", "Fitting Model",
                         "Rel. Area", "Tail E", "Tail M", "Bkg Type", "Bkg Low", "Bkg High", "Bkg Offset Low",
                         "Bkg Offset High", "Sheetname", "Pos. Constraint", "Height Constraint", "FWHM Constraint", "L/G Constraint"]
        for i, label in enumerate(column_labels):
            self.results_grid.SetColLabelValue(i, label)

        self.results_grid.SetDefaultRowSize(25)
        self.results_grid.SetDefaultColSize(60)
        self.results_grid.SetRowLabelSize(25)
        self.results_grid.SetColLabelSize(20)
        self.results_grid.SetLabelBackgroundColour(wx.Colour(255, 255, 255))
        self.results_grid.SetDefaultCellBackgroundColour(self.results_grid.GetLabelBackgroundColour())

        # Adjust specific column sizes
        col_sizes = [120, 70, 70, 70, 50, 80, 50, 20, 50, 90, 90, 50, 50, 80, 70, 70,100,100, 80, 120, 120, 120, 120]
        for i, size in enumerate(col_sizes):
            self.results_grid.SetColSize(i, size)

        # Set renderer for checkbox column
        checkbox_renderer = CheckboxRenderer()
        for row in range(self.results_grid.GetNumberRows()):

            self.results_grid.SetCellRenderer(row, 7, checkbox_renderer)
            # self.results_grid.SetCellRenderer(row, 7, wx.grid.GridCellBoolRenderer())
            # self.results_grid.SetCellEditor(row, 7, wx.grid.GridCellBoolEditor())

        results_sizer_inner.Add(self.results_grid, 1, wx.EXPAND | wx.ALL, 5)
        self.results_frame.SetSizer(results_sizer_inner)
        results_sizer.Add(self.results_frame, 1, wx.EXPAND | wx.ALL, 5)



        grids_sizer.Add(results_sizer, 1, wx.EXPAND | wx.ALL, 5)

        grids_panel.SetSizer(grids_sizer)

        # Set up the splitter
        self.splitter.SplitVertically(self.right_frame, grids_panel)
        self.splitter.SetMinimumPaneSize(0)  # Prevents making panes too small
        self.splitter.SetSashGravity(0.5)  # Makes resizing proportional

        # Set initial sash position
        self.initial_sash_position = 700  # Adjust this value as needed
        self.splitter.SetSashPosition(self.initial_sash_position)

        # Add splitter to content sizer
        content_sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 5)

        # Add vertical toolbar and content sizer to main sizer
        main_sizer.Add(self.v_toolbar, 0, wx.EXPAND)
        main_sizer.Add(content_sizer, 1, wx.EXPAND)

        self.panel.SetSizer(main_sizer)

        # Create the horizontal toolbar
        self.toolbar = create_horizontal_toolbar(self)
        toggle_Col_1(self)

        # Bind events
        self.results_grid.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.peak_params_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_grid_select)
        self.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_splitter_changed)
        # self.results_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, lambda event: on_grid_left_click(self, event))
        self.results_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_checkbox_update)
        self.canvas.mpl_connect('button_release_event', self.on_plot_mouse_release)
        self.peak_params_grid.Bind(wx.EVT_LEFT_UP, self.on_peak_params_mouse_release)


    def add_toggle_tool(self, toolbar, label, bmp):
        tool = toolbar.AddTool(wx.ID_ANY, label, bmp, kind=wx.ITEM_NORMAL)
        self.Bind(wx.EVT_TOOL, self.on_toggle_right_panel, tool)
        return tool

    def on_toggle_right_panel(self, event):
        splitter_width = self.splitter.GetSize().GetWidth()

        if self.is_right_panel_hidden:
            # The right panel is currently hidden, so show it
            new_sash_position = self.initial_sash_position
            new_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR)
            # print("Showing right panel")
            self.is_right_panel_hidden = False
        else:
            # The right panel is currently visible, so hide it
            new_sash_position = splitter_width
            new_bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR)
            # print("Hiding right panel")
            self.is_right_panel_hidden = True

        self.splitter.SetSashPosition(new_sash_position)
        # print(f"New sash position set to: {new_sash_position}")

        # Update the tool's bitmap
        self.toolbar.SetToolNormalBitmap(self.toggle_right_panel_tool.GetId(), new_bmp)

        # Ensure the splitter and its children are properly updated
        self.splitter.UpdateSize()
        self.right_frame.Layout()
        self.splitter.Refresh()
        self.canvas.draw()

        # print(f"Final sash position: {self.splitter.GetSashPosition()}")
        # print(f"Is right panel hidden: {self.is_right_panel_hidden}")


    def on_splitter_changed(self, event):
        self.right_frame.Layout()
        self.canvas.draw()



    # I DON'T THINK IT IS USED
    def on_listbox_selection(self, event):
        self.selected_indices = self.file_listbox.GetSelections()
        update_sheet_names(self)


    def on_change_sheet_name(self, event):
        new_sheet_name = self.change_to_textctrl.GetValue()
        if new_sheet_name:
            rename_sheet(self, new_sheet_name)
            wx.MessageBox(f'Sheet renamed to "{new_sheet_name}"', "Info", wx.OK | wx.ICON_INFORMATION)





    def add_peak_params(self):
        sheet_name = self.sheet_combobox.GetValue()
        num_peaks = self.peak_params_grid.GetNumberRows() // 2

        # Update bg_min_energy and bg_max_energy from window.Data
        if sheet_name in self.Data['Core levels'] and 'Background' in self.Data['Core levels'][sheet_name]:
            background_data = self.Data['Core levels'][sheet_name]['Background']
            self.bg_min_energy = background_data.get('Bkg Low')
            self.bg_max_energy = background_data.get('Bkg High')

        # Ensure bg_min_energy and bg_max_energy are not None
        if self.bg_min_energy is None or self.bg_max_energy is None:
            wx.MessageBox("Background range is not set. Please set the background first.", "Warning",
                          wx.OK | wx.ICON_WARNING)
            return

        if num_peaks == 0:
            residual = self.y_values - np.array(self.Data['Core levels'][sheet_name]['Background']['Bkg Y'])
            peak_y = residual[np.argmax(residual)]
            peak_x = self.x_values[np.argmax(residual)]
        else:

            # Call update_overall_fit_and_residuals to get the residuals
            residual = self.plot_manager.update_overall_fit_and_residuals(self)

            if residual is not None:
                peak_y = residual.max()
                peak_x = self.x_values[np.argmax(residual)]
            else:
                # Fallback if residuals couldn't be calculated
                wx.MessageBox("Unable to calculate residuals. Using default peak position.", "Warning",
                              wx.OK | wx.ICON_WARNING)
                peak_y = self.y_values.max()
                peak_x = self.x_values[np.argmax(self.y_values)]

        self.peak_count += 1

        # Add new rows to the grid
        self.peak_params_grid.AppendRows(2)
        row = self.peak_params_grid.GetNumberRows() - 2

        # Assign letter IDs
        letter_id = chr(64 + self.peak_count)


        # Set values in the grid
        self.peak_params_grid.SetCellValue(row, 0, letter_id)
        self.peak_params_grid.SetReadOnly(row, 0)
        self.peak_params_grid.SetCellValue(row, 1, f"{sheet_name} p{self.peak_count}")
        self.peak_params_grid.SetCellValue(row, 2, f"{peak_x:.2f}")
        self.peak_params_grid.SetCellValue(row, 3, f"{peak_y:.2f}")
        self.peak_params_grid.SetCellValue(row, 4, "1.6")
        self.peak_params_grid.SetCellValue(row, 5, "30")
        self.peak_params_grid.SetCellValue(row, 6, "")  # Area, initially empty
        self.peak_params_grid.SetCellValue(row, 7, "0")  # Tail E
        self.peak_params_grid.SetCellValue(row, 8, '0')  # Tail M
        self.peak_params_grid.SetCellValue(row, 9, '')  # Area, initially empty
        self.peak_params_grid.SetCellValue(row, 10, '') # Area, initially empty
        self.peak_params_grid.SetCellValue(row, 11, '')  # Split, initially empty
        self.peak_params_grid.SetCellValue(row, 12, self.selected_fitting_method)  # Fitting Model
        self.peak_params_grid.SetCellValue(row, 13, self.background_method)  # Bkg Type
        self.peak_params_grid.SetCellValue(row, 14,
                                           f"{self.bg_min_energy:.2f}" if self.bg_min_energy is not None else "")  # Bkg Low
        self.peak_params_grid.SetCellValue(row, 15,
                                           f"{self.bg_max_energy:.2f}" if self.bg_max_energy is not None else "")  # Bkg High
        self.peak_params_grid.SetCellValue(row, 16, f"{self.offset_l:.2f}")  # Bkg Offset Low
        self.peak_params_grid.SetCellValue(row, 17, f"{self.offset_h:.2f}")  # Bkg Offset High

        # Set constraint values
        self.peak_params_grid.SetReadOnly(row + 1, 0)
        for col in range(15):  # Assuming you have 15 columns in total
            # self.peak_params_grid.SetCellBackgroundColour(row + 1, col, wx.Colour(230, 230, 230))
            self.peak_params_grid.SetCellBackgroundColour(row + 1, col, wx.Colour(200,245,228))

        # Set position constraint to background range
        position_constraint = f"{self.bg_min_energy:.2f},{self.bg_max_energy:.2f}"
        self.peak_params_grid.SetCellValue(row + 1, 2, position_constraint)
        self.peak_params_grid.SetCellValue(row + 1, 3, "100,1e7")
        self.peak_params_grid.SetCellValue(row + 1, 4, "0.3,3.5")
        self.peak_params_grid.SetCellValue(row + 1, 5, "2,80")
        self.peak_params_grid.SetCellValue(row + 1, 7, "Fixed")
        self.peak_params_grid.SetCellValue(row + 1, 8, "Fixed")
        self.peak_params_grid.ForceRefresh()

        # Set selected_peak_index to the index of the new peak
        self.selected_peak_index = num_peaks

        # Update the Data structure with the new peak information
        if 'Fitting' not in self.Data['Core levels'][sheet_name]:
            self.Data['Core levels'][sheet_name]['Fitting'] = {}
        if 'Peaks' not in self.Data['Core levels'][sheet_name]['Fitting']:
            self.Data['Core levels'][sheet_name]['Fitting']['Peaks'] = {}

        self.Data['Core levels'][sheet_name]['Fitting']['Peaks'][sheet_name + f" p{self.peak_count}"] = {
            'Position': peak_x,
            'Height': peak_y,
            'FWHM': 1.6,
            'L/G': 30,
            'Area': '',
            'Tail M': 0.0,
            'Tail E': 0.0,
            'Fitting Model': self.selected_fitting_method,
            'Bkg Type': self.background_method,
            'Bkg Low': self.bg_min_energy,
            'Bkg High': self.bg_max_energy,
            'Bkg Offset Low': self.offset_l,
            'Bkg Offset High': self.offset_h,
            'Constraints': {
                'Position': position_constraint,
                'Height': "100,1e7",
                'FWHM': "0.3,3.5",
                'L/G': "2,80",
                'Tail M': "Fixed",
                'Tail E': "Fixed"
            }
        }
        # print(self.Data)
        self.show_hide_vlines()

        # Call the method to clear and replot everything
        self.clear_and_replot()

        return self.peak_count - 1  # Return the index of the added peak

    def get_peak_model(self, peak_x, peak_y, fwhm, lg_ratio):
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        gamma = lg_ratio * sigma

        if self.selected_fitting_method == "Voigt":
            peak_model = lmfit.models.VoigtModel()
            params = peak_model.make_params(center=peak_x, amplitude=peak_y, sigma=sigma, gamma=gamma)
        elif self.selected_fitting_method == "Pseudo-Voigt":
            peak_model = lmfit.models.PseudoVoigtModel()
            params = peak_model.make_params(center=peak_x, amplitude=peak_y, sigma=sigma, fraction=lg_ratio)
        elif self.selected_fitting_method == "GL":
            peak_model = lmfit.Model(PeakFunctions.gauss_lorentz)
            params = peak_model.make_params(center=peak_x, fwhm=fwhm, fraction=lg_ratio, amplitude=peak_y)
        elif self.selected_fitting_method == "SGL":
            peak_model = lmfit.Model(PeakFunctions.S_gauss_lorentz)
            params = peak_model.make_params(center=peak_x, fwhm=fwhm, fraction=lg_ratio, amplitude=peak_y)
        else:
            raise ValueError(f"Unknown fitting method: {self.selected_fitting_method}")

        return peak_model, params



    def number_to_letter(n):
        return chr(65 + n)  # 65 is the ASCII value for 'A'

    # --------------------------------------------------------------------------------------------------
    # OPEN WINDOW --------------------------------------------------------------------------------------
    def on_open_background_window(self):
        if not hasattr(self, 'background_window') or not self.background_window:
            self.background_window = BackgroundWindow(self)
            self.background_tab_selected = True
            self.background_window.Bind(wx.EVT_CLOSE, self.on_background_window_close)
        self.background_window.Show()
        self.background_window.Raise()

    def on_background_window_close(self, event):
        self.background_tab_selected = False
        self.show_hide_vlines()
        self.background_window = None
        event.Skip()

    def enable_background_interaction(self):
        self.background_tab_selected = True
        self.show_hide_vlines()

    def disable_background_interaction(self):
        self.vline1 = None
        self.vline2 = None
        self.vline3 = None
        self.vline4 = None
        self.background_tab_selected = False
        self.show_hide_vlines()

    def on_open_fitting_window(self):
        if self.fitting_window is None or not self.fitting_window:
            self.fitting_window = FittingWindow(self)
            self.background_tab_selected = True
            self.peak_fitting_tab_selected = False

            # Set the position of the fitting window relative to the main window
            main_pos = self.GetPosition()
            main_size = self.GetSize()
            fitting_size = self.fitting_window.GetSize()

            # Calculate the position to center the fitting window on the main window
            x = main_pos.x + (main_size.width - fitting_size.width) // 2
            y = main_pos.y + (main_size.height - fitting_size.height) // 2

            self.fitting_window.SetPosition((x, y))

            self.show_hide_vlines()
            self.deselect_all_peaks()

        self.fitting_window.Show()
        self.fitting_window.Raise()  # Bring the window to the front

    def on_open_noise_analysis_window(self, event):
        if self.noise_analysis_window is None or not self.noise_analysis_window:
            self.noise_analysis_window = NoiseAnalysisWindow(self)
            self.noise_tab_selected = True
            self.show_hide_vlines()

        # Get the position and size of the main window
        main_pos = self.GetPosition()
        main_size = self.GetSize()

        # Get the size of the noise analysis windo
        noise_size = self.noise_analysis_window.GetSize()

        # Calculate the position to center the noise analysis window on the main windo
        x = main_pos.x + (main_size.width - noise_size.width) // 2
        y = main_pos.y + (main_size.height - noise_size.height) // 2

        # Set the position of the noise analysis window
        self.noise_analysis_window.SetPosition((x, y))

        self.noise_analysis_window.Show()
        self.noise_analysis_window.Raise()

        # Ensure the noise window stays on top
        self.noise_analysis_window.SetWindowStyle(self.noise_analysis_window.GetWindowStyle() | wx.STAY_ON_TOP)

    def noise_window_closed(self):
        self.noise_tab_selected = False
        self.show_hide_vlines()


    # END OPEN WINDOW ----------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------------------
    # MOVE TO PLOT OPERATIONS --------------------------------------------------------------------------
    def clear_and_replot(self):
        self.plot_manager.clear_and_replot(self)

    def plot_data(self):
        self.plot_manager.plot_data(self)

    def update_overall_fit_and_residuals(self):
        self.plot_manager.update_overall_fit_and_residuals(self)

    def plot_peak(self, x, y, index):
        row = index * 2
        fwhm = float(self.peak_params_grid.GetCellValue(row, 4))
        lg_ratio = float(self.peak_params_grid.GetCellValue(row, 5))
        label = self.peak_params_grid.GetCellValue(row, 1)  # Get the label from the grid

        peak_params = {
            'row': row,
            'fwhm': fwhm,
            'lg_ratio': lg_ratio,
            'position': x,
            'height': y,
            'label': label  # Include the label in peak_params
        }

        self.plot_manager.plot_peak(
            self.x_values,
            self.background,
            self.selected_fitting_method,
            peak_params,
            self.sheet_combobox.GetValue()
        )

    def update_peak_plot(self, x, y, remove_old_peaks=True):
        self.plot_manager.update_peak_plot(self, x, y, remove_old_peaks)

    def update_peak_fwhm(self, x):
        self.plot_manager.update_peak_fwhm(self, x)


    def adjust_plot_limits(self, axis, direction):
        self.plot_config.adjust_plot_limits(self, axis, direction)




    def update_constraint(self, event):
        row = event.GetRow()
        col = event.GetCol()
        if row % 2 == 1:  # If it's a constraint row
            value = self.peak_params_grid.GetCellValue(row, col).lower()
            if value == 'f':
                self.peak_params_grid.SetCellValue(row, col, 'fixed')
        event.Skip()

    def on_grid_select(self, event):
        if self.peak_fitting_tab_selected:
            row = event.GetRow()
            if row % 2 == 0:  # Assuming peak parameters are in even rows and constraints in odd rows
                # Removing any cross that were there
                self.selected_peak_index = None
                self.clear_and_replot()

                peak_index = row // 2
                self.selected_peak_index = peak_index

                self.remove_cross_from_peak()
                self.highlight_selected_peak()  # Highlight the selected peak
            else:
                self.selected_peak_index = None
                self.deselect_all_peaks()
        else:
            # If peak fitting tab is not selected, don't allow peak selection
            self.selected_peak_index = None
            self.deselect_all_peaks()

        self.update_checkboxes_from_data()
        event.Skip()


    def remove_cross_from_peak(self):
        if hasattr(self, 'cross'):
            if self.cross in self.ax.lines:
                self.cross.remove()
            del self.cross
        self.canvas.mpl_disconnect('motion_notify_event')
        self.canvas.mpl_disconnect('button_release_event')

    def update_peak_grid(self, index, x, y):
        row = index * 2  # Assuming each peak uses two rows in the grid
        self.peak_params_grid.SetCellValue(row, 2, f"{x:.2f}")  # Update Position
        self.peak_params_grid.SetCellValue(row, 3, f"{y:.2f}")  # Update Height
        self.peak_params_grid.ForceRefresh()  # Refresh the grid to show changes

    def update_fwhm_grid(self, index, fwhm):
        row = index * 2  # Assuming each peak uses two rows in the grid
        self.peak_params_grid.SetCellValue(row, 4, f"{fwhm:.2f}")  # Update FWHM

    def on_cross_drag(self, event):
        if event.inaxes and self.selected_peak_index is not None:
            row = self.selected_peak_index * 2
            if event.button == 1:
                try:
                    if event.key == 'shift':
                        self.update_peak_fwhm(event.xdata)
                    elif self.is_mouse_on_peak(event):
                        closest_index = np.argmin(np.abs(self.x_values - event.xdata))
                        bkg_y = self.background[closest_index]

                        new_x = event.xdata
                        new_height = max(event.ydata - bkg_y, 0)

                        # Update the grid
                        self.peak_params_grid.SetCellValue(row, 2, f"{new_x:.2f}")
                        self.peak_params_grid.SetCellValue(row, 3, f"{new_height:.2f}")

                        # Update the Data structure
                        sheet_name = self.sheet_combobox.GetValue()
                        peak_label = self.peak_params_grid.GetCellValue(row, 1)
                        if sheet_name in self.Data['Core levels'] and 'Fitting' in self.Data['Core levels'][
                            sheet_name] and 'Peaks' in self.Data['Core levels'][sheet_name]['Fitting']:
                            peaks = self.Data['Core levels'][sheet_name]['Fitting']['Peaks']
                            if peak_label in peaks:
                                peaks[peak_label]['Position'] = new_x
                                peaks[peak_label]['Height'] = new_height

                        # Call the function that updates all split values
                        self.update_ratios()

                        self.clear_and_replot()
                        self.plot_manager.add_cross_to_peak(self, self.selected_peak_index)
                        self.canvas.draw_idle()

                except Exception as e:
                    print(f"Error during cross drag: {e}")

    def on_cross_release(self, event):
        if event.inaxes and self.selected_peak_index is not None:
            if event.button == 1:  # Left button release
                row = self.selected_peak_index * 2
                peak_label = self.peak_params_grid.GetCellValue(row, 1)
                sheet_name = self.sheet_combobox.GetValue()

                if event.key == 'shift':  # SHIFT + left click release for FWHM change
                    # Store the current FWHM in window.Data
                    current_fwhm = float(self.peak_params_grid.GetCellValue(row, 4))
                    if sheet_name in self.Data['Core levels'] and 'Fitting' in self.Data['Core levels'][
                        sheet_name] and 'Peaks' in self.Data['Core levels'][sheet_name]['Fitting']:
                        peaks = self.Data['Core levels'][sheet_name]['Fitting']['Peaks']
                        if peak_label in peaks:
                            peaks[peak_label]['FWHM'] = current_fwhm

                else:
                    bkg_y = self.background[np.argmin(np.abs(self.x_values - event.xdata))]
                    x = event.xdata
                    y = max(event.ydata - bkg_y, 0)  # Ensure height is not negative

                    self.update_peak_grid(self.selected_peak_index, x, y)

                    # Recalculate the area
                    height = float(self.peak_params_grid.GetCellValue(row, 3))
                    fwhm = float(self.peak_params_grid.GetCellValue(row, 4))
                    fraction = float(self.peak_params_grid.GetCellValue(row, 5))
                    model = self.peak_params_grid.GetCellValue(row, 12)
                    area = self.calculate_peak_area(model, height, fwhm, fraction)
                    self.peak_params_grid.SetCellValue(row, 6, f"{area:.2f}")

                    # Remove old cross
                    self.remove_cross_from_peak()

                    # Create new cross at final position
                    self.cross, = self.ax.plot(x, event.ydata, 'bx', markersize=15, markerfacecolor='none', picker=5,
                                               linewidth=3)

                    # self.update_peak_plot(x, y)

                    # Update the Data structure with the current label and new values
                    if sheet_name in self.Data['Core levels'] and 'Fitting' in self.Data['Core levels'][
                        sheet_name] and 'Peaks' in self.Data['Core levels'][sheet_name]['Fitting']:
                        peaks = self.Data['Core levels'][sheet_name]['Fitting']['Peaks']
                        if peak_label in peaks:
                            peaks[peak_label]['Position'] = x
                            peaks[peak_label]['Height'] = y
                        else:
                            # If the label doesn't exist, find the correct peak by index and update its label
                            old_labels = list(peaks.keys())
                            if self.selected_peak_index < len(old_labels):
                                old_label = old_labels[self.selected_peak_index]
                                peaks[peak_label] = peaks.pop(old_label)
                                peaks[peak_label]['Position'] = x
                                peaks[peak_label]['Height'] = y

            self.canvas.draw_idle()

        # Safely disconnect event handlers
        if hasattr(self, 'motion_cid'):
            self.canvas.mpl_disconnect(self.motion_cid)
            delattr(self, 'motion_cid')
        if hasattr(self, 'release_cid'):
            self.canvas.mpl_disconnect(self.release_cid)
            delattr(self, 'release_cid')

        # Refresh the grid to ensure it reflects the current state of self.Data
        self.refresh_peak_params_grid()



    def show_hide_vlines(self):
        background_lines_visible = hasattr(self, 'fitting_window') and self.background_tab_selected
        noise_lines_visible = self.noise_analysis_window is not None and self.noise_tab_selected

        if self.vline1 is not None:
            self.vline1.set_visible(background_lines_visible)
        if self.vline2 is not None:
            self.vline2.set_visible(background_lines_visible)

        if self.vline3 is not None:
            self.vline3.set_visible(noise_lines_visible)
        if self.vline4 is not None:
            self.vline4.set_visible(noise_lines_visible)

        self.canvas.draw_idle()


    def is_mouse_on_peak(self, event):
        if self.selected_peak_index is not None:
            '''
            row = self.selected_peak_index * 2
            x_peak = float(self.peak_params_grid.GetCellValue(row, 2))  # Position
            y_peak = float(self.peak_params_grid.GetCellValue(row, 3))  # Height
            bkg_y = self.background[np.argmin(np.abs(self.x_values - x_peak))]
            y_peak += bkg_y
            distance = np.sqrt((event.xdata - x_peak) ** 2 + (event.ydata - y_peak) ** 2)            
            return distance < 3000  # Smaller tolerance for more precise detection
            '''
            return True
        return False


    # GET PEAK INDEX ------------------------------------------------------------
    # USED TO MOVE THE PE
    def get_peak_index_from_position(self, x, y):
        # Transform input coordinates (x, y) to display (pixel) coordinates
        x_display, y_display = self.ax.transData.transform((x, y))

        num_peaks = self.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows

        for i in range(num_peaks):
            row = i * 2  # Assuming each peak has 2 rows (peak and constraints)
            if self.peak_params_grid.IsInSelection(row, 0):
                # Get the peak position in data coordinates
                x_peak = float(self.peak_params_grid.GetCellValue(row, 2))  # Position
                y_peak = float(self.peak_params_grid.GetCellValue(row, 3))  # Height
                bkg_y = self.background[np.argmin(np.abs(self.x_values - x_peak))]
                y_peak += bkg_y

                # Transform peak position to display (pixel) coordinates
                x_peak_display, y_peak_display = self.ax.transData.transform((x_peak, y_peak))

                # Calculate the Euclidean distance in display coordinates
                distance = np.sqrt((x_display - x_peak_display) ** 2 + (y_display - y_peak_display) ** 2)

                if distance < 10:  # Adjust the tolerance as needed (10 pixels here as an example)
                    return i
        return None


    def on_mouse_move(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.SetStatusText(f"BE: {x:.1f} eV, I: {int(y)} CTS", 1)

    def on_click(self, event):
        if event.inaxes:
            x_click = event.xdata

            if event.button == 1:  # Left click
                if event.key == 'shift':  # SHIFT + left click
                    if self.peak_fitting_tab_selected and self.selected_peak_index is not None:
                        row = self.selected_peak_index * 2  # Each peak uses two rows in the grid
                        self.initial_fwhm = float(self.peak_params_grid.GetCellValue(row, 4))  # FWHM
                        self.initial_x = event.xdata
                        self.motion_cid = self.canvas.mpl_connect('motion_notify_event', self.on_cross_drag)
                        self.release_cid = self.canvas.mpl_connect('button_release_event', self.on_cross_release)
                elif self.background_tab_selected:  # Left click and background tab selected
                    self.deselect_all_peaks()
                    sheet_name = self.sheet_combobox.GetValue()
                    if sheet_name in self.Data['Core levels']:
                        core_level_data = self.Data['Core levels'][sheet_name]
                        if self.background_method == "Adaptive Smart":
                            # Check if click is close to vline1 or vline2
                            if self.vline1 is not None and self.vline2 is not None:
                                vline1_x = self.vline1.get_xdata()[0]
                                vline2_x = self.vline2.get_xdata()[0]

                                dist1 = abs(x_click - vline1_x)
                                dist2 = abs(x_click - vline2_x)

                                if dist1 < dist2 and dist1 < self.some_threshold:
                                    self.moving_vline = self.vline1
                                elif dist2 < self.some_threshold:
                                    self.moving_vline = self.vline2
                                else:
                                    self.moving_vline = None

                                if self.moving_vline is not None:
                                    self.motion_cid = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
                                    self.release_cid = self.canvas.mpl_connect('button_release_event', self.on_release)
                                    return  # Exit to avoid creating new vlines

                        # Existing vline creation logic
                        if self.vline1 is None:
                            self.vline1 = self.ax.axvline(x_click, color='r', linestyle='--')
                            core_level_data['Background']['Bkg Low'] = float(x_click)
                        elif self.vline2 is None and abs(
                                x_click - core_level_data['Background']['Bkg Low']) > self.some_threshold:
                            self.vline2 = self.ax.axvline(x_click, color='r', linestyle='--')
                            core_level_data['Background']['Bkg High'] = float(x_click)
                            core_level_data['Background']['Bkg Low'], core_level_data['Background'][
                                'Bkg High'] = sorted([
                                core_level_data['Background']['Bkg Low'],
                                core_level_data['Background']['Bkg High']
                            ])
                        else:
                            self.moving_vline = self.vline1 if self.vline2 is None or abs(
                                x_click - core_level_data['Background']['Bkg Low']) < abs(
                                x_click - core_level_data['Background']['Bkg High']) else self.vline2
                            self.motion_cid = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
                            self.release_cid = self.canvas.mpl_connect('button_release_event', self.on_release)
                elif self.noise_tab_selected:
                    if self.vline3 is None:
                        self.vline3 = self.ax.axvline(x_click, color='b', linestyle='--')
                        self.noise_min_energy = float(x_click)
                    elif self.vline4 is None and abs(x_click - self.noise_min_energy) > self.some_threshold:
                        self.vline4 = self.ax.axvline(x_click, color='b', linestyle='--')
                        self.noise_max_energy = float(x_click)
                        self.noise_min_energy, self.noise_max_energy = sorted(
                            [self.noise_min_energy, self.noise_max_energy])
                    else:
                        self.moving_vline = self.vline3 if self.vline4 is None or abs(
                            x_click - self.noise_min_energy) < abs(
                            x_click - self.noise_max_energy) else self.vline4
                        self.motion_cid = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
                        self.release_cid = self.canvas.mpl_connect('button_release_event', self.on_release)
                elif self.peak_fitting_tab_selected:  # Only allow peak selection when peak fitting tab is selected
                    peak_index = self.get_peak_index_from_position(event.xdata, event.ydata)
                    if peak_index is not None:
                        self.selected_peak_index = peak_index
                        self.motion_cid = self.canvas.mpl_connect('motion_notify_event', self.on_cross_drag)
                        self.release_cid = self.canvas.mpl_connect('button_release_event', self.on_cross_release)
                        self.highlight_selected_peak()
                    else:
                        self.deselect_all_peaks()
                else:
                    self.deselect_all_peaks()

            self.show_hide_vlines()
            self.canvas.draw()



    def on_mouse_wheel(self, event):
        if event.step != 0:
            current_index = self.sheet_combobox.GetSelection()
            num_sheets = self.sheet_combobox.GetCount()

            if event.step > 0:
                # Scroll up, move to previous sheet
                new_index = (current_index - 1) % num_sheets
            else:
                # Scroll down, move to next sheet
                new_index = (current_index + 1) % num_sheets

            self.sheet_combobox.SetSelection(new_index)
            new_sheet = self.sheet_combobox.GetString(new_index)

            # Create a mock event to pass to on_sheet_selected
            mock_event = wx.CommandEvent(wx.EVT_COMBOBOX.typeId, self.sheet_combobox.GetId())
            mock_event.SetString(new_sheet)

            # Call on_sheet_selected with the mock event
            on_sheet_selected(self, mock_event)


    def highlight_selected_peak(self):
        if self.selected_peak_index is not None:
            num_peaks = self.peak_params_grid.GetNumberRows() // 2
            for i in range(num_peaks):
                row = i * 2
                is_selected = (i == self.selected_peak_index)

                self.peak_params_grid.SetCellBackgroundColour(row, 0, wx.LIGHT_GREY if is_selected else wx.WHITE)
                self.peak_params_grid.SetCellBackgroundColour(row + 1, 0, wx.LIGHT_GREY if is_selected else wx.WHITE)

            row = self.selected_peak_index * 2
            peak_label = self.peak_params_grid.GetCellValue(row, 1)  # Get the current label
            x_str = self.peak_params_grid.GetCellValue(row, 2)
            y_str = self.peak_params_grid.GetCellValue(row, 3)

            if x_str and y_str:
                try:
                    x = float(x_str)
                    y = float(y_str)
                    y += self.background[np.argmin(np.abs(self.x_values - x))]

                    self.remove_cross_from_peak()
                    self.cross, = self.ax.plot(x, y, 'bx', markersize=15, markerfacecolor='none', picker=5, linewidth=3)

                    self.peak_params_grid.ClearSelection()
                    self.peak_params_grid.SelectRow(row, addToSelected=False)

                    self.peak_params_grid.Refresh()
                    self.canvas.draw_idle()

                    # Update the Data structure with the current label

                    sheet_name = self.sheet_combobox.GetValue()
                    if sheet_name in self.Data['Core levels'] and 'Fitting' in self.Data['Core levels'][
                        sheet_name] and 'Peaks' in self.Data['Core levels'][sheet_name]['Fitting']:
                        peaks = self.Data['Core levels'][sheet_name]['Fitting']['Peaks']
                        old_label = list(peaks.keys())[self.selected_peak_index]
                        if old_label != peak_label:
                            peaks[peak_label] = peaks.pop(old_label)

                    self.canvas.mpl_connect('motion_notify_event', self.on_cross_drag)
                    self.canvas.mpl_connect('button_release_event', self.on_cross_release)
                except ValueError as e:
                    print(f"Warning: Invalid data for selected peak. Cannot highlight. Error: {e}")
            else:
                print(f"Warning: Empty data for selected peak. Cannot highlight.")

            self.peak_params_grid.Refresh()
        else:
            print("No peak selected (selected_peak_index is None)")

    def on_key_press(self, event):
        if self.selected_peak_index is not None:
            num_peaks = self.peak_params_grid.GetNumberRows() // 2  # Assuming each peak uses two rows

            if event.key == 'tab':
                if not self.peak_fitting_tab_selected:
                    self.show_popup_message("Open the Peak Fitting Tab to move or select a peak")
                else:
                    self.change_selected_peak(1)  # Move to next peak
                return  # Prevent event from propagating
            elif event.key == 'q':
                # print("Local Key q")
                # self.change_selected_peak(-1)
                pass

            self.highlight_selected_peak()
            self.clear_and_replot()
            self.canvas.draw_idle()

    def on_key_press_global(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_TAB:
            if not self.peak_fitting_tab_selected:
                self.show_popup_message("Open the Peak Fitting Tab to move or select a peak")
            else:
                self.change_selected_peak(1)  # Move to next peak
            return  # Prevent event from propagating
        elif keycode == ord('Q'):
            if not self.peak_fitting_tab_selected:
                self.show_popup_message("Open the Peak Fitting Tab to move or select a peak")
            else:
                self.change_selected_peak(-1)  # Move to next peak
            return  # Prevent event from propagating
        elif keycode in [ord('['), ord(']')] and event.ControlDown():
            current_index = self.sheet_combobox.GetSelection()
            num_sheets = self.sheet_combobox.GetCount()
            if keycode == ord('['):
                new_index = (current_index - 1) % num_sheets
            else:
                new_index = (current_index + 1) % num_sheets

            self.sheet_combobox.SetSelection(new_index)
            new_sheet = self.sheet_combobox.GetString(new_index)

            # Call on_sheet_selected with the new sheet name
            on_sheet_selected(self, new_sheet)
            return  # Prevent event from propagating
        elif keycode in [ord('-'), ord('=')] and event.ControlDown():
            sheet_name = self.sheet_combobox.GetValue()
            limits = self.plot_config.get_plot_limits(self, sheet_name)

            zoom_factor = 0.2
            if keycode == ord('-'):  # Zoom out
                limits['Xmin'] -= zoom_factor
                limits['Xmax'] += zoom_factor
            else:  # Zoom in
                limits['Xmin'] += zoom_factor
                limits['Xmax'] -= zoom_factor

            # Update the plot limits
            self.plot_config.update_plot_limits(self, sheet_name,
                                                x_min=limits['Xmin'],
                                                x_max=limits['Xmax'])

            # Update the plot
            self.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
            self.canvas.draw_idle()
            return  # Prevent event from propagating
        elif keycode in [wx.WXK_LEFT, wx.WXK_RIGHT] and event.ControlDown():
            sheet_name = self.sheet_combobox.GetValue()
            limits = self.plot_config.get_plot_limits(self, sheet_name)
            move_factor = 0.1
            if keycode == wx.WXK_LEFT:
                limits['Xmin'] -= move_factor
                limits['Xmax'] -= move_factor
            else:  # Right key
                limits['Xmin'] += move_factor
                limits['Xmax'] += move_factor

            # Update the plot limits
            self.plot_config.update_plot_limits(self, sheet_name,
                                                x_min=limits['Xmin'],
                                                x_max=limits['Xmax'])

            # Update the plot
            self.ax.set_xlim(limits['Xmax'], limits['Xmin'])  # Reverse X-axis
            self.canvas.draw_idle()
            return
        elif keycode in [wx.WXK_UP, wx.WXK_DOWN] and event.ControlDown():
            sheet_name = self.sheet_combobox.GetValue()
            limits = self.plot_config.get_plot_limits(self, sheet_name)
            intensity_factor = 0.05
            max_intensity = max(self.y_values)

            if keycode == wx.WXK_DOWN:  # Decrease intensity
                limits['Ymax'] = max(limits['Ymax'] - intensity_factor * max_intensity, limits['Ymin'])
            else:  # Increase intensity
                limits['Ymax'] += intensity_factor * max_intensity

            # Update the plot limits
            self.plot_config.update_plot_limits(self, sheet_name, y_max=limits['Ymax'])

            # Update the plot
            self.ax.set_ylim(limits['Ymin'], limits['Ymax'])
            self.canvas.draw_idle()
            return  # Prevent event from propagating
        event.Skip()  # Let other key events propagate normally

    def show_popup_message(self, message):
        popup = wx.adv.RichToolTip("Are you trying to select a peak?", message)
        popup.ShowFor(self)

    def show_popup_message2(self, message1, message2):
        popup = wx.adv.RichToolTip(message1, message2)
        popup.ShowFor(self)

    def change_selected_peak(self, direction):


        num_peaks = self.peak_params_grid.GetNumberRows() // 2


        if self.selected_peak_index is None:
            self.selected_peak_index = 0 if direction > 0 else num_peaks - 1
        else:
            self.selected_peak_index = (self.selected_peak_index + direction) % num_peaks



        self.remove_cross_from_peak()
        if self.peak_fitting_tab_selected:
            self.highlight_selected_peak()

        self.canvas.draw_idle()

    def on_motion(self, event):
        if event.inaxes and self.moving_vline is not None:
            x_click = event.xdata
            self.moving_vline.set_xdata([x_click])

            sheet_name = self.sheet_combobox.GetValue()
            if sheet_name in self.Data['Core levels']:
                core_level_data = self.Data['Core levels'][sheet_name]

                if self.moving_vline in [self.vline1, self.vline2]:
                    if self.moving_vline == self.vline1:
                        core_level_data['Background']['Bkg Low'] = float(x_click)
                    else:
                        core_level_data['Background']['Bkg High'] = float(x_click)

                    # Ensure Bkg Low is always less than Bkg High
                    bkg_low = core_level_data['Background']['Bkg Low']
                    bkg_high = core_level_data['Background']['Bkg High']
                    core_level_data['Background']['Bkg Low'] = min(bkg_low, bkg_high)
                    core_level_data['Background']['Bkg High'] = max(bkg_low, bkg_high)

                    # If in Adaptive Smart mode, update the background in real-time
                    if self.background_method == "Adaptive Smart":
                        # plot_background(self)
                        pass

                elif self.moving_vline in [self.vline3, self.vline4]:
                    if self.moving_vline == self.vline3:
                        self.noise_min_energy = float(x_click)
                    else:
                        self.noise_max_energy = float(x_click)

                    # Ensure noise_min_energy is always less than noise_max_energy
                    self.noise_min_energy, self.noise_max_energy = sorted(
                        [self.noise_min_energy, self.noise_max_energy])

            self.canvas.draw_idle()

    def on_release(self, event):
        if self.moving_vline is not None:
            # self.canvas.mpl_disconnect(self.motion_cid)
            # self.canvas.mpl_disconnect(self.release_cid)
            self.moving_vline = None

            # Ensure the background range is correctly ordered in the data dictionary
            sheet_name = self.sheet_combobox.GetValue()
            if sheet_name in self.Data['Core levels']:
                core_level_data = self.Data['Core levels'][sheet_name]
                if 'Background' in core_level_data:
                    bg_low = core_level_data['Background'].get('Bkg Low')
                    bg_high = core_level_data['Background'].get('Bkg High')
                    if bg_low is not None and bg_high is not None:
                        core_level_data['Background']['Bkg Low'] = min(bg_low, bg_high)
                        core_level_data['Background']['Bkg High'] = max(bg_low, bg_high)

            # If in Adaptive Smart mode, update the background
            if self.background_method == "Adaptive Smart":
                # plot_background(self)
                pass
        # If a peak is being moved, update its position and height
        if self.selected_peak_index is not None:
            row = self.selected_peak_index * 2  # Each peak uses two rows in the grid
            peak_x = float(self.peak_params_grid.GetCellValue(row, 2))  # Position
            peak_y = float(self.peak_params_grid.GetCellValue(row, 3))  # Height
            self.update_peak_plot(peak_x, peak_y, remove_old_peaks=False)

            # Update the peak information in the data dictionary
            sheet_name = self.sheet_combobox.GetValue()
            if sheet_name in self.Data['Core levels']:
                core_level_data = self.Data['Core levels'][sheet_name]
                if 'Fitting' not in core_level_data:
                    core_level_data['Fitting'] = {}
                if 'Peaks' not in core_level_data['Fitting']:
                    core_level_data['Fitting']['Peaks'] = {}

                peak_label = self.peak_params_grid.GetCellValue(row, 1)
                core_level_data['Fitting']['Peaks'][peak_label] = {
                    'Position': peak_x,
                    'Height': peak_y,
                    'FWHM': float(self.peak_params_grid.GetCellValue(row, 4)),
                    'L/G': float(self.peak_params_grid.GetCellValue(row, 5)),
                    'Tail E': float(self.peak_params_grid.GetCellValue(row, 7)),
                    'Tail M': float(self.peak_params_grid.GetCellValue(row, 8))
                }

        self.selected_peak_index = None
        self.canvas.draw_idle()

    def on_vline_drag(self, event):
        if event.inaxes and self.active_vline is not None:
            self.active_vline.set_xdata([event.xdata, event.xdata])
            self.canvas.draw_idle()

    def on_vline_release(self, event):
        if self.active_vline is not None:
            self.active_vline = None
            self.canvas.mpl_disconnect(self.motion_cid)
            self.canvas.mpl_disconnect(self.release_cid)

            # Update background if in Adaptive Smart mode
            if self.background_method == "Adaptive Smart":
                plot_background(self)


    def on_zoom_in_tool(self, event):
        self.zoom_mode = not self.zoom_mode
        if self.zoom_mode:
            if self.zoom_rect:
                self.zoom_rect.set_active(True)
            else:
                self.zoom_rect = widgets.RectangleSelector(
                    self.ax,
                    self.on_zoom_select,
                    useblit=True,
                    props=dict(facecolor='green', edgecolor='green', alpha=0.3, fill=True),
                    button=[1],
                    minspanx=5,
                    minspany=5,
                    spancoords='pixels',
                    interactive=False  # Change this to False
                )
        else:
            if self.zoom_rect:
                self.zoom_rect.set_active(False)

        if self.drag_mode:
            self.disable_drag()
            self.drag_mode = False

        self.canvas.draw_idle()

    def on_zoom_select(self, eclick, erelease):
        if self.zoom_mode:
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata

            x_min, x_max = min(x1, x2), max(x1, x2)
            y_min, y_max = min(y1, y2), max(y1, y2)

            sheet_name = self.sheet_combobox.GetValue()
            self.plot_config.update_plot_limits(self, sheet_name, x_min, x_max, y_min, y_max)

            self.ax.set_xlim(x_max, x_min)  # Reverse X-axis
            self.ax.set_ylim(y_min, y_max)

            # Deactivate zoom mode and remove the rectangle
            self.zoom_mode = False
            if self.zoom_rect:
                self.zoom_rect.set_active(False)
                self.zoom_rect = None

            self.canvas.draw_idle()

    def on_zoom_out(self, event):
        sheet_name = self.sheet_combobox.GetValue()
        self.plot_config.reset_plot_limits(self, sheet_name)
        self.plot_config.resize_plot(self)
        if self.zoom_rect:
            self.zoom_rect.set_active(False)
            self.zoom_rect = None
        self.zoom_mode = False
        self.canvas.draw_idle()
        if self.drag_mode:
            self.disable_drag()
            self.drag_mode = False

    def on_drag_tool(self, event):
        self.drag_mode = not self.drag_mode
        if self.drag_mode:
            self.enable_drag()
        else:
            self.disable_drag()

    def enable_drag(self):
        self.navigation_toolbar.pan()
        self.canvas.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.drag_release_cid = self.canvas.mpl_connect('button_release_event', self.on_drag_release)

    def disable_drag(self):
        self.navigation_toolbar.pan()
        self.canvas.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        if hasattr(self, 'drag_release_cid'):
            self.canvas.mpl_disconnect(self.drag_release_cid)
        self.drag_mode = False  # Ensure drag_mode is set to False

    def on_drag_release(self, event):
        if self.drag_mode:
            sheet_name = self.sheet_combobox.GetValue()
            self.plot_config.update_after_drag(self, sheet_name)
            self.disable_drag()
            self.canvas.draw_idle()

    def update_checkboxes_from_data2(self):
        if 'Results' in self.Data and 'Peak' in self.Data['Results']:
            for row in range(self.results_grid.GetNumberRows()):
                sheet_name = self.sheet_combobox.GetValue()
                peak_label = f"{sheet_name}_{row}"
                peak_data = self.Data['Results']['Peak'].get(peak_label)
                if peak_data:
                    checkbox_state = peak_data.get('Checkbox', '0')
                    current_grid_state = self.results_grid.GetCellValue(row, 7)
                    if checkbox_state != current_grid_state:
                        self.results_grid.SetCellValue(row, 7, checkbox_state)
                        self.results_grid.RefreshAttr(row, 7)
        self.results_grid.ForceRefresh()

    def update_checkboxes_from_data(self):
        if 'Results' in self.Data and 'Peak' in self.Data['Results']:
            for row in range(self.results_grid.GetNumberRows()):
                peak_label = f"Peak_{row}"
                peak_data = self.Data['Results']['Peak'].get(peak_label)
                if peak_data:
                    checkbox_state = peak_data.get('Checkbox', '0')
                    current_grid_state = self.results_grid.GetCellValue(row, 7)
                    if checkbox_state != current_grid_state:
                        self.results_grid.SetCellValue(row, 7, checkbox_state)
                        self.results_grid.RefreshAttr(row, 7)
        self.results_grid.ForceRefresh()

    def on_plot_mouse_release(self, event):
        self.update_checkboxes_from_data()
        # No need to call event.Skip() for Matplotlib events

    def on_peak_params_mouse_release(self, event):
        self.update_checkboxes_from_data()
        event.Skip()

    def on_peak_params_cell_select(self, event):
        self.update_checkboxes_from_data()
        event.Skip()


    def export_results(self):
        export_results(self)


    def on_cell_changed2(self, event):
        row = event.GetRow()
        col = event.GetCol()

        try:
            height = float(self.results_grid.GetCellValue(row, 2))
            fwhm = float(self.results_grid.GetCellValue(row, 3))
            rsf = float(self.results_grid.GetCellValue(row, 8))

            # Recalculate the area
            # to check because this does not seem right for all
            new_area = height * fwhm * (np.sqrt(2 * np.pi) / 2.355)
            self.results_grid.SetCellValue(row, 5, f"{new_area:.2f}")

            # Recalculate the relative area
            new_rel_area = new_area / rsf
            self.results_grid.SetCellValue(row, 10, f"{new_rel_area:.2f}")

            # Update the atomic percentages if necessary
            self.update_atomic_percentages()

        except ValueError:
            wx.MessageBox("Invalid value entered", "Error", wx.OK | wx.ICON_ERROR)

    def on_cell_changed(self, event):
        row = event.GetRow()
        col = event.GetCol()

        try:
            if col in [2, 3, 4, 5, 8]:  # Height, FWHM, L/G, RSF columns
                height = float(self.results_grid.GetCellValue(row, 2))
                fwhm = float(self.results_grid.GetCellValue(row, 3))
                rsf = float(self.results_grid.GetCellValue(row, 8))
                tail_E = float(self.results_grid.GetCellValue(row, 11))
                tail_M = float(self.results_grid.GetCellValue(row, 12))

                # Recalculate the area
                new_area = height * fwhm * (np.sqrt(2 * np.pi) / 2.355)
                self.results_grid.SetCellValue(row, 5, f"{new_area:.2f}")

                # Recalculate the relative area
                new_rel_area = new_area / rsf
                self.results_grid.SetCellValue(row, 10, f"{new_rel_area:.2f}")

                # Update the atomic percentages if necessary
                self.update_atomic_percentages()
            elif col in [16, 17, 18, 19]:  # Constraint columns
                # You may want to add logic here to handle changes in constraints
                pass

        except ValueError:
            wx.MessageBox("Invalid value entered", "Error", wx.OK | wx.ICON_ERROR)


    # Keep for now but I think it needs to be removed
    def update_atomic_percentages2(self):
        current_rows = self.results_grid.GetNumberRows()
        total_normalized_area = 0
        checked_indices = []

        # Calculate total normalized area for checked elements
        for i in range(current_rows):
            if self.results_grid.GetCellValue(i, 7) == '1':  # Checkbox is ticked
                normalized_area = float(self.results_grid.GetCellValue(i, 5)) / float(
                    self.results_grid.GetCellValue(i, 8))
                total_normalized_area += normalized_area
                checked_indices.append(i)
            else:
                # Set the atomic percentage to 0 for unticked rows
                self.results_grid.SetCellValue(i, 6, "0.00")

        # Calculate and set atomic percentages for checked elements
        for i in checked_indices:
            normalized_area = float(self.results_grid.GetCellValue(i, 5)) / float(self.results_grid.GetCellValue(i, 8))
            atomic_percent = (normalized_area / total_normalized_area) * 100 if total_normalized_area > 0 else 0
            self.results_grid.SetCellValue(i, 6, f"{atomic_percent:.2f}")

        self.results_grid.ForceRefresh()

    def update_atomic_percentages(self):
        current_rows = self.results_grid.GetNumberRows()
        total_normalized_area = 0
        checked_indices = []

        # Calculate total normalized area for checked elements
        for i in range(current_rows):
            if self.results_grid.GetCellValue(i, 7) == '1':  # Checkbox is ticked
                normalized_area = float(self.results_grid.GetCellValue(i, 5)) / float(
                    self.results_grid.GetCellValue(i, 8))
                total_normalized_area += normalized_area
                checked_indices.append(i)
            else:
                # Set the atomic percentage to 0 for unticked rows
                self.results_grid.SetCellValue(i, 6, "0.00")

        # Calculate and set atomic percentages for checked elements
        for i in checked_indices:
            normalized_area = float(self.results_grid.GetCellValue(i, 5)) / float(self.results_grid.GetCellValue(i, 8))
            atomic_percent = (normalized_area / total_normalized_area) * 100 if total_normalized_area > 0 else 0
            self.results_grid.SetCellValue(i, 6, f"{atomic_percent:.2f}")

            # Update Bkg Low, Bkg High, and Sheetname for all rows
            self.results_grid.SetCellValue(i, 13, f"{self.bg_min_energy:.2f}" if self.bg_min_energy is not None else "")
            self.results_grid.SetCellValue(i, 14, f"{self.bg_max_energy:.2f}" if self.bg_max_energy is not None else "")
            self.results_grid.SetCellValue(i, 15, self.sheet_combobox.GetValue())

            # Update constraint columns if needed
            # (You may want to add logic here if constraints can change dynamically)

        self.results_grid.ForceRefresh()

    def on_height_changed(self, event):
        row = event.GetRow()
        col = event.GetCol()

        if col == 2:  # Check if the height column was edited
            try:
                # Get the new height value
                new_height = float(self.results_grid.GetCellValue(row, col))
                # Get the corresponding FWHM value
                fwhm = float(self.results_grid.GetCellValue(row, 3))
                # Get the corresponding RSF value
                rsf = float(self.results_grid.GetCellValue(row, 8))

                # Recalculate the area
                new_area = new_height * fwhm * (np.sqrt(2 * np.pi) / 2.355)
                self.results_grid.SetCellValue(row, 5, f"{new_area:.2f}")

                # Recalculate the relative area
                new_rel_area = new_area / rsf
                self.results_grid.SetCellValue(row, 10, f"{new_rel_area:.2f}")

                # Update the atomic percentages if necessary
                self.update_atomic_percentages()

            except ValueError:
                wx.MessageBox("Invalid height value", "Error", wx.OK | wx.ICON_ERROR)

    def calculate_peak_area(self, model, height, fwhm, fraction):
        if model == "Voigt":
            sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
            gamma = fraction * sigma
            amplitude = height / PeakFunctions.get_voigt_height(1, sigma, gamma)
            area = amplitude * (sigma * np.sqrt(2 * np.pi))
        elif model == "Pseudo-Voigt":
            sigma = fwhm / 2.355
            amplitude = height / PeakFunctions.get_pseudo_voigt_height(1, sigma, fraction)
            area = amplitude
        elif model in ["GL", "SGL", "Unfitted"]:
            area = height * fwhm * np.sqrt(np.pi / (4 * np.log(2)))
        else:
            raise ValueError(f"Unknown fitting model: {model}")
        return round(area, 2)

    def on_peak_params_cell_changed(self, event):
        row = event.GetRow()
        col = event.GetCol()
        new_value = self.peak_params_grid.GetCellValue(row, col)
        sheet_name = self.sheet_combobox.GetValue()
        peak_index = row // 2

        if col in [0,6, 9,10,11]:
            event.Veto()
            return
        # Allow only numeric input for specific columns in non-constraint rows
        elif col not in [1, 12, 13] and row % 2 == 0:
            try:
                float(new_value)  # This will handle integers, floats, and scientific notation
            except ValueError:
                event.Veto()
                return

        if new_value.lower() in ['fi', 'fix', 'fixe', 'fixed']:
            new_value = 'Fixed'
        elif new_value == 'F':
            new_value = 'F*1'
        elif new_value.startswith('#'):
            peak_value = float(self.peak_params_grid.GetCellValue(row-1, col))
            new_value = str(round(peak_value-float(new_value[1:]),2))+':'+str(round(peak_value+float(new_value[1:]),2))
        # Convert lowercase letters to uppercase
        elif new_value.lower() in 'abcdefghijklmnop':
            new_value = new_value.upper() + '*1'
            self.peak_params_grid.SetCellValue(row, col, new_value)

        # Convert lowercase to uppercase in expressions like a*0.5
        if '*' in new_value or '+' in new_value:
            parts = new_value.split('*' if '*' in new_value else '+')
            if len(parts) == 2 and parts[0].lower() in 'abcdefghij':
                parts[0] = parts[0].upper()
                new_value = ('*' if '*' in new_value else '+').join(parts)
                self.peak_params_grid.SetCellValue(row, col, new_value)

        if sheet_name in self.Data['Core levels'] and 'Fitting' in self.Data['Core levels'][sheet_name] and 'Peaks' in \
                self.Data['Core levels'][sheet_name]['Fitting']:
            peaks = self.Data['Core levels'][sheet_name]['Fitting']['Peaks']
            peak_keys = list(peaks.keys())

            if peak_index < len(peak_keys):
                correct_peak_key = peak_keys[peak_index]

                if row % 2 == 0:  # Main parameter row
                    if col == 1:  # Label
                        # Update the label while preserving order
                        new_peaks = {}
                        for i, (key, value) in enumerate(peaks.items()):
                            if i == peak_index:
                                new_peaks[new_value] = value
                            else:
                                new_peaks[key] = value
                        self.Data['Core levels'][sheet_name]['Fitting']['Peaks'] = new_peaks
                    elif col == 2:  # Position
                        peaks[correct_peak_key]['Position'] = float(new_value)
                    elif col in [3, 4, 5, 7, 8]:  # Height, FWHM, or L/G changed
                        height = float(self.peak_params_grid.GetCellValue(row, 3))
                        fwhm = float(self.peak_params_grid.GetCellValue(row, 4))
                        fraction = float(self.peak_params_grid.GetCellValue(row, 5))
                        tail_E = float(self.peak_params_grid.GetCellValue(row, 7))
                        tail_M = float(self.peak_params_grid.GetCellValue(row, 8))
                        model = peaks[correct_peak_key]['Fitting Model']

                        # Recalculate area
                        area = self.calculate_peak_area(model, height, fwhm, fraction)
                        self.update_ratios()
                        # Update grid and data
                        self.peak_params_grid.SetCellValue(row, 6, f"{area:.2f}")
                        peaks[correct_peak_key].update({
                            'Height': round(height, 2),
                            'FWHM': round(fwhm, 2),
                            'L/G': round(fraction, 2),
                            'Area': area,
                            'Tail E': tail_E,
                            'Tail M': tail_M
                        })
                    elif col == 12:  # Fitting Model changed
                        peaks[correct_peak_key]['Fitting Model'] = new_value

                        # Recalculate area with new model
                        height = float(self.peak_params_grid.GetCellValue(row, 3))
                        fwhm = float(self.peak_params_grid.GetCellValue(row, 4))
                        fraction = float(self.peak_params_grid.GetCellValue(row, 5))
                        area = self.calculate_peak_area(new_value, height, fwhm, fraction)

                        self.peak_params_grid.SetCellValue(row, 6, f"{area:.2f}")
                        peaks[correct_peak_key]['Area'] = area
                else:  # Constraint row
                    if col in [2, 3, 4, 5, 7, 8]:
                        constraint_keys = ['Position', 'Height', 'FWHM', 'L/G', 'Tail E', 'Tail M']
                        column_to_constraint = {2: 0, 3: 1, 4: 2, 5: 3, 7: 4, 8: 5}
                        constraint_key = constraint_keys[column_to_constraint[col]]

                        if 'Constraints' not in peaks[correct_peak_key]:
                            peaks[correct_peak_key]['Constraints'] = {}

                        # Set default constraints if cell is empty
                        if not new_value:
                            default_constraints = {
                                'Position': '0,1000',
                                'Height': '100,1e7',
                                'FWHM': '0.3,3.5',
                                'L/G': '5,80',
                                'Tail E': 'Fixed',
                                'Tail M': 'Fixed'
                            }
                            new_value = default_constraints[constraint_key]
                            self.peak_params_grid.SetCellValue(row, col, new_value)

                        peaks[correct_peak_key]['Constraints'][constraint_key] = new_value

            # Ensure numeric values are displayed with 2 decimal places
        if col in [2, 3, 4, 5,7,8] and row % 2 == 0:  # Only for main parameter rows, not constraint rows
            try:
                formatted_value = f"{float(new_value):.2f}"
                self.peak_params_grid.SetCellValue(row, col, formatted_value)
            except ValueError:
                pass

        event.Skip()

        # Refresh the grid to ensure it reflects the current state of self.Data
        self.refresh_peak_params_grid()

        # Replot the peaks with updated parameters
        self.clear_and_replot()

    def update_ratios(self):
        num_peaks = self.peak_params_grid.GetNumberRows() // 2
        if num_peaks < 1:
            return  # No peaks to calculate ratios for

        # Set first peak's ratios and split to 0.00
        self.peak_params_grid.SetCellValue(0, 9, "100.00")  # I ratio
        self.peak_params_grid.SetCellValue(0, 10, "100.00")  # A ratio
        self.peak_params_grid.SetCellValue(0, 11, "0.00")  # Split

        if num_peaks < 2:
            return  # No other ratios to calculate with only one peak

        # Get first peak's height and area
        first_position = float(self.peak_params_grid.GetCellValue(0, 2))
        first_height = float(self.peak_params_grid.GetCellValue(0, 3))
        first_area = float(self.peak_params_grid.GetCellValue(0, 6))

        for i in range(1, num_peaks):
            row = i * 2
            position = float(self.peak_params_grid.GetCellValue(row, 2))
            height = float(self.peak_params_grid.GetCellValue(row, 3))
            area = float(self.peak_params_grid.GetCellValue(row, 6))

            # Calculate ratios
            i_ratio = height / first_height if first_height != 0 else 0
            a_ratio = area / first_area if first_area != 0 else 0
            split = position - first_position

            # Update grid
            self.peak_params_grid.SetCellValue(row, 9, f"{i_ratio*100:.0f}")
            self.peak_params_grid.SetCellValue(row, 10, f"{a_ratio*100:.0f}")
            self.peak_params_grid.SetCellValue(row, 11, f"{split:.2f}")

        self.peak_params_grid.ForceRefresh()

    def refresh_peak_params_grid(self):
        sheet_name = self.sheet_combobox.GetValue()
        if sheet_name in self.Data['Core levels'] and 'Fitting' in self.Data['Core levels'][sheet_name] and 'Peaks' in \
                self.Data['Core levels'][sheet_name]['Fitting']:
            peaks = self.Data['Core levels'][sheet_name]['Fitting']['Peaks']
            for i, (peak_label, peak_data) in enumerate(peaks.items()):
                row = i * 2
                self.peak_params_grid.SetCellValue(row, 1, peak_label)
                self.peak_params_grid.SetCellValue(row, 2, f"{peak_data['Position']:.2f}")
                self.peak_params_grid.SetCellValue(row, 3, f"{peak_data['Height']:.2f}")
                self.peak_params_grid.SetCellValue(row, 4, f"{peak_data['FWHM']:.2f}")
                self.peak_params_grid.SetCellValue(row, 5, f"{peak_data['L/G']:.2f}")
                self.peak_params_grid.SetCellValue(row, 7, f"{peak_data['Tail E']:.2f}")
                self.peak_params_grid.SetCellValue(row, 8, f"{peak_data['Tail M']:.2f}")
                if 'Constraints' in peak_data:
                    self.peak_params_grid.SetCellValue(row + 1, 2, str(peak_data['Constraints'].get('Position', '')))
                    self.peak_params_grid.SetCellValue(row + 1, 3, str(peak_data['Constraints'].get('Height', '')))
                    self.peak_params_grid.SetCellValue(row + 1, 4, str(peak_data['Constraints'].get('FWHM', '')))
                    self.peak_params_grid.SetCellValue(row + 1, 5, str(peak_data['Constraints'].get('L/G', '')))
                    self.peak_params_grid.SetCellValue(row + 1, 7, str(peak_data['Constraints'].get('Tail E', '')))
                    self.peak_params_grid.SetCellValue(row + 1, 8, str(peak_data['Constraints'].get('Tail M', '')))
        self.peak_params_grid.ForceRefresh()

    def on_checkbox_update(self, event):
        row = event.GetRow()
        col = event.GetCol()

        if col == 7:  # Checkbox column
            current_value = self.results_grid.GetCellValue(row, col)
            new_value = '1' if current_value == '0' else '0'
            self.results_grid.SetCellValue(row, col, new_value)

            sheet_name = self.sheet_combobox.GetValue()
            peak_label = f"Peak_{row}"  # Construct the peak_label based on the row
            if 'Results' in self.Data and 'Peak' in self.Data['Results'] and peak_label in self.Data['Results']['Peak']:
                self.Data['Results']['Peak'][peak_label]['Checkbox'] = new_value

            print(f"Checkbox updated: {peak_label}, New value: {new_value}")
            self.update_atomic_percentages()
            self.results_grid.ForceRefresh()

        event.Skip()

    def on_key_down(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_DELETE:
            selected_rows = self.get_selected_rows()
            if selected_rows:
                selected_rows.sort(reverse=True)
                for row in selected_rows:
                    peak_name = self.results_grid.GetCellValue(row, 0)  # Get the peak name from the first column
                    self.results_grid.DeleteRows(row)

                    # Remove the peak from self.Data
                    for key, value in list(self.Data['Results']['Peak'].items()):
                        if value.get('Name') == peak_name:
                            del self.Data['Results']['Peak'][key]
                            break

                # Renumber the remaining peaks in self.Data
                new_data = {}
                for i, (key, value) in enumerate(self.Data['Results']['Peak'].items()):
                    new_key = f"Peak_{i}"
                    new_data[new_key] = value
                self.Data['Results']['Peak'] = new_data

                self.results_grid.ForceRefresh()
                self.update_atomic_percentages()
        else:
            event.Skip()

    def refresh_results_grid(self):
        self.results_grid.ClearGrid()
        for i, (peak_label, peak_data) in enumerate(self.Data['Results']['Peak'].items()):
            for j, value in enumerate(peak_data.values()):
                self.results_grid.SetCellValue(i, j, str(value))

    def get_selected_rows(self):
        """
        Get a list of selected rows in the grid.
        """
        selected_rows = []
        for row in range(self.results_grid.GetNumberRows()):
            if self.results_grid.IsInSelection(row, 0):  # Check if the row is selected
                selected_rows.append(row)
        return selected_rows





    def deselect_all_peaks(self):
        self.selected_peak_index = None
        self.remove_cross_from_peak()

        # Clear any selections in the peak_params_grid
        self.peak_params_grid.ClearSelection()

        # If you want to uncheck any checkboxes in the results_grid
        for row in range(self.results_grid.GetNumberRows()):
            self.results_grid.SetCellValue(row, 7, '0')  # Assuming column 7 is the checkbox column

        self.update_peak_plot(None, None, remove_old_peaks=True)

        # Refresh both grids
        self.peak_params_grid.ForceRefresh()
        self.results_grid.ForceRefresh()



    def set_max_iterations(self, value):
        self.max_iterations = value

    def set_fitting_method(self, method):
        self.selected_fitting_method = method
        # print("Set Fitting Method: "+ str(method))

    def set_background_method(self, method):
        self.background_method = method
        # print(f"Updated background method to: {self.background_method}")

    # Method to update Offset (H)
    def set_offset_h(self, value):
        try:
            self.offset_h = float(value)
        except ValueError:
            self.offset_h = 0

    def set_offset_l(self, value):
        try:
            self.offset_l = float(value)
        except ValueError:
            self.offset_l = 0





    def get_data_for_save2(self):
        data = {
            'x_values': self.x_values,
            'y_values': self.y_values,
            'background': self.background if hasattr(self, 'background') else None,
            'calculated_fit': None,
            'individual_peak_fits': [],
            'peak_params_grid': self.peak_params_grid if hasattr(self, 'peak_params_grid') else None,
            'results_grid': self.results_grid if hasattr(self, 'results_grid') else None
        }

        # Use existing fit_peaks function to get the fit data
        from Functions import fit_peaks
        fit_result = fit_peaks(self, self.peak_params_grid)

        if fit_result:
            r_squared, chi_square, red_chi_square = fit_result

            # The overall fit (envelope) is stored as 'fitted_peak' in fit_peaks
            if hasattr(self, 'ax'):
                for line in self.ax.lines:
                    if line.get_label() == 'Envelope':
                        data['calculated_fit'] = line.get_ydata()
                        break

            # Individual peaks are stored as fill_between plots
            if hasattr(self, 'ax'):
                for collection in self.ax.collections:
                    if collection.get_label().startswith(self.sheet_combobox.GetValue()):
                        data['individual_peak_fits'].append(collection.get_paths()[0].vertices[:, 1])

        return data

    def get_data_for_save(self):
        data = {
            'x_values': self.x_values,
            'y_values': self.y_values,
            'background': self.background if hasattr(self, 'background') else None,
            'calculated_fit': None,
            'residuals': None,
            'individual_peak_fits': [],
            'peak_params_grid': self.peak_params_grid if hasattr(self, 'peak_params_grid') else None,
            'results_grid': self.results_grid if hasattr(self, 'results_grid') else None
        }

        # Use existing fit_peaks function to get the fit data
        from Functions import fit_peaks
        fit_result = fit_peaks(self, self.peak_params_grid)

        if fit_result:
            r_squared, chi_square, red_chi_square = fit_result

            if hasattr(self, 'ax'):
                for line in self.ax.lines:
                    if line.get_label() == 'Overall Fit':
                        data['calculated_fit'] = line.get_ydata()
                    elif line.get_label() == 'Residuals':
                        data['residuals'] = line.get_ydata()

                # Individual peaks are stored as fill_between plots
                for collection in self.ax.collections:
                    if collection.get_label().startswith(self.sheet_combobox.GetValue()):
                        data['individual_peak_fits'].append(collection.get_paths()[0].vertices[:, 1])

        return data

    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                self.plot_style = config.get('plot_style', self.plot_style)
                self.scatter_size = config.get('scatter_size', self.scatter_size)
                self.line_width = config.get('line_width', self.line_width)
                self.line_alpha = config.get('line_alpha', self.line_alpha)
                self.scatter_color = config.get('scatter_color', self.scatter_color)
                self.line_color = config.get('line_color', self.line_color)
                self.scatter_marker = config.get('scatter_marker', self.scatter_marker)
                self.background_color = config.get('background_color', self.background_color)
                self.background_alpha = config.get('background_alpha', self.background_alpha)
                self.background_linestyle = config.get('background_linestyle', self.background_linestyle)
                self.envelope_color = config.get('envelope_color', self.envelope_color)
                self.envelope_alpha = config.get('envelope_alpha', self.envelope_alpha)
                self.envelope_linestyle = config.get('envelope_linestyle', self.envelope_linestyle)
                self.residual_color = config.get('residual_color', self.residual_color)
                self.residual_alpha = config.get('residual_alpha', self.residual_alpha)
                self.residual_linestyle = config.get('residual_linestyle', self.residual_linestyle)
                self.raw_data_linestyle = config.get('raw_data_linestyle', self.raw_data_linestyle)
                self.peak_colors = config.get('peak_colors', self.peak_colors)
                self.peak_alpha = config.get('peak_alpha', self.peak_alpha)
        else:
            print("No config file found, using default values.")

    def save_config(self):
        config = {
            'plot_style': self.plot_style,
            'scatter_size': self.scatter_size,
            'line_width': self.line_width,
            'line_alpha': self.line_alpha,
            'scatter_color': self.scatter_color,
            'line_color': self.line_color,
            'scatter_marker': self.scatter_marker,
            'background_color': self.background_color,
            'background_alpha': self.background_alpha,
            'background_linestyle': self.background_linestyle,
            'envelope_color': self.envelope_color,
            'envelope_alpha': self.envelope_alpha,
            'envelope_linestyle': self.envelope_linestyle,
            'residual_color': self.residual_color,
            'residual_alpha': self.residual_alpha,
            'residual_linestyle': self.residual_linestyle,
            'raw_data_linestyle': self.raw_data_linestyle,
            'peak_colors': self.peak_colors,
            'peak_alpha': self.peak_alpha
        }

        with open('config.json', 'w') as f:
            json.dump(config, f)



    def on_preferences(self, event):
        pref_window = PreferenceWindow(self)
        pref_window.Show()

    def update_plot_preferences(self):
        self.plot_manager.update_plot_style(
            self.plot_style,
            self.scatter_size,
            self.line_width,
            self.line_alpha,
            self.scatter_color,
            self.line_color,
            self.scatter_marker,
            self.background_color,
            self.background_alpha,
            self.background_linestyle,
            self.envelope_color,
            self.envelope_alpha,
            self.envelope_linestyle,
            self.residual_color,
            self.residual_alpha,
            self.residual_linestyle,
            self.raw_data_linestyle,
            self.peak_colors,  # Add this line
            self.peak_alpha  # Add this line
        )

        if hasattr(self, 'sheet_combobox'):
            selected_sheet = self.sheet_combobox.GetValue()
            if selected_sheet and 'FilePath' in self.Data and self.Data['FilePath']:
                self.clear_and_replot()
            else:
                print("No sheet selected or no file open. Skipping replot.")
        else:
            print("sheet_combobox not created yet. Skipping replot.")

        if hasattr(self, 'canvas'):
            self.canvas.draw_idle()

    def on_be_correction_change(self, event):
        new_correction = self.be_correction_spinbox.GetValue()
        self.apply_be_correction(new_correction)

    def on_auto_be(self, event):
        c1s_correction = self.calculate_c1s_correction()
        if c1s_correction is not None:
            self.be_correction_spinbox.SetValue(c1s_correction)
            self.apply_be_correction(c1s_correction)

    def apply_be_correction(self, correction):
        delta_correction = correction - self.be_correction
        self.be_correction = correction

        # Update window.Data
        self.Data['BEcorrection'] = correction

        # Update all sheets
        for sheet_name, sheet_data in self.Data['Core levels'].items():
            # Update B.E. values
            sheet_data['B.E.'] = [be + delta_correction for be in sheet_data['B.E.']]

            # Update Background Low and High if they exist
            if 'Background' in sheet_data:
                if 'Bkg Low' in sheet_data['Background']:
                    sheet_data['Background']['Bkg Low'] += delta_correction
                if 'Bkg High' in sheet_data['Background']:
                    sheet_data['Background']['Bkg High'] += delta_correction

            # Update peak positions in Fitting data
            if 'Fitting' in sheet_data and 'Peaks' in sheet_data['Fitting']:
                for peak in sheet_data['Fitting']['Peaks'].values():
                    peak['Position'] += delta_correction

        # Update plot limits
        for sheet_name in self.Data['Core levels']:
            if sheet_name in self.plot_config.plot_limits:
                limits = self.plot_config.plot_limits[sheet_name]
                limits['Xmin'] += delta_correction
                limits['Xmax'] += delta_correction

        # Update current sheet display
        current_sheet = self.sheet_combobox.GetValue()
        on_sheet_selected(self, current_sheet)

        # Update plots
        self.plot_manager.update_plots_be_correction(self, delta_correction)

        print(f"Applied BE correction of {correction:.2f} eV")

    def calculate_c1s_correction(self):
        c1s_sheet = next((sheet for sheet in self.Data['Core levels'] if sheet.startswith('C1s')), None)
        if c1s_sheet:
            c1s_peaks = self.Data['Core levels'][c1s_sheet]['Fitting']['Peaks']
            c_c_peak = next((peak for label, peak in c1s_peaks.items() if 'C-C' in label), None)
            if c_c_peak:
                return 284.8 - c_c_peak['Position']
        return None

    def load_be_correction(self):
        if 'BEcorrection' in self.Data:
            self.be_correction = self.Data['BEcorrection']
            self.be_correction_spinbox.SetValue(self.be_correction)

    def on_toggle_peak_fill(self, event):
        new_state = self.plot_manager.toggle_peak_fill()
        self.clear_and_replot()
        print(f"Peak fill toggled in main window. New state: {new_state}")  # Debugging line

    def on_mini_help(self, event):
        from libraries.Help import show_quick_help
        show_quick_help(self)




if __name__ == '__main__':

    app = wx.App(False)
    splash = show_splash(duration=3000, delay=2)

    frame = MyFrame(None, "KherveFitting - V1.0 - Sept 2024")
    frame.Show(True)

    if splash:
        splash.Destroy()

    # print("Entering app.MainLoop()")
    app.MainLoop()

