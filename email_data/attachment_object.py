class AttachmentObject():
    def __init__(self, attachment_dict:"dict[str, any]") -> None:
        self.__args = attachment_dict

    @property
    def Filename(self):
        return self.__args["filename"]
    
    @property
    def Content_type(self):
        return self.__args["content-type"]
    
    @property
    def Pay_load(self):
        return self.__args["pay_load"]