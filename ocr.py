import os
import wx
import imghdr
from pubsub    import pub
from datetime  import datetime
from paddleocr import PaddleOCR

def is_image_file(filename) -> bool:
    img_type = imghdr.what(filename)
    return img_type is not None

def count_files_in_directory(directory_path) -> int:
    return len([entry for entry in os.listdir(directory_path) if is_image_file(os.path.join(directory_path, entry))])

# need to run only once to download and load model into memory
OCR = PaddleOCR( show_log=False, use_angle_cls=True, lang="ch")

class OCRHandle:
    def __init__(self, invoices_path: str, prompt: list):
        self.invoices_path = invoices_path
        self.prompt = prompt
        self.total_invoices_count = 0
        self.total_error_invoice_list=[]
        self.total_account = 0            # invoice account of all invoice pictures
        self.cur_invoice_path = ""        # invoice picture which is currently handling
        self.cur_invoice_index = 0        # invoice picture index of all invoices
        self.cur_account = 0              # invoice account
        self.cur_account_str = ""         # invoice account string
        self.cur_text_list = []           # invoice picture to text
        self.log_file = ""                # detailed log in docx format


    # Convert picture to text list, discards box coordinates and predicate score.
    def __convert_once(self):
        result = OCR.ocr(self.cur_invoice_path, cls=True)
        # BUG: why result[0]?
        for index, line in enumerate(result[0]):
            text=line[1][0]
            self.cur_text_list.append(text)


    # Check whether text lists  is valid
    def __check_text_list(self):
        if not self.cur_text_list:
            raise RuntimeError("without text list")


    # Extract account number from text list
    def __get_cur_account(self):
        account_str_list=[]
        for text in self.cur_text_list:
            for prompt in self.prompt:
                if text.find(prompt) != -1:
                    account_str_list.append(text)

        if len(account_str_list) == 0:
            raise RuntimeError("without account string")

        if len(account_str_list) > 1:
            raise RuntimeError("too many account strings")

        # exactly one
        self.cur_account_str = account_str_list[0]
        print(f'Index: {self.cur_invoice_index}, \
              account string: {self.cur_account_str} of invoice picture: {self.cur_invoice_path}')

        numbers = re.findall(r'\d+\.\d+|\d+', self.cur_account_str)
        if len(numbers) != 1:
            raise RuntimeError("too many accounts from account string")

        self.cur_account = float(numbers[0])
        print(f'Index: {self.cur_invoice_index}, \
              account number: {self.cur_account} of invoice picture: {self.cur_invoice_path}')


    def __creat_log_file(self):
        current_datetime_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = f"{current_datetime_str}.doc"
        with open(file_name, 'w') as file:
            pass
        self.log_file = file_name


    # if is_success, then append current picture to success part.
    def __append_to_detail_log(self, is_success):
        if is_success:
            pass
        else:
            pass

    def __finish_one_picture(self):
        print("__finish_one_picture")
        self.total_account += self.cur_account
        self.cur_account = 0
        self.cur_invoice_path = ""
        self.cur_account_str = ""
        self.cur_text_list = []

    def run(self) -> None:
        if not os.path.isdir(self.invoices_path):
            raise RuntimeError(f"提供的发票文件夹有误: {self.invoices_path}")

        self.total_invoices_count = count_files_in_directory(self.invoices_path)
        print(f"total invoces count: {self.total_invoices_count}")
        if self.total_invoices_count == 0:
            raise RuntimeError(f"提供的发票文件夹中不包含发票图片")

        for filename in os.listdir(self.invoices_path):
            invoice = os.path.join(self.invoices_path, filename)
            if os.path.isfile(invoice):
                if not is_image_file(invoice):
                    continue
                try:
                    print(f"dealing: {invoice}")
                    self.cur_invoice_path = invoice
                    self.cur_invoice_index += 1
                    self.__convert_once()
                    self.__check_text_list()
                    self.__append_to_detail_log(True)
                    cur_progress = int(self.cur_invoice_index * 1.0 / self.total_invoices_count * 100)
                    wx.CallAfter(pub.sendMessage, "update_process", count=cur_progress)
                except Exception as e:
                    print(str(e))
                    self.total_error_invoice_list.append(self.cur_invoice_path)
                    self.__append_to_detail_log(False)
                self.__finish_one_picture()

        print(f'total account of all tickets: {self.total_account}')
        wx.CallAfter(pub.sendMessage,
                     "finish_compute",
                     result=self.total_account,
                     detailed_result_file=self.log_file)
