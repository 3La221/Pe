import calendar
from datetime import date, timedelta
import locale
import os
import shutil
from django.contrib.auth import authenticate, login
from django.shortcuts import render,redirect
from django.http import FileResponse, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from openpyxl import load_workbook
from pointage.forms import *
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time
from django.contrib.auth import logout
from .models import *



def pointage2(request,ID):
    station = Station.objects.get(id=ID)
    instances=Employe.objects.filter(station=station)
    date=datetime.now().date()  
    f_date = date - timedelta(days=5)
    print(date)
    date_range = [f_date + timedelta(days=i) for i in range(10)]
    if request.method == 'POST':
        
        
        credentials = service_account.Credentials.from_service_account_file(
        './petromagpointage-be9f913f9b9e.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
        )
        MI=['1',"2","3","4","5","MS"]
        Conge=['C','CSS']
        # Specify the ID of your Google Sheet
        spreadsheet_id = station.SheetID
        service = build('sheets', 'v4', credentials=credentials)
        for i in instances:
            ranges_and_values={}
            for date in date_range:
                cell=find_cell(date)
                choice=request.POST.get(f'{i.ID}_{date}')
                
                sheet_range = f"{i.ID}!{cell}"
                code=Code_Employe.objects.filter(employe=i,date=date)
                if  choice == "" :
                    if code.exists():
                                ranges_and_values[sheet_range]=[['']]
                                month_emp=Month_stat.objects.filter(Employe=i,period=f'{date.month}{date.year}')
                                if code.code_id in MI:
                                    month_emp.mission-=1
                                elif code.code_id in "8":
                                    month_emp.absent-=1
                                elif code.code_id in Conge:
                                    month_emp.conge-=1
                                elif code.code_id  == "7":
                                    month_emp.abs_autorise-=1
                                elif code.code_id in "MLD":
                                    month_emp.mld-=1
                                elif code.code_id in "RS":
                                    month_emp.rs-=1
                                elif code.code_id in "6":
                                    month_emp.eve_fam-=1

                                code.delete()
                    else:
                        continue
                elif choice == None :
                    continue
                else:
                    if code.exists():
                        period_i=f'{date.month}{date.year}'
                        print(period_i)
                        try:
                            if code[0].stored:
                                month_emp=Month_stat.objects.get(employe=i,period=period_i)
                                if code[0].code_id in MI:
                                    month_emp.mission-=1
                                elif code[0].code_id in "8":
                                    month_emp.absent-=1
                                elif code[0].code_id in Conge:
                                    month_emp.conge-=1
                                elif code[0].code_id  == "7":
                                    month_emp.abs_autorise-=1
                                elif code[0].code_id in "MLD":
                                    month_emp.mld-=1
                                elif code[0].code_id in "RS":
                                    month_emp.rs-=1
                                elif code[0].code_id in "6":
                                    month_emp.eve_fam-=1
                                elif code[0].code_id in 'T':
                                    month_emp.travail-=1
                        except:
                            pass            
                        code[0].delete()
                        
                    code_emp=Code_Employe()
                    code_emp.employe=i
                    code_emp.date=date
                    code_emp.last_update = timezone.now().date()
                    code_emp.code=Code.objects.get(pk=choice)
                    code_emp.save()
                    ranges_and_values[sheet_range] = [[f"{choice}"]]
            requests = [
                {
                    "range": range_,
                    "values": values,
                }
                for range_, values in ranges_and_values.items()
                ]
            service.spreadsheets().values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"valueInputOption": "RAW", "data": requests},
            ).execute()

            station.last_update= datetime.now().date()
            station.save()

        return redirect("menu_view")
    else:
        if date.day>=16:
            start_date=datetime(date.year,date.month,16)
            end_date=datetime(date.year,date.month+1,15)
            if end_date.month==13:
                end_date.month=1
        else:
            start_date=datetime(date.year,date.month-1,16)
            end_date=datetime(date.year,date.month,15)
            if start_date.month==0:
                start_date.month=12
        tmp = {}
        res = {}
        overworked_employes=[]
        for i in instances :
                codes_emp = Code_Employe.objects.filter(employe=i)
                overwork=codes_emp.filter(code_id="T",date__range=(start_date,end_date)).count()
                if overwork > 6 :
                    overworked_employes.append(i)  
                tmp = {}
                for d in date_range:
                    try :
                        e = codes_emp.get(date=d)
                        
                        tmp[str(d)] = e 
                    except:
                        tmp[str(d)] = ""
                
                res[i.ID] = tmp
        codes=Code.objects.all()
        context={'date':date,'instances':instances,'date_range':date_range,'codes':codes,'res':res,'today':date,'overwork':overworked_employes}
        return render(request,'pointage.html',context)


