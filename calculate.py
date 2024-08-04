import wx
from gui import MainFrame

if __name__ == "__main__":
    app = wx.App()
    main_frame = MainFrame()
    main_frame.Show()
    app.MainLoop()

