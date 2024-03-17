import calendar
from django.db import models,connection
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext as _


class ValidDate(models.Model):
    nom = models.CharField(max_length=30)
    date_of_validation= models.DateField()
    month = models.IntegerField(default=2)

class Code(models.Model):
    ID=models.CharField(primary_key=True,max_length=3)
    Description=models.TextField()
    def __str__(self) -> str:
        return str(self.ID)

class Month_stat(models.Model):
    period=models.CharField(max_length=6)
    employe=models.ForeignKey('Employe',on_delete=models.CASCADE)
    absent=models.IntegerField(default=0)
    travail=models.IntegerField(default=0)
    mission=models.IntegerField(default=0)
    conge=models.IntegerField(default=0)
    rs=models.IntegerField(default=0)
    eve_fam=models.IntegerField(default=0)
    mld=models.IntegerField(default=0)
    abs_autorise=models.IntegerField(default=0)

    def __str__(self) -> str:
        return f'{self.employe} Month {self.period}'


class Code_Employe(models.Model):
    employe=models.ForeignKey("Employe",on_delete=models.CASCADE,related_name="code_emp")
    date=models.DateField(default=timezone.now)
    code=models.ForeignKey("Code",on_delete=models.CASCADE)
    open_to_edit = models.BooleanField(default=False)
    last_update =models.DateField(default=timezone.now)
    stored = models.BooleanField(default=False)
    
    @property
    def is_editable(self):
        today = timezone.now().date() 
        if self.code.ID == "8" :
            diff = (today - self.date).days
            return diff <= 5  # Example: Editable if the difference is less than 7 days
        
        return False  # Not editable if code.ID is not "8" 
    
    
        
    def __str__(self) -> str:
        return str(self.code.ID)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,default=1,related_name="profile")
    station = models.ForeignKey("Station",on_delete=models.CASCADE,null=True)
    da = models.IntegerField(default=3)
    def __str__(self):
        if self.da == 3 :
            return f'Respon Pointage {self.station}'
        elif self.da == 2:
            return f'Chef Station {self.station}'
        else : 
            return f'Directeur Generale'


class Station(models.Model):
    
    Nom_Station=models.CharField(max_length=40,unique=True)
    SheetID = models.CharField(max_length=70,null=True ) 
    last_update = models.DateField(null=True , blank=True)
    sheets_created=models.ForeignKey("User_sheets", on_delete=models.SET_NULL,null=True)

    
    
    def __str__(self):
        return self.Nom_Station

code_counts = {
            "RS": 0,
            "C": 0,
            "8": 0,
            "7": 0,
            "MLD": 0,
            "5": 0,
            "3": 0,
            "6": 0
        }
    
class User_sheets(models.Model):
    sheets_id = models.CharField(max_length=1000)  # Adjust max_length as needed

    def get(self):
        return self.sheets_id.split(',')

    def add(self, value_to_append):
        if self.sheets_id:
            self.sheets_id += ',' + str(value_to_append)
        else:
            self.sheets_id = str(value_to_append)
               
class Employe(models.Model):
    ID=models.AutoField(primary_key=True)
    Nom=models.CharField(max_length=30)
    Prenom=models.CharField(max_length=30)
    Adresse=models.CharField(max_length=50,null=True)
    Date_Recrutement=models.DateField(default=timezone.now)
    Affect_Origin=models.CharField(max_length=30,null=True)
    Fonction=models.CharField(max_length=30)
    Date_Detach= models.DateField(null=True)
    station=models.ForeignKey(Station,on_delete=models.CASCADE,null=True)
    Situation_Familliale=models.CharField(max_length=30,null=True)
    Nbr_Enfants=models.IntegerField(null=True)
    Sheet_ID=models.IntegerField(unique=True,null=True)
    recup = models.IntegerField(default=0)
    remboursement_total=models.IntegerField(default=0)
    remboursement_mois=models.IntegerField(default=0)
    actif = models.BooleanField(default=True)
    
    
    
    
    
    def save(self, *args, **kwargs):
        '''call_parameter = kwargs.pop('call', True) 
        if not call_parameter:'''

        '''Employe.objects.all().delete()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='pointage_employe';")

# Step 3: Vacuum the database to reclaim storage space
        with connection.cursor() as cursor:
            cursor.execute("VACUUM;")'''
        try:
            test=Employe.objects.get(pk=self.pk)
            credentials = service_account.Credentials.from_service_account_file(
            './petromagpointage-be9f913f9b9e.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets'],
            )
            
    # Specify the ID of your Google Sheet
            spreadsheet_id = '1lj3NUBuA-4I3KvsTvndZdd3owXWftdO7ma_hfhTQvjg'
            service = build('sheets', 'v4', credentials=credentials)
            ranges_and_values = {
                f"{self.ID}!AG6:AJ6": [[f"{self.Date_Recrutement}"]],
                f"{self.ID}!B8:N8": [[f"{self.Fonction}"]],
                f"{self.ID}!U6:X6": [[f"{self.ID}"]],
                f"{self.ID}!B6:N6": [[f"{self.Nom}"]],  # Update B2:N6 with "Value1"
                f"{self.ID}!B7:N7": [[f"{self.Prenom}"]],  # Update B7:N7 with "Value2"
                f"{self.ID}!AG8:AJ8": [["" if f"{self.Date_Detach}" == 'None' else f"{self.Date_Detach}"]],
                f"{self.ID}!B10:X10": [["" if f"{self.Adresse}" == 'None' else f"{self.Adresse}"]],
                f"{self.ID}!AG9:AM9": [["" if f"{self.Affect_Origin}" == 'None' else f"{self.Affect_Origin}"]],
                f"{self.ID}!AG10:AJ10": [["" if f"{self.Situation_Familliale}" == 'None' else f"{self.Situation_Familliale}"]],
                f"{self.ID}!AG11:AH11": [["" if f"{self.Nbr_Enfants}" == 'None' else f"{self.Nbr_Enfants}"]],
                f"{self.ID}!AO4:AT4": [[datetime.now().year]],
            }
