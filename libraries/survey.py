import wx
import numpy as np
from libraries.Sheet_Operations import on_sheet_selected


class PeriodicTableWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Survey Identification / Labelling",
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.parent_window = parent  # Store the parent window
        self.SetBackgroundColour(wx.WHITE)

        self.library_data = self.parent_window.library_data

        self.button_states = {}
        self.element_lines = {}
        self.InitUI()

        # Bind the close event
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def InitUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.WHITE)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Info text
        self.info_text1 = wx.StaticText(panel, style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.info_text1.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(self.info_text1, 0, wx.EXPAND | wx.ALL, 0)

        self.info_text2 = wx.StaticText(panel, style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.info_text2.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(self.info_text2, 0, wx.EXPAND | wx.ALL, 0)

        # Split the window horizontally
        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left side: Periodic Table
        periodic_sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(10, 18, 2, 2)

        elements = [
            "H", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "He",
            "Li", "Be", "", "", "", "", "", "", "", "", "", "", "B", "C", "N", "O", "F", "Ne",
            "Na", "Mg", "", "", "", "", "", "", "", "", "", "", "Al", "Si", "P", "S", "Cl", "Ar",
            "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
            "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe",
            "Cs", "Ba", "", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "", "At", "Rn",
            "", "Ra", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            # "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "",
            "", "", "", "Th", "", "U", "Np", "Pu", "Am", "Cm", "", "", "", "", "", "", "", ""
        ]

        button_size = (30, 30)
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        for element in elements:
            if element:
                btn = wx.Button(panel, label=element, size=button_size)
                btn.SetFont(font)
                btn.Bind(wx.EVT_ENTER_WINDOW, self.OnElementHover)
                btn.Bind(wx.EVT_LEAVE_WINDOW, self.OnElementLeave)
                btn.Bind(wx.EVT_BUTTON, self.OnElementClick)
                btn.SetBackgroundColour(wx.WHITE)
                self.button_states[element] = False
            else:
                btn = wx.StaticText(panel, label="")
            grid.Add(btn, 0, wx.EXPAND)

        periodic_sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 5)
        hsizer.Add(periodic_sizer, 0, wx.EXPAND)

        # Right side: Core Level List and Buttons
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        self.core_level_list = wx.ListBox(panel, style=wx.LB_MULTIPLE, size=(170, -1))
        right_sizer.Add(self.core_level_list, 1, wx.EXPAND | wx.ALL, 5)

        # Buttons
        button_sizer = wx.GridBagSizer(5, 5)

        self.add_labels_btn = wx.Button(panel, label="Add Labels")
        self.add_peak_btn = wx.Button(panel, label="Add to Grid")
        self.remove_selected_btn = wx.Button(panel, label="Clear Selected")
        self.remove_all_btn = wx.Button(panel, label="Clear All List")
        self.remove_last_label_btn = wx.Button(panel, label="Clear Last Label")
        self.remove_all_labels_btn = wx.Button(panel, label="Clear All Labels")

        self.add_labels_btn.Bind(wx.EVT_BUTTON, self.OnAddLabels)
        self.add_peak_btn.Bind(wx.EVT_BUTTON, self.OnAddPeak)
        self.remove_selected_btn.Bind(wx.EVT_BUTTON, self.OnRemoveSelected)
        self.remove_all_btn.Bind(wx.EVT_BUTTON, self.OnRemoveAll)
        self.remove_last_label_btn.Bind(wx.EVT_BUTTON, self.OnRemoveLastLabel)
        self.remove_all_labels_btn.Bind(wx.EVT_BUTTON, self.OnRemoveAllLabels)

        button_sizer.Add(self.add_labels_btn, pos=(0, 0), flag=wx.EXPAND)
        button_sizer.Add(self.add_peak_btn, pos=(0, 1), flag=wx.EXPAND)
        button_sizer.Add(self.remove_selected_btn, pos=(1, 0), flag=wx.EXPAND)
        button_sizer.Add(self.remove_all_btn, pos=(1, 1), flag=wx.EXPAND)
        button_sizer.Add(self.remove_last_label_btn, pos=(2, 0), flag=wx.EXPAND)
        button_sizer.Add(self.remove_all_labels_btn, pos=(2, 1), flag=wx.EXPAND)

        right_sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 5)

        hsizer.Add(right_sizer, 0, wx.EXPAND)

        main_sizer.Add(hsizer, 1, wx.EXPAND)
        panel.SetSizer(main_sizer)
        self.SetSize(815, 320)

    def OnRemoveLastLabel(self, event):
        sheet_name = self.parent_window.sheet_combobox.GetValue()
        if 'Labels' in self.parent_window.Data['Core levels'][sheet_name]:
            labels = self.parent_window.Data['Core levels'][sheet_name]['Labels']
            if labels:
                labels.pop()
                # Clear all existing text annotations
                for text in self.parent_window.ax.texts[:]:
                    text.remove()
                # Redraw remaining labels
                maxY = max(self.parent_window.y_values)
                for label_data in labels:
                    self.parent_window.ax.text(
                        label_data['x'],
                        label_data['y'],
                        label_data['text'],
                        rotation=90,
                        va='bottom',
                        ha='center'
                    )
                self.parent_window.canvas.draw_idle()

    def OnRemoveAllLabels(self, event):
        sheet_name = self.parent_window.sheet_combobox.GetValue()
        if 'Labels' in self.parent_window.Data['Core levels'][sheet_name]:
            self.parent_window.Data['Core levels'][sheet_name]['Labels'] = []
            # Clear all text annotations
            for text in self.parent_window.ax.texts[:]:
                text.remove()
            self.parent_window.canvas.draw_idle()

    def get_element_transitions(self, element):
        allowed_orbitals = ['1s', '2s', '2p', '3s', '3p', '3d', '4s', '4p', '4d', '4f', '5s', '5p', '5d', '5f']
        transitions = {}
        photon_energy = self.parent_window.photons  # Get photon energy

        for (elem, orbital), data in self.library_data.items():
            if elem == element:
                # Choose instrument based on whether it's an Auger line
                if 'Any' in data:
                    instrument = 'Any'  # For Auger lines
                else:
                    instrument = 'Al' if 'Al' in data else next(iter(data))

                if 'position' in data[instrument] and float(data[instrument]['position']) >= 20:
                    # Check if it's a core level or Auger transition
                    is_auger = instrument == 'Any'
                    # is_auger = data[instrument]['Auger'] == '1'  # Corrected this line
                    orbital_lower = orbital.lower()

                    if is_auger:
                        # Subtract photon energy for Auger transitions
                        kinetic_energy = float(data[instrument]['position'])
                        binding_energy = photon_energy - kinetic_energy  # Convert KE to BE
                        transitions[orbital_lower] = binding_energy
                    else:
                        # For core levels
                        main_orbital = ''.join([c for c in orbital_lower if c.isalpha() or c.isdigit()])[:2]
                        if main_orbital in allowed_orbitals:
                            energy = float(data[instrument]['position'])
                            if main_orbital not in transitions or energy > transitions[main_orbital]:
                                transitions[main_orbital] = energy

        sorted_transitions = sorted(transitions.items(), key=lambda x: x[1])
        return sorted_transitions

    def OnElementClick(self, event):
        element = event.GetEventObject().GetLabel()
        self.button_states[element] = not self.button_states[element]

        if self.button_states[element]:
            event.GetEventObject().SetBackgroundColour(wx.GREEN)
            self.plot_element_lines(element)
            transitions = self.get_element_transitions(element)

            # Add transitions to list without clearing existing items
            existing_items = [self.core_level_list.GetString(i) for i in range(self.core_level_list.GetCount())]
            for orbital, be in transitions:
                item = f"{element}{orbital}: {be:.1f} eV"
                if item not in existing_items:
                    self.core_level_list.Append(item)
        else:
            event.GetEventObject().SetBackgroundColour(wx.WHITE)
            self.remove_element_lines(element)

        event.GetEventObject().Refresh()

    def OnAddLabels(self, event):
        selections = self.core_level_list.GetSelections()
        for selection in selections:
            label = self.core_level_list.GetString(selection)
            element_orbital, be_str = label.split(':')
            print(f'Element Orbital: {element_orbital}')
            be = float(be_str.replace(' eV', ''))
            formatted_label = ".."

            # Extract element and orbital correctly
            import re
            match = re.match(r'([A-Z][a-z]*)(\d+[spdf])', element_orbital)
            if match:
                element, orbital = match.groups()
                formatted_label = f"{element} {orbital[0]}{orbital[1]}"  # e.g., "C 1 s"
            elif any(element_orbital.endswith(x) for x in ['kll', 'mnn', 'mvv', 'mnv', 'lmm']):
                auger = element_orbital[-3:]
                formatted_label = f"{element_orbital[:-3]} {auger.upper()}"

            if formatted_label != "..":
                # Get max intensity in ±5 eV range
                x_values = self.parent_window.x_values
                y_values = self.parent_window.y_values
                maxY = max(y_values)
                mask = (x_values >= be - 5) & (x_values <= be + 5)
                if np.any(mask):
                    local_max = np.max(y_values[mask])
                    # Add label at 1.2 times the local maximum height
                    self.parent_window.ax.text(be, local_max +0.05*maxY, formatted_label,
                                               rotation=90, va='bottom', ha='center')
                    self.parent_window.canvas.draw_idle()

                sheet_name = self.parent_window.sheet_combobox.GetValue()

                if 'Labels' not in self.parent_window.Data['Core levels'][sheet_name]:
                    # print('Labels not in sheetname')
                    self.parent_window.Data['Core levels'][sheet_name]['Labels'] = []

                self.parent_window.Data['Core levels'][sheet_name]['Labels'].append({
                    'text': formatted_label,
                    'x':be,
                    'y': local_max +0.05*maxY
                })

    def add_peak_to_grid(self, peak_name):

        # Add peak to window.Data first
        sheet_name = self.parent_window.sheet_combobox.GetValue()

        # Initialize the full structure if it doesn't exist
        if 'Fitting' not in self.parent_window.Data['Core levels'][sheet_name]:
            self.parent_window.Data['Core levels'][sheet_name]['Fitting'] = {}
        if 'Peaks' not in self.parent_window.Data['Core levels'][sheet_name]['Fitting']:
            self.parent_window.Data['Core levels'][sheet_name]['Fitting']['Peaks'] = {}

        # Better element and orbital extraction
        import re
        match = re.match(r'([A-Z][a-z]*)(\d+[spdf])', peak_name)
        if match:
            element, orbital = match.groups()
        else:
            return False

        position = None
        for (elem, orb), data in self.library_data.items():
            if elem == element and orb.lower() == orbital.lower():
                instrument = 'Al' if 'Al' in data else next(iter(data))
                if 'position' in data[instrument]:
                    position = float(data[instrument]['position'])
                    break

        if position:
            # Add to window.Data
            peak_data = {
                'Position': position,
                'Height': 0,
                'FWHM': 2.0,
                'L/G': 30,
                'Area': 0,
                'Fitting Model': 'SurveyID'
            }
            self.parent_window.Data['Core levels'][sheet_name]['Fitting']['Peaks'][peak_name] = peak_data

            # Add to grid
            current_rows = self.parent_window.peak_params_grid.GetNumberRows()

            self.parent_window.peak_params_grid.AppendRows(2)

            # Make sure to add the letter ID
            letter_id = chr(65 + (current_rows // 2))  # A, B, C, etc.

            self.parent_window.peak_params_grid.SetCellValue(current_rows, 0, letter_id)
            self.parent_window.peak_params_grid.SetCellValue(current_rows, 1, peak_name)
            self.parent_window.peak_params_grid.SetCellValue(current_rows, 2, f"{position:.2f}")
            self.parent_window.peak_params_grid.SetCellValue(current_rows, 4, "2.0")  # FWHM
            self.parent_window.peak_params_grid.SetCellValue(current_rows, 5, "30")  # L/G
            self.parent_window.peak_params_grid.SetCellValue(current_rows, 13, "SurveyID")

            # Set constraint row background color
            for col in range(self.parent_window.peak_params_grid.GetNumberCols()):
                self.parent_window.peak_params_grid.SetCellBackgroundColour(current_rows + 1, col,
                                                                            wx.Colour(200, 245, 228))

            # Update peak count
            self.parent_window.peak_count = current_rows // 2 + 1

            self.parent_window.peak_params_grid.ForceRefresh()
            return True
        else:
            print(f"No position found for peak {peak_name}")
            return False

    def OnAddPeak(self, event):
        selections = self.core_level_list.GetSelections()
        sheet_name = self.parent_window.sheet_combobox.GetValue().lower()

        if any(x in sheet_name for x in ['survey', 'wide']):
            for selection in selections:
                label = self.core_level_list.GetString(selection)
                element = label.split(':')[0]
                # Check if it's a main core level
                if any(element.endswith(x) for x in ['1s', '2p', '3d', '4f']):
                    self.add_peak_to_grid(element)

    def OnRemoveSelected(self, event):
        selections = list(self.core_level_list.GetSelections())
        selections.reverse()  # Remove from bottom to top to avoid index issues
        for selection in selections:
            self.core_level_list.Delete(selection)

    def OnRemoveAll(self, event):
        self.core_level_list.Clear()


    def get_main_core_level(self, element):
        main_core_levels = {
            'Li': '1s', 'Be': '1s', 'B': '1s', 'C': '1s', 'N': '1s', 'O': '1s', 'F': '1s', 'Ne': '1s',
            'Na': '1s', 'Mg': '1s', 'Al': '2p', 'Si': '2p', 'P': '2p', 'S': '2p', 'Cl': '2p',
            'K': '2p', 'Ca': '2p', 'Sc': '2p', 'Ti': '2p', 'V': '2p', 'Cr': '2p', 'Mn': '2p',
            'Fe': '2p', 'Co': '2p', 'Ni': '2p', 'Cu': '2p', 'Zn': '2p', 'Ga': '2p', 'Ge': '3d',
            'As': '3d', 'Se': '3d', 'Br': '3d', 'Sr': '3d', 'Y': '3d', 'Zr': '3d', 'Nb': '3d',
            'Mo': '3d', 'Tc': '3d', 'Ru': '3d', 'Rh': '3d', 'Pd': '3d', 'Ag': '3d', 'Cd': '3d',
            'In': '3d', 'Sn': '3d', 'Sb': '3d', 'Te': '3d', 'I': '3d', 'Xe': '3d', 'Cs': '3d',
            'Ba': '3d', 'La': '3d', 'W': '4f'
        }
        return main_core_levels.get(element)

    def plot_element_lines(self, element):

        transitions = self.get_element_transitions(element)
        print(f"transitions: {transitions}")

        if transitions:
            xmin, xmax = self.parent_window.ax.get_xlim()
            ymin, ymax = self.parent_window.ax.get_ylim()


            # Filter transitions within xmin and xmax
            valid_transitions = [t for t in transitions if xmax <= t[1] <= xmin]

            if valid_transitions:
                # Get RSF values for each transition
                rsf_values = self.get_rsf_values(element, [t[0] for t in valid_transitions])
                # print("RSF  " + str(rsf_values))

                if rsf_values:
                    max_rsf = max(rsf_values)

                    # Initialize the list for this element
                    self.element_lines[element] = []

                    for (orbital, be), rsf in zip(valid_transitions, rsf_values):
                        intensity = (rsf / max_rsf) * 0.6 * (ymax - ymin)
                        line = self.parent_window.ax.vlines(be, ymin - intensity, ymin + intensity, color='red',
                                                            linewidth=1)
                        self.element_lines[element].append(line)

                        # Add text label
                        text = self.parent_window.ax.text(
                            be + 0.1,  # Slightly to the left of the line
                            ymin+0.01*(ymax-ymin),  # At the bottom of the plot
                            element+""+orbital,
                            rotation=90,
                            va='bottom',
                            ha='right',
                            fontsize=7,
                            color='red'
                        )
                        self.element_lines[element].append(text)

                    self.parent_window.canvas.draw_idle()
                else:
                    print(f"No RSF values found for {element}")
            else:
                print(f"No valid transitions found for {element} in the current plot range")

    def remove_element_lines(self, element):
        if element in self.element_lines:
            for line in self.element_lines[element]:
                line.remove()
            del self.element_lines[element]
            self.parent_window.canvas.draw_idle()

    def reset_all_buttons(self):
        for element, button in self.button_states.items():
            if button:
                self.button_states[element] = False
                btn = self.FindWindowByLabel(element)
                if btn:
                    btn.SetBackgroundColour(wx.WHITE)
                    btn.Refresh()

        for element, lines in self.element_lines.items():
            for line in lines:
                line.remove()
        self.element_lines.clear()
        self.parent_window.canvas.draw_idle()

    def get_rsf_values(self, element, orbitals):
        rsf_values = []
        print(f"Searching RSF values for element: {element}")
        print(f"Orbitals to search for: {orbitals}")

        for (elem, orbital), data in self.library_data.items():
            if elem == element:
                orbital_lower = orbital.lower()
                if orbital_lower in [o.lower() for o in orbitals]:
                    # Check if 'Al' key exists, if not, use the first available instrument
                    instrument = 'Al' if 'Al' in data else next(iter(data))
                    print(data[instrument])
                    if 'rsf' in data[instrument]:
                        rsf_values.append(float(data[instrument]['rsf']))
                        print(f"Added RSF value: {data[instrument]['rsf']} for orbital {orbital}")

        print(f"Final RSF values: {rsf_values}")
        return rsf_values

    def OnElementHover(self, event):
        element = event.GetEventObject().GetLabel()
        self.UpdateElementInfo(element)

    def OnElementLeave(self, event):
        self.info_text1.SetLabelMarkup("")
        self.info_text2.SetLabelMarkup("")
        self.Layout()

    def UpdateElementInfo(self, element):
        element_names = {
            'H': 'Hydrogen', 'He': 'Helium', 'Li': 'Lithium', 'Be': 'Beryllium', 'B': 'Boron',
            'C': 'Carbon', 'N': 'Nitrogen', 'O': 'Oxygen', 'F': 'Fluorine', 'Ne': 'Neon',
            'Na': 'Sodium', 'Mg': 'Magnesium', 'Al': 'Aluminum', 'Si': 'Silicon', 'P': 'Phosphorus',
            'S': 'Sulfur', 'Cl': 'Chlorine', 'Ar': 'Argon', 'K': 'Potassium', 'Ca': 'Calcium',
            'Sc': 'Scandium', 'Ti': 'Titanium', 'V': 'Vanadium', 'Cr': 'Chromium', 'Mn': 'Manganese',
            'Fe': 'Iron', 'Co': 'Cobalt', 'Ni': 'Nickel', 'Cu': 'Copper', 'Zn': 'Zinc',
            'Ga': 'Gallium', 'Ge': 'Germanium', 'As': 'Arsenic', 'Se': 'Selenium', 'Br': 'Bromine',
            'Kr': 'Krypton', 'Rb': 'Rubidium', 'Sr': 'Strontium', 'Y': 'Yttrium', 'Zr': 'Zirconium',
            'Nb': 'Niobium', 'Mo': 'Molybdenum', 'Ru': 'Ruthenium', 'Rh': 'Rhodium', 'Pd': 'Palladium',
            'Ag': 'Silver', 'Cd': 'Cadmium', 'In': 'Indium', 'Sn': 'Tin', 'Sb': 'Antimony',
            'Te': 'Tellurium', 'I': 'Iodine', 'Xe': 'Xenon', 'Cs': 'Cesium', 'Ba': 'Barium',
            'La': 'Lanthanum', 'Ce': 'Cerium', 'Pr': 'Praseodymium', 'Nd': 'Neodymium', 'Pm': 'Promethium',
            'Sm': 'Samarium', 'Eu': 'Europium', 'Gd': 'Gadolinium', 'Tb': 'Terbium', 'Dy': 'Dysprosium',
            'Ho': 'Holmium', 'Er': 'Erbium', 'Tm': 'Thulium', 'Yb': 'Ytterbium', 'Lu': 'Lutetium',
            'Hf': 'Hafnium', 'Ta': 'Tantalum', 'W': 'Tungsten', 'Re': 'Rhenium', 'Os': 'Osmium',
            'Ir': 'Iridium', 'Pt': 'Platinum', 'Au': 'Gold', 'Hg': 'Mercury', 'Tl': 'Thallium',
            'Pb': 'Lead', 'Bi': 'Bismuth', 'At': 'Astatine', 'Rn': 'Radon', 'Ra': 'Radium',
            'Th': 'Thorium', 'U': 'Uranium', 'Np': 'Neptunium', 'Pu': 'Plutonium', 'Am': 'Americium',
            'Cm': 'Curium'
        }

        transitions = self.get_element_transitions(element)
        if transitions:
            info1 = f"<b>{element_names.get(element, element)}</b>: "
            info2 = ", ".join(f"{orbital}: {be:.1f} eV" for orbital, be in transitions)

            # Split info2 into two lines if it's too long
            max_line_length = 60
            if len(info2) > max_line_length:
                split_point = info2.rfind(", ", 0, max_line_length) + 2
                info1 += info2[:split_point]
                info2 = info2[split_point:]
            else:
                info1 += info2
                info2 = ""

            self.info_text1.SetLabelMarkup(info1)
            self.info_text2.SetLabelMarkup(info2)
        else:
            self.info_text1.SetLabelMarkup(f"<b>{element_names.get(element, element)}</b>: No BE transitions found")
            self.info_text2.SetLabelMarkup("")
        self.Layout()

    def Close(self, force=False):
        self.reset_all_buttons()
        super().Close(force)

    def OnClose(self, event):
        self.reset_all_buttons()
        self.Destroy()


def open_periodic_table(parent):
    periodic_table = PeriodicTableWindow(parent)
    periodic_table.Show()