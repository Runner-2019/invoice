import wx
from threading import Thread
from pubsub import pub
from ocr import OCRHandle

# Details             :  https://docs.wxpython.org/wx.1moduleindex.html
# universal API format:  parent, id, title, pos, size, style
# -1 always represents default id

APP_ICON = './resource/rabbit.png'

class OcrThread(Thread):
    def __init__(self, app, ocr_handle):
        Thread.__init__(self)
        self.app = app
        self.ocr_handle = ocr_handle

    def run(self):
        try:
            self.ocr_handle.run()
        except Exception as e:
            print(e)
            self.app.show_message(str(e))
            wx.CallAfter(pub.sendMessage, "execute_error")


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1, title=u"计算发票总金额", size=(640, 480))
        self.SetBackgroundColour(wx.Colour(206, 115, 168))
        self.Center()
        self.SetIcon(wx.Icon(APP_ICON))

        box_main = wx.BoxSizer(wx.VERTICAL)

        hint_content = u"😋  使用指南: 选择发票  ---> 输入提示词  --->  开始计算"
        hint_text = wx.StaticText(self, -1, hint_content, style=wx.ALIGN_CENTER)

        btn_choose = wx.Button(self, -1, u"选择发票")
        btn_choose.Bind(wx.EVT_BUTTON,self.__on_choose_invoice_directory)
        self.dir_hint_text = wx.StaticText(self, -1, "", style=wx.ALIGN_LEFT)
        box_invoice = wx.BoxSizer(wx.HORIZONTAL)
        box_invoice.Add(btn_choose, 0, wx.RIGHT, border=20)
        box_invoice.Add(self.dir_hint_text, 0, wx.RIGHT, border=00)
        self.invoices_dir=""

        input_label = wx.StaticText(self, -1, u"输入提示词\n用于从发票图片中提取发票金额\n(英文逗号分割, 回车确认):")
        self.text_input = wx.TextCtrl(self, -1, "小写,", style=wx.TE_PROCESS_ENTER, size=(100, 30))
        self.text_input.Bind(wx.EVT_TEXT_ENTER, self.__on_input_prompt)
        self.label_inputed = wx.StaticText(self, -1, "当前使用的提示符: \"小写\"")
        self.prompt=["小写"]
        box_input = wx.BoxSizer(wx.HORIZONTAL)
        box_input.Add(input_label,        0, wx.RIGHT, 10)
        box_input.Add(self.text_input,    0, wx.RIGHT | wx.ALIGN_CENTER, 10)
        box_input.Add(self.label_inputed, 0, wx.RIGHT | wx.ALIGN_CENTER, 10)

        self.btn_compute = wx.Button(self, -1, u"开始计算")
        self.btn_compute.Bind(wx.EVT_BUTTON,self.__on_start_compute)
        self.gauge = wx.Gauge(self, range=100, size=(180, 20))
        self.gauge.SetValue(0)
        box_compute=wx.BoxSizer(wx.VERTICAL)
        box_compute.Add(self.btn_compute, 0, wx.DOWN, 10)
        box_compute.Add(self.gauge, 0, wx.DOWN, 10)


        self.result1 = wx.StaticText(self, -1, "总金额: 0",    style=wx.ALIGN_LEFT)
        self.result2 = wx.StaticText(self, -1, "详细文件: 无", style=wx.ALIGN_LEFT)
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

        pub.subscribe(self.finish_compute,   'finish_compute')
        pub.subscribe(self.update_process,   'update_process')
        pub.subscribe(self.on_execute_error, 'execute_error')

    def __on_choose_invoice_directory(self, event):
        dlg = wx.DirDialog(self, u"选择发票所在文件夹", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.invoices_dir = dlg.GetPath()
            self.dir_hint_text.SetLabel(f"已选路径: {dlg.GetPath()}")
        dlg.Destroy()

    def __on_input_prompt(self, evt):
        input_text = self.text_input.GetValue()
        self.prompt = list(filter(None, input_text.split(',')))
        number = len(self.prompt)
        self.label_inputed.SetLabel(f"已输入了{number}个提示符，分别是: {self.prompt}")

    def __on_start_compute(self, evt):
        print("Start to compute......")
        self.btn_compute.Disable()
        ocr_handle = OCRHandle(self.invoices_dir, self.prompt)
        ocr_thread = OcrThread(self, ocr_handle)
        ocr_thread.start()

    def finish_compute(self, result: float, detailed_result_file: str):
        print("Finished compute.")
        self.result1.SetLabel(f"😋  总金额: {result}")
        self.result2.SetLabel(f"😋  详细文件: {detailed_result_file}")
        self.detailed_result=detailed_result_file
        self.btn_compute.Enable()
        self.gauge.SetValue(0)

    def on_execute_error(self):
        self.btn_compute.Enable()
        self.gauge.SetValue(0)

    def show_message(self, message: str):
        wx.MessageDialog(self, message, "操作出错").ShowModal()

    def update_process(self, count: int):
        print(f"Update process: {count}")
        self.gauge.SetValue(count)

