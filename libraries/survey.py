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
        main_sizer.Add(self.info_text, 0, wx.EXPAND | wx.ALL, 5)

        grid = wx.GridSizer(10, 18, 2, 2)  # Added spacing between buttons

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
        transitions = {}
        with open('library.txt', 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                if parts[0] == element and parts[2] == 'BE':
                    orbital = parts[1].split()[0]  # Take only the main part (e.g., '2s' from '2s1/2')
                    if orbital[-1] in 's p d f'.split():  # Only consider main orbitals
                        if orbital not in transitions or float(parts[3]) > transitions[orbital]:
                            transitions[orbital] = float(parts[3])
        return sorted(transitions.items(), key=lambda x: x[1], reverse=True)

    def OnElementClick(self, event):
        element = event.GetEventObject().GetLabel()
        transitions = self.get_element_transitions(element)
        if transitions:
            info = ", ".join(f"{orbital}: {be:.1f} eV" for orbital, be in transitions)
            # Split into two lines if too long
            if len(info) > 50:
                midpoint = len(info) // 2
                split_point = info.rfind(", ", 0, midpoint) + 2
                info = info[:split_point] + "\n" + info[split_point:]
            self.info_text.SetLabel(info)
        else:
            self.info_text.SetLabel(f"No BE transitions found for {element}")
        self.Layout()


def open_periodic_table(parent):
    periodic_table = PeriodicTableWindow(parent)
    periodic_table.Show()