def logout_view(request):
    logout(request)
    return redirect("/")

def find_cell(date):
    if (date.day <=25):
        alphabet=chr(ord('B') + (date.day)%26 -1)
    else:
        alphabet="A"+chr(ord('A') + (date.day)%26)
    return (f"{alphabet}{date.month+13}")



def main_view(request,ID):
    i=Employe.objects.get(pk=ID)
    return render(request,'main.html',{'result':i})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("menu_view")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('menu_view')  # Redirect to home page after successful login
        else:
            # Handle invalid login
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})
    else:
        return render(request, 'login.html')






def menu_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    id = request.user.profile.station.id
    if request.user.profile.da == 1 and request.GET.get('station'):
        print(request.GET.get('station'))
        id=request.GET.get('station') 
    stations = Station.objects.all()
    station = Station.objects.get(id=id)
    
    yyyy = datetime.now().year
    mm = datetime.now().month
    if datetime.now().day < 16:
        mm = mm - 1
    if mm == 0 :
        mm = 12
        
    periode = f'{mm}{yyyy}'
    
    last_update =station.last_update
    if 1 :
        employes=Employe.objects.filter(station_id=id)
        MI=['1',"2","3","4","5","MS"]
        Conge=['C','CSS']
        for employe in employes:
            code_emp=''
            month_emp=''
            try:
                code_emps=Code_Employe.objects.filter(employe=employe,last_update=last_update)
                print("CODE EMP : ",code_emp)
                if code_emps:
                    month_emp , _ = Month_stat.objects.get_or_create(employe=employe,period=periode)
                    print("Month Emp",month_emp)
                    for code_emp in code_emps:
                        if not code_emp.stored :
                            if code_emp.code_id == "T":
                                month_emp.travail+=1
                                month_emp.save()
                            try:
                                valid_date = ValidDate.objects.get(month=datetime.now().month)
                                if code_emp.date.day > valid_date.date_of_validation.day and code_emp.date.month == valid_date.month :
                                    if code_emp.code_id in MI:
                                        month_emp.mission+=1
                                    elif code_emp.code_id in "8":
                                        month_emp.absent+=1
                                    elif code_emp.code_id in Conge:
                                        month_emp.conge+=1
                                    elif code_emp.code_id  == "7":
                                        month_emp.abs_autorise+=1
                                    elif code_emp.code_id in "MLD":
                                        month_emp.mld+=1
                                    elif code_emp.code_id in "RS":
                                        month_emp.rs+=1
                                    elif code_emp.code_id in "6":
                                        month_emp.eve_fam+=1
                            except:
                                pass
                                
                            code_emp.stored = True
                            code_emp.save()
            except Code_Employe.DoesNotExist:
                    continue
    
        
    return render(request, 'menu.html',{'id':id ,'station':station ,'stations':stations , 'today':datetime.now().day})


