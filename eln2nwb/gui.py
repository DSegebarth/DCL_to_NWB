import ipywidgets as w
from ipyfilechooser import FileChooser
from IPython.display import display
from eln2nwb import labfolder as eln
from eln2nwb import eln2widget
from eln2nwb import convert2nwb
from nwbwidgets import nwb2widget
from pynwb import NWBHDF5IO
import os


INITIAL_PARAMS = {'project_options': ['AG Tovote - States', 'AG Ip - Deep brain stimulation']}

class GUI:
    
    def __init__(self):
        self.launch_converter = Launch_converter(INITIAL_PARAMS['project_options'])
        
        self.out = w.Output()
        
        self.widget = w.VBox([self.launch_converter.widget,
                              self.out])
        
        
        self.launch_converter.button.on_click(self.on_launch_converter_button_clicked)
        
        

    def on_launch_converter_button_clicked(self, b):
        if self.launch_converter.dropdown.value == 'AG Tovote - States':
            with self.out:
                self.converter = Convert_states(self.out, self.widget)
                self.widget.children = [self.converter.widget,
                                        self.out]
            
        elif self.launch_converter.dropdown.value == 'AG Ip - Deep brain stimulation':
            with self.out:
                print('Coming soon!')
                
                
class Launch_converter:
    
    def __init__(self, options):
        self.dropdown = w.Dropdown(description='In order to launch the correct NWB converter, please select your project:', 
                                    options=options,
                                    value=options[0],
                                    layout={'width': '80%'},
                                    style={'description_width': 'initial'})

        self.button = w.Button(description='Launch converter', icon='rocket')

        self.widget = w.HBox([self.dropdown, self.button])
        
        
