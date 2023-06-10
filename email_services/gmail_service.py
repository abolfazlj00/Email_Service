from bclib import edge
from email_services.base_email_service import BaseEmailService

class GmailService(BaseEmailService):

    def __init__(self, email_configurations: "dict") -> "None":
        super().__init__(email_configurations)

    def send_email(self):
        print("sent")

    def _clean_mailbox_name(self, mailbox_name: str) -> "str":
        return mailbox_name.replace('"', "").split("/")[-1].strip()
  