def add_employe(request,ID):
    if request.user.profile.station.id != ID and (request.user.profile.da != 1) :
        return redirect("menu_view")
    if request.user.profile.da == 1:
        if request.method == 'POST':
            form = EmployeFormForDg(request.POST)
            if form.is_valid():
                user=form.save()
                return redirect('table_employe',ID)
        else :
            form = EmployeFormForDg()
    else:
        if request.method == 'POST':
            form = EmployeForm(request.POST)
            if form.is_valid():
                user=form.save()
                user.station=ID
                user.save()
                return redirect('table_employe',ID)
        else:
            form = EmployeForm()
            
    return render (request, 'add_employe.html', {'form': form,'id':ID})

def table_employe(request,ID):
    if request.user.profile.station.id != ID  and (request.user.profile.da != 1) :
        return redirect("menu_view")
    instances=Employe.objects.filter(station=ID)
    return render(request,'table_employe.html',{'id':ID,'instances':instances,'da':request.user.profile.da})


        
def pointage_mois(request,ID):
    # if request.user.profile.station.id != ID and (request.user.profile.da == 1) :
    #     return redirect("menu_view")
    instance=Employe.objects.get(pk=ID)
    return render(request,'mois_form.html',{'instance':instance})




def affichage_mois(request,ID):

    month_names_french = {
        0: 'janvier',
        1: 'janvier',
        2: 'février',
        3: 'mars',
        4: 'avril',
        5: 'mai',
        6: 'juin',
        7: 'juillet',
        8: 'août',
        9: 'septembre',
        10: 'octobre',
        11: 'novembre',
        12: 'décembre',
    }
    
    

    i=Employe.objects.get(pk=ID)
    mois=request.POST.get('month')
    credentials = service_account.Credentials.from_service_account_file(
    './petromagpointage-be9f913f9b9e.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets'],
    )
    station=Station.objects.get(pk=i.station_id)
    # Create a service using the credentials
    service = build('sheets', 'v4', credentials=credentials)
    source_spreadsheet_id = station.SheetID
    dest_spreadsheet_id = '1mcaMIJmwYZV-TytMXaRlrNQwZHjEp2yCP7W1GSyjaSk'
    last_day=calendar.monthrange(2024,int(mois))[1]
    if station.sheets_created:
        user_sheet=station.sheets_created
    else:
        user_sheet=User_sheets()
        user_sheet.save()
        station.sheets_created=user_sheet
        station.save()
    print(last_day)
    if last_day==31:
        sheet_name=f'{i.ID} {request.user.username}'
        range_to_fill = f'{sheet_name}!B18:AF18'
        spreadsheet_metadata = service.spreadsheets().get(spreadsheetId=dest_spreadsheet_id).execute()
# Check if the target sheet name exists
        sheet_exists = next((sheet for sheet in spreadsheet_metadata['sheets'] if sheet['properties']['title'] == sheet_name), None)
        if sheet_exists is None: 
            new_sheet = service.spreadsheets().sheets().copyTo(
                spreadsheetId=dest_spreadsheet_id,
                sheetId=903521796,
                body={'destinationSpreadsheetId': dest_spreadsheet_id}
                ).execute()
            Sheet_ID=new_sheet['sheetId']
            user_sheet.add(Sheet_ID)
            user_sheet.save()
            service.spreadsheets().batchUpdate(
                spreadsheetId=dest_spreadsheet_id,
                body={'requests': [{'updateSheetProperties': {'properties': {'sheetId': str(Sheet_ID), 'title': sheet_name}, 'fields': 'title'}}]}
                ).execute()
        else:
            Sheet_ID=sheet_exists['properties']['sheetId']
        borders = {
            "style": "SOLID",
            "width": 1,
            "color": {
                "red": 0.0,
                "green": 0.0,
                "blue": 0.0
            }
        }

        # Build the request body
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": Sheet_ID,
                            "startRowIndex": 16,  # Row index 17 (0-based)
                            "endRowIndex": 18,    # Row index 18 (0-based)
                            "startColumnIndex": 1,  # Column index B (0-based)
                            "endColumnIndex": 32   # Column index AF (0-based)
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "borders": {
                                    "top": borders,
                                    "bottom": borders,
                                    "left": borders,
                                    "right": borders
                                }
                            }
                        },
                        "fields": "userEnteredFormat.borders"
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(spreadsheetId=dest_spreadsheet_id, body=body).execute()
        temp=1
    elif last_day==30:
        sheet_name=f'{i.ID} {request.user.username}'
        range_to_fill = f'{sheet_name}!B18:AE18'
        spreadsheet_metadata = service.spreadsheets().get(spreadsheetId=dest_spreadsheet_id).execute()

