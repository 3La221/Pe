#the first part is a script that takes information from a sheet and create instances for each employe in that sheet If you want to use it you should modify model so that it won't check for pk
'''credentials = service_account.Credentials.from_service_account_file(
        './petromagpointage-be9f913f9b9e.json',
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
        )
        # Specify the ID of your Google Sheet
    spreadsheet_id = '1JfI_phAUr1L5069xB-Wv9ctXlaJgtFdurxBu0TsQ1SA'
    service = build('sheets', 'v4', credentials=credentials)
    max=14
    if ID == 1:
        max+=13
        sheet='R770-01-(13)'
    elif ID == 2:
        max+=9
        sheet='R770-02-(9)'
    elif ID == 3:
        max+=19
        sheet='R770-03-(19)'
    elif ID == 4:
        max+=14
        sheet='R770-04-(14)'
    elif ID== 5:
        max+=11
        sheet='R770-05-(11)'
    ranges=[]
    column=['C','D','E','F']
    for row in range(14,max): #this loop will prepare the range of the information to be fetched (used in .get)
        range_list = [f'{sheet}!{column[0]}{row}',f'{sheet}!{column[1]}{row}',f'{sheet}!{column[2]}{row}',f'{sheet}!{column[3]}{row}']
        ranges.append(range_list)
# Fetch values from each range
    all_values = []
    for range_ in ranges:
        print(range_)
        result = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, ranges=range_).execute()
        for value_range in result['valueRanges']:
            values = value_range.get('values', [])
            all_values.append(values)
        employe=Employe()
        i=0
        for values_list in all_values:
            for row in values_list:
                for value in row:
                    if i==0:
                        employe.ID=int(value)
                    elif i==1:
                        employe.Nom=value
                    elif i==2:
                        employe.Prenom=value
                    elif i==3 :
                        employe.Fonction=value
                    i+=1
        employe.station_id=ID
        employe.save()
        all_values=[]
        print('next\n')'''