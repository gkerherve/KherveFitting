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

        grid = wx.GridSizer(10, 18, 1, 1)

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

        self.info_text = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        main_sizer.Add(self.info_text, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(main_sizer)
        self.SetSize(460, 400)  # Increased height to accommodate the text area

    def get_element_transitions(self, element):
        transitions = {}
        with open('library.txt', 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                if parts[0] == element and parts[2] == 'BE':
                    orbital = parts[1].split('/')[0] if '/' in parts[1] else parts[1]
                    if orbital not in transitions or float(parts[3]) > transitions[orbital]:
                        transitions[orbital] = float(parts[3])
        return sorted(transitions.items(), key=lambda x: x[1], reverse=True)

    def OnElementClick(self, event):
        element = event.GetEventObject().GetLabel()
        transitions = self.get_element_transitions(element)
        if transitions:
            info = f"Transitions for {element}:\n\n"
            for orbital, be in transitions:
                info += f"{orbital}: {be:.1f} eV\n"
            self.info_text.SetValue(info)
        else:
            self.info_text.SetValue(f"No BE transitions found for {element}")


def open_periodic_table(parent):
    periodic_table = PeriodicTableWindow(parent)
    periodic_table.Show()