# Check if the target sheet name exists
        sheet_exists = next((sheet for sheet in spreadsheet_metadata['sheets'] if sheet['properties']['title'] == sheet_name), None)
        if sheet_exists is None: 
            new_sheet = service.spreadsheets().sheets().copyTo(
                spreadsheetId=dest_spreadsheet_id,
                sheetId=903521796,
                body={'destinationSpreadsheetId': dest_spreadsheet_id}
                ).execute()
            Sheet_ID=new_sheet['sheetId']
            user_sheet.add(Sheet_ID)
            user_sheet.save()    
            service.spreadsheets().batchUpdate(
                spreadsheetId=dest_spreadsheet_id,
                body={'requests': [{'updateSheetProperties': {'properties': {'sheetId': str(Sheet_ID), 'title': sheet_name}, 'fields': 'title'}}]}
                ).execute()
        else:
            Sheet_ID=sheet_exists['properties']['sheetId']
        
        borders = {
            "style": "SOLID",
            "width": 1,
            "color": {
                "red": 0.0,
                "green": 0.0,
                "blue": 0.0
            }
        }

        # Build the request body
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": Sheet_ID,
                            "startRowIndex": 16,  # Row index 17 (0-based)
                            "endRowIndex": 18,    # Row index 18 (0-based)
                            "startColumnIndex": 1,  # Column index B (0-based)
                            "endColumnIndex": 31   # Column index AF (0-based)
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "borders": {
                                    "top": borders,
                                    "bottom": borders,
                                    "left": borders,
                                    "right": borders
                                }
                            }
                        },
                        "fields": "userEnteredFormat.borders"
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(spreadsheetId=dest_spreadsheet_id, body=body).execute()
        temp=2
    elif last_day==29:
        sheet_name=f'{i.ID} {request.user.username}'
        range_to_fill = f'{sheet_name}!B18:AD18'
        spreadsheet_metadata = service.spreadsheets().get(spreadsheetId=dest_spreadsheet_id).execute()

# Check if the target sheet name exists
        sheet_exists = next((sheet for sheet in spreadsheet_metadata['sheets'] if sheet['properties']['title'] == sheet_name), None)
        if sheet_exists is None: 
            new_sheet = service.spreadsheets().sheets().copyTo(
                spreadsheetId=dest_spreadsheet_id,
                sheetId=903521796,
                body={'destinationSpreadsheetId': dest_spreadsheet_id}
                ).execute()
            Sheet_ID=new_sheet['sheetId']
            user_sheet.add(Sheet_ID)
            user_sheet.save()
            service.spreadsheets().batchUpdate(
                spreadsheetId=dest_spreadsheet_id,
                body={'requests': [{'updateSheetProperties': {'properties': {'sheetId': str(Sheet_ID), 'title': sheet_name}, 'fields': 'title'}}]}
                ).execute()
        else:
            Sheet_ID=sheet_exists['properties']['sheetId']
        
        borders = {
            "style": "SOLID",
            "width": 1,
            "color": {
                "red": 0.0,
                "green": 0.0,
                "blue": 0.0
            }
        }

        # Build the request body
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": Sheet_ID,
                            "startRowIndex": 16,  # Row index 17 (0-based)
                            "endRowIndex": 18,    # Row index 18 (0-based)
                            "startColumnIndex": 1,  # Column index B (0-based)
                            "endColumnIndex": 30   # Column index AF (0-based)
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "borders": {
                                    "top": borders,
                                    "bottom": borders,
                                    "left": borders,
                                    "right": borders
                                }
                            }
                        },
                        "fields": "userEnteredFormat.borders"
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(spreadsheetId=dest_spreadsheet_id, body=body).execute()
        temp=3
    elif last_day==28:
        sheet_name=f'{i.ID} {request.user.username}'
        range_to_fill=f'{sheet_name}!B18:AC18'
        spreadsheet_metadata = service.spreadsheets().get(spreadsheetId=dest_spreadsheet_id).execute()

