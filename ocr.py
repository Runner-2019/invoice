import os
import imghdr
from datetime import datetime
from paddleocr import PaddleOCR

def is_image_file(filename) -> bool:
    img_type = imghdr.what(filename)
    return img_type is not None

def count_files_in_directory(directory_path):
    return len([entry for entry in os.listdir(directory_path) if is_image_file(os.path.join(directory_path, entry))])

# need to run only once to download and load model into memory
OCR = PaddleOCR(use_angle_cls=True, lang="ch")

class OCRHandle:
    # The gui application must contain these API:
    #      1. show_message()
    #      2. update_process()
    #      3. set_result()
    def __init__(self, app, invoices_path, prompt):
        # passed-in paramters
        self.app = app
        self.invoices_path = invoices_path
        self.prompt = prompt
        self.total_invoices_index = 0

        # inner paramters
        self.total_account=0        # total invoice account of all invoice pictures
        self.cur_invoice_path = ""  # invoice picture which is currently handling
        self.cur_invoice_index = 0  # invoice picture index of all invoices
        self.cur_account = 0        # invoice account
        self.cur_account_str = ""   # invoice account string
        self.cur_text_list = []     # picture to text
        self.cur_status = True      # current handle status
        self.detailed_log_path = "" # detailed log in docx format


    # Convert picture to text list, discards box coordinate and score.
    def __convert_once(self):
        result = OCR.ocr(self.cur_invoice_path, cls=True)
        # BUG: why result[0]?
        for index, line in enumerate(result[0]):
            text=line[1][0]
            self.cur_text_list.append(text)

    def __check_text_list(self):
        self.cur_status = True

    def __get_cur_account(self) -> bool:
        account_str_list=[]
        for text in self.cur_text_list:
            for prompt in self.prompt:
                if text.find(prompt) != -1:
                    account_str_list.append(text)

        if len(account_str_list) == 0:
            self.app.show_message("未能根据提示词找到发票金额, 可能是当前图片转文字出错了")
            self.cur_status = False
            return

        if len(account_str_list) > 1:
            self.app.show_message("根据提示词找到了多个发票金额, 可能是当前图片转文字出错了")
            self.cur_status = False
            return

        # exactly one
        self.cur_account_str = account_str_list[0]
        print(f'account string: {self.cur_account_str}')
        numbers = re.findall(r'\d+\.\d+|\d+', self.cur_account_str)
        if len(numbers) != 1:
            self.app.show_message(f"从发票金额中:{self.cur_account_str}中提取具体的金额失败了")
            self.cur_status = False
            return

        print(f'account number: {numbers[0]}')
        try:
            self.cur_account = float(numbers[0])
        except Exception as e:
            self.app.show_message(f"从发票金额:{self.cur_account_str}中提取具体的金额失败了")
            self.cur_status = False
            return


    def __creat_log_file(self):
        current_datetime_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_name = f"{current_datetime_str}.doc"
        with open(file_name, 'w') as file:
            pass
        self.detailed_log_path = file_name


    # if is_success, then append current picture to success part.
    def __append_to_detail_log(self):
        if self.cur_status:
            pass
        else:
            pass

    def __finish_one_picture(self):
        self.total_account += self.cur_account
        self.cur_account = 0
        self.cur_invoice_path = ""
        self.cur_account_str = ""
        self.cur_text_list = []

    def run(self) -> None:
        if not os.path.isdir(self.invoices_path):
            self.app.show_message(f"提供的发票文件夹有误: {self.invoices_path}")
            return


        self.total_invoices_index = count_files_in_directory(self.invoices_path)
        print(f"total invoces count: {self.total_invoices_index}")

        for filename in os.listdir(self.invoices_path):
            invoice = os.path.join(self.invoices_path, filename)
            if os.path.isfile(invoice):
                if not is_image_file(invoice):
                    continue

                print(f"正在处理: {invoice}")
                self.cur_invoice_path=invoice
                self.cur_invoice_index += 1
                self.__convert_once()
                self.__check_text_list()
                self.__append_to_detail_log()
                cur_progress = int(self.cur_invoice_index * 1.0 / self.total_invoices_index * 100)
                self.app.update_process(cur_progress)
                self.__finish_one_picture()

        print(f'total account of all tickets: {self.total_account}')
        self.app.set_result(self.total_account, self.detailed_log_path)


