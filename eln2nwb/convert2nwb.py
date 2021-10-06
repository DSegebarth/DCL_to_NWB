import datetime
from datetime import date
import pytz
import string
import random

import pandas as pd
import numpy as np
import h5py
import math
import os

from skimage import io
from skimage.draw import polygon

#import matplotlib.pyplot as plt

#from nwbwidgets import nwb2widget

from pynwb import NWBFile, TimeSeries, NWBHDF5IO
from pynwb.file import Subject
from pynwb.device import Device
from pynwb.behavior import SpatialSeries, Position, BehavioralEpochs
from pynwb.ophys import TwoPhotonSeries, OpticalChannel, ImageSegmentation, Fluorescence

def find_nearest(array,value):
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx-1]) < math.fabs(value - array[idx])):
        return idx-1
    else:
        return idx
    
def take_first(elem):
    return elem[0]


def convert_states(params):
    
    
    file_dir = params['file_dir']

    # Tracking, scored behavioral events, ROI contours, fluorescence traces
    d_dfs = pd.read_excel(file_dir + '175_F7-49_201030_OF_AllData.xls', sheet_name=None)
    # Raw calcium imaging movie
    f = h5py.File(file_dir + '175_F7-49_201030_OF_PP-1_PF-1_MC-1.h5', 'r')
    #img_stack = io.imread('175_F7-49_201030_OF_PP.tiff')

    # For dummy thermal trace:
    df_states = pd.read_csv(file_dir + 'States_ceiling_reduced.csv', index_col=0)


    l_ROI_IDs = [elem[:-2] for elem in d_dfs['CAI - ROIS'].columns[::2]]
    l_ROI_masks = []

    for ROI_ID in l_ROI_IDs:

        x = d_dfs['CAI - ROIS']['{}_X'.format(ROI_ID)].values
        last_idx = np.where(~np.isnan(x))[0][-1] + 1
        x = x[:last_idx]
        y = d_dfs['CAI - ROIS']['{}_Y'.format(ROI_ID)].values[:last_idx]
        xx, yy = polygon(x,y)
        ROI_mask = np.zeros((348, 385))
        ROI_mask[xx, yy] = 1
        l_ROI_masks.append((ROI_ID, ROI_mask))

    
    x = d_dfs['Tracking']['CenterG_X'].values
    y = d_dfs['Tracking']['CenterG_Y'].values

    times = d_dfs['Tracking']['Times'].values


    position_data = np.array((x,y)).T
    position_times = d_dfs['Tracking']['Times'].values


    l_behaviors = [elem[:elem.index('_')] for elem in d_dfs['Behaviour'].columns[::2]]

    l_behavioral_time_intervals = []

    for behavior in l_behaviors:
        behavior_id = l_behaviors.index(behavior) +1
        df_temp = d_dfs['Behaviour'][['{}_1'.format(behavior), '{}_2'.format(behavior)]].copy()
        for i in range(df_temp.shape[0]):

            start_time = df_temp.loc[i, '{}_1'.format(behavior)]
            stop_time = df_temp.loc[i, '{}_2'.format(behavior)]
            if start_time > 0: 
                l_behavioral_time_intervals.append((start_time, stop_time, behavior))         
            else:
                continue

    l_behavioral_time_intervals.sort(key=take_first)

    
    tz = pytz.timezone('Europe/Berlin')
    N = 12
    
    surgery_injection = 'Virus injection on {} by {} (steretaxic coordinates: AP: {}, ML: {}, DV: {} [units: mm])'.format(params['injection']['date'],
                                                                                                                          params['injection']['experimenter'],
                                                                                                                          params['injection']['AP'],
                                                                                                                          params['injection']['ML'], 
                                                                                                                          params['injection']['DV'])
    surgery_implantation = 'GRIN-lense implantation on {} by {} (steretaxic coordinates: AP: {}, ML: {}, DV: {} [units: mm])'.format(params['implantation']['date'],
                                                                                                                          params['implantation']['experimenter'],
                                                                                                                          params['implantation']['AP'],
                                                                                                                          params['implantation']['ML'], 
                                                                                                                          params['implantation']['DV'])
    surgery_string = surgery_injection + surgery_implantation
    if params['injection']['experimenter'] != params['implantation']['experimenter']:
        l_experimenter = [params['injection']['experimenter'], params['implantation']['experimenter'], 'Dr. Jérémy Signoret-Genest', 'Prof. Dr. Philip Tovote']
    else:
        l_experimenter = [params['injection']['experimenter'], 'Dr. Jérémy Signoret-Genest', 'Prof. Dr. Philip Tovote']
    
    nwbfile = NWBFile(
        session_description = params['session_description'],
        session_id = params['session_id'],
        surgery = surgery_string,
        virus = '{}, source: in-house production'.format(params['injection']['viral_construct']),
        identifier=''.join(random.choices(string.ascii_uppercase + string.digits, k=N)),
        session_start_time=datetime.datetime(2020,10,30,9,30, tzinfo=tz),
        experimenter = l_experimenter,
        lab = 'Defense Circuits Lab',
        institution = 'University Hospital Wuerzburg, Institute of Clinical Neurobiology'
    )
    
    recording_day = date(2020, 10, 30)
    dob = params['injection']['date_of_birth']
    day_of_birth = date(int(dob[:4]), int(dob[5:7]), int(dob[8:]))
    age = recording_day - day_of_birth

    nwbfile.subject = Subject(
        subject_id = params['injection']['mouse_id'],
        age = 'P{}D'.format(str(age.days)), 
        date_of_birth = datetime.datetime(int(dob[:4]), int(dob[5:7]), int(dob[8:]), tzinfo=tz),
        #strain = 'B6J.129S6(FVB)-Slc17a6tm2(cre)Lowl/MwarJ',
        description = 'Mouse #F{} of line {}'.format(params['injection']['mouse_id'][5:], params['injection']['mouse_id'][:3]),
        genotype = params['injection']['genotype'],
        species = 'Mus musculus', 
        sex = params['injection']['sex']
    )
    
    from pynwb.epoch import TimeIntervals

    time_interval_table = TimeIntervals('behavioral_intervals', description='scored behavioral intervals', id=None)
    time_interval_table.add_column('behavior', description='type of behavior')

    for elem in l_behavioral_time_intervals:
        time_interval_table.add_interval(elem[0], elem[1], behavior=elem[2])   
        
    timestamps = d_dfs['HeartRate']['Times'].values
    data = d_dfs['HeartRate']['HeartRate'].values

    heartrate_obj = TimeSeries('Heart rate recording', data=data, timestamps=timestamps, unit='beats per minute')
    
    
    timestamps = df_states.loc[(df_states['Session'] == 'OF') & (df_states['Animal_ID'] == '175_F4-37'), 'Times'].values
    temperature = df_states.loc[(df_states['Session'] == 'OF') & (df_states['Animal_ID'] == '175_F4-37'), 'Temperature'].values

    temperature_obj = TimeSeries('Thermal recording', data=temperature, timestamps=timestamps, unit='degrees celsius')
    
    device = Device(name='Miniscope', description='NVista3.0', manufacturer='Inscopix, US')
    nwbfile.add_device(device)
    
    optical_channel = OpticalChannel('my_optchan', 'description', 500.)
    imaging_plane = nwbfile.create_imaging_plane('my_imgpln', optical_channel,
                                                 description='{} (AP={}, ML={}, DV={})'.format(params['implantation']['target_region'],
                                                                                               params['implantation']['AP'],
                                                                                               params['implantation']['ML'],
                                                                                               params['implantation']['DV']),
                                                 device=device, excitation_lambda=475., imaging_rate=10., 
                                                 indicator=params['injection']['viral_construct'][params['injection']['viral_construct'].index('GCaMP'):],
                                                 location=params['implantation']['target_region'],
                                                 unit='millimeter')
    
    image_series = TwoPhotonSeries(name='CaI', data=f['mov'][:200],
                                   dimension=[385, 348],
                                   imaging_plane=imaging_plane,
                                   starting_frame=[0], format='tiff', starting_time=0.0, rate=1.0, unit='millimeter')
    
    nwbfile.add_acquisition(image_series)
    
    mod = nwbfile.create_processing_module('ophys', 'contains optical physiology processed data')
    img_seg = ImageSegmentation()
    mod.add(img_seg)
    ps = img_seg.create_plane_segmentation('ROI segmentations',
                                           imaging_plane, 'my_planeseg', image_series)

    ID = 0
    for ROI_ID in range(len(l_ROI_masks)):
        if ROI_ID in [3, 4, 10, 12, 14, 16, 22, 25]:
            continue
        else:
            ps.add_roi(image_mask=l_ROI_masks[ROI_ID][1], id=ID)
            ID = ID+ 1


    l_ROI_IDs_included = []
    l_ROI_IDs_excluded = []

    for ROI_ID in range(len(l_ROI_masks)):
        if ROI_ID in [3, 4, 10, 12, 14, 16, 22, 25]:
            l_ROI_IDs_excluded.append(l_ROI_masks[ROI_ID][0])
        else:
            l_ROI_IDs_included.append(l_ROI_masks[ROI_ID][0])
            
    fl = Fluorescence()
    mod.add(fl)

    rt_region = ps.create_roi_table_region(description='all ROIs')
    data_included = d_dfs['CAI - Traces'][l_ROI_IDs_included].values
    data_excluded = d_dfs['CAI - Traces'][l_ROI_IDs_excluded].values
    timestamps = d_dfs['CAI - Traces']['Times'].values
    rrs = fl.create_roi_response_series('included', data=data_included, rois=rt_region, unit='lumens', timestamps=timestamps)    
    
    # Create a SpatialSeries that contains the data - extension of TimeSeries
    spatial_series_obj = SpatialSeries(
        name = 'SpatialSeries', 
        description = '(x,y) position in {}'.format(params['session_description']),
        data = position_data,
        timestamps = position_times,   # if no timestamps are provided, session_start_time from file setup will be used - ?
        reference_frame = '(0,0) is bottom left corner'
    )

    # Create a container "Position" that can contain multiple 
    # SpatialSeries - e.g. if multiple trials are used? not sure though
    position_obj = Position(spatial_series=spatial_series_obj) # name is set to 'Position' by default

    # Create a "Processing_module" to store the behavioral data, 
    # since it is not considered as raw due to preprocessing 
    # by other alglorithms / softwares
    behavior_module = nwbfile.create_processing_module(
        name='behavior', 
        description='processed behavioral data'
    )

    # Add the Processing_module to the NWB:N file
    behavior_module.add(position_obj)    
    
    hr_mod = nwbfile.create_processing_module('cardiac', 'processed heart rate recording data')
    hr_mod.add(heartrate_obj)
    
    temp_mod = nwbfile.create_processing_module('thermal', 'processed temperature recording data')
    temp_mod.add(temperature_obj)
    
    return nwbfile