# Check if the target sheet name exists
        sheet_exists = next((sheet for sheet in spreadsheet_metadata['sheets'] if sheet['properties']['title'] == sheet_name), None)
        if sheet_exists is None: 
            new_sheet = service.spreadsheets().sheets().copyTo(
                spreadsheetId=dest_spreadsheet_id,
                sheetId=903521796,
                body={'destinationSpreadsheetId': dest_spreadsheet_id}
                ).execute()
            Sheet_ID=new_sheet['sheetId']
            user_sheet.add(Sheet_ID)
            user_sheet.save()
            #connect the sheets to the owner 
            service.spreadsheets().batchUpdate(
                spreadsheetId=dest_spreadsheet_id,
                body={'requests': [{'updateSheetProperties': {'properties': {'sheetId': str(Sheet_ID), 'title': sheet_name}, 'fields': 'title'}}]}
                ).execute()
        else:
            Sheet_ID=sheet_exists['properties']['sheetId']
        
        borders = {
            "style": "SOLID",
            "width": 1,
            "color": {
                "red": 0.0,
                "green": 0.0,
                "blue": 0.0
            }
        }

        # Build the request body
        body = {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": Sheet_ID,
                            "startRowIndex": 16,  # Row index 17 (0-based)
                            "endRowIndex": 18,    # Row index 18 (0-based)
                            "startColumnIndex": 1,  # Column index B (0-based)
                            "endColumnIndex": 29   # Column index AF (0-based)
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "borders": {
                                    "top": borders,
                                    "bottom": borders,
                                    "left": borders,
                                    "right": borders
                                }
                            }
                        },
                        "fields": "userEnteredFormat.borders"
                    }
                }
            ]
        }
        service.spreadsheets().batchUpdate(spreadsheetId=dest_spreadsheet_id, body=body).execute()
        temp=4
    range_to_clear=f'{sheet_name}!B17:AF17'
    service.spreadsheets().values().clear(
        spreadsheetId=dest_spreadsheet_id,
        range=range_to_clear
    ).execute()
    start_date = datetime(2024, int(mois), 16)

    # Calculate the end date as the 15th of the next month
    end_date = datetime(2024, int(mois) + 1, 15)

    # Generate the list of day numbers from start_date to end_date
    day_numbers = [day.day for day in (start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1))]

    born_inf=int(mois)
    born_sup=(int(mois)+1) if (int(mois)+1) <=12 else 1
# Specify the sheet name and range to copy
    ranges = [f"{ID}!AO4:AT4",f"{ID}!Q{born_inf+13}:AG{born_inf+13}",f"{ID}!B{born_sup+13}:AG{born_sup+13}"]
