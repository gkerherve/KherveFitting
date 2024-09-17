# In libraries/Widgets_Toolbars.py

import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from libraries.Sheet_Operations import CheckboxRenderer
from libraries.Open import ExcelDropTarget
from libraries.Plot_Operations import PlotManager
from Functions import create_menu, create_statusbar, create_horizontal_toolbar, create_vertical_toolbar, toggle_Col_1
from libraries.Save import update_undo_redo_state


def create_widgets(window):
    # Main sizer
    main_sizer = wx.BoxSizer(wx.HORIZONTAL)

    # Create the vertical toolbar as a child of the panel
    window.v_toolbar = create_vertical_toolbar(window.panel, window)

    # Content sizer (everything except vertical toolbar)
    content_sizer = wx.BoxSizer(wx.HORIZONTAL)

    # Create a splitter window
    window.splitter = wx.SplitterWindow(window.panel, style=wx.SP_LIVE_UPDATE)

    # Right frame for the plot
    window.right_frame = wx.Panel(window.splitter)
    window.right_frame.SetBackgroundColour(wx.Colour(255, 255, 255))
    right_frame_sizer = wx.BoxSizer(wx.VERTICAL)

    # Create the FigureCanvas
    window.canvas = FigureCanvas(window.right_frame, -1, window.figure)

    # Set up drag and drop for Excel files
    file_drop_target = ExcelDropTarget(window)
    window.canvas.SetDropTarget(file_drop_target)

    plt.tight_layout()
    right_frame_sizer.Add(window.canvas, 1, wx.EXPAND | wx.ALL, 0)

    # Initialize plot_manager
    window.plot_manager = PlotManager(window.ax, window.canvas)
    window.plot_manager.plot_initial_logo()

    # Update plot manager with loaded or default values
    window.update_plot_preferences()

    # Create a hidden NavigationToolbar
    window.navigation_toolbar = NavigationToolbar(window.canvas)
    window.navigation_toolbar.Hide()

    window.right_frame.SetSizer(right_frame_sizer)

    # Create grids panel
    grids_panel = create_grids_panel(window)

    # Set up the splitter
    window.splitter.SplitVertically(window.right_frame, grids_panel)
    window.splitter.SetMinimumPaneSize(0)
    window.splitter.SetSashGravity(0.5)

    # Set initial sash position
    window.initial_sash_position = 800
    window.splitter.SetSashPosition(window.initial_sash_position)

    # Add splitter to content sizer
    content_sizer.Add(window.splitter, 1, wx.EXPAND | wx.ALL, 5)

    # Add vertical toolbar and content sizer to main sizer
    main_sizer.Add(window.v_toolbar, 0, wx.EXPAND)
    main_sizer.Add(content_sizer, 1, wx.EXPAND)

    window.panel.SetSizer(main_sizer)

    # Create the horizontal toolbar
    window.toolbar = create_horizontal_toolbar(window)
    update_undo_redo_state(window)
    toggle_Col_1(window)

    # Bind events
    bind_events(window)


def create_grids_panel(window):
    grids_panel = wx.Panel(window.splitter)
    grids_sizer = wx.BoxSizer(wx.VERTICAL)

    # Create peak params grid
    peak_params_sizer = create_peak_params_grid(window, grids_panel)
    grids_sizer.Add(peak_params_sizer, 1, wx.EXPAND | wx.ALL, 5)

    # Create results grid
    results_sizer = create_results_grid(window, grids_panel)
    grids_sizer.Add(results_sizer, 1, wx.EXPAND | wx.ALL, 5)

    grids_panel.SetSizer(grids_sizer)
    return grids_panel


def create_peak_params_grid(window, parent):
    peak_params_frame_box = wx.StaticBox(parent, label="Peak Fitting Parameters")
    peak_params_sizer = wx.StaticBoxSizer(peak_params_frame_box, wx.VERTICAL)

    window.peak_params_frame = wx.Panel(peak_params_frame_box)
    window.peak_params_frame.SetBackgroundColour(wx.Colour(255, 255, 255))
    peak_params_sizer_inner = wx.BoxSizer(wx.VERTICAL)

    window.peak_params_grid = wx.grid.Grid(window.peak_params_frame)
    window.peak_params_grid.CreateGrid(0, 18)

    # Set column labels and sizes
    column_labels = ["ID", "Label", "Position", "Height", "FWHM", "L/G", "Area", "Tail E", "Tail M",
                     "I ratio", "A ratio", "Split", "Fitting Model", "Bkg Type", "Bkg Low", "Bkg High",
                     "Bkg Offset Low", "Bkg Offset High"]
    for i, label in enumerate(column_labels):
        window.peak_params_grid.SetColLabelValue(i, label)

    # Set grid properties
    window.peak_params_grid.SetDefaultRowSize(25)
    window.peak_params_grid.SetDefaultColSize(60)
    window.peak_params_grid.SetLabelBackgroundColour(wx.Colour(255, 255, 255))
    window.peak_params_grid.SetDefaultCellBackgroundColour(window.peak_params_grid.GetLabelBackgroundColour())
    window.peak_params_grid.SetRowLabelSize(25)
    window.peak_params_grid.SetColLabelSize(20)

    # Adjust individual column sizes
    col_sizes = [20, 90, 80, 80, 80, 50, 60, 50, 50, 60, 60, 60, 100, 80, 80, 80, 100, 100]
    for i, size in enumerate(col_sizes):
        window.peak_params_grid.SetColSize(i, size)

    peak_params_sizer_inner.Add(window.peak_params_grid, 1, wx.EXPAND | wx.ALL, 5)
    window.peak_params_frame.SetSizer(peak_params_sizer_inner)
    peak_params_sizer.Add(window.peak_params_frame, 1, wx.EXPAND | wx.ALL, 5)

    return peak_params_sizer


