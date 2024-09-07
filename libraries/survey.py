import wx


class PeriodicTableWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Periodic Table",
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetBackgroundColour(wx.WHITE)
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.WHITE)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.info_text = wx.StaticText(panel, style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
        self.info_text.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.info_text.Wrap(440)  # Adjust this value as needed
        main_sizer.Add(self.info_text, 0, wx.EXPAND | wx.ALL, 5)

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

        button_size = (24, 24)
        font = wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        for element in elements:
            if element:
                btn = wx.Button(panel, label=element, size=button_size)
                btn.SetFont(font)
                btn.Bind(wx.EVT_BUTTON, self.OnElementClick)
            else:
                btn = wx.StaticText(panel, label="")
            grid.Add(btn, 0, wx.EXPAND)

        main_sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(main_sizer)
        self.SetSize(460, 280)

    def get_element_transitions(self, element):
        allowed_orbitals = ['1s', '2s', '2p', '3s', '3p', '3d', '4s', '4p', '4d', '4f', '5s', '5p', '5d', '5f']
        transitions = {}
        print(f"Searching transitions for {element}")  # Debug print
        with open('library.txt', 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) >= 4 and parts[0] == element and parts[2] == 'BE':
                    print(f"Original line: {line.strip()}")  # Debug print
                    orbital = parts[1].lower()  # Convert to lowercase
                    print(f"Found orbital: {orbital}")  # Debug print

                    # Extract main orbital (1s, 2s, 2p, etc.)
                    main_orbital = ''.join([c for c in orbital if c.isalpha() or c.isdigit()])[:2]
                    print(f"Main orbital: {main_orbital}")  # Debug print

                    if main_orbital in allowed_orbitals:
                        energy = float(parts[3])
                        if main_orbital not in transitions or energy > transitions[main_orbital]:
                            transitions[main_orbital] = energy
                            print(f"Added/Updated {main_orbital}: {energy} eV")  # Debug print
                    else:
                        print(f"Orbital {main_orbital} not in allowed list")  # Debug print

        sorted_transitions = sorted(transitions.items(), key=lambda x: allowed_orbitals.index(x[0]))
        print(f"Final transitions: {sorted_transitions}")  # Debug print
        return sorted_transitions

    def OnElementClick(self, event):
        element = event.GetEventObject().GetLabel()
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
            info = f"<b>{element_names.get(element, element)}</b>: "
            info += ", ".join(f"{orbital}: {be:.1f} eV" for orbital, be in transitions)
            # Split into two lines if too long
            if len(info) > 100:
                midpoint = len(info) // 2
                split_point = info.rfind(", ", 0, midpoint) + 2
                info = info[:split_point] + "\n" + info[split_point:]
            self.info_text.SetLabelMarkup(info)
            print(info)
        else:
            self.info_text.SetLabelMarkup(f"<b>{element_names.get(element, element)}</b>: No BE transitions found")
        self.Layout()


def open_periodic_table(parent):
    periodic_table = PeriodicTableWindow(parent)
    periodic_table.Show()