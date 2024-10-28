DELETE FROM honeycomb_package_dependency;
DELETE FROM honeycomb_dependency;
DELETE FROM honeycomb;

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    1,
    "Query to get records from MySQL", 
    "This honeycomb retrieves all the records from a MySQL table",
    1,
    '{ "/src/mysql.py": "import mysql.connector\\n\\ndef get_record_from_mysql(host, username, password, db_name, table_name):\\n    \\"\\"\\"\\n    Returns all the rows from given @table_name\\n\\n    Args:\\n        host (str): db hostname.\\n        username (str): db login.\\n        password (str): db password.\\n        db_name (str): database name.\\n        table_name (str): the name of the table from @db_name from which the data will be retrieved.\\n\\n    Returns:\\n        list: a list of tuples representing all rows from @table_name\\n    \\"\\"\\"\\n    connect = mysql.connector.connect(\\n        host=host,\\n        user=username,\\n        password=password,\\n        database=db_name\\n    )\\n\\n    cursor = connect.cursor()\\n\\n    cursor.execute(\\"SELECT * FROM %s\\" % table_name)\\n\\n    return cursor.fetchall()\\n\\n" }'
);

-- mysql-connector-python
INSERT INTO honeycomb_package_dependency(honeycomb_id, package_dependency_id, package_version) VALUES (
    1,
    (SELECT id FROM package WHERE name="mysql-connector-python" LIMIT 1),
    '8.0.26'
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    2,
    "Login to Google Cloud Service using OAuth2", 
    "This honeycomb includes a function for logging into a Google Service using Client OAuth2, recommended for end users",
    1,
    '{ "/src/gcloud.py": "from googleapiclient.discovery import build\\nfrom google_auth_oauthlib.flow import InstalledAppFlow\\nfrom google.auth.transport.requests import Request\\nfrom google.oauth2.credentials import Credentials\\nfrom google.oauth2.service_account import Credentials as ServiceAccountCredentials\\nimport os\\n\\ndef gcloud_service_as_client(client_secret_file, api_name, api_version, scopes):\\n    \\"\\"\\"\\n    Function for logging into a Google Service using Client OAuth2, recommended for end users\\n\\n    args:\\n        client_secret_file(str): name of the client_secret_file example: ''secret.json''\\n        api_name(str): name of the api example: ''sheets''\\n        api_version(str): api_version example: ''v4''\\n        scopes(list): list of the scope urls. example: [''https://www.googleapis.com/auth/spreadsheets'']\\n\\n    returns:\\n        google service object\\n\\n    \\"\\"\\"\\n    creds = None\\n    # The file token.json stores the user''s access and refresh tokens, and is\\n    # created automatically when the authorization flow completes for the first\\n    # time.\\n    if os.path.exists(''token.json''):\\n        creds = Credentials.from_authorized_user_file(''token.json'', scopes)\\n\\n    # If there are no (valid) credentials available, let the user log in.\\n    if not creds or not creds.valid:\\n        if creds and creds.expired and creds.refresh_token:\\n            creds.refresh(Request())\\n        else:\\n            flow = InstalledAppFlow.from_client_secrets_file(\\n                client_secret_file, scopes)\\n            creds = flow.run_local_server(port=0)\\n        # Save the credentials for the next run\\n        with open(''token.json'', ''w'') as token:\\n            token.write(creds.to_json())\\n\\n    try:\\n        service = build(api_name, api_version, credentials=creds)\\n        return service\\n    except Exception as e:\\n        print(''Unable to connect.'')\\n        print(e)\\n        return None\\n\\n\\ndef gcloud_service_as_service_account(service_secret_file, api_name, api_version, scopes):\\n    \\"\\"\\"\\n    Function for logging into a Google Service using a service account file, recommended for bots and apps\\n\\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''secret.json''\\n        api_name(str): name of the api example: ''sheets''\\n        api_version(str): api_version example: ''v4''\\n        scopes(list): list of the scope urls. example: [''''https://www.googleapis.com/auth/spreadsheets'']\\n\\n    returns:\\n        google service object\\n\\n    \\"\\"\\"\\n    try:\\n        credentials = ServiceAccountCredentials.from_service_account_file(service_secret_file, scopes=scopes)\\n        service = build(api_name, api_version, credentials=credentials)\\n        return service\\n    except Exception as e:\\n        print(''Unable to connect.'')\\n        print(e)\\n        return None" }'
);

INSERT INTO honeycomb_package_dependency(honeycomb_id, package_dependency_id, package_version) VALUES (
    2,
    (SELECT id FROM package WHERE name="google-api-python-client" LIMIT 1),
    '2.19.0'
);

INSERT INTO honeycomb_package_dependency(honeycomb_id, package_dependency_id, package_version) VALUES (
    2,
    (SELECT id FROM package WHERE name="google-auth-oauthlib" LIMIT 1),
    '0.4.5'
);

INSERT INTO honeycomb_package_dependency(honeycomb_id, package_dependency_id, package_version) VALUES (
    2,
    (SELECT id FROM package WHERE name="google-auth-httplib2" LIMIT 1),
    '0.1.0'
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    3,
    "Login to Google Cloud Service using a service account", 
    "This honeycomb includes a function for logging into a Google Service using service account credentials, recommended for bots and apps",
    1,
    '{ "/src/gcloud.py": "from googleapiclient.discovery import build\\nfrom google_auth_oauthlib.flow import InstalledAppFlow\\nfrom google.auth.transport.requests import Request\\nfrom google.oauth2.credentials import Credentials\\nfrom google.oauth2.service_account import Credentials as ServiceAccountCredentials\\nimport os\\n\\ndef gcloud_service_as_client(client_secret_file, api_name, api_version, scopes):\\n    \\"\\"\\"\\n    Function for logging into a Google Service using Client OAuth2, recommended for end users\\n\\n    args:\\n        client_secret_file(str): name of the client_secret_file example: ''secret.json''\\n        api_name(str): name of the api example: ''sheets''\\n        api_version(str): api_version example: ''v4''\\n        scopes(list): list of the scope urls. example: [''https://www.googleapis.com/auth/spreadsheets'']\\n\\n    returns:\\n        google service object\\n\\n    \\"\\"\\"\\n    creds = None\\n    # The file token.json stores the user''s access and refresh tokens, and is\\n    # created automatically when the authorization flow completes for the first\\n    # time.\\n    if os.path.exists(''token.json''):\\n        creds = Credentials.from_authorized_user_file(''token.json'', scopes)\\n\\n    # If there are no (valid) credentials available, let the user log in.\\n    if not creds or not creds.valid:\\n        if creds and creds.expired and creds.refresh_token:\\n            creds.refresh(Request())\\n        else:\\n            flow = InstalledAppFlow.from_client_secrets_file(\\n                client_secret_file, scopes)\\n            creds = flow.run_local_server(port=0)\\n        # Save the credentials for the next run\\n        with open(''token.json'', ''w'') as token:\\n            token.write(creds.to_json())\\n\\n    try:\\n        service = build(api_name, api_version, credentials=creds)\\n        return service\\n    except Exception as e:\\n        print(''Unable to connect.'')\\n        print(e)\\n        return None\\n\\n\\ndef gcloud_service_as_service_account(service_secret_file, api_name, api_version, scopes):\\n    \\"\\"\\"\\n    Function for logging into a Google Service using a service account file, recommended for bots and apps\\n\\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''secret.json''\\n        api_name(str): name of the api example: ''sheets''\\n        api_version(str): api_version example: ''v4''\\n        scopes(list): list of the scope urls. example: [''''https://www.googleapis.com/auth/spreadsheets'']\\n\\n    returns:\\n        google service object\\n\\n    \\"\\"\\"\\n    try:\\n        credentials = ServiceAccountCredentials.from_service_account_file(service_secret_file, scopes=scopes)\\n        service = build(api_name, api_version, credentials=credentials)\\n        return service\\n    except Exception as e:\\n        print(''Unable to connect.'')\\n        print(e)\\n        return None" }'
);

