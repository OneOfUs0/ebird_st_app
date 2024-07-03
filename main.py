import pandas as pd
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from ebird.api import get_observations

from ebird.api import get_regions, get_adjacent_regions, get_region
from ebird.api import get_taxonomy, get_taxonomy_forms, get_taxonomy_versions

from ebird.api import get_visits, get_checklist

from ebird.api import get_notable_observations, get_nearby_notable, \
    get_species_observations, get_nearby_species

import pandas as pd
import  traceback, sys, os, json
import streamlit as st

api_key = '39ed2uqtlp87'

def ExceptHandler():
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    print(pymsg)

# ====== INIT

# Get the list of states in the US.
if 'usastates' not in st.session_state:
    states = get_regions(api_key, 'subnational1', 'US')  # this is a dict
    st.session_state.usastates = states

if 'counties' not in st.session_state:
    st.session_state.counties = {}
if 'df_species' not in st.session_state:
    st.session_state.df_species = []

if 'selected_state' not in st.session_state:
    st.session_state.selected_state = ''
if 'selected_county' not in st.session_state:
    st.session_state.selected_county = ''
if 'selected_counties' not in st.session_state:
    st.session_state.selected_counties = ''

if 'selected_species' not in st.session_state:
    st.session_state.selected_species = ''

if 'alltaxa' not in st.session_state:
    st.session_state.alltaxa = get_taxonomy(api_key)

if 'namefrag' not in st.session_state:
    st.session_state.namefrag = ''

# query
if 'query_records' not in st.session_state:
    st.session_state.query_records = []
if 'query_result_excel' not in st.session_state:
    st.session_state.query_result_excel = ''
if 'jsut_ran_query' not in st.session_state:
    st.session_state.just_ran_query = False

if 'downloadfilename' not in st.session_state:
    st.session_state.downloadfilename = ''
if 'selected_subid' not in st.session_state:
    st.session_state.selected_subid = ''

if 'obs_checklist' not in st.session_state:
    st.session_state.obs_checklist = []

st.session_state.just_ran_query = False  # default

# ====== FUNCTIONS ======================================================

def GetUSAStates():
    try:
        # Get the list of states in the US.
        st.session_state.usastates = get_regions(api_key, 'subnational1', 'US')

    except:
        ExceptHandler()

def GetCounties():
    try:
        # Get the list of counties in New York state.
        counties = get_regions(api_key, 'subnational2', st.session_state.selected_state)

        st.session_state.counties = counties #json.load(counties)

    except:
        ExceptHandler()

def GetSpeciesMatches():
    try:

        st.session_state.df_species = []  # clear previous list of species names

        search = st.session_state.namefrag
        print('search for ' + search)

        # region
        if st.session_state.selected_county != '':
            region = st.session_state.selected_county
        else:
            region = st.session_state.selected_state

        alltaxa = st.session_state.alltaxa

        #print('alltaxa type: ' + str(type(alltaxa)) + ' which is ' + str(len(alltaxa)) + ' long.')

        spplist = []
        for rec in alltaxa:
            if search.lower() in rec['comName'].lower():
                spplist.append({'Code':rec['speciesCode'],'Cname':rec['comName']})


        if len(spplist) > 0:
            st.session_state.df_species = spplist # pd.DataFrame.from_dict(sppdict)

    except:
        ExceptHandler()

def GetObseravations():
    try:
        print('go get ebird data')
        # species
        sppname = st.session_state.selected_species

        # region
        if st.session_state.selected_county != '':
            region = st.session_state.selected_county
        else:
            region = st.session_state.selected_state

        # query
        records = get_species_observations(api_key, sppname, region)
        print('Got ' + str(len(records)) + ' observation records.')

        st.session_state.query_records = records

        # to Pandas Dataframe
        #pDf = pd.DataFrame(records)

        st.session_state.just_ran_query = True


        # # to Excel
        # outputfile = '_'.join(['ebird_download',region,sppname]) + '.xlsx'
        # data = pDf.to_excel(outputfile)
        #
        # # settings for the download button to use.
        # st.session_state.downloadfilename = outputfile
        # st.session_state.query_result_excel = data

    except:
        ExceptHandler()
def GetChecklistInfo(chklistid:str):
    try:
        chklist = get_checklist(api_key,chklistid)

        st.session_state.obs_checklist = chklist


    except:
        ExceptHandler()
# def Download_save():
#     try:
#         st.session_state.queryresult = pdf
#         st.session_state.queryparams = {'region': region, 'sppcode': sppname}
#
#     except:
#         ExceptHandler()

# ============================= CALLBACKS ======================================

def btnQuery_click():
    try:
        GetObseravations()



    except:
        ExceptHandler()

def txtSppName_change():
    try:
        # get species names that match this text.
        st.session_state.namefrag = st.session_state.txtSppName

        # call to get the species names
        GetSpeciesMatches()

    except:
        ExceptHandler()

def df_Species_select():
    try:
        adict = st.session_state.df_Species

        if len(adict['selection']['rows']):
            idx = adict['selection']['rows'][0]
            sppcode = st.session_state.df_species[idx]['Code']
        else:
            sppcode = ''

        st.session_state.selected_species = sppcode

    except:
        ExceptHandler()

def df_states_select():
    try:
        adict = st.session_state.df_states
        idx = adict['selection']['rows'][0]

        if idx != '':
            state = st.session_state.usastates[idx]['code']
        else:
            state = ''

        st.session_state.selected_state = state

        # clear any previously selected counties.
        st.session_state.selected_county = ''
        st.session_state.selected_counties = ''

        print('Selected: ' + str(st.session_state.selected_state))

        # call to get the counties for this state
        GetCounties()
    except:
        ExceptHandler()

