import traceback
import sys

class CustomException(Exception):
    """
    Custom Exception class for handling exceptions with detailed error messages.
    Inherits from the base Exception class.
    Attributes:
        error_message (str): Detailed error message including file name and line number.
    Methods:
        get_detailed_error_message(error_message, error_detail): Static method to generate detailed error message
    """
    
    def __init__(self, error_message, error_detail:sys):
        super().__init__(error_message)
        self.error_message = self.get_detailed_error_message(error_message,error_detail)

    @staticmethod
    def get_detailed_error_message(error_message , error_detail:sys):

        _, _, exc_tb = traceback.sys.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno

        return f"Error in {file_name} , line {line_number} : {error_message}"
    
    def __str__(self):
        return self.error_message