INSERT INTO honeycomb_package_dependency(honeycomb_id, package_dependency_id, package_version) VALUES (
    3,
    (SELECT id FROM package WHERE name="google-api-python-client" LIMIT 1),
    '2.19.0'
);

INSERT INTO honeycomb_package_dependency(honeycomb_id, package_dependency_id, package_version) VALUES (
    3,
    (SELECT id FROM package WHERE name="google-auth-oauthlib" LIMIT 1),
    '0.4.5'
);

INSERT INTO honeycomb_package_dependency(honeycomb_id, package_dependency_id, package_version) VALUES (
    3,
    (SELECT id FROM package WHERE name="google-auth-httplib2" LIMIT 1),
    '0.1.0'
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    4,
    "Connect to the Google sheets service", 
    "This honeycomb includes a function for connecting to Google Sheets API",
    1,
    '{ "/src/gsheet.py": "import gcloud\\n\\ndef get_sheets_service(service_secret_file, scopes):\\n    \\"\\"\\"\\n    Function for connecting to Google Sheets API\\n\\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''client_secrets.json''\\n        scopes(list): List of scope urls. example: [''https://www.googleapis.com/auth/spreadsheets'']\\n\\n    returns:\\n        service object\\n\\n    \\"\\"\\"\\n    return gcloud.gcloud_service_as_service_account(service_secret_file, ''sheets'', ''v4'', scopes)\\n" }'
);

