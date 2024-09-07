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

        for element in elements:
            if element:
                btn = wx.Button(panel, label=element, size=(30, 30))
                btn.Bind(wx.EVT_BUTTON, self.OnElementClick)
            else:
                btn = wx.StaticText(panel, label="")
            grid.Add(btn, 0, wx.EXPAND)

        panel.SetSizer(grid)
        self.SetSize(700, 400)

    def get_element_transitions(self, element):
        transitions = []
        with open('library.txt', 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                if parts[0] == element and parts[2] == 'BE':
                    transitions.append((parts[1], float(parts[3]), float(parts[4])))
        return sorted(transitions, key=lambda x: x[1], reverse=True)

    def OnElementClick(self, event):
        element = event.GetEventObject().GetLabel()
        transitions = self.get_element_transitions(element)
        if transitions:
            info = f"Transitions for {element}:\n\n"
            for transition, be, rsf in transitions:
                info += f"{transition}: BE = {be:.2f} eV, RSF = {rsf:.4f}\n"
            wx.MessageBox(info, "Element Information", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox(f"No BE transitions found for {element}", "Element Information", wx.OK | wx.ICON_INFORMATION)