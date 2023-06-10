class EmailObject():
    def __init__(self, email_dict:"dict[str, any]") -> None:
        self.__args = email_dict

    @property
    def From(self):
        return self.__args["from"]

    @property
    def To(self):
        return self.__args["to"]
    
    @property
    def UID(self):
        return self.__args["uid"]
    
    @property
    def MessageID(self):
        return self.__args["message_id"]
    
    @property
    def Body(self):
        return self.__args["body"]

    @property
    def Text(self):
        return self.__args["text"]
    
    @property
    def Date(self):
        return self.__args["date"]
    
    @property
    def Subject(self):
        return self.__args["subject"]

    @property
    def Size(self):
        return self.__args["size"]

    @property
    def Flags(self):
        return self.__args["flags"]

    @property
    def References(self):
        return self.__args["references"]

    @property
    def Attachments(self):
        return self.__args.get("attachments", list())

    @property
    def Clean_subject(self):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in self.Subject)
    
    def as_dict(self):
        return {
            "UID": self.UID,
            "MessageID": self.MessageID,
            "Date": self.Date,
            "Subject": self.Subject,
            "Clean_subject": self.Clean_subject,
            "From": self.From,
            "To": self.To,
            "Flags": self.Flags,
            "Size": self.Size,
            "References": self.References,
            "Attachmets": self.Attachments,
            # "Text": self.Text,
            # "Body": self.Body,
        }