INSERT INTO honeycomb_dependency(honeycomb_id, honeycomb_dependency_id) VALUES (
    4,
    3
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    5,
    "Create a Google sheets spreadsheet",
    "This honeycomb includes a function for creating a Google spreadsheet",
    1,
    '{ "/src/gsheet.py": "import gcloud\\n\\ndef create_spreadsheet(service_secret_file, title):\\n    \\"\\"\\"\\n    Function to create a spreadsheet\\n\\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''client_secrets.json''\\n        title(str): Title of the spreadsheet.\\n\\n    returns:\\n        spreadhseet id\\n\\n    \\"\\"\\"\\n    service = get_sheets_service(service_secret_file,[''https://www.googleapis.com/auth/spreadsheets''] )\\n    spreadsheet = {\\n        ''properties'': {\\n            ''title'': title\\n        }\\n    }\\n    spreadsheet = service.spreadsheets().create(body=spreadsheet,\\n                                                fields=''spreadsheetId'').execute()\\n    print(''Spreadsheet ID: {0}''.format(spreadsheet.get(''spreadsheetId'')))\\n    return spreadsheet.get(''spreadsheetId'')\\n" }'
);

INSERT INTO honeycomb_dependency(honeycomb_id, honeycomb_dependency_id) VALUES (
    5,
    3
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    6,
    "Get values from Google sheet",
    "This honeycomb includes a function that retrieves cell values for a Google sheet",
    1,
    '{ "/src/gsheet.py": "import gcloud\\n\\ndef get_values(service_secret_file, spreadsheet_id, range_name):\\n    \\"\\"\\"\\n    Funtion to get the cell values of a spreadsheet.\\n\\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''client_secrets.json''\\n        spreadsheet_id(str):  Id of the spreadsheet\\n        range_name(str): name of the range example ''A1''.\\n            The A1 notation or R1C1 notation of the range to retrieve values from.\\n\\n    returns:\\n        Dictionary containing values, majorDimension and the range\\n    \\"\\"\\"\\n\\n    service = gcloud.gcloud_service_as_service_account(service_secret_file,''sheets'', ''v4'', [''https://www.googleapis.com/auth/spreadsheets.readonly''] )\\n    result = service.spreadsheets().values().get(\\n        spreadsheetId=spreadsheet_id, range=range_name).execute()\\n    rows = result.get(''values'', [])\\n    print(''{0} rows retrieved.''.format(len(rows)))\\n    return result\\n" }'
);

