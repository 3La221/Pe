from django import forms
from .models import *

# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = '__'
#         widgets = {
#             'Password': forms.PasswordInput(),  # Use PasswordInput widget for password
#         }
class PointageForm(forms.Form):
    CHOICES = [
        ('T', 'T'),
        ('R', 'R'),
        ('1', '1'),
        ('I', 'I'),
        ('2', '2'),
        ('M', 'M'),
        ('A', 'A'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('C', 'C'),
        ('Cr', 'Cr'),
        
    ]

    dropdown_menu = forms.ChoiceField(choices=CHOICES)



class EmployeForm(forms.ModelForm):
    class Meta:
        model=Employe
        exclude = ['id','Sheet_ID','station','actif','remboursement_total','remboursement_mois']
    
    def __init__(self, *args, **kwargs):
        super(EmployeForm,self).__init__(*args, **kwargs)
        self.fields['Adresse'].required = False
        self.fields['Date_Recrutement'].required = False
        self.fields['Date_Detach'].required = False
        self.fields['Situation_Familliale'].required = False
        self.fields['Affect_Origin'].required = False
        self.fields['Nbr_Enfants'].required = False

class EmployeFormForDg(forms.ModelForm):
    class Meta:
        model=Employe
        exclude = ['id','Sheet_ID','actif','remboursement_total','remboursement_mois']
    
    def __init__(self, *args, **kwargs):
        super(EmployeFormForDg,self).__init__(*args, **kwargs)
        self.fields['Adresse'].required = False
        self.fields['Date_Recrutement'].required = False
        self.fields['Date_Detach'].required = False
        self.fields['Situation_Familliale'].required = False
        self.fields['Affect_Origin'].required = False
        self.fields['Nbr_Enfants'].required = False

class remboursementForm(forms.ModelForm):
    class Meta:
        model=Employe
        fields=['remboursement_total']