# Iterate through each range and retrieve values
    result=service.spreadsheets().values().batchGet(
        spreadsheetId=source_spreadsheet_id,
        ranges=ranges,
        ).execute()
    list1 = result['valueRanges'][1]['values']
    list1f=list1[0][:-temp]
    list2 = result['valueRanges'][2]['values']
    list2f=list2[0][:15]
    merged_list = list1f + list2f
    ranges_and_values = {
        f'{sheet_name}!B17:AF17':[day_numbers],#new
        f'{sheet_name}!W4:Y4':[[f'15 {month_names_french[(int(mois)+1)%13]} {result["valueRanges"][0]["values"][0][0]}']],
        f'{sheet_name}!S4:U4':[[f'16 {month_names_french[int(mois)]} {result["valueRanges"][0]["values"][0][0]}']],
        f'{range_to_fill}': [merged_list],
        f"{sheet_name}!R13:X13": [[f"{i.Fonction}"]],
        f"{sheet_name}!C11:E11": [[f"{i.ID}"]],
        f"{sheet_name}!H11:L11": [[f"{i.Nom}"]],  # Update B2:N6 with "Value1"
        f"{sheet_name}!R11:V11": [[f"{i.Prenom}"]],  # Update B7:N7 with "Value2"
        f"{sheet_name}!AC1:AF1":[[f"{i.station} {datetime.now().date()}"]]
        # Add more ranges and values as needed
    }
    requests = [
        {
            'range':range_,
            'values':values,
        }
        for range_,values in ranges_and_values.items()
    ]

    service.spreadsheets().values().batchUpdate(
        spreadsheetId=dest_spreadsheet_id,
        body={"valueInputOption": "RAW", "data": requests},
        ).execute()
    return render(request,'mois.html',{'ID':i.station_id})

def update_employe(request,ID):
    employe=Employe.objects.get(ID=ID)
    if request.method == 'POST':
        form=EmployeForm(request.POST,instance=employe)
        if form.is_valid():
            form.save()
            return redirect(table_employe,employe.station.id)
    else:
        form=EmployeForm(instance=employe)
        return render(request,'update_employe.html',{'i':employe,'form':form})






def corriger_erreur(request):
    
    employees = Employe.objects.all()
    message=""
    if request.method == "POST":
        date = request.POST.get("date")
        employe_id = request.POST.get("selected")
        print(employe_id)
        code = Code_Employe.objects.filter(employe = employe_id , date=date)
        if code : 
            print(code[0].open_to_edit)
            code[0].open_to_edit = True
            code[0].save()
            message = str(code[0])
        else :
            message = "NONE"
    return render(request , 'err.html' , {'employees':employees , 'message':message})

def remboursement_formule(request,ID):
    employe=Employe.objects.get(pk=ID)
    if request.method=='POST':
        form=remboursementForm(request.POST,instance=employe)
        if form.is_valid():
            form.save()
            return redirect(table_employe,employe.station_id)
    else:
        form=remboursementForm(instance=employe)
        return render(request,'remboursement.html',{'employe':employe,'form':form})
    