INSERT INTO honeycomb_dependency(honeycomb_id, honeycomb_dependency_id) VALUES (
    6,
    3
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    7,
    "Google sheet batch update",
    "This honeycomb includes a function to performs updates to a spreadsheet. For example, you can use this method to update cells, rename worksheets, update conditional formatting rules, add charts, create filter views etc.",
    1,
    '{ "/src/gsheet.py": "import gcloud\\n\\ndef batch_update(service_secret_file, spreadsheet_id):\\n    \\"\\"\\"\\n    Function to performs updates to a spreadsheet. \\n    For example you can use this method to update cells, rename worksheets, update conditional formatting rules, add charts, create filter views etc.\\n    \\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''client_secrets.json''\\n        spreadsheet_id(str):  Id of the spreadsheet\\n        title(str): new title of the spreadsheet\\n        find(str): finds all cell values containing the text. Example \\n                a cell containing ''abcd'' will be found when find is ''abc'' or ''bcd''\\n        replacement(str): replacement string\\n    placeholders:\\n        __batch_update_requests__(Request[]): list of requests to perform [https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request#Request]\\n                                            Examples\\n                                            UPDATE SPREADSHEET TITLE\\n                                            {\\n                                                ''updateSpreadsheetProperties'': { \\n                                                    ''properties'': {\\n                                                        ''title'': title \\n                                                    },\\n                                                    ''fields'': ''title''\\n                                                }\\n                                            }\\n                                            \\n                                            FIND AND REPLACE TEXT REQUEST\\n                                            {\\n                                                ''findReplace'': {\\n                                                    ''find'': find,\\n                                                    ''replacement'': replacement,\\n                                                    ''allSheets'': True\\n                                                }\\n                                            }\\n    \\n    returns:\\n        Dictionary containing info about the updates applied. The responses align to the list of requests as detailed here [https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/response#UpdateDeveloperMetadataResponse]\\n\\n    \\"\\"\\"\\n    service = gcloud.gcloud_service_as_service_account(service_secret_file,''sheets'', ''v4'', [''https://www.googleapis.com/auth/spreadsheets''] )\\n    requests = []\\n    requests.append(__batch_update_requests__)\\n    body = {\\n        ''requests'': requests\\n    }\\n    response = service.spreadsheets().batchUpdate(\\n        spreadsheetId=spreadsheet_id,\\n        body=body).execute()\\n    return response\\n" }'
);

INSERT INTO honeycomb_dependency(honeycomb_id, honeycomb_dependency_id) VALUES (
    7,
    3
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    8,
    "Google sheet batch get values",
    "This honeycomb includes a function to get values of cells in a range",
    1,
    '{ "/src/gsheet.py": "import gcloud\\n\\ndef batch_get_values(service_secret_file, spreadsheet_id, range_names):\\n    \\"\\"\\"\\n    Function to get cell values given a range\\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''client_secrets.json''\\n        spreadsheet_id(str):  Id of the spreadsheet\\n        range_names(list): list of ranges example [''A1:A3'',''D1:D5'']\\n\\n    returns:\\n        Dictionary containing values and other info.\\n\\n\\n    \\"\\"\\"\\n    service = gcloud.gcloud_service_as_service_account(service_secret_file,''sheets'', ''v4'', [''https://www.googleapis.com/auth/spreadsheets.readonly''] )\\n    result = service.spreadsheets().values().batchGet(\\n        spreadsheetId=spreadsheet_id, ranges=range_names).execute()\\n    ranges = result.get(''valueRanges'', [])\\n    print(''{0} ranges retrieved.''.format(len(ranges)))\\n    return result\\n" }'
);

INSERT INTO honeycomb_dependency(honeycomb_id, honeycomb_dependency_id) VALUES (
    8,
    3
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    9,
    "Google sheet update values",
    "This honeycomb includes a function to update a cell value given a range",
    1,
    '{ "/src/gsheet.py": "import gcloud\\n\\ndef update_values(service_secret_file, spreadsheet_id, range_name, value_input_option, values):\\n    \\"\\"\\"\\n    Function to update cell values given a range\\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''client_secrets.json''\\n        spreadsheet_id(str):  Id of the spreadsheet\\n        range_name(str): range example ''A1:B2''\\n        value_input_option(str): Determines how input data should be interpreted. \\n            Example\\n            INPUT_VALUE_OPTION_UNSPECIFIED  Default input value. This value must not be used.\\n            RAW   The values the user has entered will not be parsed and will be stored as-is.\\n            USER_ENTERED    The values will be parsed as if the user typed them into the UI. \\n                            Numbers will stay as numbers, but strings may be converted to numbers, dates, etc. \\n                            following the same rules that are applied when entering text into a cell via the Google Sheets UI.\\n        values(list): two dimentional list of updated values to apply. example [[''A'',''B''],[''abc'',''Deqqeqw'']]\\n    returns:\\n        Dictionary containing info about the updates applied.\\n\\n\\n    \\"\\"\\"\\n            \\n    service = gcloud.gcloud_service_as_service_account(service_secret_file,''sheets'', ''v4'', [''https://www.googleapis.com/auth/spreadsheets''] )\\n    body = {\\n        ''values'': values\\n    }\\n    result = service.spreadsheets().values().update(\\n        spreadsheetId=spreadsheet_id, range=range_name,\\n        valueInputOption=value_input_option, body=body).execute()\\n    print(''{0} cells updated.''.format(result.get(''updatedCells'')))\\n    return result\\n" }'
);

