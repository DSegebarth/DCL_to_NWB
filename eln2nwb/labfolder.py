import requests
import json
import mimetypes
import urllib.request

# default parameters
base_URL = 'https://eln.labfolder.com'
use_verify = True
verbose = False
proxies = {}

def authenticate_v1(labfolder_username, labfolder_password, base_URL=base_URL, verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    Note: API v1 is deprecated.
    Function to authenticate against labfolder API v1. It is recommended to use v2 wherever possible.
    :param labfolder_username: string, e-mail address which with user is registered
    :param labfolder_password: string, password for user
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    use 'False' only for self-signed certificates.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return:    auth_token, string: labfolder API v1 authentication token
                message, string:
    '''
    API_base_URL = base_URL + '/api/v1'
    data = [
        ('email', labfolder_username),
        ('password', labfolder_password),
    ]
    r = requests.post(API_base_URL + '/login', data=data, verify=use_verify, proxies=proxies)
    response = r.json()
    status = response['status']
    if verbose == True:
        print(response)
    if status == 1:
        message = "Your user name or password is incorrect"
        labfolder_auth_token = ''
    elif status == 0:
        labfolder_auth_token = response['dataObj']
        message = 'Authentication successful'
    else:
        rmessage = "Authentication failed. Please check your connection"
    return labfolder_auth_token, message


def insert_text_v1(labfolder_auth_token, text_string, entry_id, base_URL=base_URL, verbose=verbose, verify=use_verify, proxies=proxies):
    '''
    Note: API v1 is deprecated.
    Function to add a text element to a labfolder entry.
    :param labfolder_auth_token: string, labfolder API v1 authentication token
    :param text_string: text string to be added to labfolder entry. HTML formatting accepted.
    :param entry_id: Entry ID of labfolder entry to which text should be added
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, response of labfolder API
    '''
    API_base_URL = base_URL + '/api/v1'
    data = {'textContent': text_string}
    headers = {'AuthToken': labfolder_auth_token}
    r = requests.post(API_base_URL + '/entries/' + str(entry_id) + '/text', headers=headers, data=data, verify=use_verify, proxies=proxies)
    response = r.json()
    if verbose == True:
        print(response)
    return response


def insert_file_v1(v1_auth_token, entry_id, filename, base_URL=base_URL, verify=use_verify, proxies=proxies):
    '''
    Note: API v1 is deprecated.
    Function to add a file to a labfolder entry using API v1. It is recommended to use API v2 wherever possible.
    :param v1_auth_token: string, labfolder API v1 authentication token
    :param entry_id: Entry ID of labfolder entry to which file should be added
    :param filename: Name of file with full path which should be added to labfolder entry
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, response of labfolder API
    '''
    API_base_URL = base_URL + '/api/v1'

    headers = {
        'AuthToken': v1_auth_token,
    }

    files = {
        'file': (filename, open(filename, 'rb')),
    }

    response = requests.post(API_base_URL + '/entries/' + str(entry_id) + '/file', headers=headers, files=files, verify=use_verify, proxies=proxies)

    return response


def authenticate(labfolder_username, labfolder_password, base_URL=base_URL,
                 verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    Authenticate against labfolder API v2.
    See https://eln.labfolder.com/api/v2/docs/development.html#access-endpoints-post
    :param labfolder_username: string, e-mail address which with user is registered
    :param labfolder_password: string, password for user
    :param API_base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: string authentification Token, string date of token expiry, string success message
    '''
    API_base_URL = base_URL + '/api/v2'

    headers = {"Content-Type": "application/json"
               # "User - Agent": "PythonSDK; "+labfolder_username
               }
    data = {
        "user": labfolder_username,
        "password": labfolder_password
    }
    r = requests.post(API_base_URL + '/auth/login', headers=headers, data=json.dumps(data), verify=use_verify, proxies=proxies)
    success = False
    if verbose == True:
        print(r.json)
    if r.status_code == 200:
        response = r.json()
        labfolder_auth_token = response['token']
        expires = response['expires']
        message = 'Authentication successful'
        success = True
    elif r.status_code == 401:
        message = "Your user name or password is incorrect"
        labfolder_auth_token = ''
        expires = ''
    elif r.status_code == 404:
        message = "The server could not be reached (Error code: 404)"
        expires = ''
        labfolder_auth_token = ''
    else:
        if verbose is True:
            print(r.status_code)
        expires = ''
        labfolder_auth_token = ''
        message = "Server error code:" + str(r.status_code)

    return labfolder_auth_token, expires, message, success

def logout(labfolder_auth_token, base_URL=base_URL, use_verify=use_verify, proxies=proxies):
    '''
    Invalidate all API access tokens.
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: int, response http status
    '''
    API_base_URL = base_URL + '/api/v2'

    headers = {#"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    r = requests.post(API_base_URL + '/auth/logout', headers=headers,
                     verify=use_verify, proxies=proxies)
    return r.status_code

def get_all_projects(labfolder_auth_token, group_id='',owner_id='',only_root_level='',folder_id='',
                 project_ids=[],limit=20,offset=0,
                 verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    Returns a list of projects the user has access to. See also https://eln.labfolder.com/api/v2/docs/development.html#projects-projects-resource-get
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param group_id: int or string (optional), Only return the projects that belong to the specified group
    :param owner_id: int or string (optional), Only return the projects that are owned by the given user
    :param only_root_level: boolean (optional), Default: false. Only return root (top) level projects - I.e. projects that do not reside within a folder.
    :param folder_id: int or string (optional), Only return projects that reside within the specified folder.
    :param project_ids: list of strings (optional), A comma separated list of project ids specifying the projects to be returned.
    :param verbose: boolean (optional), Default: False, whether output should be printed.
    :param use_verify: boolean (optional), Default: True, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: server response as json, see also:https://eln.labfolder.com/api/v2/docs/development.html#projects-projects-resource-get
    '''
    API_base_URL = base_URL + '/api/v2'

    headers = {#"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    params = {}

    if group_id != '':
        params['group_id']=str(group_id)
    if owner_id!='':
        params['owner_id']=str(owner_id)
    if only_root_level!='':
        params['only_root_level'] = only_root_level
    if folder_id!='':
        params['folder_id'] = str(folder_id)
    if project_ids!=[]:
        params['folder_id'] = project_ids
    params['limit'] = int(limit)
    params['offset'] = int(offset)

    r = requests.get(API_base_URL+'/projects', headers=headers, params=params, verify=use_verify, proxies=proxies)
    response_json = r.json()
    response_headers = r.headers
    total_projects = int(response_headers['X-Total-Count'])
    limit = int(response_headers['X-Limit'])
    if total_projects > (limit+1)*offset:
        offset+=1
        new_response_json = get_all_projects(labfolder_auth_token, group_id=group_id,owner_id=owner_id,only_root_level=only_root_level,folder_id=folder_id,
                 project_ids=project_ids,limit=limit,offset=offset,
                 verbose=verbose, use_verify=use_verify, proxies=proxies)
        for project in new_response_json:
            response_json.append(project)
    return response_json

def get_all_folders(labfolder_auth_token, group_id='',owner_id='',only_root_level='',content_type='',
                    parent_folder_id='',folder_ids='',limit=0,offset=20,
                    verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    Returns a list of folders the user has access to. See also: https://eln.labfolder.com/api/v2/docs/development.html#folders-folders-resource-get
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param group_id: int or string (optional), Only return the folders that belong to the specified group.
    :param owner_id: int or string (optional), Only return the folders that are owned by the given user.
    :param only_root_level: boolean (optional), Only return root (top) level folders - I.e. folders that do not reside within another folder.
    :param content_type: string (optional), Default: 'PROJECTS'. Choices: 'PROJECTS', 'TEMPLATES'. The desired type of folders to retrieve.
    :param parent_folder_id: int or string (optional), Only return folders that reside within the specified folder.
    :param folder_ids: list of strings (optional), A comma separated list of project ids specifying the projects to be returned.
    :param limit: int (optional), Maximum number of folders to return.
    :param offset: int (optional), Offset into result-set (useful for pagination).
    :param verbose: verbose: boolean (optional), Default: False, whether output should be printed.
    :param use_verify: boolean (optional), Default: True, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: server response as json, see also https://eln.labfolder.com/api/v2/docs/development.html#folders-folders-resource-get.
    '''
    API_base_URL = base_URL + '/api/v2'

    headers = {  # "Content-Type": "application/json",
        # "User-Agent": "PythonSDK",
        "Authorization": "Token " + labfolder_auth_token
    }

    params = {}
    if group_id != '':
        params['group_id']=str(group_id)
    if owner_id!='':
        params['owner_id']=str(owner_id)
    if only_root_level!='':
        params['only_root_level'] = only_root_level
    if content_type!='':
        params['content_type'] = content_type
    if parent_folder_id!='':
        params['parent_folder_id'] = str(parent_folder_id)
    if folder_ids!=[]:
        params['folder_ids'] = folder_ids
    params['limit'] = int(limit)
    params['offset'] = int(offset)
    r = requests.get(API_base_URL+'/folders', headers=headers, params=params, verify=use_verify, proxies=proxies)
    response_json = r.json()
    response_headers = r.headers
    total_projects = int(response_headers['X-Total-Count'])
    limit = int(response_headers['X-Limit'])
    if total_projects > (limit+1)*offset:
        offset+=1
        new_response_json = get_all_folders(labfolder_auth_token, group_id=group_id,owner_id=owner_id,
                                            only_root_level=only_root_level,
                                            content_type=content_type, parent_folder_id=parent_folder_id,folder_ids=folder_ids,
                                            limit=limit,offset=offset,
                                            verbose=verbose, use_verify=use_verify, proxies=proxies)
        for project in new_response_json:
            response_json.append(project)
    return response_json

def create_folder(labfolder_auth_token, title='New Project',content_type='',group_id='',parent_folder_id='',verbose=verbose, use_verify=use_verify, proxies=proxies):
    """
    Create a folder. A folder may either contain projects or templates, as well as children folders of the same type. A private folder is intended for your use only, while a group folder may be shared with the members of that group. See also: https://eln.labfolder.com/api/v2/docs/development.html#folders-folders-resource-post
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param title: string, the display name of the folder
    :param content_type: string (optional), indicate if the folder should hold Projects or Templates. Options: 'PROJECTS' or 'TEMPLATES', Default: 'PROJECTS'.
    :param group_id: int or string (optional), the id of the group to which the folder is associated.
    :param parent_folder_id: int or string (optional), the id of the folder in which the folder is stored
    :param verbose: verbose: boolean (optional), Default: False, whether output should be printed.
    :param use_verify: boolean (optional), Default: True, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: server response as json if successful, see also: https://eln.labfolder.com/api/v2/docs/development.html#folders-folders-resource-post,
             http error code otherwise
    """
    API_base_URL = base_URL + '/api/v2'

    headers = { "Content-Type": "application/json;charset=UTF-8",
                # "User-Agent": "PythonSDK",
                "Authorization": "Token " + labfolder_auth_token
    }

    params = {}
    params['title']=title
    if content_type!='':
        params['content_type'] = str(content_type)
    if group_id!='':
        params['group_id'] = str(group_id)
    if parent_folder_id!='':
        params['parent_folder_id'] = str(parent_folder_id)

    r=requests.post(API_base_URL+'/folders', headers=headers, params=params, verify=use_verify, proxies=proxies)

    if r.status_code==201:
        return r.json()
    else:
        return r.status_code

def display_folder_tree(folder_json):

    top_level_folders = []

    for folder in folder_json:
        if folder['parent_folder_id']=="":
            pass

def get_last_entry_by_title(labfolder_auth_token, title, base_URL=base_URL, verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    Retrieve entry with latest date of modification that where the parameter 'title' is a substring of the entry title
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param title: substring to be used in title filter of entry search
    :param API_base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: entry_id: string, ID of entry which matches search result. Empty string if no entry matches the search criteria or if there is a server error.
             entry: dict, json reprentation of entry.
             status_code: string, HTTP status code of server response.
    '''
    API_base_URL = base_URL + '/api/v2'

    version_dict = {}
    entry_dict = {}
    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }
    data = {
        "omit_empty_title": 'true',
        "title": title,
        "limit": '50'

    }
    r = requests.get(API_base_URL + '/entries/?sort=&omit_empty_title=true&title=' + title, headers=headers,
                     verify=use_verify, proxies=proxies)
    if r.status_code == 200:
        response = r.json()
        for entry in response:
            version_dict[entry['version_date']] = entry['id']
            entry_dict[entry['id']] = entry
        sorted_timestamps = list(version_dict.keys())
        sorted_timestamps.sort()
        sorted_timestamps.reverse()
        entry_id = version_dict[sorted_timestamps[0]]
        if verbose == True:
            message = 'Entry ' + (str(entry_id)) + ' found.'
            print(message)
    else:
        entry_id = ''
        entry = {}
        message = "Server Error. Error code :" + str(r.status_code) + ')'
        if verbose == True:
            print(message)
    return entry_id, entry, r.status_code

def get_wellplate(labfolder_auth_token, plate_id, version_id, base_URL=base_URL, verbose=verbose,
                  use_verify=use_verify, proxies=proxies):
    '''
    :param labfolder_auth_token:
    :param plate_id:
    :param version_id:
    :param base_URL:
    :param verbose:
    :param use_verify:
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return:
    '''
    API_base_URL = base_URL + '/api/v2'

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": "Token " + labfolder_auth_token
    }

    r = requests.get(API_base_URL + '/elements/well-plate/' + str(plate_id) + '/version/' + str(version_id),
                     headers=headers,
                     verify=use_verify, proxies=proxies)
    response = r.json()
    if verbose == True:
        print(response)
    return response


def get_all_wellplates(labfolder_auth_token, entry_dict={}, base_URL=base_URL, offset=0, omit='', title='', sort='',
                       verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    :param labfolder_auth_token:
    :param entry_dict:
    :param base_URL:
    :param offset:
    :param omit:
    :param title:
    :param sort:
    :param verbose:
    :param use_verify:
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return:
    '''
    API_base_URL = base_URL + '/api/v2'

    new_entry_dict = entry_dict

    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    r = requests.get(
        API_base_URL + '/entries?sort=' + sort + '&omit_empty_title=' + omit + '&expand=author,project&limit=&offset=' + str(
            offset), headers=headers,
        verify=use_verify, proxies=proxies)
    response = r.json()

    for entry in response:
        elements = entry['elements']
        wp_dict = {}
        wp_counter = 1
        for element in elements:
            if element['type'] == "WELL_PLATE":
                plate_id = element['id']
                version_id = element['version_id']
                wellplate = get_wellplate(labfolder_auth_token, plate_id, version_id, base_URL=base_URL,
                                          verbose=verbose, use_verify=use_verify, proxies=proxies)
                try:
                    wellplate_size = wellplate['meta_data']['plate']['size']
                    if wellplate_size == '96':
                        wp_title = str(wp_counter) + ': ' + wellplate['title']
                        wp_dict[wp_title] = [plate_id, version_id]
                        wp_counter += 1
                        entry_id_dict = {}
                        author = entry['author']['email']
                        project = entry['project']['title']
                        title = entry['title']
                        entry_number = entry["entry_number"]
                        if title == None:
                            title = 'None'
                        date = entry['version_date'][:10]
                        outstring = '#' + str(entry_number) +' in Project '+ project + ' by ' + author + ' on ' + date
                        entry_id_dict['author'] = author
                        # entry_id_dict['project'] = project
                        # entry_id_dict['title'] = title
                        # entry_id_dict['date'] = date
                        entry_id_dict['id'] = entry['id']
                        entry_id_dict['wellplates'] = wp_dict
                        new_entry_dict[outstring] = entry_id_dict
                except KeyError:
                    pass

    if len(response) > 0:
        out = get_all_wellplates(labfolder_auth_token, entry_dict=new_entry_dict, base_URL=base_URL, offset=offset + 20,
                           omit='', title='', sort='', verbose=verbose, use_verify=use_verify, proxies=proxies)

    if verbose == True:
        print(len(entry_dict), entry_dict)

    return new_entry_dict

def wellplate2TecanPL(wellplate_json):
    pre_column_indices = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23"]
    pre_row_indices = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
    pre_row_names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]
    pre_column_names = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12","13","14","15","16","17","18","19","20","21","22","23","24"]
    try:
        num_columns = wellplate_json["content"]["sheets"]["Composite"]["columnCount"]
    except KeyError:
        num_columns = wellplate_json["content"]["sheets"]["Übersicht"]["columnCount"]
    if num_columns == 3:
        num_rows = 2
    elif num_columns == 4:
        num_rows = 3
    elif num_columns == 6:
        num_rows = 4
    elif num_columns == 8:
        num_rows = 6
    elif num_columns == 12:
        num_rows = 8
    elif num_columns == 24:
        num_rows = 16
    else:
        return "JSON input format has incorrect dimension parameters"
    column_indices = pre_column_indices[:num_columns]
    row_indices = pre_row_indices[:num_rows]
    row_names = pre_row_names[:num_rows]
    column_names = pre_column_names[:num_columns]
    all_names = []
    for row_name in row_names:
        for column_name in column_names:
            all_names.append(row_name + column_name)
    sample_ID_dict = {}
    for name in all_names:
        sample_ID_dict[name] = ['', '', '']
    colum_namedict = dict(zip(column_indices, column_names))
    row_namedict = dict(zip(row_indices, row_names))
    layers = wellplate_json["content"]["sheets"]
    layer_list = list(layers)
    try:
        layer_list.remove('Composite')
    except ValueError:
        layer_list.remove('Übersicht')
    descriptive_layers = []
    numerical_layers = []
    dilution_layers = []
    layers_meta = wellplate_json["meta_data"]["layers"]
    for layer in layers_meta:
        layer_type = layer["type"]
        if layer_type == "DESCRIPTIVE":
            descriptive_layers.append(layer["name"])
        if layer_type == "NUMERICAL":
            if layer["unit"] == "dilution":
                dilution_layers.append(layer["name"])
            else:
                numerical_layers.append(layer["name"])
    if len(descriptive_layers) > 3:
        descriptive_layers = descriptive_layers[:3]
    if len(dilution_layers) > 1:
        dilution_layers = dilution_layers[0]
    definition_dict = {}
    dilution_dict = {}
    pipetting_status_dict = {}
    first_any_layer = wellplate_json["content"]["sheets"][layer_list[0]]["data"]["dataTable"]
    first_any_layer_name = wellplate_json["content"]["sheets"][layer_list[0]]['name']
    SM_counter = 1
    ST_counter = 1
    for row in first_any_layer:
        row_name = row_namedict[row]
        columns = first_any_layer[row]
        for column in columns:
            cell_name = row_name + colum_namedict[column]
            cell = columns[column]
            cell_identifier = cell['style']
            if isinstance(cell_identifier, dict):
                cell_identifier = cell['style']['parentName']
            if cell_identifier == first_any_layer_name:
                cell_identifier = 'SM1_' + str(SM_counter)
                pipetting_status_dict[cell_name] = '0'
                SM_counter += 1
            elif cell_identifier == 'ST':
                cell_identifier = 'ST1_' + str(ST_counter)
                pipetting_status_dict[cell_name] = '0'
                ST_counter += 1
            elif cell_identifier == 'CPR':
                cell_identifier = 'SM1_' + str(SM_counter)
                SM_counter += 1
                pipetting_status_dict[cell_name] = '2'
            elif cell_identifier == 'BF':
                cell_identifier = 'BF1'
                pipetting_status_dict[cell_name] = '0'
            elif cell_identifier == 'BL':
                cell_identifier = 'BL1'
                pipetting_status_dict[cell_name] = '0'
            elif cell_identifier == 'HPC':
                cell_identifier = 'HPC1'
                pipetting_status_dict[cell_name] = '0'
            elif cell_identifier == 'LPC':
                cell_identifier = 'LPC1'
                pipetting_status_dict[cell_name] = '0'
            elif cell_identifier == 'PC':
                cell_identifier = 'PC1'
                pipetting_status_dict[cell_name] = '0'
            elif cell_identifier == 'NC':
                cell_identifier = 'NC1'
                pipetting_status_dict[cell_name] = '0'
            elif cell_identifier == 'RF':
                cell_identifier = 'RF1'
                pipetting_status_dict[cell_name] = '0'
            else:
                pipetting_status_dict[cell_name] = '0'
                cell_identifier = 'SM1_' + str(SM_counter)
                SM_counter += 1
            definition_dict[cell_name] = cell_identifier
    if len(dilution_layers) == 1:
        dilution_layer = wellplate_json["content"]["sheets"][dilution_layers[0]]["data"]["dataTable"]
        dilution_layer_name = wellplate_json["content"]["sheets"][dilution_layers[0]]['name']
        for row in dilution_layer:
            row_name = row_namedict[row]
            columns = dilution_layer[row]
            for column in columns:
                cell_name = row_name + colum_namedict[column]
                cell = columns[column]
                try:
                    dilution = str(cell['value'])
                except KeyError:
                    dilution = '1'
                dilution_dict[cell_name] = dilution
    else:
        for cell_name in all_names:
            dilution_dict[cell_name] = '1'
    for layer_name in descriptive_layers:
        layer_index = descriptive_layers.index(layer_name)
        descriptive_layer = wellplate_json["content"]["sheets"][descriptive_layers[layer_index]]["data"]["dataTable"]
        for row in descriptive_layer:
            row_name = row_namedict[row]
            columns = descriptive_layer[row]
            for column in columns:
                cell_name = row_name + colum_namedict[column]
                cell = columns[column]
                try:
                    SampleID = str(cell['value'])
                except KeyError:
                    SampleID = ''
                SampleIDs = sample_ID_dict[cell_name]
                SampleIDs[layer_index] = SampleID
                sample_ID_dict[cell_name] = SampleIDs
    outstring = ''

    for name in all_names:
        outstring += definition_dict[name] + '\t' + name + '\t' + sample_ID_dict[name][0] + '\t' + \
                     pipetting_status_dict[name] + '\t' + sample_ID_dict[name][1] + '\t' + sample_ID_dict[name][2] + '\t' + dilution_dict[name] + '\n'
    return outstring

def create_entry(labfolder_auth_token, project_ID, entry_title='', custom_dates=[], tags=[],
                 base_URL=base_URL,
                 verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    Create entry in project with specified project ID.
    See https://eln.labfolder.com/api/v2/docs/development.html#notebook-entries-post for details.
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param project_ID: int project ID of project in which entry should be created
    :param entry_title: string, title of entry to be created, defaults to empty string (no title)
    :param custom_dates: dict custom dates, defaults to no custom dates.
    :param tags: dict tags, defaults to no tags
    :param API_base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: response: dict, response of labfolder API
    '''
    API_base_URL = base_URL + '/api/v2'

    key_list = ['project_id']
    value_list = [str(project_ID)]

    if entry_title != '':
        key_list.append('title')
        value_list.append(str(entry_title))
    if custom_dates != []:
        key_list.append('custom_dates')
        value_list.append(custom_dates)
    if tags != []:
        key_list.append('tags')
        value_list.append(tags)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + labfolder_auth_token
    }
    data = dict(zip(key_list, value_list))

    r = requests.post(API_base_URL + '/entries', headers=headers, data=json.dumps(data), verify=use_verify, proxies=proxies)
    status_code = r.status_code
    if status_code == 201:
        response = r.json()
        entry_id = response['id']
        if verbose == True:
            print(response)
    else:
        entry_id = ''
        response = r
        if verbose == True:
            print('Error', status_code)

    return entry_id, status_code, response


def create_single_DE(labfolder_auth_token, labfolder_entry_id,
                     title, value, unit,
                     base_URL=base_URL,
                     verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    Insert Numerical Data Element (Single Data ELement) to labfolder entry specified by entry ID
    For details, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-post
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param labfolder_entry_id: int, ID of entry to which Data Element should be added
    :param title: string, title of numerical data element
    :param value: number (int or float), value of numerical data element
    :param unit: string, physical unit of numerical data element.
    Must follow nomenclature described here: https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-file-elements-get-1
    :param API_base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: status_code: int, HTTP status reponse of labfolder server, message: string, response of labfolder server
    '''

    API_base_URL = base_URL + '/api/v2'

    headers = {"Content-Type": "application/json",
               "User-Agent": "PythonSDK;",
               "Authorization": "Token " + labfolder_auth_token
               }
    data = {
        "entry_id": labfolder_entry_id,
        "data_elements": [
            {
                "type": "SINGLE_DATA_ELEMENT",
                "title": title,
                "value": value,
                "unit": unit
            }
        ]
    }
    r = requests.post(API_base_URL + '/elements/data', headers=headers, data=json.dumps(data), verify=use_verify, proxies=proxies)
    if r.status_code == 201:
        message = 'Data Element added'
        if verbose == True:
            print(message)
            print(r.json())
    else:
        message = "labfolder Server Error. Error code :" + str(r.status_code)
        if verbose == True:
            print(message)
    return r.status_code, message


def create_descriptive_DE(labfolder_auth_token, entry_id,
                          title, value,
                          base_URL=base_URL,
                          verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    Insert Descriptive Data Element to labfolder entry specified by entry ID
    For details, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-post
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param entry_id: int, ID of entry to which Data Element should be added
    :param title: string, title of numerical data element
    :param value: string, descriptive value data element.
    :param API_base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: status_code: int, HTTP status reponse of labfolder server, message: string, response of labfolder server
    '''

    API_base_URL = base_URL + '/api/v2'

    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    data = {
        "entry_id": str(entry_id),
        "data_elements": [
            {
                "type": "DESCRIPTIVE_DATA_ELEMENT",
                "title": title,
                "description": value
            }
        ]
    }
    r = requests.post(API_base_URL + '/elements/data', headers=headers, data=json.dumps(data), verify=use_verify, proxies=proxies)
    if r.status_code == 201:
        message = 'Data Element added'
        if verbose == True:
            print(message)
            print(r.json())
    else:
        message = "labfolder Server Error. Error code :" + str(r.status_code)
        if verbose == True:
            print(message)
    return r.status_code, message


def create_Material_DE(labfolder_auth_token, entry_id, item_id,
                       base_URL=base_URL, verbose=verbose, use_verify=use_verify, proxies=proxies):
    """
    Insert Material Data Element to labfolder entry specified by entry ID
    For details, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-post
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param entry_id: int, ID of entry to which Data Element should be added
    :param item_id: str, ID of Material Item from MDB
    :param API_base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: status_code: int, HTTP status reponse of labfolder server, message: string, response of labfolder server
    """

    API_base_URL = base_URL + '/api/v2'

    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    data = {
        "entry_id": str(entry_id),
        "data_elements": [
            {
                "type": "MATERIAL_DATA_ELEMENT",
                "item_id": str(item_id)
            }
        ]
    }
    r = requests.post(API_base_URL + '/elements/data', headers=headers, data=json.dumps(data), verify=use_verify, proxies=proxies)
    if r.status_code == 201:
        message = 'Data Element added'
        if verbose == True:
            print(message)
            print(r.json())
    else:
        message = "labfolder Server Error. Error code :" + str(r.status_code)
        if verbose == True:
            print(message)
    return r.status_code, message


def create_DE_group(labfolder_auth_token, entry_id, data_elements,
                    base_URL=base_URL, verbose=verbose, use_verify=use_verify, proxies=proxies):
    """
    Insert Material Data Element Group to labfolder entry specified by entry ID
    For details, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-post
    :param labfolder_auth_token: string, labfolder API v2 authentication token
    :param entry_id: int, ID of entry to which Data Element should be added
    :param data_elements: list of data elements, following syntax described at https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-post
    :param API_base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: status_code: int, HTTP status reponse of labfolder server, message: string, response of labfolder server
    """

    API_base_URL = base_URL + '/api/v2'

    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    data = {
        "entry_id": str(entry_id),
        "data_elements":  data_elements
    }
    r = requests.post(API_base_URL + '/elements/data', headers=headers, data=json.dumps(data), verify=use_verify, proxies=proxies)
    if r.status_code == 201:
        message = 'Data Element added'
        if verbose == True:
            print(message)
            print(r.json())
    else:
        message = "labfolder Server Error. Error code :" + str(r.status_code)
        if verbose == True:
            print(message)
    return r.status_code, message

def create_text_element(labfolder_auth_token, text, entry_id, base_URL=base_URL,
                        verbose=verbose, use_verify=use_verify, proxies=proxies):
    '''
    Create a new text element for the provided notebook entry. The text element content may be plain text or basic HTML. Note: Images should be included in the entry as file elements.
    For details, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-text-elements-post
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param text: string, text of new text element to be inserted
    :param entry_id: int or string, entry ID of labfolder entry to which Text Element should be added.
    :param API_base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, labfolder server reponse in JSON, see
    '''
    API_base_URL = base_URL + '/api/v2'

    headers = {
        "Content-Type": "application/json",
        # "User-Agent": "PythonSDK",
        "Authorization": "Token " + labfolder_auth_token
    }
    data = {
        "entry_id": str(entry_id),
        "content": str(text)
    }
    r = requests.post(API_base_URL + '/elements/text', headers=headers, data=json.dumps(data), verify=use_verify, proxies=proxies)

    return r.json()


def create_file_element(labfolder_auth_token, filename, entry_id,
                        base_URL=base_URL,
                        verbose=verbose, use_verify=use_verify, proxies=proxies):
    """
    Insert File Element to labfolder entry specified by entry ID
    For details, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-file-elements-post
    Function will guess the mime type of file and correct image interpretation of labfolder API.
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param filename: string, file name with full path to file from which File Element should be created.
    :param entry_id: int, entry ID of labfolder entry to which File Element should be added.
    :param API_base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verbose: boolean, whether output should be printed
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: status_code: int, HTTP status reponse of labfolder server, message: string, response of labfolder server
    """

    API_base_URL = base_URL + '/api/v2'
    file_url = urllib.request.pathname2url(filename)
    mime_type = mimetypes.guess_type(file_url)[0]
    if mime_type == 'image/tiff':
        mime_type = 'image/png'
    if mime_type == None:
        mime_type = 'application/octet-stream'

    headers = {
        "Content-Type": mime_type,
        # "User-Agent": "PythonSDK",
        "Authorization": "Token " + labfolder_auth_token
    }

    data = open(filename, 'rb').read()

    file_name_list = filename.split('\\')
    last = file_name_list[-1]
    pre_uploadfilename = last
    p_uploadfilename = pre_uploadfilename.replace('#', '')
    uploadfilename = p_uploadfilename.replace('-','')

    r = requests.post(API_base_URL + '/elements/file?entry_id=' + str(entry_id) + '&file_name=' + p_uploadfilename,
                      headers=headers, data=data, verify=use_verify, proxies=proxies)

    status_code = r.status_code

    if status_code == 201:
        message = 'Data Element added'
        if verbose == True:
            print(message)
            print(r.json())
    else:
        message = "labfolder Server Error. Error code :" + str(status_code)
        verbose = True
        if verbose == True:
            print(message)
            print(r.json())

    return status_code, message


def get_table(labfolder_auth_token, table_id,
              base_URL=base_URL,
              use_verify=use_verify, proxies=proxies):
    '''
    fetch a labfolder table by table ID and return the table JSON
    For details, see: https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-table-elements-get
    For details on the grapecity table JSON schema, visit: http://help.grapecity.com/spread/SpreadSheets11/webframe.html#fullschema.html

    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param table_id: int, ID of table to retrieve
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, response of labfolder server including JSON of labfolder table or error message
    '''

    API_base_URL = base_URL + '/api/v2'

    headers = {
        "Content-Type": "application/json",
        # "User-Agent": "PythonSDK",
        "Authorization": "Token " + labfolder_auth_token
    }

    r = requests.get(API_base_URL + '/elements/table/' + str(table_id), headers=headers, verify=use_verify, proxies=proxies)

    return (r.json())


def get_table_file(labfolder_auth_token, table_id, table_json_file_name='',
                   base_URL='https://eln.labfolder.com/', verbose=verbose,
                   use_verify=use_verify, proxies=proxies):
    '''
    fetch a labfolder table by table ID and store the table JSON as a file
    For details, see: https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-table-elements-get
    For details on the grapecity table JSON schema, visit: http://help.grapecity.com/spread/SpreadSheets11/webframe.html#fullschema.html

    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param table_id: int, ID of table to retrieve
    :param table_json_file_name: full path of file name of file containing JSON table. Defaults to table name.
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, response of labfolder server including JSON of labfolder table or error message
    '''

    API_base_URL = base_URL + '/api/v2'

    headers = {
        "Content-Type": "application/json",
        # "User-Agent": "PythonSDK",
        "Authorization": "Token " + labfolder_auth_token
    }

    r = requests.get(API_base_URL + '/elements/table/' + str(table_id), headers=headers, verify=use_verify, proxies=proxies)
    response = r.json()

    if table_json_file_name == '':
        table_json_file_name = response['title'] + '.json'

    with open(table_json_file_name, 'w') as outfile:
        json.dump(response['content'], outfile)

    return response


def create_table(labfolder_auth_token, entry_id, table_title, table_json,
                 base_URL='https://eln.labfolder.com/',
                 use_verify=use_verify, proxies=proxies):
    '''
    Append labfolder Table Element to entry with given entry ID based on the input of the JSON of the table.
    For details, see: https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-table-elements-post
    For details on the grapecity table JSON schema, visit: http://help.grapecity.com/spread/SpreadSheets11/webframe.html#fullschema.html
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param entry_id: int, entry ID of labfolder entry to which Table Element should be added.
    :param table_title: string, title of Table Element to be appended to labfolder entry
    :param table_json: dict, JSON of labfolder Table Element to be appended to labfolder entry
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, labfolder server reponse in JSON, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-table-elements-post for details
    '''

    API_base_URL = base_URL + '/api/v2'

    headers = {
        "Content-Type": "application/json",
        # "User-Agent": "PythonSDK",
        "Authorization": "Token " + labfolder_auth_token
    }

    data = {
        "entry_id": str(entry_id),
        "title": table_title,
        "content": table_json
    }

    r = requests.get(API_base_URL + '/elements/table', headers=headers, data=data, verify=use_verify, proxies=proxies)

    return r.json()


def create_table_json_file(labfolder_auth_token, entry_id, table_title, json_filename,
                           base_URL=base_URL, use_verify=use_verify, proxies=proxies):
    '''
    Append labfolder Table Element to entry with given entry ID based on the input of the JSON file of the table.
    For details, see: https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-table-elements-post
    For details on the grapecity table JSON schema, visit: http://help.grapecity.com/spread/SpreadSheets11/webframe.html#fullschema.html
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param entry_id: int, entry ID of labfolder entry to which Table Element should be added.
    :param table_title: string, title of Table Element to be appended to labfolder entry
    :param json_filename: full path of file name of file containing JSON table.
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain.
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, labfolder server reponse in JSON, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-table-elements-post for details

    '''
    API_base_URL = base_URL + '/api/v2'

    with open(json_filename) as f:
        table_json = json.load(f)

    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    data = {
        "entry_id": str(entry_id),
        "title": table_title,
        "content": table_json
    }

    r = requests.post(API_base_URL + '/elements/table', headers=headers, data=json.dumps(data), verify=use_verify, proxies=proxies)

    return r.json()


def array2labfolder_table(inputarray, table_json_filename, table_name='Sheet1'):
    '''
    Convert input array to labfolder Table Element JSON.
    For details on the grapecity table JSON schema, visit: http://help.grapecity.com/spread/SpreadSheets11/webframe.html#fullschema.html
    :param inputarray: numpy array or list of lists
    :return: dict, labfolder Table Element JSON
    '''

    true = True  # loading boolean into string variable, required for json_dict

    json_dict = {
        "version": "12.0.10",
        "scrollbarMaxAlign": true,
        "cutCopyIndicatorBorderColor": "rgba(131, 198, 159, 1)",
        "grayAreaBackColor": "white",
        "allowExtendPasteRange": true,
        "copyPasteHeaderOptions": 0,
        "sheets": {
            "Sheet1": {
                "name": "Sheet1",
                "activeRow": 2,
                "activeCol": 2,
                "theme": {
                    "name": "Labfolder",
                    "themeColor": {
                        "name": "Labfolder",
                        "background1": {
                            "a": 255,
                            "r": 255,
                            "g": 255,
                            "b": 255
                        },
                        "background2": {
                            "a": 255,
                            "r": 247,
                            "g": 247,
                            "b": 247
                        },
                        "text1": {
                            "a": 255,
                            "r": 51,
                            "g": 51,
                            "b": 51
                        },
                        "text2": {
                            "a": 255,
                            "r": 209,
                            "g": 209,
                            "b": 184
                        },
                        "accent1": {
                            "a": 255,
                            "r": 97,
                            "g": 189,
                            "b": 109
                        },
                        "accent2": {
                            "a": 255,
                            "r": 84,
                            "g": 172,
                            "b": 210
                        },
                        "accent3": {
                            "a": 255,
                            "r": 247,
                            "g": 218,
                            "b": 100
                        },
                        "accent4": {
                            "a": 255,
                            "r": 251,
                            "g": 160,
                            "b": 38
                        },
                        "accent5": {
                            "a": 255,
                            "r": 226,
                            "g": 80,
                            "b": 65
                        },
                        "accent6": {
                            "a": 255,
                            "r": 147,
                            "g": 101,
                            "b": 184
                        },
                        "hyperlink": {
                            "a": 255,
                            "r": 44,
                            "g": 130,
                            "b": 201
                        },
                        "followedHyperlink": {
                            "a": 0,
                            "r": 0,
                            "g": 0,
                            "b": 0
                        }
                    },
                    "headingFont": "Arial, sans-serif",
                    "bodyFont": "Arial, sans-serif"
                },
                "data": {
                    "dataTable": {
                    },
                    "defaultDataNode": {
                        "style": {
                            "foreColor": "Text 1 0",
                            "themeFont": "Body"
                        }
                    }
                },
                "rowHeaderData": {
                    "defaultDataNode": {
                        "style": {
                            "themeFont": "Body"
                        }
                    }
                },
                "colHeaderData": {
                    "defaultDataNode": {
                        "style": {
                            "themeFont": "Body"
                        }
                    }
                },
                "rows": [
                    {
                        "size": 21
                    },
                    {
                        "size": 21
                    }
                ],
                "selections": {
                    "0": {
                        "row": 2,
                        "rowCount": 1,
                        "col": 2,
                        "colCount": 1
                    },
                    "length": 1
                },
                "defaults": {
                    "colHeaderRowHeight": 20,
                    "colWidth": 62,
                    "rowHeaderColWidth": 40,
                    "rowHeight": 19
                },
                "selectionBackColor": "rgba(131, 198, 159, 0.2)",
                "selectionBorderColor": "rgba(131, 198, 159, 1)",
                "index": 0
            }
        }
    }

    json_dict['sheets']['Sheet1']['name'] = table_name

    data_dict = {}
    row_index = 0

    for row in inputarray:
        row_index_string = str(row_index)
        row_index += 1
        col_index = 0
        row_dict = {}
        for column in row:
            col_index_str = str(col_index)
            col_index += 1
            row_dict[col_index_str] = {"value": column}
        data_dict[row_index_string] = row_dict

    json_dict['sheets']['Sheet1']['data']['dataTable'] = data_dict
    with open(table_json_filename, 'w') as outfile:
        json.dump(json_dict, outfile)

    return json_dict

def get_apps(labfolder_auth_token, app_id = '', group_id = '', limit=20, base_URL=base_URL, use_verify=use_verify, proxies=proxies):
    '''
    Returns a list of the group app installations for any groups the requesting user is a member of. The list is ordered by creation date descending.
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param app_id: optional, int, Only return app installations of specific app, defaults to None
    :param group_id: optional, int, Only return app installations of specific group, defaults to None
    :param limit: optional, int, Maximum number of app installations to return. The maximum for limit is 50 items. Defaults to 20
    :param base_URL: optional, string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param use_verify: optional, boolean, whether certificate of https server should be verified against certifi keychain, defaults to True
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, labfolder server reponse in JSON, see https://eln.labfolder.com/api/v2/docs/development.html#apps-app-installations-get
    '''
    API_base_URL = base_URL + '/api/v2'

    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    params = {}

    if app_id != '':
        params['app_id']=str(app_id)
    if group_id != '':
        params['group_id']=str(group_id)
    if limit != 20:
        params['limit'] = str(limit)

    r = requests.get(API_base_URL + '/app-installations/group?app_id=15', headers=headers, params=params, verify=use_verify, proxies=proxies)
    response = r.json()
    return response


def check_app_installation(labfolder_auth_token, app_id, base_URL=base_URL, use_verify=use_verify, proxies=proxies):
    '''
    Returns True if an App with a designated ID is installed for the authenticating user, False otherwise
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param app_id: int, ID of app for which installation should be verified
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain, defaults to True
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: boolean, True if app with ID specified in parameter app_id is installed for authenticating user, False otherwise
    '''
    API_base_URL = base_URL + '/api/v2'

    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    params = {
        "app_id":str(app_id)
    }

    r = requests.get(API_base_URL + '/app-installations/group', headers=headers, params=params, verify=use_verify, proxies=proxies)

    response = r.json()
    if response == []:
        return False
    else:
        return True


def get_xhtml_exports(labfolder_auth_token, status='', limit='', offset=20, base_URL=base_URL, use_verify=use_verify, proxies=proxies):
    '''
    Get all created XHTML Exports the requesting user has created.
    :param labfolder_auth_token: labfolder_auth_token: string, labfolder API v2 authentication token.
    :param status: optional, string, A comma separated list of statuses to be filtered. Choices: NEW RUNNING FINISHED REMOVED ERROR QUEUED
    :param limit: optional, int, Maximum number of exports to return. The maximum for limit is 50 items.. Defaults to 20.
    :param offset: optional, int, Offset into result-set (useful for pagination). Defaults to 0
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param use_verify: boolean, whether certificate of https server should be verified against certifi keychain, defaults to True
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, labfolder server reponse in JSON, see https://eln.labfolder.com/api/v2/docs/development.html#export-xhtml-exports-post
    '''
    API_base_URL = base_URL + '/api/v2'

    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    params = {}

    if status != '':
        params['status']=str(status)
    if limit != '':
        params['limit']=str(limit)
    if offset != 20:
        params['offset'] = str(offset)

    r = requests.get(API_base_URL + '/exports/xhtml', headers=headers, params=params, verify=use_verify, proxies=proxies)

    return r.json()

def get_xhtml_export(labfolder_auth_token, export_id, base_URL=base_URL, use_verify=use_verify, proxies=proxies):
    '''
    Returns the current version of the XHTML export.
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param export_id: string, id of the XHTML export
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param use_verify: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, labfolder server reponse in JSON, see https://eln.labfolder.com/api/v2/docs/development.html#export-xhtml-exports-get-1
    '''
    API_base_URL = base_URL + '/api/v2'
    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    r = requests.get(API_base_URL + '/exports/xhtml/'+str(export_id), headers=headers, verify=use_verify, proxies=proxies)

    return r.json()


def create_xhtml_export(labfolder_auth_token, base_URL=base_URL, verify=use_verify, proxies=proxies):
    '''
    Create a XHTML export of all content (Projects with their Entries & Templates) the requesting user owns.
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, labfolder server reponse in JSON, see https://eln.labfolder.com/api/v2/docs/development.html#export-xhtml-exports-post
    '''
    API_base_URL = base_URL + '/api/v2'
    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    r = requests.post(API_base_URL + '/exports/xhtml', headers=headers, verify=use_verify, proxies=proxies)

    return r.json()

def download_xhtml_export(labfolder_auth_token, export_id, export_filename, base_URL=base_URL, verify=use_verify, proxies=proxies):
    '''
    Download the result file of a finished XHTML export.
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param export_id: string, id of the XHTML export
    :param export_filename: string, file path and base name of .zip archive that will be downloaded. '.zip' will be added at end of input string.
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param use_verify: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: string, "Success" if download was successful, one of ["NEW", "RUNNING", "REMOVED", "ERROR", "QUEUED"] if not. See https://eln.labfolder.com/api/v2/docs/development.html#export-xhtml-exports-get for details.
    '''

    api_response = get_xhtml_export(labfolder_auth_token, export_id, base_URL=base_URL, use_verify=use_verify, proxies=proxies)

    file_status = api_response["status"]

    if file_status == 'FINISHED':
        download_url = api_response['download_href']
        r = requests.get(download_url, allow_redirects=True)
        open(export_filename+'.zip', 'wb').write(r.content)
        return "Success"
    else:
        return file_status

def get_data_element(labfolder_auth_token, element_id, base_URL=base_URL, verify=use_verify, proxies=proxies):
    """
    Get a data element by id, see also: https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-get
    :param labfolder_auth_token: string, labfolder API v2 authentication token.
    :param element_id: string, id of data element to retrieve
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verify: bool, whether to verify ssl certificate of server, defaults to true
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, labfolder server reponse in JSON, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-get
    """
    API_base_URL = base_URL + '/api/v2'
    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    r = requests.get(API_base_URL + '/elements/data/' + str(element_id), headers=headers, verify=verify,
                     proxies=proxies)

    return r.json()

def update_data_element(labfolder_auth_token, entry_id, element_id, new_data_element, base_URL=base_URL, verify=use_verify, proxies=proxies):
    """
    Get a data element in entry by id, see also: https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-put
    :param labfolder_auth_token: labfolder_auth_token: string, labfolder API v2 authentication token
    :param entry_id: string, id of entry containing data element to be updated
    :param element_id: string, id of data element to update
    :param new_data_element: json of new data element, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-put
    :param base_URL: string, URL of labfolder server including protocol, defaults to 'https://eln.labfolder.com'
    :param verify: bool, whether to verify ssl certificate of server, defaults to true
    :param proxies: dict, proxies used for http/https connections, defaults to no proxy (empty dict). See also: https://2.python-requests.org/en/v1.1.0/user/advanced/#proxies
    :return: dict, labfolder server reponse in JSON, see https://eln.labfolder.com/api/v2/docs/development.html#entry-elements-data-elements-get
    """
    API_base_URL = base_URL + '/api/v2'
    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    data = {
        "id": str(element_id),
        "entry_id": str(entry_id),
        "data_elements": new_data_element
    }

    r = requests.put(API_base_URL + '/elements/data/' + str(element_id), headers=headers, data=json.dumps(data), verify=use_verify,
                     proxies=proxies)

    return r.json()

def get_labregister_category(labfolder_auth_token, category_id, base_URL=base_URL, verify=use_verify, proxies=proxies):
    
    API_base_URL = base_URL + '/api/v2'
    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    r = requests.get(API_base_URL + '/mdb/categories/' + str(category_id)+'?expand=creator', headers=headers, verify=use_verify,
                     proxies=proxies)

    return r.json()

def get_labregister_item(labfolder_auth_token, item_id, base_URL=base_URL, verify=use_verify, proxies=proxies):
    
    API_base_URL = base_URL + '/api/v2'
    headers = {"Content-Type": "application/json",
               # "User-Agent": "PythonSDK",
               "Authorization": "Token " + labfolder_auth_token
               }

    r = requests.get(API_base_URL + '/mdb/items/' + str(item_id)+'?expand=category', headers=headers, verify=use_verify,
                     proxies=proxies)

    return r.json()
 