def fiche_de_paie(validation_date , valid):
    month_names_french = {
        0: 'janvier',
        1: 'janvier',
        2: 'février',
        3: 'mars',
        4: 'avril',
        5: 'mai',
        6: 'juin',
        7: 'juillet',
        8: 'août',
        9: 'septembre',
        10: 'octobre',
        11: 'novembre',
        12: 'décembre',
    }
    end= {
    15: 'T',
    16: 'U',
    17: 'V',
    18: 'W',
    19: 'X',
    20: 'Y',
    21: 'Z',
    22: 'AA',
    23: 'AB',
    24: 'AC',
    25: 'AD',
    26: 'AE',
    27: 'AF',
    28: 'AG',
    29: 'AH',
    30: 'AI',
    31: 'AJ'
}
    print(validation_date)
    endcell = end[validation_date.day]
    endtmp = None
    if len(endcell) >= 2:
        endtmp = endcell 
        endcell = 'Z'
    
    
    yyyy = datetime.now().year
    mm = datetime.now().month 
    
    if calendar.monthrange(yyyy, mm)[1] == 31 :
            default_excel ="./excel/default31.xlsx"
            final_cell = 'J'
    elif calendar.monthrange(yyyy, mm)[1] == 30 :
            default_excel ="./excel/default30.xlsx"
            final_cell = 'I'
    elif calendar.monthrange(yyyy, mm)[1] == 28 :
            default_excel ="./excel/default28.xlsx"
            final_cell = 'G'
    elif calendar.monthrange(yyyy, mm)[1] == 29 :
            default_excel ="./excel/default29.xlsx"
            final_cell = 'H'
    
            
    
    dd = datetime.now().day
    employees = Employe.objects.all()
    if not valid:
        path = f'./excel/fiche_de_pointage{month_names_french[mm]}{yyyy}NonValide.xlsx'
    else :
        path = f'./excel/fiche_de_pointage{month_names_french[mm]}{yyyy}.xlsx'
    shutil.copy(default_excel,path)
    worbook = load_workbook(path)
    sheet = worbook.active 
    i = 20 
    sheet[f'F6'] = f'{date(validation_date.year , validation_date.month,1)}'
    month_periode = datetime.now().month - 1
    if month_periode == 0 :
        month_periode = 12
    tt =92
    t = 92
    for employe in employees:
        mission = {
        "5":0 , "4":0 , "3":0 , "2" : 0 , "1" : 0 , "MS":0 
        }   
        tmp_date = datetime.now().replace(day=1) 
        sheet[f'C{i}'] = f'{employe.Nom} {employe.Prenom}'
        sheet[f'B{i}'] = employe.ID
        sheet[f'E{i}'] = employe.Fonction
        if employe.remboursement_mois != 0 :
            sheet[f'D{i}'] = f'{employe.remboursement_mois}'
            employe.remboursement_total -= employe.remboursement_mois
            employe.remboursement_mois = 0 
            employe.save()
        for cell in range(ord('F'),ord(endcell)):
            code = Code_Employe.objects.filter(employe=employe,date=tmp_date)
            try:
                if str(code[0]) in mission:
                    sheet[f'{chr(cell)}{i}'] = "MI"
                    mission[str(code[0])] += 1
                else:
                    sheet[f'{chr(cell)}{i}'] = str(code[0])
            except:
                sheet[f'{chr(cell)}{i}'] = " "
            tmp_date = tmp_date + timedelta(days=1)
        if endtmp is None:
            if endcell != 'Z':
                for cell in range(ord(endcell)+1 , ord('Z') + 1): 
                    sheet[f'{chr(cell)}{i}'] = "T"
            for cell in range(ord('A'),ord(final_cell)+1):
                sheet[f'A{chr(cell)}{i}'] = "T"
        else:
            c = endtmp[1]
            for cell in range(ord('A'),ord(c)+1):
                try:
                    if str(code[0]) in mission:
                        sheet[f'{chr(cell)}{i}'] = "MI"
                        mission[str(code[0])] += 1
                    else:
                        sheet[f'{chr(cell)}{i}'] = str(code[0])
                except:
                    sheet[f'{chr(cell)}{i}'] = " "   
            for cell in range(ord(c)+1,ord(final_cell)+1):
                sheet[f'A{chr(cell)}{i}'] = "T"
        
        
        print(f'{month_periode}{yyyy}')
        try :
            month_stat = Month_stat.objects.get(employe=employe , period = f'{month_periode}{yyyy}')
            # print("have : ", month_stat)
            sheet[f'AL{i}'].value += f'+{month_stat.conge}' 
            sheet[f'AM{i}'].value += f'+{month_stat.absent}'
            sheet[f'AN{i}'].value += f'+{month_stat.abs_autorise}'
            sheet[f'AO{i}'].value += f'+{month_stat.rs}'
            sheet[f'AP{i}'].value += f'+{month_stat.eve_fam}'
            sheet[f'AQ{i}'].value += f'+{month_stat.mission}'
            sheet[f'AR{i}'].value += f'+{month_stat.mld}'
        except:
            pass
        
        
        for k,v in mission.items() :
            if v != 0 :
                print("Employe name : " , employe.Nom)
                sheet[f'F{tt}'].value = f'{employe.Nom} {employe.Prenom} : {v} j mission en code ({k})'
                tt += 1
        
        
        if month_stat.absent != 0:
            # print("Employe name : " , employe.Nom)
            sheet[f'AC{t}'].value = f'{employe.Nom} {employe.Prenom} : {month_stat.absent} j Absence  sur le mois {month_names_french[mm-1]}'
            t = t+1
        if month_stat.abs_autorise != 0:
            sheet[f'AC{t}'].value = f'{employe.Nom} {employe.Prenom} : {month_stat.abs_autorise} j Absence  Autorise sur le mois {month_names_french[mm-1]}'
            t = t+1
        if month_stat.conge != 0:
            sheet[f'AC{t}'].value = f'{employe.Nom} {employe.Prenom} : {month_stat.conge} j Conge {month_names_french[mm-1]}'
            t = t+1
        if month_stat.rs != 0:
            sheet[f'AC{t}'].value = f'{employe.Nom} {employe.Prenom} : {month_stat.rs} j Recuperation {month_names_french[mm-1]}'
            t = t+1
        if month_stat.mld != 0:
            sheet[f'AC{t}'].value = f'{employe.Nom} {employe.Prenom} : {month_stat.mld} j Maladie {month_names_french[mm-1]}'
            t = t+1
        
        i = i + 1
    if valid:
        sheet['F14'].value = f'validee le {validation_date} '
    worbook.save(f"./excel/fiche_de_pointage{month_names_french[mm]}{yyyy}.xlsx")
    
    
    return redirect('menu_view')