INSERT INTO honeycomb_dependency(honeycomb_id, honeycomb_dependency_id) VALUES (
    9,
    3
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    10,
    "Google sheet batch update values",
    "This honeycomb includes a function to update values in a spreadsheet in batch",
    1,
    '{ "/src/gsheet.py": "import gcloud\\n\\ndef batch_update_values(service_secret_file, spreadsheet_id, range_name,\\n                        value_input_option, values):\\n    \\"\\"\\"\\n    Function to update values in a spreadsheet in batch\\n    \\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''client_secrets.json''\\n        spreadsheet_id(str):  Id of the spreadsheet\\n        range_name(str): range example ''A1:B2''\\n        value_input_option(str): Determines how input data should be interpreted. \\n            Example\\n            INPUT_VALUE_OPTION_UNSPECIFIED  Default input value. This value must not be used.\\n            RAW   The values the user has entered will not be parsed and will be stored as is.\\n            USER_ENTERED    The values will be parsed as if the user typed them into the UI. \\n                            Numbers will stay as numbers, but strings may be converted to numbers, dates, etc. \\n                            following the same rules that are applied when entering text into a cell via the Google Sheets UI.\\n          values(list): list of updated values to apply. example [''A'',''B'',''abc'',''Deqqeqw'']\\n    \\n    returns:\\n        Dictionary containing info about the updates applied.\\n    \\"\\"\\"\\n    service = gcloud.gcloud_service_as_service_account(service_secret_file,''sheets'', ''v4'', [''https://www.googleapis.com/auth/spreadsheets''] )\\n    data = [\\n        {\\n            ''range'': range_name,\\n            ''values'': values\\n        },\\n        # Additional ranges to update ...\\n    ]\\n    body = {\\n        ''valueInputOption'': value_input_option,\\n        ''data'': data\\n    }\\n    result = service.spreadsheets().values().batchUpdate(\\n        spreadsheetId=spreadsheet_id, body=body).execute()\\n    print(''{0} cells updated.''.format(result.get(''totalUpdatedCells'')))\\n    return result\\n" }'
);

INSERT INTO honeycomb_dependency(honeycomb_id, honeycomb_dependency_id) VALUES (
    10,
    3
);

-- INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
--     NOW(),
--     11,
--     "Google sheet append values",
--     "This honeycomb includes a function to append values to a range of cells",
--     1,
--     '{ "/src/gsheet.py": "import gcloud\\n\\ndef append_values(service_secret_file, spreadsheet_id, range_name, value_input_option,\\n                    values):  \\n    \\"\\"\\"\\n    Function to append values to a range of cells\\n    \\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''client_secrets.json''\\n        spreadsheet_id(str):  Id of the spreadsheet\\n        range_name(str): range example ''A1:B2''\\n        value_input_option(str): Determines how input data should be interpreted. \\n            Example\\n            INPUT_VALUE_OPTION_UNSPECIFIED  Default input value. This value must not be used.\\n            RAW   The values the user has entered will not be parsed and will be stored as is.\\n            USER_ENTERED    The values will be parsed as if the user typed them into the UI. \\n                            Numbers will stay as numbers, but strings may be converted to numbers, dates, etc. \\n                            following the same rules that are applied when entering text into a cell via the Google Sheets UI.\\n\\n        values(list): list of updated values to apply. example [''A'',''B'',''abc'',''Deqqeqw'']\\n    \\n    returns:\\n        Dictionary containing info about the updates applied.\\n    \\"\\"\\"  \\n    service = gcloud.gcloud_service_as_service_account(service_secret_file,''sheets'', ''v4'', [''https://www.googleapis.com/auth/spreadsheets''] )\\n    body = {\\n        ''values'': values\\n    }\\n    result = service.spreadsheets().values().append(\\n        spreadsheetId=spreadsheet_id, range=range_name,\\n        valueInputOption=value_input_option, body=body).execute()\\n    print(''{0} cells appended.''.format(result \\\n                                            .get(''updates'') \\\n                                            .get(''updatedCells'')))\\n    return result\\n" }'
-- );

