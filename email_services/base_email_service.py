from abc import ABC, abstractmethod
import asyncio
from bclib import edge
import imaplib
import ssl
import imaplib
from email import message_from_bytes
from email.header import decode_header, Header
import os
from email_data.email_object import EmailObject
from email_data.attachment_object import AttachmentObject
from datetime import datetime, timedelta
import time
import re

class BaseEmailService(ABC):
    DEFAULT_SAVE_COUNT = 100

    def __init__(self, email_configurations:"dict") -> None:
        super().__init__()
        self._username = email_configurations["username"]
        self._password = email_configurations["password"]
        self._imap_host = email_configurations["imap_host"]
        self._imap_port = email_configurations["imap_port"]
        self._smtp_host = email_configurations["smtp_host"]
        self._smtp_port = email_configurations["smtp_port"]
        self._has_ssl = bool(email_configurations["has_ssl"])
        self._save_count = email_configurations["save_count"] if "save_count" in email_configurations else BaseEmailService.DEFAULT_SAVE_COUNT

    def login(self) -> "imaplib.IMAP4|imaplib.IMAP4_SSL":
        context = ssl.create_default_context()
        if self._has_ssl:
            server = imaplib.IMAP4_SSL(self._imap_host, self._imap_port, ssl_context=context)
            # server = imaplib.IMAP4_SSL(self._smtp_host, self._smtp_port)
        else:
            server = imaplib.IMAP4(self._imap_host, self._imap_port)
            server.starttls(ssl_context=context)
        server.login(self._username, self._password)
        return server
    
    def logout(self, server:"imaplib.IMAP4|imaplib.IMAP4_SSL"):
        while True:
            resp, _ = server.logout()
            if resp == "BYE":
                break

    @abstractmethod
    def _clean_mailbox_name(self, mailbox_name:"str"): ...

    def mailbox_names_list(self) -> "list":
        ret_val = list()
        server = self.login()
        with server:
            status, mailbox_list = server.list()
            if status == "OK":
                for mailbox in mailbox_list:
                    mailbox_name = mailbox.decode().split('"/"')[-1].strip()
                    ret_val.append({
                        "original_name": mailbox_name,
                        "clean_name": self._clean_mailbox_name(mailbox_name)
                    })
            self.logout(server)
        return ret_val

    def __create_email_object(self, uid:"int", messages:"list") -> "EmailObject":

        def decode_handler(obj: "Header|str"):
            return "".join([
                item[0].decode()
                if isinstance(item[0], bytes) else item[0]
                for item in decode_header(obj) 
            ])
        
        email_dict = dict()
        for message in messages:
            if isinstance(message, tuple):
                body = None
                text = None
                size_match = re.search(r'RFC822\.SIZE (\d+)', message[0].decode('utf-8'))
                size_data = int(size_match.group(1))
                msg = message_from_bytes(message[1])
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        # extract content type of email
                        try:
                            # get the email body
                            email_content = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                if "attachments" not in email_dict:
                                    email_dict["attachments"] = list()
                                email_dict["attachments"].append(AttachmentObject({
                                    "filename": filename,
                                    "content-type": content_type,
                                    "pay_load": part.get_payload(decode=True)
                                }))
                        elif content_type in ("text/plain", "text/html"):
                            if content_type == "text/plain":
                                text = email_content
                            elif content_type == "text/html":
                                body = email_content
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    try:
                        email_content = msg.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain":
                        text = email_content
                    elif content_type == "text/html":
                        body = email_content
                email_dict.update({
                    "uid": uid,
                    "message_id": msg["Message-ID"],
                    "subject": decode_handler(msg["Subject"]),
                    "from": decode_handler(msg["From"]),
                    "to": decode_handler(msg["To"]),
                    "size": size_data,
                    "references": msg["References"],
                    "body": body,
                    "text": text,
                })
            else:
                time_struct:"time.struct_time" = imaplib.Internaldate2tuple(message)
                flags = list()
                for flag_byte in imaplib.ParseFlags(message):
                    flags.append(flag_byte.decode())
                # Extract the size data
                email_dict.update({
                    "flags": flags,
                    "date": datetime(
                        year=time_struct.tm_year, 
                        month=time_struct.tm_mon, 
                        day=time_struct.tm_mday, 
                        hour=time_struct.tm_hour, 
                        minute=time_struct.tm_min, 
                        second=time_struct.tm_sec
                    ) - timedelta(hours=time_struct.tm_isdst)
                })
        return EmailObject(email_dict)

    def get_emails(self, folder:"str", count:"int") -> "list[EmailObject]":
        email_objects:"list[EmailObject]" = list()
        server:"imaplib.IMAP4_SSL" = self.login()
        with server:
            try:
                resp, mail_count = server.select(mailbox=folder)
                if resp == "OK":
                    mail_count = int(mail_count[0].decode())
                    for uid in range(mail_count, mail_count - count, -1):
                        # fetch the email message by ID
                        response, messages = server.fetch(str(uid), "(INTERNALDATE FLAGS RFC822.SIZE RFC822)")
                        if response == "OK":
                            email_objects.append(self.__create_email_object(uid, messages))
            except Exception as ex:
                print("[Get Emails Error]", repr(ex))
            self.logout(server)
        return email_objects

    def get_email_by_uid(self, folder:"str", uid:"int") -> "EmailObject|None":
        email_object = None
        server:"imaplib.IMAP4_SSL" = self.login()
        with server:
            try:
                resp, mail_count = server.select(mailbox=folder)
                if resp == "OK":
                    mail_count = int(mail_count[0].decode())
                    # fetch the email message by ID
                    response, messages = server.fetch(str(uid), "(INTERNALDATE FLAGS RFC822.SIZE RFC822)")
                    if response == "OK":
                        email_object = self.__create_email_object(uid, messages)
            except Exception as ex:
                print("[Get Email Error]", repr(ex))
            self.logout(server)
        return email_object
    
    @abstractmethod
    def send_email(self): ...