# def download_excel(request,name):
#     path = f"./excel/{name}.xlsx"
#     print("DOWNLOAD")
#     if os.path.exists(path):
#         response = FileResponse(open(path, 'rb'))
#         response['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(name)
#         return response
#     else:
#         # Handle the case where the file is not found
#         return HttpResponse("The file you are trying to download does not exist.", status=404)


def validation_fdp(request):
    month_names_french = {
        0: 'janvier',
        1: 'janvier',
        2: 'février',
        3: 'mars',
        4: 'avril',
        5: 'mai',
        6: 'juin',
        7: 'juillet',
        8: 'août',
        9: 'septembre',
        10: 'octobre',
        11: 'novembre',
        12: 'décembre',
    }
    if request.user.profile.da != 1:
        return redirect("menu_view")
    employe_rembourse = Employe.objects.filter(remboursement_total__gt=0)
    e = ValidDate.objects.filter(month=datetime.now().month).exists()
    if request.method == "POST":
        validation_date = datetime.strptime(request.POST.get("date"), '%Y-%m-%d')

        for emp in employe_rembourse:
            value = request.POST.get(f'{emp.ID}Rmois')
            emp.remboursement_mois = int(value) 
            emp.save()
        if 'button_without_validation' in request.POST:
            valid = False
        elif 'button_with_validation' in request.POST:
            valid = True
            validation_date = datetime.strptime(request.POST.get("date"), '%Y-%m-%d')
            valid_date = ValidDate.objects.create(
                                            date_of_validation=validation_date ,
                                            nom = "p" ,
                                            month=datetime.now().month
                                            ) 
            valid_date.save()
        fiche_de_paie(validation_date,valid)
        
    
      
    p = f'{month_names_french[datetime.now().month]}{datetime.now().year}'   
    print(p) 
    return render(request , 'validation_fdp.html', {"today":datetime.now().day, 'employees': employe_rembourse  , "exist":e , "p":p})



def download_excel(request, p):
    path = f"./excel/fiche_de_pointage{p}.xlsx"
    if os.path.exists(path):
        response = FileResponse(open(path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="fiche_de_pointage{p}.xlsx"'
        return response
    else:
        # Handle the case where the file is not found
        return HttpResponse("The file you are trying to download does not exist.", status=404)