-- INSERT INTO honeycomb_dependency(honeycomb_id, honeycomb_dependency_id) VALUES (
--     11,
--     3
-- );

-- INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
--     NOW(),
--     12,
--     "Create pivot table in Google spreadsheet",
--     "This honeycomb includes a function that lets you create a new pivot table within a spreadsheet",
--     1,
--     '{ "/src/gsheet.py": "import gcloud\\n\\ndef pivot_tables(service_secret_file, spreadsheet_id):\\n    \\"\\"\\"\\n    Function that lets you create a new pivot table within a spreadsheet. \\n    The Pivot table definition is described here: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/pivot-tables#PivotTable\\n\\n    args:\\n        service_secret_file(str): name of the service_secret_file example: ''client_secrets.json''\\n        spreadsheet_id(str):  Id of the spreadsheet\\n    \\n    placeholders:\\n        __pivot_source_sheet_id__(int): Id of the worksheet containing the pivot data (value of parameter ''gid'' in sheet url)\\n        __pivot_source_start_row_index__(int): The start row index of the source data\\n        __pivot_source_start_column_index__(int): The start column index of the source data\\n        __pivot_source_end_row_index__(int): The end row index of the source data\\n        __pivot_source_end_column_index__(int): The end column index of the source data\\n        __pivot_group_rows_json__(PivotGroup): Definition of a single row [PivotGroup](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/pivot-tables#PivotGroup)\\n                                                Example \\n                                                [\\n                                                    {\\n                                                        ''sourceColumnOffset'': 1,\\n                                                        ''showTotals'': True,\\n                                                        ''sortOrder'': ''ASCENDING'',\\n\\n                                                    }\\n                                                ]\\n        __pivot_group_columns_json__(PivotGroup): Definition of a single column [PivotGroup](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/pivot-tables#PivotGroup)\\n                                                Example \\n                                                [\\n                                                    {\\n                                                        ''sourceColumnOffset'': 4,\\n                                                        ''sortOrder'': ''DESCENDING'',\\n                                                        ''showTotals'': True,\\n\\n                                                    }\\n                                                ]       \\n        __pivot_values_calculation__(PivotValue): The definition on how a value in the pivot should be calculated [PivotValue](https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/pivot-tables#PivotValue)\\n                                                Example\\n                                                [\\n                                                    {\\n                                                        ''summarizeFunction'': ''COUNTA'',\\n                                                        ''sourceColumnOffset'': 4\\n                                                    }\\n                                                ]\\n        __pivot_value_layout__(\\"HORIZONTAL\\"|\\"VERTICAL\\"): The layout of the pivot table\\n    \\n    returns:\\n        dictionary containing info about the updates applied\\n    \\"\\"\\"\\n\\n    service = gcloud.gcloud_service_as_service_account(service_secret_file,''sheets'', ''v4'', [''https://www.googleapis.com/auth/spreadsheets''] )\\n    # Create a new sheet for the pivot table.\\n    body = {\\n        ''requests'': [{\\n            ''addSheet'': {}\\n        }]\\n    }\\n    batch_update_response = service.spreadsheets() \\\n        .batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()\\n    target_sheet_id = batch_update_response.get(''replies'')[0] \\\n        .get(''addSheet'').get(''properties'').get(''sheetId'')\\n    requests = []\\n    requests.append({\\n        ''updateCells'': {\\n            ''rows'': {\\n                ''values'': [\\n                    {\\n                        ''pivotTable'': {\\n                            ''source'': {\\n                                ''sheetId'': __pivot_source_sheet_id__,\\n                                ''startRowIndex'': __pivot_source_start_row_index__,\\n                                ''startColumnIndex'': __pivot_source_start_column_index__,\\n                                ''endRowIndex'': __pivot_source_end_row_index__,\\n                                ''endColumnIndex'': __pivot_source_end_column_index__\\n                            },\\n                            ''rows'': __pivot_group_rows_json__,\\n                            ''columns'': __pivot_group_columns_json__,\\n                            ''values'': __pivot_values_calculation__,\\n                            ''valueLayout'': __pivot_value_layout__\\n                        }\\n                    }\\n                ]\\n            },\\n            ''start'': {\\n                ''sheetId'': target_sheet_id,\\n                ''rowIndex'': 0,\\n                ''columnIndex'': 0\\n            },\\n            ''fields'': ''pivotTable''\\n        }\\n    })\\n    body = {\\n        ''requests'': requests\\n    }\\n    response = service.spreadsheets() \\\n        .batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()\\n    return response\\n" }'
-- );

