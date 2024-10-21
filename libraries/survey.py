import wx


class PeriodicTableWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Periodic Table",
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

        self.info_text1 = wx.StaticText(panel, style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.info_text1.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(self.info_text1, 0, wx.EXPAND | wx.ALL, 0)

        self.info_text2 = wx.StaticText(panel, style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.info_text2.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        main_sizer.Add(self.info_text2, 0, wx.EXPAND | wx.ALL, 0)

        grid = wx.GridSizer(10, 18, 2, 2)

        elements = [
            "H", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "He",
            "Li", "Be", "", "", "", "", "", "", "", "", "", "", "B", "C", "N", "O", "F", "Ne",
            "Na", "Mg", "", "", "", "", "", "", "", "", "", "", "Al", "Si", "P", "S", "Cl", "Ar",
            "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
            "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe",
            "Cs", "Ba", "", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "", "At", "Rn",
            "", "Ra", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
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

        main_sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 5)
        panel.SetSizer(main_sizer)
        self.SetSize(560, 340)

    def get_element_transitions(self, element):
        allowed_orbitals = ['1s', '2s', '2p', '3s', '3p', '3d', '4s', '4p', '4d', '4f', '5s', '5p', '5d', '5f']
        transitions = {}
        for (elem, orbital), data in self.library_data.items():

            if elem == element:
                orbital_lower = orbital.lower()
                main_orbital = ''.join([c for c in orbital_lower if c.isalpha() or c.isdigit()])[:2]
                if main_orbital in allowed_orbitals:
                    # Check if 'Al' key exists, if not, use the first available instrument
                    instrument = 'Al' if 'Al' in data else next(iter(data))
                    if 'position' in data[instrument]:
                        energy = float(data[instrument]['position'])
                        if main_orbital not in transitions or energy > transitions[main_orbital]:
                            transitions[main_orbital] = energy

        sorted_transitions = sorted(transitions.items(), key=lambda x: allowed_orbitals.index(x[0]))
        return sorted_transitions

    def OnElementClick(self, event):
        element = event.GetEventObject().GetLabel()
        self.button_states[element] = not self.button_states[element]

        if self.button_states[element]:
            event.GetEventObject().SetBackgroundColour(wx.GREEN)
            self.plot_element_lines(element)
        else:
            event.GetEventObject().SetBackgroundColour(wx.WHITE)
            self.remove_element_lines(element)

        event.GetEventObject().Refresh()

    def plot_element_lines(self, element):
        transitions = self.get_element_transitions(element)

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