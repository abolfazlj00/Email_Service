
from email_services.gmail_service import GmailService
from private_options import email_config

gmail = GmailService(email_config)

# print(gmail.mailbox_names_list())

# emails = gmail.get_emails('inbox', 100)

# for email in emails:
#     print(email.as_dict())
#     print("="*50)

# print(gmail.get_email_by_uid("INBOX", 377).as_dict())