-- INSERT INTO honeycomb_dependency(honeycomb_id, honeycomb_dependency_id) VALUES (
--     12,
--     3
-- );

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    13,
    "Send slack message", 
    "This honeycomb supports sending messages on arbitrary Slack channels",
    1,
    '{ "/src/slack.py": "import requests\\nimport json\\n\\ndef send_slack_message(channel_id, message):\\n    \\"\\"\\"\\n    Funtion for sending a slack message using the [Slack Web API](https://api.slack.com/web).\\n    __SLACK_BOT_TOKEN__ is the OAuth token created for your [Slack app](https://api.slack.com/apps/). \\n    Slack app should have sufficient scopes for sending a message (chat:write) distributed to your workspace and your bot should be invited to the channel (/invite @BOT_NAME) \\n    See instructions for quickstarting an app [here](https://api.slack.com/authentication/basics)\\n\\n    args:\\n        channel_id(str): id of the slack channel to send the message to\\n        message(str): message to send via slack\\n    placeholders:\\n        __SLACK_BOT_TOKEN__(str): your slack app authentication token\\n\\n    returns:\\n        JSON response as specified [here](https://api.slack.com/methods/chat.postMessage#responses)\\n\\n    \\"\\"\\"\\n    \\n    headers ={''Content-type'': ''application/json; charset=utf-8'',''Authorization'': f''Bearer {__SLACK_BOT_TOKEN__}''}\\n    params = {''text'':message,''channel'':channel_id}\\n    \\n    try:\\n        res = requests.post(''https://slack.com/api/chat.postMessage'',headers=headers,data=json.dumps(params))\\n        return res.content\\n        \\n    except Exception as e:\\n        print(f\\"Error: {e}\\")\\n" }'
);

INSERT INTO honeycomb_package_dependency(honeycomb_id, package_dependency_id, package_version) VALUES (
    13,
    (SELECT id FROM package WHERE name="requests" LIMIT 1),
    '2.26.0'
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    14,
    "Login to a webapp with Selenium", 
    "This honeycomb lets you connect to a webapp using Selenium",
    1,
    '{ "/src/selenium_login.py": "from selenium import webdriver\\nfrom selenium.webdriver.support.ui import WebDriverWait\\n\\n\\ndef login_selenium(login_url, username, password):\\n    \\"\\"\\"\\n    Function for signing up to any webpage using Selenium\\n\\n    args:\\n        login_url(str): name of the service_secret_file example: ''client_secrets.json''\\n        username(str): username or email of account\\n        password(str): password of account\\n    \\n    placeholders :\\n        __USERNAME_INPUT_CSS_SELECTOR__(str): css selector for username element, example:\\"input[type=''email'']\\"\\n        __PASSWORD_INPUT_CSS_SELECTOR__ (str): css selector for password element, example:\\"input[type=''password'']\\"\\n        __SUBMIT_BUTTON_CSS_SELECTOR__ (str): css selector for submit button, example:\\"input[type=''submit'']\\"\\n        __FAILED_LOGIN_MSG__ (str): message that is displayed after login if failed, example: ''Bad email or password.''\\n        __FAILED_LOGIN_CSS_SELECTOR__(str): css selector for dom element that shows an error message if login failed, example:\\".form__field-error\\"\\n\\n    returns:\\n        bool\\n\\n    \\"\\"\\"\\n\\n    options = webdriver.ChromeOptions()\\n    options.add_argument(''--headless'')\\n    options.add_argument(''--disable-gpu'')\\n    options.add_argument(''--no-sandbox'')\\n    driver = webdriver.Chrome(options=options)\\n    driver.get(login_url)\\n\\n    username_input = driver.find_element_by_css_selector(__USERNAME_INPUT_CSS_SELECTOR__)\\n    username_input.clear()\\n    username_input.send_keys(username)\\n    \\n    password_input = driver.find_element_by_css_selector(__PASSWORD_INPUT_CSS_SELECTOR__)\\n    password_input.clear()\\n    password_input.send_keys(password)\\n    \\n    login_button = driver.find_element_by_css_selector(__SUBMIT_BUTTON_CSS_SELECTOR__)\\n    login_button.click() \\n    \\n    WebDriverWait(driver=driver, timeout=10).until(\\n        lambda x: x.execute_script(\\"return document.readyState == ''complete''\\")\\n    )\\n\\n    error_message = __FAILED_LOGIN_MSG__\\n    errors = driver.find_elements_by_css_selector(__FAILED_LOGIN_CSS_SELECTOR__)\\n            \\n    driver.quit()\\n    if any(error_message in e.text for e in errors):\\n        return False\\n    else:\\n        return True\\n" }'
);

