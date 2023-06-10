from base_email_service import BaseEmailService
from gmail_service import GmailService
from abc import ABC

class EmailFactory(ABC):
    @staticmethod
    def create(email_type:"str", email_configuration:"dict") -> "BaseEmailService":
        if email_type == "gmail":
            return GmailService(email_configuration)
        raise ValueError(f"Invalid type=${email_type}")