def create_results_grid(window, parent):
    results_frame_box = wx.StaticBox(parent, label="Results")
    results_sizer = wx.StaticBoxSizer(results_frame_box, wx.VERTICAL)

    window.results_frame = wx.Panel(results_frame_box)
    results_sizer_inner = wx.BoxSizer(wx.VERTICAL)

    window.results_grid = wx.grid.Grid(window.results_frame)
    window.results_grid.CreateGrid(0, 23)

    # Set column labels and properties for results grid
    column_labels = ["Peak", "Position", "Height", "FWHM", "L/G", "Area", "at. %", " ", "RSF", "Fitting Model",
                     "Rel. Area", "Tail E", "Tail M", "Bkg Type", "Bkg Low", "Bkg High", "Bkg Offset Low",
                     "Bkg Offset High", "Sheetname", "Pos. Constraint", "Height Constraint", "FWHM Constraint",
                     "L/G Constraint"]
    for i, label in enumerate(column_labels):
        window.results_grid.SetColLabelValue(i, label)

    window.results_grid.SetDefaultRowSize(25)
    window.results_grid.SetDefaultColSize(60)
    window.results_grid.SetRowLabelSize(25)
    window.results_grid.SetColLabelSize(20)
    window.results_grid.SetLabelBackgroundColour(wx.Colour(255, 255, 255))
    window.results_grid.SetDefaultCellBackgroundColour(window.results_grid.GetLabelBackgroundColour())

    # Adjust specific column sizes
    col_sizes = [120, 70, 70, 70, 50, 80, 50, 20, 50, 90, 90, 50, 50, 80, 70, 70, 100, 100, 80, 120, 120, 120, 120]
    for i, size in enumerate(col_sizes):
        window.results_grid.SetColSize(i, size)

    # Set renderer for checkbox column
    checkbox_renderer = CheckboxRenderer()
    for row in range(window.results_grid.GetNumberRows()):
        window.results_grid.SetCellRenderer(row, 7, checkbox_renderer)

    results_sizer_inner.Add(window.results_grid, 1, wx.EXPAND | wx.ALL, 5)
    window.results_frame.SetSizer(results_sizer_inner)
    results_sizer.Add(window.results_frame, 1, wx.EXPAND | wx.ALL, 5)

    return results_sizer


def bind_events(window):
    window.results_grid.Bind(wx.EVT_KEY_DOWN, window.on_key_down)
    window.peak_params_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, window.on_grid_select)
    window.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, window.on_splitter_changed)
    window.results_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, window.on_checkbox_update)
    window.canvas.mpl_connect('button_release_event', window.on_plot_mouse_release)
    window.peak_params_grid.Bind(wx.EVT_LEFT_UP, window.on_peak_params_mouse_release)



#--------------KEEP PREVIOUS DEF JUST IN CASE

def create_widgets_MAIN(self):
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

    # After creating self.canvas
    file_drop_target = ExcelDropTarget(self)
    self.canvas.SetDropTarget(file_drop_target)

    plt.tight_layout()
    right_frame_sizer.Add(self.canvas, 1, wx.EXPAND | wx.ALL, 0)

    # Initialize plot_manager after self.ax and self.canvas are created
    self.plot_manager = PlotManager(self.ax, self.canvas)
    self.plot_manager.plot_initial_logo()



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
    self.initial_sash_position = 800  # Adjust this value as needed
    self.splitter.SetSashPosition(self.initial_sash_position)

    # Add splitter to content sizer
    content_sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL, 5)

    # Add vertical toolbar and content sizer to main sizer
    main_sizer.Add(self.v_toolbar, 0, wx.EXPAND)
    main_sizer.Add(content_sizer, 1, wx.EXPAND)

    self.panel.SetSizer(main_sizer)

    # Create the horizontal toolbar
    self.toolbar = create_horizontal_toolbar(self)
    update_undo_redo_state(self)
    toggle_Col_1(self)


    # Bind events
    self.results_grid.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
    self.peak_params_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_grid_select)
    self.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_splitter_changed)
    # self.results_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, lambda event: on_grid_left_click(self, event))
    self.results_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.on_checkbox_update)
    self.canvas.mpl_connect('button_release_event', self.on_plot_mouse_release)
    self.peak_params_grid.Bind(wx.EVT_LEFT_UP, self.on_peak_params_mouse_release)

