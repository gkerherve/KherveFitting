# In libraries/Widgets_Toolbars.py
import os
import sys
import wx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from libraries.Sheet_Operations import CheckboxRenderer
from libraries.Open import ExcelDropTarget
from libraries.Plot_Operations import PlotManager
from Functions import create_statusbar, toggle_Col_1
from libraries.Save import update_undo_redo_state

from Functions import open_xlsx_file, on_save, save_all_sheets_with_plots, save_results_table, open_vamas_file_dialog, \
    import_avantage_file, open_avg_file, import_multiple_avg_files, create_plot_script_from_excel, on_save_plot, \
    on_save_plot_pdf, on_save_plot_svg, on_exit, undo, redo, toggle_plot, show_shortcuts, on_about


from Functions import open_xlsx_file, refresh_sheets, on_sheet_selected_wrapper, toggle_plot, on_save, on_save_plot, on_save_all_sheets, toggle_Col_1, undo, redo



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
    bind_events_widgets(window)


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


def bind_events_widgets(window):
    window.results_grid.Bind(wx.EVT_KEY_DOWN, window.on_key_down)
    window.peak_params_grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, window.on_grid_select)
    window.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, window.on_splitter_changed)
    window.results_grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, window.on_checkbox_update)
    window.canvas.mpl_connect('button_release_event', window.on_plot_mouse_release)
    window.peak_params_grid.Bind(wx.EVT_LEFT_UP, window.on_peak_params_mouse_release)



def create_menu(window):
    menubar = wx.MenuBar()

    # Create menus
    file_menu = wx.Menu()
    import_menu = wx.Menu()
    export_menu = wx.Menu()
    edit_menu = wx.Menu()
    view_menu = wx.Menu()
    tools_menu = wx.Menu()
    help_menu = wx.Menu()
    save_menu = wx.Menu()

    # File menu items
    open_item = file_menu.Append(wx.ID_OPEN, "Open \tCtrl+O")
    window.Bind(wx.EVT_MENU, lambda event: open_xlsx_file(window), open_item)

    save_Excel_item = file_menu.Append(wx.ID_SAVE, "Save Sheet \tCtrl+S")
    window.Bind(wx.EVT_MENU, lambda event: on_save(window), save_Excel_item)

    # Save submenu items
    save_all_item = save_menu.Append(wx.NewId(), "Save All")
    window.Bind(wx.EVT_MENU, lambda event: save_all_sheets_with_plots(window), save_all_item)

    save_Excel_item2 = save_menu.Append(wx.NewId(), "Save Sheet")
    window.Bind(wx.EVT_MENU, lambda event: on_save(window), save_Excel_item2)

    save_Table_item = save_menu.Append(wx.NewId(), "Save Results Table")
    window.Bind(wx.EVT_MENU, lambda event: save_results_table(window), save_Table_item)

    file_menu.AppendSubMenu(save_menu, "Save")

    # Import submenu items
    import_vamas_item = import_menu.Append(wx.NewId(), "Import Vamas file")
    window.Bind(wx.EVT_MENU, lambda event: open_vamas_file_dialog(window), import_vamas_item)

    import_avantage_item = import_menu.Append(wx.NewId(), "Import Avantage file")
    window.Bind(wx.EVT_MENU, lambda event: import_avantage_file(window), import_avantage_item)

    import_avg_item = import_menu.Append(wx.NewId(), "Import AVG file")
    window.Bind(wx.EVT_MENU, lambda event: open_avg_file(window), import_avg_item)

    import_multiple_avg_item = import_menu.Append(wx.NewId(), "Import Multiple AVG files")
    window.Bind(wx.EVT_MENU, lambda event: import_multiple_avg_files(window), import_multiple_avg_item)

    # Export submenu items
    export_python_plot_item = export_menu.Append(wx.NewId(), "Python Plot")
    window.Bind(wx.EVT_MENU, lambda event: create_plot_script_from_excel(window), export_python_plot_item)

    save_plot_item = export_menu.Append(wx.NewId(), "Export as PNG")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot(window), save_plot_item)

    save_plot_item_pdf = export_menu.Append(wx.NewId(), "Export as PDF")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot_pdf(window), save_plot_item_pdf)

    save_plot_item_svg = export_menu.Append(wx.NewId(), "Export as SVG")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot_svg(window), save_plot_item_svg)

    # Recent files submenu
    window.recent_files_menu = wx.Menu()
    file_menu.AppendSubMenu(window.recent_files_menu, "Recent Files")

    # Append submenus to file menu
    file_menu.AppendSubMenu(import_menu, "Import")
    file_menu.AppendSubMenu(export_menu, "Export")

    # Exit item
    file_menu.AppendSeparator()
    exit_item = file_menu.Append(wx.ID_EXIT, "Exit\tCtrl+Q")
    window.Bind(wx.EVT_MENU, lambda event: on_exit(window, event), exit_item)

    # Edit menu items
    undo_item = edit_menu.Append(wx.ID_UNDO, "Undo\tCtrl+Z")
    redo_item = edit_menu.Append(wx.ID_REDO, "Redo\tCtrl+Y")
    window.Bind(wx.EVT_MENU, lambda event: undo(window), undo_item)
    window.Bind(wx.EVT_MENU, lambda event: redo(window), redo_item)
    edit_menu.AppendSeparator()

    preferences_item = edit_menu.Append(wx.ID_PREFERENCES, "Preferences")
    window.Bind(wx.EVT_MENU, window.on_preferences, preferences_item)

    # View menu items
    ToggleFitting_item = view_menu.Append(wx.NewId(), "Toggle Peak Fitting")
    window.Bind(wx.EVT_MENU, lambda event: toggle_plot(window), ToggleFitting_item)

    ToggleLegend_item = view_menu.Append(wx.NewId(), "Toggle Legend")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_legend(), ToggleLegend_item)

    ToggleFit_item = view_menu.Append(wx.NewId(), "Toggle Fit Results")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_fitting_results(), ToggleFit_item)

    ToggleRes_item = view_menu.Append(wx.NewId(), "Toggle Residuals")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_residuals(), ToggleRes_item)

    toggle_energy_item = view_menu.AppendCheckItem(wx.NewId(), "Show Kinetic Energy\tCtrl+B")
    window.Bind(wx.EVT_MENU, lambda event: window.toggle_energy_scale(), toggle_energy_item)
    window.toggle_energy_item = toggle_energy_item

    # Tools menu items
    Area_item = tools_menu.Append(wx.NewId(), "Calculate Area\tCtrl+A")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_background_window(), Area_item)

    Fitting_item = tools_menu.Append(wx.NewId(), "Peak Fitting\tCtrl+P")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_fitting_window(), Fitting_item)

    Noise_item = tools_menu.Append(wx.NewId(), "Noise Analysis")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_noise_analysis_window, Noise_item)

    # Help menu items
    mini_help_item = help_menu.Append(wx.NewId(), "Help")
    window.Bind(wx.EVT_MENU, window.on_mini_help, mini_help_item)

    shortcuts_item = help_menu.Append(wx.NewId(), "List of Shortcuts\tCtrl+K")
    window.Bind(wx.EVT_MENU, lambda event: show_shortcuts(window), shortcuts_item)

    about_item = help_menu.Append(wx.ID_ABOUT, "About")
    window.Bind(wx.EVT_MENU, lambda event: on_about(window, event), about_item)

    # Add menus to menubar
    menubar.Append(file_menu, "&File")
    menubar.Append(edit_menu, "&Edit")
    menubar.Append(view_menu, "&View")
    menubar.Append(tools_menu, "&Tools")
    menubar.Append(help_menu, "&Help")

    window.SetMenuBar(menubar)

