from django import forms


class ToDoForm(forms.Form):
    email = forms.EmailField(max_length=40)
    key = forms.CharField(widget=forms.Textarea(attrs={"rows":1, "cols":20}))
    description = forms.CharField(widget=forms.Textarea(attrs={"rows":5, "cols":30}))
    image1 = forms.FileField()
    image2 = forms.FileField()
    
class decForm(forms.Form):
    key2 = forms.CharField(widget=forms.Textarea(attrs={"rows":1, "cols":20}))
    snap = forms.FileField()