import wx

# Details             :  https://docs.wxpython.org/wx.1moduleindex.html
# universal API format:  parent, id, title, pos, size, style
# -1 always represents default id

def set_selected_directory(dir_path: str):
    print(f"dir_path: {dir_path}")
    pass

APP_ICON = './resource/rabbit.png'

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1, title=u"计算发票总金额", size=(640, 480))
        self.SetBackgroundColour(wx.Colour(206, 115, 168))
        self.Center()
        self.SetIcon(wx.Icon(APP_ICON))

        box_main = wx.BoxSizer(wx.VERTICAL)

        hint_content = u"😋使用指南: 选择发票 -> 输入提示词 -> 开始计算 "
        hint_text = wx.StaticText(self, -1, hint_content, style=wx.ALIGN_CENTER)

        bt_choose = wx.Button(self, -1, u"选择发票")
        bt_choose.Bind(wx.EVT_BUTTON,self.choose_directory)
        self.dir_hint_text = wx.StaticText(self, -1, "", style=wx.ALIGN_LEFT)
        box_invoice = wx.BoxSizer(wx.HORIZONTAL)
        box_invoice.Add(bt_choose, 0, wx.RIGHT, border=20)
        box_invoice.Add(self.dir_hint_text, 0, wx.RIGHT, border=00)


        input_label = wx.StaticText(self, -1, u"输入提示词\n(逗号分割, 回车确认):")
        self.text_input = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER, size=(100, 30))
        self.text_input.Bind(wx.EVT_TEXT_ENTER, self.on_input)
        self.label_inputed = wx.StaticText(self, -1, "")
        self.user_input_list=""
        box_input = wx.BoxSizer(wx.HORIZONTAL)
        box_input.Add(input_label,        0, wx.RIGHT, 10)
        box_input.Add(self.text_input,    0, wx.RIGHT | wx.ALIGN_CENTER, 10)
        box_input.Add(self.label_inputed, 0, wx.RIGHT | wx.ALIGN_CENTER, 10)

        bt_compute = wx.Button(self, -1, u"开始计算")
        bt_compute.Bind(wx.EVT_BUTTON,self.start_to_compute)
        self.gauge = wx.Gauge(self, range=100, size=(180, 20))
        self.gauge.SetValue(0)
        box_compute=wx.BoxSizer(wx.VERTICAL)
        box_compute.Add(bt_compute, 0, wx.DOWN, 10)
        box_compute.Add(self.gauge, 0, wx.DOWN, 10)


        self.result1 = wx.StaticText(self, -1, "总金额   : 0",  style=wx.ALIGN_LEFT)
        self.result2 = wx.StaticText(self, -1, "详细文件 : 无", style=wx.ALIGN_LEFT)
        box_result= wx.BoxSizer(wx.VERTICAL)
        box_result.Add(self.result1, 0)
        box_result.Add(self.result2, 0)
        self.detailed_result=""

        box_main.Add(hint_text,   0, wx.DOWN | wx.EXPAND, 20)
        box_main.Add(box_invoice, 0, wx.LEFT | wx.DOWN,   20)
        box_main.Add(box_input,   0, wx.LEFT | wx.DOWN,   20)
        box_main.Add(box_compute, 0, wx.LEFT | wx.DOWN,   20)
        box_main.Add(box_result,  0, wx.LEFT | wx.DOWN,   20)
        self.SetSizer(box_main)


    def choose_directory(self, event):
        dlg = wx.DirDialog(self, u"选择发票所在文件夹", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            set_selected_directory(dlg.GetPath())
            self.dir_hint_text.SetLabel(f"已选择的发票文件夹路径: {dlg.GetPath()}")
        dlg.Destroy()


    def start_to_compute(self, evt):
        print("start to compute")
        self.update_process(10)
        self.update_process(20)

    def on_input(self, evt):
        input_text=self.text_input.GetValue()
        self.user_input_list = list(filter(None, input_text.split(',')))
        number = len(self.user_input_list)
        self.label_inputed.SetLabel(f"已输入了{number}个提示符，分别是: {self.user_input_list}")

    def show_message_and_stop(self, message: str):
        wx.MessageDialog(self, message, "操作出错").ShowModal()

    def update_process(self, count: int):
        self.gauge.SetValue(count)

    def set_result(self, result: float, detailed_result_file: str):
        self.result1.SetLabel(f"😋总金额   : {result}")
        self.result2.SetLabel(f"😋详细文件 : {detailed_result_file}")
        self.detailed_result=detailed_result_file


if __name__ == "__main__":
    app = wx.App()
    main_frame = MainFrame()
    main_frame.Show()
    app.MainLoop()