def create_horizontal_toolbar(window):
    toolbar = window.CreateToolBar()
    toolbar.SetBackgroundColour(wx.Colour(220, 220, 220))
    toolbar.SetToolBitmapSize(wx.Size(25, 25))

    # Determine the correct path for icons
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(application_path, "Icons")

    separators = []

    # File operations
    open_file_tool = toolbar.AddTool(wx.ID_ANY, 'Open File', wx.Bitmap(os.path.join(icon_path, "open-folder-25-green.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open File\tCtrl+O")
    refresh_folder_tool = toolbar.AddTool(wx.ID_ANY, 'Refresh Excel File', wx.Bitmap(os.path.join(icon_path, "refresh-96g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Refresh Excel File")
    save_tool = toolbar.AddTool(wx.ID_ANY, 'Save', wx.Bitmap(os.path.join(icon_path, "save-Excel-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save the Fitted Results to Excel for this Core Level \tCtrl+S")
    save_plot_tool = toolbar.AddTool(wx.ID_ANY, 'Save Plot', wx.Bitmap(os.path.join(icon_path, "save-PNG-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save this Figure to Excel")
    save_all_tool = toolbar.AddTool(wx.ID_ANY, 'Save All Sheets', wx.Bitmap(os.path.join(icon_path, "save-Multi-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save all sheets with plots")

    toolbar.AddSeparator()
    window.undo_tool = toolbar.AddTool(wx.ID_ANY, 'Undo', wx.Bitmap(os.path.join(icon_path, "undo-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Undo -- For peaks properties only")
    window.redo_tool = toolbar.AddTool(wx.ID_ANY, 'Redo', wx.Bitmap(os.path.join(icon_path, "redo-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Redo -- For peaks properties only")
    toolbar.AddSeparator()

    # Skip rows spinbox
    window.skip_rows_spinbox = wx.SpinCtrl(toolbar, min=0, max=200, initial=0, size=(60, -1))
    window.skip_rows_spinbox.SetToolTip("Set the number of rows to skip in the sheet of the Excel file")
    toolbar.AddControl(window.skip_rows_spinbox)

    # Sheet selection
    window.sheet_combobox = wx.ComboBox(toolbar, style=wx.CB_READONLY)
    window.sheet_combobox.SetToolTip("Select Sheet")
    toolbar.AddControl(window.sheet_combobox)
    window.sheet_combobox.Bind(wx.EVT_COMBOBOX, lambda event: on_sheet_selected(window, event))

    toolbar.AddSeparator()
    add_vertical_separator(toolbar, separators)
    toolbar.AddSeparator()

    # BE correction
    window.be_correction_spinbox = wx.SpinCtrlDouble(toolbar, value='0.00', min=-20.00, max=20.00, inc=0.01, size=(70, -1))
    window.be_correction_spinbox.SetDigits(2)
    window.be_correction_spinbox.SetToolTip("BE Correction")
    toolbar.AddControl(window.be_correction_spinbox)

    auto_be_button = toolbar.AddTool(wx.ID_ANY, 'Auto BE', wx.Bitmap(os.path.join(icon_path, "BEcorrect-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Automatic binding energy correction")

    toolbar.AddSeparator()
    add_vertical_separator(toolbar, separators)
    toolbar.AddSeparator()

    # Plot adjustment tools
    plot_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Plot', wx.Bitmap(os.path.join(icon_path, "scatter-plot-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle between Raw Data and Fit")
    toggle_peak_fill_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Peak Fill', wx.Bitmap(os.path.join(icon_path, "STO-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Peak Fill")
    toggle_legend_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Legend', wx.Bitmap(os.path.join(icon_path, "Legend-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Legend")
    toggle_fit_results_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Fit Results', wx.Bitmap(os.path.join(icon_path, "ToggleFit-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Fit Results")
    toggle_residuals_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Residuals', wx.Bitmap(os.path.join(icon_path, "Res-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Residuals")

    toolbar.AddSeparator()
    add_vertical_separator(toolbar, separators)
    toolbar.AddSeparator()

    # Analysis tools
    bkg_tool = toolbar.AddTool(wx.ID_ANY, 'Background', wx.Bitmap(os.path.join(icon_path, "BKG-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Calculate Area \tCtrl+A")
    fitting_tool = toolbar.AddTool(wx.ID_ANY, 'Fitting', wx.Bitmap(os.path.join(icon_path, "C1s-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open Fitting Window \tCtrl+P")
    noise_analysis_tool = toolbar.AddTool(wx.ID_ANY, 'Noise Analysis', wx.Bitmap(os.path.join(icon_path, "Noise-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Open Noise Analysis Window")

    toolbar.AddSeparator()
    add_vertical_separator(toolbar, separators)
    toolbar.AddSeparator()

    id_tool = toolbar.AddTool(wx.ID_ANY, 'ID', wx.Bitmap(os.path.join(icon_path, "ID-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Element identifications")

    toolbar.AddStretchableSpace()

    # Export and toggle tools
    export_tool = toolbar.AddTool(wx.ID_ANY, 'Export Results', wx.Bitmap(os.path.join(icon_path, "Export-25g.png"), wx.BITMAP_TYPE_PNG), shortHelp="Export to Results Grid")
    toggle_Col_1_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Residuals', wx.Bitmap(os.path.join(icon_path, "HideColumn-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Toggle Columns Peak Fitting Parameters")
    window.toggle_right_panel_tool = window.add_toggle_tool(toolbar, "Toggle Right Panel", wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR))

    toolbar.Realize()

    # Bind events
    bind_toolbar_events(window, open_file_tool, refresh_folder_tool, plot_tool, bkg_tool, fitting_tool, noise_analysis_tool,
                        toggle_legend_tool, toggle_fit_results_tool, toggle_residuals_tool, save_tool, save_plot_tool,
                        save_all_tool, toggle_Col_1_tool, export_tool, auto_be_button, toggle_peak_fill_tool, id_tool)

    return toolbar

def add_vertical_separator(toolbar, separators):
    separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    separators[-1].SetSize((2, 24))
    toolbar.AddControl(separators[-1])

def bind_toolbar_events(window, open_file_tool, refresh_folder_tool, plot_tool, bkg_tool, fitting_tool, noise_analysis_tool,
                        toggle_legend_tool, toggle_fit_results_tool, toggle_residuals_tool, save_tool, save_plot_tool,
                        save_all_tool, toggle_Col_1_tool, export_tool, auto_be_button, toggle_peak_fill_tool, id_tool):
    window.Bind(wx.EVT_TOOL, lambda event: open_xlsx_file(window), open_file_tool)
    window.Bind(wx.EVT_TOOL, lambda event: refresh_sheets(window, on_sheet_selected_wrapper), refresh_folder_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_plot(window), plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_background_window(), bkg_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_fitting_window(), fitting_tool)
    window.Bind(wx.EVT_TOOL, window.on_open_noise_analysis_window, noise_analysis_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_legend(), toggle_legend_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_fitting_results(), toggle_fit_results_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_residuals(), toggle_residuals_tool)
    window.sheet_combobox.Bind(wx.EVT_COMBOBOX, lambda event: on_sheet_selected_wrapper(window, event))
    window.Bind(wx.EVT_TOOL, lambda event: on_save(window), save_tool)
    window.Bind(wx.EVT_TOOL, lambda event: on_save_plot(window), save_plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: on_save_all_sheets(window, event), save_all_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_Col_1(window), toggle_Col_1_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.export_results(), export_tool)
    window.be_correction_spinbox.Bind(wx.EVT_SPINCTRLDOUBLE, window.on_be_correction_change)
    window.Bind(wx.EVT_TOOL, window.on_auto_be, auto_be_button)
    window.Bind(wx.EVT_TOOL, window.on_toggle_peak_fill, toggle_peak_fill_tool)
    window.Bind(wx.EVT_TOOL, lambda event: undo(window), window.undo_tool)
    window.Bind(wx.EVT_TOOL, lambda event: redo(window), window.redo_tool)
    window.Bind(wx.EVT_TOOL, window.open_periodic_table, id_tool)
    window.Bind(wx.EVT_TOOL, window.on_toggle_right_panel, window.toggle_right_panel_tool)


def create_vertical_toolbar(parent, frame):
    v_toolbar = wx.ToolBar(parent, style=wx.TB_VERTICAL | wx.TB_FLAT)
    v_toolbar.SetBackgroundColour(wx.Colour(220, 220, 220))
    v_toolbar.SetToolBitmapSize(wx.Size(25, 25))

    # Get the correct path for icons
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "Icons")

    # Zoom tools
    zoom_in_tool = v_toolbar.AddTool(wx.ID_ANY, 'Zoom In',
                                     wx.Bitmap(os.path.join(icon_path, "ZoomIN-25.png"), wx.BITMAP_TYPE_PNG),
                                     shortHelp="Zoom In")
    zoom_out_tool = v_toolbar.AddTool(wx.ID_ANY, 'Zoom Out',
                                      wx.Bitmap(os.path.join(icon_path, "ZoomOUT-25.png"), wx.BITMAP_TYPE_PNG),
                                      shortHelp="Zoom Out")
    drag_tool = v_toolbar.AddTool(wx.ID_ANY, 'Drag',
                                  wx.Bitmap(os.path.join(icon_path, "drag-25.png"), wx.BITMAP_TYPE_PNG),
                                  shortHelp="Drag Plot")

    v_toolbar.AddSeparator()

    # BE adjustment tools
    high_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE +',
                                              wx.Bitmap(os.path.join(icon_path, "Right-Red-25g.png"), wx.BITMAP_TYPE_PNG),
                                              shortHelp="Decrease High BE")
    high_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE -',
                                              wx.Bitmap(os.path.join(icon_path, "Left-Red-25g.png"), wx.BITMAP_TYPE_PNG),
                                              shortHelp="Increase High BE")

    v_toolbar.AddSeparator()

    low_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE +',
                                             wx.Bitmap(os.path.join(icon_path, "Left-Blue-25g.png"), wx.BITMAP_TYPE_PNG),
                                             shortHelp="Increase Low BE")
    low_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE -',
                                             wx.Bitmap(os.path.join(icon_path, "Right-Blue-25g.png"), wx.BITMAP_TYPE_PNG),
                                             shortHelp="Decrease Low BE")

    v_toolbar.AddSeparator()

    # Intensity adjustment tools
    high_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int +',
                                               wx.Bitmap(os.path.join(icon_path, "Up-Red-25g.png"), wx.BITMAP_TYPE_PNG),
                                               shortHelp="Increase High Intensity")
    high_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int -',
                                               wx.Bitmap(os.path.join(icon_path, "Down-Red-25g.png"), wx.BITMAP_TYPE_PNG),
                                               shortHelp="Decrease High Intensity")

    v_toolbar.AddSeparator()

    low_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low Int +',
                                              wx.Bitmap(os.path.join(icon_path, "Up-Blue-25g.png"), wx.BITMAP_TYPE_PNG),
                                              shortHelp="Increase Low Intensity")
    low_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low Int -',
                                              wx.Bitmap(os.path.join(icon_path, "Down-Blue-25g.png"), wx.BITMAP_TYPE_PNG),
                                              shortHelp="Decrease Low Intensity")

    v_toolbar.AddSeparator()

    v_toolbar.Realize()

    # Bind events to the frame
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_be', 'increase'), high_be_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_be', 'decrease'), high_be_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_be', 'increase'), low_be_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_be', 'decrease'), low_be_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_int', 'increase'), high_int_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_int', 'decrease'), high_int_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_int', 'increase'), low_int_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_int', 'decrease'), low_int_decrease_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_zoom_in_tool, zoom_in_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_zoom_out, zoom_out_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_drag_tool, drag_tool)

    return v_toolbar


# --------------KEEP PREVIOUS DEF JUST IN CASE----------------------------------------------------
# ------------------------------------------------------------------------------------------------

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

def create_menu_FUNCTIONS(window):
    menubar = wx.MenuBar()
    file_menu = wx.Menu()
    import_menu = wx.Menu()
    export_menu = wx.Menu()
    edit_menu = wx.Menu()
    view_menu = wx.Menu()
    tools_menu = wx.Menu()
    help_menu = wx.Menu()
    save_menu = wx.Menu()

    open_item = file_menu.Append(wx.ID_OPEN, "Open \tCtrl+O")
    window.Bind(wx.EVT_MENU, lambda event: open_xlsx_file(window), open_item)

    save_Excel_item = file_menu.Append(wx.ID_SAVE, "Save Sheet \tCtrl+S")
    window.Bind(wx.EVT_MENU, lambda event: on_save(window), save_Excel_item)

    save_all_item = save_menu.Append(wx.NewId(), "Save All")
    window.Bind(wx.EVT_MENU, lambda event: save_all_sheets_with_plots(window), save_all_item)

    save_Excel_item2 = save_menu.Append(wx.NewId(), "Save Sheet")
    window.Bind(wx.EVT_MENU, lambda event: on_save(window), save_Excel_item2)

    save_Table_item = save_menu.Append(wx.NewId(), "Save Results Table")
    window.Bind(wx.EVT_MENU, lambda event: save_results_table(window), save_Table_item)

    file_menu.AppendSubMenu(save_menu, "Save")

    import_vamas_item = import_menu.Append(wx.NewId(), "Import Vamas file")
    window.Bind(wx.EVT_MENU, lambda event: open_vamas_file_dialog(window), import_vamas_item)

    import_avantage_item = import_menu.Append(wx.NewId(), "Import Avantage file")
    window.Bind(wx.EVT_MENU, lambda event: import_avantage_file(window), import_avantage_item)

    import_avg_item = import_menu.Append(wx.NewId(), "Import AVG file")
    window.Bind(wx.EVT_MENU, lambda event: open_avg_file(window), import_avg_item)

    import_multiple_avg_item = import_menu.Append(wx.NewId(), "Import Multiple AVG files")
    window.Bind(wx.EVT_MENU, lambda event: import_multiple_avg_files(window), import_multiple_avg_item)

    export_python_plot_item = export_menu.Append(wx.NewId(), "Python Plot")
    window.Bind(wx.EVT_MENU, lambda event: create_plot_script_from_excel(window), export_python_plot_item)

    save_plot_item = export_menu.Append(wx.NewId(), "Export as PNG")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot(window), save_plot_item)

    save_plot_item_pdf = export_menu.Append(wx.NewId(), "Export as PDF")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot_pdf(window), save_plot_item_pdf)

    save_plot_item_svg = export_menu.Append(wx.NewId(), "Export as SVG")
    window.Bind(wx.EVT_MENU, lambda event: on_save_plot_svg(window), save_plot_item_svg)

    window.recent_files_menu = wx.Menu()
    file_menu.AppendSubMenu(window.recent_files_menu, "Recent Files")

    file_menu.AppendSubMenu(import_menu, "Import")
    file_menu.AppendSubMenu(export_menu, "Export")

    file_menu.AppendSeparator()
    exit_item = file_menu.Append(wx.ID_EXIT, "Exit\tCtrl+Q")
    window.Bind(wx.EVT_MENU, lambda event: on_exit(window, event), exit_item)

    undo_item = edit_menu.Append(wx.ID_UNDO, "Undo\tCtrl+Z")
    redo_item = edit_menu.Append(wx.ID_REDO, "Redo\tCtrl+Y")
    window.Bind(wx.EVT_MENU, lambda event: undo(window), undo_item)
    window.Bind(wx.EVT_MENU, lambda event: redo(window), redo_item)
    edit_menu.AppendSeparator()

    preferences_item = edit_menu.Append(wx.ID_PREFERENCES, "Preferences")
    window.Bind(wx.EVT_MENU, window.on_preferences, preferences_item)

    ToggleFitting_item = view_menu.Append(wx.NewId(), "Toggle Peak Fitting")
    window.Bind(wx.EVT_MENU, lambda event: toggle_plot(window), ToggleFitting_item)

    ToggleLegend_item = view_menu.Append(wx.NewId(), "Toggle Legend")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_legend(), ToggleLegend_item)

    ToggleFit_item = view_menu.Append(wx.NewId(), "Toggle Fit Results")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_fitting_results(), ToggleFit_item)

    ToggleRes_item = view_menu.Append(wx.NewId(), "Toggle Residuals")
    window.Bind(wx.EVT_MENU, lambda event: window.plot_manager.toggle_residuals(), ToggleRes_item)

    toggle_energy_item = view_menu.AppendCheckItem(wx.NewId(), "Show Kinetic Energy\tCtrl+B")
    window.Bind(wx.EVT_MENU, lambda event: window.toggle_energy_scale(), toggle_energy_item)
    window.toggle_energy_item = toggle_energy_item

    Area_item = tools_menu.Append(wx.NewId(), "Calculate Area\tCtrl+A")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_background_window(), Area_item)

    Fitting_item = tools_menu.Append(wx.NewId(), "Peak Fitting\tCtrl+P")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_fitting_window(), Fitting_item)

    Noise_item = tools_menu.Append(wx.NewId(), "Noise Analysis")
    window.Bind(wx.EVT_MENU, lambda event: window.on_open_noise_analysis_window, Noise_item)

    # Manual_item = help_menu.Append(wx.NewId(), "Manual - TBD")

    mini_help_item = help_menu.Append(wx.NewId(), "Help")
    window.Bind(wx.EVT_MENU, window.on_mini_help, mini_help_item)

    shortcuts_item = help_menu.Append(wx.NewId(), "List of Shortcuts\tCtrl+K")
    window.Bind(wx.EVT_MENU, lambda event: show_shortcuts(window), shortcuts_item)

    about_item = help_menu.Append(wx.ID_ABOUT, "About")
    window.Bind(wx.EVT_MENU, lambda event: on_about(window, event), about_item)

    menubar.Append(file_menu, "&File")
    menubar.Append(edit_menu, "&Edit")
    menubar.Append(view_menu, "&View")
    menubar.Append(tools_menu, "&Tools")
    menubar.Append(help_menu, "&Help")
    window.SetMenuBar(menubar)

def create_horizontal_toolbar_FUNCTIONS(window):
    toolbar = window.CreateToolBar()
    toolbar.SetBackgroundColour(wx.Colour(220, 220, 220))
    toolbar.SetToolBitmapSize(wx.Size(25, 25))

    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # icon_path = os.path.join(current_dir, "Icons")
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, use the bundle's directory
        application_path = sys._MEIPASS
    else:
        # If the application is run as a script, use the script's directory
        application_path = os.path.dirname(os.path.abspath(__file__))

    icon_path = os.path.join(application_path, "Icons")



    separators = []

    # File operations
    open_file_tool = toolbar.AddTool(wx.ID_ANY, 'Open File', wx.Bitmap(os.path.join(icon_path,
                                                                                    "open-folder-25-green.png"),
                                                                       wx.BITMAP_TYPE_PNG), shortHelp="Open "
                                                                                                      "File\tCtrl+O")
    refresh_folder_tool = toolbar.AddTool(wx.ID_ANY, 'Refresh Excel File', wx.Bitmap(os.path.join(icon_path,
                                                                                         "refresh-96g.png"),
                                                                                     wx.BITMAP_TYPE_PNG),
                                          shortHelp="Refresh Excel File")
    save_tool = toolbar.AddTool(wx.ID_ANY, 'Save', wx.Bitmap(os.path.join(icon_path, "save-Excel-25.png"),
                                                             wx.BITMAP_TYPE_PNG), shortHelp="Save the Fitted Results "
                                                                                            "to Excel for this Core "
                                                                                            "Level \tCtrl+S")
    save_plot_tool = toolbar.AddTool(wx.ID_ANY, 'Save Plot', wx.Bitmap(os.path.join(icon_path, "save-PNG-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save this Figure to Excel")
    save_all_tool = toolbar.AddTool(wx.ID_ANY, 'Save All Sheets', wx.Bitmap(os.path.join(icon_path, "save-Multi-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Save all sheets with plots")

    toolbar.AddSeparator()
    window.undo_tool = toolbar.AddTool(wx.ID_ANY, 'Undo',wx.Bitmap(os.path.join(icon_path, "undo-25.png"),
                                                             wx.BITMAP_TYPE_PNG),
                                shortHelp="Undo -- For peaks properties only")
    window.redo_tool = toolbar.AddTool(wx.ID_ANY, 'Redo',wx.Bitmap(os.path.join(icon_path, "redo-25.png"),
                                                             wx.BITMAP_TYPE_PNG),
                                shortHelp="Redo -- For peaks properties only")
    toolbar.AddSeparator()


    window.skip_rows_spinbox = wx.SpinCtrl(toolbar, min=0, max=200, initial=0, size=(60, -1))
    window.skip_rows_spinbox.SetToolTip("Set the number of rows to skip in the sheet of the Excel file")
    toolbar.AddControl(window.skip_rows_spinbox)

    # Sheet selection
    window.sheet_combobox = wx.ComboBox(toolbar, style=wx.CB_READONLY)
    window.sheet_combobox.SetToolTip("Select Sheet")
    toolbar.AddControl(window.sheet_combobox)

    # Add the binding here
    window.sheet_combobox.Bind(wx.EVT_COMBOBOX, lambda event: on_sheet_selected(window, event))


    toolbar.AddSeparator()

    separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    separators[-1].SetSize((2, 24))
    toolbar.AddControl(separators[-1])

    toolbar.AddSeparator()


    # Add BE correction spinbox
    window.be_correction_spinbox = wx.SpinCtrlDouble(toolbar, value='0.00', min=-20.00, max=20.00, inc=0.01, size=(70, -1))
    window.be_correction_spinbox.SetDigits(2)
    window.be_correction_spinbox.SetToolTip("BE Correction")
    toolbar.AddControl(window.be_correction_spinbox)

    # Add Auto BE button
    auto_be_button = toolbar.AddTool(wx.ID_ANY, 'Auto BE',wx.Bitmap(os.path.join(icon_path, "BEcorrect-25.png"), wx.BITMAP_TYPE_PNG), shortHelp="Automatic binding energy correction")

    toolbar.AddSeparator()

    separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    separators[-1].SetSize((2, 24))
    toolbar.AddControl(separators[-1])

    toolbar.AddSeparator()

    # Plot adjustment tools
    plot_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Plot',wx.Bitmap(os.path.join(icon_path, "scatter-plot-25.png"),wx.BITMAP_TYPE_PNG), shortHelp="Toggle between Raw Data and Fit")
    toggle_peak_fill_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Peak Fill',wx.Bitmap(os.path.join(icon_path, "STO-25.png"), wx.BITMAP_TYPE_PNG),shortHelp="Toggle Peak Fill")

    # resize_plot_tool = toolbar.AddTool(wx.ID_ANY, 'Resize Plot', wx.Bitmap(os.path.join(icon_path, "ResPlot-100.png"), wx.BITMAP_TYPE_PNG), shortHelp="Resize Plot")
    toggle_legend_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Legend',
                                         wx.Bitmap(os.path.join(icon_path, "Legend-25.png"), wx.BITMAP_TYPE_PNG),
                                         shortHelp="Toggle Legend")
    toggle_fit_results_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Fit Results',
                                              wx.Bitmap(os.path.join(icon_path, "ToggleFit-25.png"),
                                                        wx.BITMAP_TYPE_PNG), shortHelp="Toggle Fit Results")
    toggle_residuals_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Residuals',
                                            wx.Bitmap(os.path.join(icon_path, "Res-25.png"), wx.BITMAP_TYPE_PNG),
                                            shortHelp="Toggle Residuals")

    toolbar.AddSeparator()

    separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    separators[-1].SetSize((2, 24))
    toolbar.AddControl(separators[-1])

    toolbar.AddSeparator()

    # Analysis tools
    bkg_tool = toolbar.AddTool(wx.ID_ANY, 'Background', wx.Bitmap(os.path.join(icon_path, "BKG-25.png"),
                                                                  wx.BITMAP_TYPE_PNG),shortHelp="Calculate Area "
                                                                                                "\tCtrl+A")
    # bkg_tool = toolbar.AddTool(wx.ID_ANY, 'Background', wx.Bitmap(wx.Bitmap(os.path.join(icon_path, "Plot_Area.ico")), wx.BITMAP_TYPE_PNG), shortHelp="Calculate Area under Peak")
    fitting_tool = toolbar.AddTool(wx.ID_ANY, 'Fitting', wx.Bitmap(os.path.join(icon_path, "C1s-25.png"),
                                                                   wx.BITMAP_TYPE_PNG), shortHelp="Open Fitting "
                                                                                                  "Window \tCtrl+P")
    noise_analysis_tool = toolbar.AddTool(wx.ID_ANY, 'Noise Analysis', wx.Bitmap(os.path.join(icon_path,
                                                                                              "Noise-25.png"),
                                                                                 wx.BITMAP_TYPE_PNG), shortHelp="Open Noise Analysis Window")

    toolbar.AddSeparator()

    separators.append(wx.StaticLine(toolbar, style=wx.LI_VERTICAL))
    separators[-1].SetSize((2, 24))
    toolbar.AddControl(separators[-1])

    toolbar.AddSeparator()

    id_tool = toolbar.AddTool(wx.ID_ANY, 'ID', wx.Bitmap(os.path.join(icon_path, "ID-25.png"), wx.BITMAP_TYPE_PNG),
                              shortHelp="Element identifications")


    # Add a spacer to push the following items to the right
    toolbar.AddStretchableSpace()

    # Add export button
    export_tool = toolbar.AddTool(wx.ID_ANY, 'Export Results',
                                  wx.Bitmap(os.path.join(icon_path, "Export-25g.png"), wx.BITMAP_TYPE_PNG),
                                  shortHelp="Export to Results Grid")

    # Hide columns in Peak Fitting Parameters
    toggle_Col_1_tool = toolbar.AddTool(wx.ID_ANY, 'Toggle Residuals',
                                            wx.Bitmap(os.path.join(icon_path, "HideColumn-25.png"),
                                                      wx.BITMAP_TYPE_PNG), shortHelp="Toggle Columns Peak Fitting Parameters")

    # Add toggle button for the right panel
    window.toggle_right_panel_tool = window.add_toggle_tool(toolbar, "Toggle Right Panel",
                                                            wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR))


    # Bind the toggle event
    window.Bind(wx.EVT_TOOL, window.on_toggle_right_panel, window.toggle_right_panel_tool)

    toolbar.Realize()

    # Bind events (keeping the same bindings as before, except for BE adjustment tools)
    window.Bind(wx.EVT_TOOL, lambda event: open_xlsx_file(window), open_file_tool)
    window.Bind(wx.EVT_TOOL, lambda event: refresh_sheets(window, on_sheet_selected_wrapper), refresh_folder_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_plot(window), plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_background_window(), bkg_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.on_open_fitting_window(), fitting_tool)
    window.Bind(wx.EVT_TOOL, window.on_open_noise_analysis_window, noise_analysis_tool)
    # window.Bind(wx.EVT_TOOL, lambda event: window.resize_plot(), resize_plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_legend(), toggle_legend_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_fitting_results(), toggle_fit_results_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.plot_manager.toggle_residuals(), toggle_residuals_tool)
    window.sheet_combobox.Bind(wx.EVT_COMBOBOX, lambda event: on_sheet_selected_wrapper(window, event))
    window.Bind(wx.EVT_TOOL, lambda event: on_save(window), save_tool)
    window.Bind(wx.EVT_TOOL, lambda event: on_save_plot(window), save_plot_tool)
    window.Bind(wx.EVT_TOOL, lambda event: on_save_all_sheets(window,event), save_all_tool)
    window.Bind(wx.EVT_TOOL, lambda event: toggle_Col_1(window), toggle_Col_1_tool)
    window.Bind(wx.EVT_TOOL, lambda event: window.export_results(), export_tool)
    window.be_correction_spinbox.Bind(wx.EVT_SPINCTRLDOUBLE, window.on_be_correction_change)
    window.Bind(wx.EVT_TOOL, window.on_auto_be, auto_be_button)
    window.Bind(wx.EVT_TOOL, window.on_toggle_peak_fill, toggle_peak_fill_tool)
    window.Bind(wx.EVT_TOOL, lambda event: undo(window), window.undo_tool)
    window.Bind(wx.EVT_TOOL, lambda event: redo(window), window.redo_tool)
    window.Bind(wx.EVT_TOOL, window.open_periodic_table, id_tool)

    return toolbar

def create_vertical_toolbar_FUNCTIONS(parent, frame):
    v_toolbar = wx.ToolBar(parent, style=wx.TB_VERTICAL | wx.TB_FLAT)
    v_toolbar.SetBackgroundColour(wx.Colour(220, 220, 220))
    v_toolbar.SetToolBitmapSize(wx.Size(25, 25))

    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "Icons")


    # Add zoom tool
    # Add zoom in tool
    zoom_in_tool = v_toolbar.AddTool(wx.ID_ANY, 'Zoom In',
                                     wx.Bitmap(os.path.join(icon_path, "ZoomIN-25.png"), wx.BITMAP_TYPE_PNG),
                                     shortHelp="Zoom In")

    # Add zoom out tool (previously resize_plot)
    zoom_out_tool = v_toolbar.AddTool(wx.ID_ANY, 'Zoom Out',
                                      wx.Bitmap(os.path.join(icon_path, "ZoomOUT-25.png"), wx.BITMAP_TYPE_PNG),
                                      shortHelp="Zoom Out")

    # Add drag tool
    drag_tool = v_toolbar.AddTool(wx.ID_ANY, 'Drag',
                                  wx.Bitmap(os.path.join(icon_path, "drag-25.png"), wx.BITMAP_TYPE_PNG),
                                  shortHelp="Drag Plot")

    v_toolbar.AddSeparator()

    # BE adjustment tools
    high_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE +', wx.Bitmap(os.path.join(icon_path,
                                                                                             "Right-Red-25g.png"),
                                                                                wx.BITMAP_TYPE_PNG),
                                                                                shortHelp="Decrease High BE")
    high_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High BE -', wx.Bitmap(os.path.join(icon_path,
                                                                                             "Left-Red-25g.png"),
                                                                                wx.BITMAP_TYPE_PNG),
                                                                                shortHelp="Increase High BE")

    v_toolbar.AddSeparator()

    low_be_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE +', wx.Bitmap(os.path.join(icon_path,
                                                                                           "Left-Blue-25g.png"),
                                                                              wx.BITMAP_TYPE_PNG), shortHelp="Increase Low BE")
    low_be_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low BE -', wx.Bitmap(os.path.join(icon_path,
                                                                                           "Right-Blue-25g.png"),
                                                                              wx.BITMAP_TYPE_PNG), shortHelp="Decrease Low BE")

    # v_toolbar.AddSeparator()

    # # Add increment spin control
    # increment_label = wx.StaticText(v_toolbar, label="Increment:")
    # v_toolbar.AddControl(increment_label)
    # frame.be_increment_spin = wx.SpinCtrlDouble(v_toolbar, value='1.0', min=0.1, max=10.0, inc=0.1, size=(60, -1))
    # # v_toolbar.AddControl(frame.be_increment_spin)   #  DO NOT ADD YET


    v_toolbar.AddSeparator()

    # Intensity adjustment tools
    high_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int +', wx.Bitmap(os.path.join(icon_path,
                                                                                               "Up-Red-25g.png"),
                                                                                  wx.BITMAP_TYPE_PNG), shortHelp="Increase High Intensity")
    high_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY, 'High Int -', wx.Bitmap(os.path.join(icon_path,
                                                                                               "Down-Red-25g.png"),
                                                                                  wx.BITMAP_TYPE_PNG), shortHelp="Decrease High Intensity")

    v_toolbar.AddSeparator()

    low_int_increase_tool = v_toolbar.AddTool(wx.ID_ANY, 'Low Int +', wx.Bitmap(os.path.join(icon_path,
                                                                                             "Up-Blue-25g.png"),
                                                                                wx.BITMAP_TYPE_PNG), shortHelp="Increase Low Intensity")
    low_int_decrease_tool = v_toolbar.AddTool(wx.ID_ANY,
                                              'Low Int -',
                                              wx.Bitmap(os.path.join(icon_path, "Down-Blue-25g.png"),
                                              wx.BITMAP_TYPE_PNG),
                                              shortHelp="Decrease Low Intensity")

    v_toolbar.AddSeparator()

    # resize_plot_tool = v_toolbar.AddTool(wx.ID_ANY, 'Resize Plot',
    #                                    wx.Bitmap(os.path.join(icon_path, "ZoomOUT.png"), wx.BITMAP_TYPE_PNG),
    #                                    shortHelp="Resize Plot")



    v_toolbar.Realize()

    # Bind events to the frame
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_be', 'increase'), high_be_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_be', 'decrease'), high_be_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_be', 'increase'), low_be_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_be', 'decrease'), low_be_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_int', 'increase'), high_int_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('high_int', 'decrease'), high_int_decrease_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_int', 'increase'), low_int_increase_tool)
    frame.Bind(wx.EVT_TOOL, lambda event: frame.adjust_plot_limits('low_int', 'decrease'), low_int_decrease_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_zoom_in_tool, zoom_in_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_zoom_out, zoom_out_tool)
    frame.Bind(wx.EVT_TOOL, frame.on_drag_tool, drag_tool)


    return v_toolbar

