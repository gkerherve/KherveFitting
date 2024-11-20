import wx

class LabelWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Labels Manager")
        self.parent = parent
        self.SetSize((400, 400))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.list_box = wx.ListBox(panel, style=wx.LB_SINGLE)
        sizer.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 5)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        add_btn = wx.Button(panel, label="Add")
        edit_btn = wx.Button(panel, label="Edit")
        remove_btn = wx.Button(panel, label="Remove")

        btn_sizer.Add(add_btn, 0, wx.ALL, 5)
        btn_sizer.Add(edit_btn, 0, wx.ALL, 5)
        btn_sizer.Add(remove_btn, 0, wx.ALL, 5)

        add_btn.Bind(wx.EVT_BUTTON, self.on_add)
        edit_btn.Bind(wx.EVT_BUTTON, self.on_edit)
        remove_btn.Bind(wx.EVT_BUTTON, self.on_remove)

        sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER)
        panel.SetSizer(sizer)

        self.update_list()

    def update_list(self):
        self.list_box.Clear()
        sheet_name = self.parent.sheet_combobox.GetValue()
        if 'Labels' in self.parent.Data['Core levels'][sheet_name]:
            for label in self.parent.Data['Core levels'][sheet_name]['Labels']:
                self.list_box.Append(f"{label['text']} ({label['x']:.1f}, {label['y']:.1f})")

    def on_add(self, event):
        dlg = wx.TextEntryDialog(self, 'Enter text:', 'Add Text Annotation')
        if dlg.ShowModal() == wx.ID_OK:
            text = dlg.GetValue()
            sheet_name = self.parent.sheet_combobox.GetValue()
            maxY = max(self.parent.y_values)
            x = (self.parent.ax.get_xlim()[0] + self.parent.ax.get_xlim()[1]) / 2
            y = maxY * 1.1

            if 'Labels' not in self.parent.Data['Core levels'][sheet_name]:
                self.parent.Data['Core levels'][sheet_name]['Labels'] = []

            self.parent.Data['Core levels'][sheet_name]['Labels'].append({
                'text': text,
                'x': x,
                'y': y
            })

            # Clear all existing text annotations
            for txt in self.parent.ax.texts[:]:
                txt.remove()

            # Redraw all labels
            for label_data in self.parent.Data['Core levels'][sheet_name]['Labels']:
                self.parent.ax.text(
                    label_data['x'],
                    label_data['y'],
                    label_data['text'],
                    rotation=90,
                    va='bottom',
                    ha='center'
                )

            self.parent.canvas.draw_idle()
            self.update_list()
        dlg.Destroy()

    def on_edit(self, event):
        selection = self.list_box.GetSelection()
        if selection != wx.NOT_FOUND:
            sheet_name = self.parent.sheet_combobox.GetValue()
            label = self.parent.Data['Core levels'][sheet_name]['Labels'][selection]

            dlg = wx.Dialog(self, title="Edit Label")
            sizer = wx.BoxSizer(wx.VERTICAL)

            text_ctrl = wx.TextCtrl(dlg, value=label['text'])
            x_ctrl = wx.SpinCtrlDouble(dlg, value=str(label['x']), min=-10, max=1e4)
            y_ctrl = wx.SpinCtrlDouble(dlg, value=str(label['y']), min=-10000, max=1e10)

            sizer.Add(text_ctrl, 0, wx.ALL, 5)
            sizer.Add(x_ctrl, 0, wx.ALL, 5)
            sizer.Add(y_ctrl, 0, wx.ALL, 5)

            btn_sizer = dlg.CreateButtonSizer(wx.OK | wx.CANCEL)
            sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 5)

            dlg.SetSizer(sizer)

            if dlg.ShowModal() == wx.ID_OK:
                label['text'] = text_ctrl.GetValue()
                label['x'] = x_ctrl.GetValue()
                label['y'] = y_ctrl.GetValue()

                # Clear all existing text annotations
                for txt in self.parent.ax.texts[:]:
                    txt.remove()

                # Redraw all labels
                for label_data in self.parent.Data['Core levels'][sheet_name]['Labels']:
                    self.parent.ax.text(
                        label_data['x'],
                        label_data['y'],
                        label_data['text'],
                        rotation=90,
                        va='bottom',
                        ha='center'
                    )

                self.parent.canvas.draw_idle()
                self.update_list()

            dlg.Destroy()

    def on_remove(self, event):
        selection = self.list_box.GetSelection()
        if selection != wx.NOT_FOUND:
            sheet_name = self.parent.sheet_combobox.GetValue()
            labels = self.parent.Data['Core levels'][sheet_name]['Labels']
            labels.pop(selection)

            # Clear all existing text annotations
            for text in self.parent.ax.texts[:]:
                text.remove()

            # Redraw remaining labels
            for label_data in labels:
                self.parent.ax.text(
                    label_data['x'],
                    label_data['y'],
                    label_data['text'],
                    rotation=90,
                    va='bottom',
                    ha='center'
                )

            self.parent.canvas.draw_idle()
            self.update_list()