class Convert_states:
    
    def __init__(self, parent_out, parent_widget):
        self.params = {}
        
        
        self.hspace = w.Label(value='', layout={'width': '10px'})
        self.vspace = w.Label(value='', layout={'height': '3px'})
        self.intro = w.Label(value='First, please provide the IDs of the ELN entries where you documented the respective surgeries:')
        self.set_injection_eln_entry_id = w.Text(description='ID of injection ELN entry:',
                                               placeholder='1234567',
                                               layout={'width': '40%', 'height': '50px'},
                                               style={'description_width': 'initial'})
        self.set_implantation_eln_entry_id = w.Text(description='ID of implantation ELN entry',
                                               placeholder='1234567',
                                               layout={'width': '40%', 'height': '50px'},
                                               style={'description_width': 'initial'})
        self.button_retrieve_eln_data = w.Button(description='Confirm', icon='check')
        
        self.out_injection = w.Output(layout={'width': '40%'})
        self.out_implantation = w.Output(layout={'width': '40%'})
        
        
        self.sessions_accordion = w.Accordion(children=[], 
                                              layout={'width': '90%', 
                                                      'visibility': 'hidden'})
        self.sessions_accordion.children = [States_session(self.sessions_accordion, 0).widget]
        self.sessions_accordion.set_title(0, 'session 1')
        self.vspace = w.Label(value='', layout={'width': '90%', 'height': '20px'})
        self.button_initialize_conversion = w.Button(description='Initialize conversion', icon='rocket',
                                                    style={'description_width': 'initial', 
                                                           'button_color': 'orange',
                                                           'fontcolor': 'black'},
                                                     layout={'width': '90%',
                                                             'visibility': 'hidden'})
        
        self.parent_out = parent_out
        
        self.widget = w.VBox([self.intro,
                              self.vspace,
                              w.HBox([self.set_injection_eln_entry_id,
                                      self.hspace,
                                      self.set_implantation_eln_entry_id, 
                                      self.button_retrieve_eln_data], 
                                     layout={'width': '90%'}),
                              w.HBox([self.out_injection, self.hspace, self.out_implantation], layout={'width': '90%'}),
                              self.vspace,
                              self.sessions_accordion,
                              self.vspace,
                              self.button_initialize_conversion])
        
        self.button_initialize_conversion.on_click(self.on_button_initialize_conversion_clicked)
        self.button_retrieve_eln_data.on_click(self.on_button_retrieve_eln_data_clicked)
        
    def on_button_retrieve_eln_data_clicked(self, b):
        self.get_login_credentials()
        self.params['injection'] = {'eln_entry_id': self.set_injection_eln_entry_id.value}
        self.params['implantation'] = {'eln_entry_id': self.set_implantation_eln_entry_id.value}
        
        self.params = eln2widget.States(self.params).get_metadata_injection()
        self.params = eln2widget.States(self.params).get_metadata_implantation()
        
        # Call functions from labfolder bindings to retrieve the information
        with self.out_injection:
            self.out_injection.clear_output()
            print('LabFolder entry found:')
            print('--> Procedure: ', self.params['injection']['procedure'])
            print('--> Animal ID: ', self.params['injection']['mouse_id'])
            print('--> Viral construct: ', self.params['injection']['viral_construct'])
            print('--> Date: ', self.params['injection']['date'])
            print('--> Experimenter: ', self.params['injection']['experimenter'])
        
        with self.out_implantation:
            self.out_implantation.clear_output()
            print('LabFolder entry found:')
            print('--> Procedure: ', self.params['implantation']['procedure'])
            print('--> Animal ID: ', self.params['implantation']['mouse_id'])
            print('--> Target region: ', self.params['implantation']['target_region'])
            print('--> Date: ', self.params['implantation']['date'])
            print('--> Experimenter: ', self.params['implantation']['experimenter'])
        
        self.sessions_accordion.layout.visibility = 'visible'
        self.button_initialize_conversion.layout.visibility = 'visible'
        
    def on_button_initialize_conversion_clicked(self, b):
        self.params['file_dir'] = self.sessions_accordion.children[0].children[2].value
        self.params['session_description'] = self.sessions_accordion.children[0].children[0].children[0].value
        if self.params['session_description'] == 'open field':
            self.params['session_id'] = 'OF'
        elif self.params['session_description'] == 'elevated plus maze':
            self.params['session_id'] = 'EPM'
        elif self.params['session_description'] == 'conditioning day 1':
            self.params['session_id'] = 'CD1'
        elif self.params['session_description'] == 'conditioning day 2':
            self.params['session_id'] = 'CD2'
        with self.parent_out:
            print('Conversion initialized! This might take some moments... ')
        self.params['nwbfile'] = convert2nwb.convert_states(self.params)
        with self.parent_out:
            self.parent_out.clear_output()  
        self.inspect = Inspect(self.params)
        self.widget.children = [self.inspect.widget]
            
    def get_login_credentials(self):
        with open('ELN_login.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if lines.index(line) == len(lines)-1: #if its the last line
                    correct_for_newline = len(line)
                else:
                    correct_for_newline = -1
                if line.startswith('username'):
                    self.params['username'] = line[line.index(' ')+1:correct_for_newline]
                if line.startswith('password'):
                    self.params['password'] = line[line.index(' ')+1:correct_for_newline]
                    
class States_session:
    
    def __init__(self, parent, session_id):
        self.parent = parent
        self.session_id = session_id
        self.dropdown = w.Dropdown(options=['open field', 'elevated plus maze', 'conditioning day 1', 'conditioning day 2'], 
                                   description='Please specify the session type:',
                                   layout={'width': '75%'},
                                   style={'description_width': 'initial'})
        self.checkbox = w.Checkbox(description='Create ELN entry', value=False)
        self.describe_selection = w.Label(value='Please select the directory in which the recorded data can be found:')
        self.select_directory = FileChooser('/home/ds/')
        self.select_directory.show_only_dirs = True
        self.button_add_more = w.Button(description='Add another session', icon='plus',
                                        style={'description_width': 'initial'},
                                        layout={'width': 'initial'})
        self.button_delete_session = w.Button(description='Delete this session', icon='warning',
                                             style={'description_width': 'initial'},
                                             layout={'width': 'initial'})  
        self.vspace = w.Label(value='', layout={'hight': '30px'})
        self.hspace = w.Label(value='', layout={'width': '10px'})
        self.out = w.Output()
        self.widget = w.VBox([w.HBox([self.dropdown, self.checkbox]),
                              self.describe_selection,
                              self.select_directory,
                              self.vspace,
                              w.HBox([self.button_add_more, self.hspace, self.button_delete_session, self.out])])
                              
        
        self.button_add_more.on_click(self.on_button_add_more_clicked)
        self.button_delete_session.on_click(self.on_button_delete_session_clicked)
        
    def on_button_add_more_clicked(self, b):
        with self.out:
            self.out.clear_output()
        self.parent.children = self.parent.children + (States_session(self.parent, len(self.parent.children)).widget, )
        self.parent.set_title(len(self.parent.children)-1, 'session {}'.format(str(len(self.parent.children))))
        
    def on_button_delete_session_clicked(self, b):
        l_children = list(self.parent.children)
        if len(l_children) > 1:
            del l_children[self.session_id]
            self.parent.children = tuple(l_children)
        else:
            with self.out:
                print('This is the last session. Please add another session first!')

class Inspect:
    
    def __init__(self, params):
        self.params = params
        self.intro = w.Label(value='NWB conversion was successfull!! Please use this last step to insepct the created files carefully! Once you´re done, don´t forget to save them :-)', 
                            layout={'width': '90%'})
        self.select_nwb_file = w.Dropdown(options=[self.params['session_description']],
                                           value=self.params['session_description'],
                                           description='Please select for which session you would like to inspect the NWB file:',
                                           style={'description_width': 'initial'},
                                           layout={'width': '75%'})
        self.button_inspect_nwb_file = w.Button(description='Inspect', icon='search')
        self.button_save_nwb_file = w.Button(description='Save', icon='save')
        
        self.vspace = w.Label(value=' ', layout={'heigth': '20px'})
        
        self.widget = w.VBox([self.intro, 
                              self.vspace,
                              w.HBox([self.select_nwb_file, self.button_inspect_nwb_file, self.button_save_nwb_file], layout={'width': '90%'})])
        
        self.button_inspect_nwb_file.on_click(self.button_inspect_nwb_file_clicked)
        self.button_save_nwb_file.on_click(self.button_save_nwb_file_clicked)
        
    def button_inspect_nwb_file_clicked(self, b):
        self.widget.children = [self.intro,
                                self.vspace,
                                w.HBox([self.select_nwb_file, self.button_inspect_nwb_file, self.button_save_nwb_file], layout={'width': '90%'}),
                                self.vspace,
                                nwb2widget(self.params['nwbfile'])]
    def button_save_nwb_file_clicked(self, b):
        filepath = '{}/{}_{}.nwb'.format(os.getcwd(), self.params['injection']['mouse_id'], self.params['session_id'])
        with NWBHDF5IO(filepath, 'w') as io:
            io.write(self.params['nwbfile'])
        
        self.widget.children = [self.intro,
                                self.vspace,
                                w.HBox([self.select_nwb_file, self.button_inspect_nwb_file, self.button_save_nwb_file], layout={'width': '90%'}),
                                self.vspace,
                                w.Label(value='Your NWB file was successfully saved!')]
        
        
def launch():
    display(GUI().widget) 