def df_counties_select():

    try:

        adict = st.session_state.df_counties

        counties = []
        if len(adict['selection']['rows']) > 10:
            st.warning('The query has a maximum of 10 counties.')
        else:
            for idx in adict['selection']['rows']:
                county = st.session_state.counties[idx]['code']
                counties.append(county)

        st.session_state.selected_county = counties
        st.session_state.selected_counties = ','.join(counties)


        print('Selected: ' + str(st.session_state.selected_county))

    except:
        ExceptHandler()

def df_query_records_select():
    try:

        adict = st.session_state.df_query_records # the widget
        idx = adict['selection']['rows'][0]
        print('selected row ' + str(idx))

        subid = ''
        if idx != '':
            subid = st.session_state.query_records[idx]['subId']

        st.session_state.selected_subid = subid

    except:
        ExceptHandler()
def btn_Checklist_click():
    try:

        #recid = 'S183888820'

        GetChecklistInfo(st.session_state.selected_subid)

    except:
        ExceptHandler()

# ================== UI ===================
try:
    st.set_page_config(page_title='Setup',
                       layout="wide",
                       page_icon=':baby_chick:',
                       menu_items={'About': 'Created by OneOfUs0, June 2024',
                                   'Get Help': 'https://somafm.com/dronezone/'},
                       initial_sidebar_state = "collapsed"
                       )


    with st.container():


        PPH = '''
        **Instructions**  
        Use this to retrieve obseravation records from EBIRD.  First define the query below by selecting a ***state*** and one or several ***counties***.  Next, 
        type the species common
        name and choose the species from the list.   Click ***Query EBIRD***.   Any results returned will displayed in the table at the bottom of the page. 
        Save the records in the table by using the ***Download as CSV*** at the upper right corner of the table.
        '''
        st.title('EBIRD')
        st.markdown(PPH)
        #st.html(PPH4_html_outline)

        col1, space1, col2, space2, col3 = st.columns([6,1,5,1,3])
        with col1:
            st.header('Define Geographic Area')

            subcol1, subcol2 = st.columns([2,2])
            with subcol1:
                st.subheader('State')
                st.markdown('''Select one.
                ''')
                st.dataframe(st.session_state.usastates,
                             key='df_states',
                             selection_mode='single-row',
                             on_select=df_states_select)


            with subcol2:
                st.subheader('Counties')
                st.markdown('''Select up to 10.
                ''')
                disable_counties = not bool(st.session_state.selected_state)
                st.dataframe(st.session_state.counties,
                             key='df_counties',
                             on_select=df_counties_select
                             )

        with col2:
            st.header('Define the Species')

            st.text_input('Type species common name below and hit enter.',
                          key='txtSppName',
                          help='Type species name as you know it and hit Enter to search for that.',
                          on_change=txtSppName_change
                          )


            st.dataframe(st.session_state.df_species,
                         use_container_width=True,
                         hide_index=True,
                         selection_mode='single-row',
                         key='df_Species',
                         on_select=df_Species_select)

        with col3:
            st.header('Query EBIRD')
            st.subheader('State: ' + st.session_state.selected_state)
            st.subheader('Counties: ' + st.session_state.selected_counties)
            st.subheader('Species: ' + st.session_state.selected_species)

            disable_button = True
            if bool(st.session_state.selected_species):
                if bool(st.session_state.selected_county) and bool(st.session_state.selected_state):
                    disable_button = False

            st.button('Query EBIRD',
                      type='primary',
                      key='btnQuery',
                      help='Click to execute your query.',
                      disabled=disable_button,
                      on_click=btnQuery_click)

            if True: #st.session_state.just_ran_query:
                if len(st.session_state.query_records):
                    count = len(st.session_state.query_records)
                    st.success('Retrieved ' + str(count) + ' Records (scroll down to view)')
                else:
                    st.error('No records found.')


            # if st.session_state.downloadfilename != '':
            #     st.download_button('Download as Excel',
            #                    data = st.session_state.query_result_excel,
            #                    file_name=st.session_state.downloadfilename,
            #                    type='primary',
            #                    key='btnDownload',
            #                    help='Click to download to the query results to the browsers download folder.',
            #                    disabled=disable_button)

    st.divider()

    with st.container(): # BOTTOM CONTAINER

        st.subheader('Observation Records')

        st.dataframe(st.session_state.query_records,
                     key='df_query_records',
                     use_container_width=True,
                     selection_mode='single-row',
                     on_select=df_query_records_select
                     )

        col1, col2 = st.columns([4,10])

        with col1:
            st.divider()

            st.subheader('Single Observation Details')

            st.button('Get Checklist',
                      type='primary',
                      key='btn_Checklist',
                      help='Get checklist information for the selected record.',
                      disabled=bool(st.session_state.selected_subid == ''),
                      on_click=btn_Checklist_click)

            if st.session_state.selected_subid != '':

                subcol1, subcol2 = st.columns([6,5])
                with subcol1:
                    st.markdown('''
                    Observation ***Checklist*** Information for
                    ''')
                with subcol2:
                    st.subheader(st.session_state.selected_subid)

                st.dataframe(st.session_state.obs_checklist,
                             use_container_width=True,
                             key='df_checklist')

except:
    ExceptHandler()

