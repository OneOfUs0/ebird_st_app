import streamlit as st
import  traceback, sys

def ExceptHandler():
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    print(pymsg)

try:

    with st.container():

        'If map does not display, resize the map to full page using the expand arrows to the far right.'
        st.map(st.session_state.query_records,
               latitude='lat',
               longitude='lng',
               use_container_width=True,
               size=3000,
               color=tuple([255,255,0,200
                            ]))

    st.page_link('main.py',
                 label='Go Back to main page.')
except:
    ExceptHandler()