# Build the requests using list comprehension
            requests = [
                {
                    "range": range_,
                    "values": values,
                }
                for range_, values in ranges_and_values.items()
                ]

# Make the API request to update multiple cells
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"valueInputOption": "RAW", "data": requests},
            ).execute()
        except:
            credentials = service_account.Credentials.from_service_account_file(
            './petromagpointage-be9f913f9b9e.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets'],
            )
            station=Station.objects.get(pk=self.station_id)
            
    # Specify the ID of your Google Sheet
            spreadsheet_id = station.SheetID
            print(station.SheetID)
    # Create a service using the credentials
            service = build('sheets', 'v4', credentials=credentials)
            source_sheet_id='106559687'
            new_sheet = service.spreadsheets().sheets().copyTo(
            spreadsheetId=spreadsheet_id,
            sheetId=source_sheet_id,
            body={'destinationSpreadsheetId': spreadsheet_id}
            ).execute()
            super(Employe, self).save(*args, **kwargs)
            self.Sheet_ID=new_sheet['sheetId']
            new_sheet_title=str(self.ID)
            service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={'requests': [{'updateSheetProperties': {'properties': {'sheetId': str(self.Sheet_ID), 'title': new_sheet_title}, 'fields': 'title'}}]}
            ).execute()
            ranges_and_values = {
                f"{self.ID}!AG6:AJ6": [[f"{self.Date_Recrutement}"]],
                f"{self.ID}!B8:N8": [[f"{self.Fonction}"]],
                f"{self.ID}!U6:X6": [[f"{self.ID}"]],
                f"{self.ID}!B6:N6": [[f"{self.Nom}"]],  # Update B2:N6 with "Value1"
                f"{self.ID}!B7:N7": [[f"{self.Prenom}"]],  # Update B7:N7 with "Value2"
                f"{self.ID}!AG8:AJ8": [["" if f"{self.Date_Detach}" == 'None' else f"{self.Date_Detach}"]],
                f"{self.ID}!B10:X10": [["" if f"{self.Adresse}" == 'None' else f"{self.Adresse}"]],
                f"{self.ID}!AG9:AM9": [["" if f"{self.Affect_Origin}" == 'None' else f"{self.Affect_Origin}"]],
                f"{self.ID}!AG10:AJ10": [["" if f"{self.Situation_Familliale}" == 'None' else f"{self.Situation_Familliale}"]],
                f"{self.ID}!AG11:AH11": [["" if f"{self.Nbr_Enfants}" == 'None' else f"{self.Nbr_Enfants}"]],
                f"{self.ID}!AO4:AT4": [[datetime.now().year]],
            }
# Build the requests using list comprehension
            requests = [
                {
                    "range": range_,
                    "values": values,
                }
                for range_, values in ranges_and_values.items()
                ]

# Make the API request to update multiple cells
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"valueInputOption": "RAW", "data": requests},
            ).execute()
            
        super(Employe, self).save(*args, **kwargs)
    # Call the original save method to save the instance
        

    def __str__(self):
        return f"{self.Nom} - {self.Prenom}"
    
