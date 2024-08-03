import wx
import os
import re
import time
from paddleocr import PaddleOCR, draw_ocr

# need to run only once to download and load model into memory
ocr = PaddleOCR(use_angle_cls=True, lang="ch")

def get_one_picture_text(img_path: str)->list:
    text_list=[]
    result = ocr.ocr(img_path, cls=True)
    for index, line in enumerate(result[0]):
        text=line[1][0]
        text_list.append(text)
    return text_list

def check_text_list(text_list: list) -> bool:
    return True

def get_account(text_list: list)-> float:
    account_str=""
    for text in text_list:
        if text.find("小写") != -1:
            account_str=text

    if not account_str:
        raise("can't find account")

    print(f'account string: {account_str}')
    numbers = re.findall(r'\d+\.\d+|\d+', account_str)
    if len(numbers) > 1:
        raise("Parse error. There are more than one account.")
    print(f'account number: {numbers[0]}')
    return float(numbers[0])


def on_user_select_directory(dir_path: str) -> float:
    if not os.path.isdir(dir_path):
        print(f"提供的路径不是一个有效的目录: {dir_path}")
        return

    total=0
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        # 确保是文件而不是目录
        if os.path.isfile(file_path):
            print(file_path)
            text_list = get_one_picture_text(file_path)
            check_text_list(text_list)
            account = get_account(text_list)
            total += account
    print(f'total account of all tickets: {total}')
    return total



# class DirDialog(wx.Frame):
#  
#
#     def __init__(self):
#         wx.Frame.__init__(self, None, -1, u"文件夹选择对话框")
#         self.button = wx.Button(self, -1, u"文件夹选择对话框")
#         self.text_1 = wx.TextCtrl(self, wx.ID_ANY, "")
#         self.Bind(wx.EVT_BUTTON, self.OnButton, self.button)
#         sizer_1 = wx.BoxSizer(wx.VERTICAL)
#         sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
#         sizer_2.Add(self.text_1, 1, wx.ALL, 0)
#         sizer_2.Add(self.button, 0, 0, 0)
#         sizer_1.Add(sizer_2, 0, wx.ALL | wx.EXPAND, 0)
#         self.SetSizer(sizer_1)
#         self.Layout()
#
#     def OnButton(self, event):
#         dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
#         if dlg.ShowModal() == wx.ID_OK:
#             total = on_user_select_directory(dlg.GetPath())
#             self.text_1.SetValue(str(total))
#
#         dlg.Destroy()


if __name__ == "__main__":
    frame = wx.PySimpleApp()
    app = DirDialog()
    app.Show()
    frame.MainLoop()


