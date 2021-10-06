from eln2nwb import labfolder as eln

class States:
    
    def __init__(self, params):
        self.params = params
        self.username = self.params['username']
        self.password = self.params['password']
        
        self.base_url = 'https://labfolder.ukw.de'
        self.use_verify = False
        self.verbose = False
        self.proxies = {}
        
    def get_metadata_injection(self):
        token, expires, message, success = eln.authenticate(self.username, self.password, 
                                                            base_URL=self.base_url,verbose=self.verbose, 
                                                            use_verify=self.use_verify, proxies=self.proxies)
        entry_id, entry, status_code = eln.get_last_entry_by_title(token, title=self.params['injection']['eln_entry_id'],
                                                                    base_URL=self.base_url,verbose=self.verbose, 
                                                                    use_verify=self.use_verify, proxies=self.proxies)
        
        data_element_id = entry['elements'][0]['id']
        data_element = eln.get_data_element(token, element_id=data_element_id, base_URL=self.base_url, verify=self.use_verify, proxies=self.proxies)

        self.params['injection']['date'] = data_element['data_elements'][0]['children'][0]['description']
        self.params['injection']['experimenter'] = data_element['data_elements'][0]['children'][1]['description']
        self.params['injection']['procedure'] = data_element['data_elements'][0]['children'][2]['description']
        self.params['injection']['mouse_id'] = data_element['data_elements'][2]['children'][0]['description']
        self.params['injection']['genotype'] = data_element['data_elements'][2]['children'][1]['description']
        self.params['injection']['sex'] = data_element['data_elements'][2]['children'][2]['description']
        self.params['injection']['date_of_birth'] = data_element['data_elements'][2]['children'][3]['description']
        self.params['injection']['bodyweight'] = data_element['data_elements'][2]['children'][4]['value']
        self.params['injection']['viral_construct'] = data_element['data_elements'][3]['children'][1]['description']
        self.params['injection']['target_region'] = data_element['data_elements'][3]['children'][3]['description']
        self.params['injection']['AP'] = data_element['data_elements'][3]['children'][4]['children'][0]['description']
        self.params['injection']['ML'] = data_element['data_elements'][3]['children'][4]['children'][1]['description']
        self.params['injection']['DV'] = data_element['data_elements'][3]['children'][4]['children'][2]['description']
        
        eln.logout(token, base_URL=self.base_url, use_verify=self.use_verify, proxies=self.proxies)
        return self.params
    
    def get_metadata_implantation(self):
        token, expires, message, success = eln.authenticate(self.username, self.password, 
                                                            base_URL=self.base_url,verbose=self.verbose, 
                                                            use_verify=self.use_verify, proxies=self.proxies)
        entry_id, entry, status_code = eln.get_last_entry_by_title(token, title=self.params['implantation']['eln_entry_id'],
                                                                    base_URL=self.base_url,verbose=self.verbose, 
                                                                    use_verify=self.use_verify, proxies=self.proxies)
        
        data_element_id = entry['elements'][0]['id']
        data_element = eln.get_data_element(token, element_id=data_element_id, base_URL=self.base_url, verify=self.use_verify, proxies=self.proxies)        
        
        self.params['implantation']['date'] = data_element['data_elements'][0]['children'][0]['description']
        self.params['implantation']['experimenter'] = data_element['data_elements'][0]['children'][1]['description']
        self.params['implantation']['procedure'] = data_element['data_elements'][0]['children'][2]['description']
        self.params['implantation']['mouse_id'] = data_element['data_elements'][2]['children'][0]['description']
        self.params['implantation']['genotype'] = data_element['data_elements'][2]['children'][1]['description']
        self.params['implantation']['sex'] = data_element['data_elements'][2]['children'][2]['description']
        self.params['implantation']['date_of_birth'] = data_element['data_elements'][2]['children'][3]['description']
        self.params['implantation']['bodyweight'] = data_element['data_elements'][2]['children'][4]['value']
        self.params['implantation']['implanted_item'] = data_element['data_elements'][3]['children'][0]['description']
        self.params['implantation']['target_region'] = data_element['data_elements'][3]['children'][1]['description']
        self.params['implantation']['AP'] = data_element['data_elements'][3]['children'][2]['children'][0]['description']
        self.params['implantation']['ML'] = data_element['data_elements'][3]['children'][2]['children'][1]['description']
        self.params['implantation']['DV'] = data_element['data_elements'][3]['children'][2]['children'][2]['description']
        
        eln.logout(token, base_URL=self.base_url, use_verify=self.use_verify, proxies=self.proxies)
        return self.params
    
    