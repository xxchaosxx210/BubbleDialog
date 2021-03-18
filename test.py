import wx

from bubbledialog import BubbleDialog


class TestFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, -1)

        button = wx.Button(self, -1, "Launch Dialog")

        gs = wx.GridSizer(cols=1, rows=1, vgap=0, hgap=0)
        gs.Add(button, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(gs)

        self.Bind(wx.EVT_BUTTON, self._on_launch, button)

        self.SetSize((300, 300))

    def _on_launch(self, evt):
        dlg = BubbleDialog(self, -1, "", "", (640, 480))
        dlg.ShowModal()
        dlg.Destroy()


if __name__ == '__main__':
    app = wx.App()
    TestFrame().Show()
    app.MainLoop()
