## Forms for the csd demo file up-load forms#from django import formsclass FileNameForm(forms.Form):    file_name = forms.FileField(label='Song file name   ', max_length=150)        def get_name(self):        return self.file_nameclass FileNameForm2(forms.Form):    file_nam1 = forms.FileField(label='Song file name 1   ', max_length=150)    file_nam2 = forms.FileField(label='Song file name 2   ', max_length=150)    def get_name1(self):        return self.file_nam1    def get_nam2(self):        return self.file_nam2