INSERT INTO honeycomb_package_dependency(honeycomb_id, package_dependency_id, package_version) VALUES (
    14,
    (SELECT id FROM package WHERE name="selenium" LIMIT 1),
    '3.141.0'
);

INSERT INTO honeycomb(created, id, name, description, version, code) VALUES (
    NOW(),
    15,
    "Docker files for Django project",
    "This honeycomb contains Docker configurations (Dockerfile, docker-compose.yml and proxy configuration) for running a Django project.\nAfter adding it to your project you should change the APP_NAME value in the `docker-compose.yml` file.\n\nTo run the project using Docker run: `docker-compose up --build`.",
    1,
    '{ "/Dockerfile": "FROM python:3.9-slim\\n\\n# create non-root user for running the app\\nRUN addgroup --gid 10001 nonroot && \\\\\\n    adduser --uid 10000 --ingroup nonroot --home /home/nonroot --disabled-password --gecos \\"\\" nonroot\\n\\n# add tini and use it as the entrypoint\\nADD https://github.com/krallin/tini/releases/download/v0.19.0/tini /tini\\nRUN chmod +x /tini\\nENTRYPOINT [\\"/tini\\", \\"--\\"]\\n\\n# install library dependencies if any are needed\\n# RUN apt-get update && \\\\\\n#     apt-get install -y --no-install-recommends postgresql-client && \\\\\\n#     rm -rf /var/lib/apt/lists/*\\n\\nWORKDIR /usr/src/app\\n\\n# install app python requirements and gunicorn\\nCOPY requirements.txt ./\\nRUN pip install --no-cache-dir -r requirements.txt && \\\\\\n    pip install --no-cache-dir gunicorn==20.1.0\\n\\n# copy the source directory\\nCOPY . .\\n\\nEXPOSE 8080\\n\\nUSER nonroot\\n\\n# the command runs gunicorn, binds it to port 8080 with 3 workers, info log level\\n# and stdout as log output. replace APP_NAME with your Django application name so\\n# that gunicorn can find your wsgi file\\nCMD [ \\\\\\n    \\"gunicorn\\", \\\\\\n    \\"--bind\\", \\\\\\n    \\"0.0.0.0:8080\\", \\\\\\n    \\"--workers=3\\", \\\\\\n    \\"--log-level=info\\", \\\\\\n    \\"--access-logfile\\", \\\\\\n    \\"-\\", \\\\\\n    \\"APP_NAME.wsgi\\" \\\\\\n]\\n", "/docker-compose.yml": "version: \\"3\\"\\n\\nservices:\\n  django_service:\\n    build: .\\n\\n  proxy:\\n    image: nginx:1.21-alpine\\n    depends_on:\\n      - django_service\\n    ports:\\n      - 8080:8080\\n    volumes:\\n      - ./ops/proxy/default.conf:/etc/nginx/conf.d/default.conf\\n      - ./static:/usr/share/nginx/django_static\\n", "/ops/proxy/default.conf": "server {\\n    listen 8080;\\n\\n    # don\'t send version banner with requests\\n    server_tokens off;\\n\\n    location /static {\\n        # serve django static files\\n        alias /usr/share/nginx/django_static/;\\n    }\\n\\n    location / {\\n        # proxy non-static requests to the django service\\n        proxy_pass http://django_service:8080;\\n\\n        proxy_set_header Host $http_host;\\n        proxy_set_header X-Real-IP $remote_addr;\\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\\n        proxy_set_header X-Forwarded-Proto $scheme;\\n    }\\n}\\n" }'
);
