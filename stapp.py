import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

##################################
#           LOAD DATA            #
##################################
ID = '1Cd-NSkZvJ0D1KMrRKZwawK875TCifQBjfmwqCYNAksI'
sheet1 = 'data'
sheet2 = 'enroll'
URL1 = f'https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet={sheet1}'
URL2 = f'https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet={sheet2}'

df = pd.read_csv(URL1)
enroll = pd.read_csv(URL2)

# --------------------
# master data frame
df = df.iloc[:,:7]
df['Stu_CloseContactAllowedOnCampus'] = df['Stu_CloseContactAllowedOnCampus'].astype('Int64')
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date', ascending=True)

# ---------------------
# school enroll number, lat and long
enroll = enroll.iloc[:,:3]
enroll[['lat','long']] = enroll['lat_long'].str.split(',',expand=True)
enroll[['lat','long']] = enroll[['lat','long']].astype('float')
enroll['lat'] = np.round(enroll.lat, 4)
enroll['long'] = np.round(enroll.long, 4)
school_list = ['John Cary Early Childhood Center','Beasley Elementary School',
                  'Bierbaum Elementary School','Blades Elementary School',
                  'Forder Elementary School','Hagemann Elementary School',
                  'MOSAIC Elementary School','Oakville Elementary School',
                  'Point Elementary School','Rogers Elementary School',
                  'Trautwein Elementary School','Wohlwend Elementary School',
                  'Bernard Middle School','Buerkle Middle School','Oakville Middle School',
                  'Washington Middle School','Mehlville High School',
                  'Oakville High School','SCOPE (Alternative School)']

# ---------------------
# filter down to one specific school
# df_schl = df[df['school']=='Mehlville High School'].sort_values('date')

# ---------------------
# filter down to current week
df_curr = (df.copy()
           .loc[df['date']==df['date'].max(), :]
           .loc[df['school'].isin(school_list), :])
df_curr = df_curr.merge(enroll[['school', 'lat', 'long', 'num_enroll']], on='school', how='left')
df_curr['total_new_case'] = df_curr.staff_newPos + df_curr.stu_newPos

# ---------------------
# group by week
df_weekSum = df.copy().groupby('date').sum().sort_values('date', ascending=True)


##################################
#         DEFINE CONFIG          #
##################################
# plot config
# ---------------------
LINECHART_LAYOUT = dict(
    barmode='group',
    legend = dict(yanchor='top', y=0.99, xanchor='left',x=0.01),
    margin={"r":10,"t":65,"l":10,"b":10},
    height = 300, width = 400,
    hovermode='x unified',
    hoverlabel=dict(bgcolor='white',font_size=10),
    title=dict(text='School District Weekly Case Trend',
               x=0.02, y=0.9))

BARCHART_LAYOUT = dict(
    barmode='group',
    legend = dict(yanchor='top', y=0.99, xanchor='left',x=0.01),
    margin={"r":10,"t":65,"l":10,"b":10},
    height = 300, width = 800,
    hovermode='x unified',
    hoverlabel=dict(bgcolor='white',font_size=10))

##################################
#       SET UP PAGE CONFIG       #
##################################
st.set_page_config(
    page_title='MSD Covid-19 Dashboard',
    layout='wide')

##################################
#            SIDE BAR            #
##################################
#st.sidebar.header('Select a School')

    ## -- Define Filter --
    
with st.sidebar:
    st.write('## Select a School')
    school = st.radio(
        'to see the weekly update of Covid-19 cases:',
        options= school_list
        #np.sort(df.school.unique())
    )

    ## -- SET UP FILTER LOGIC -- ##
df_schl = df.query('school==@school')


##################################
#            MAIN PAGE           #
##################################
    ## -- SET UP PAGE TITLE -- ##
st.header('Mehlville School District COVID-19 Dashboard')
st.subheader(f'Last Updated: {str(df.date.max())[:-8]}')

    ## -- TOP KPI SECTION -- ##
#col1.metric('weekly student new case','9', '9')
studCase_new = df_weekSum.iloc[-1,:].stu_newPos
studCase_lastWk = df_weekSum.iloc[-2,:].stu_newPos
studCase_change = studCase_new-studCase_lastWk

#col2.metric('weekly student off-campus', '9', '9')
studOffc_new = df_weekSum.iloc[-1,:].stu_offCampus
studOffc_lastWk = df_weekSum.iloc[-2,:].stu_offCampus
studOffc_change = studOffc_new-studOffc_lastWk

#col3.metric('weekly staff new case', '9', '9')
stafCase_new = df_weekSum.iloc[-1,:].staff_newPos
stafCase_lastWk = df_weekSum.iloc[-2,:].staff_newPos
stafCase_change = stafCase_new-stafCase_lastWk

#col4.metric('weekly staff off-campus', '9', '9')
stafOffc_new = df_weekSum.iloc[-1,:].staff_offCampus
stafOffc_lastWk = df_weekSum.iloc[-2,:].staff_offCampus
stafOffc_change = stafOffc_new-stafOffc_lastWk

col1, col2, col3, col4 = st.columns(4)
col1.metric('weekly student new case',f'{int(studCase_new)}', f'{int(studCase_change)}', 'inverse')
# col2.metric('weekly student off-campus', f'{int(studOffc_new)}', f'{int(studOffc_change)}', 'inverse')
col2.metric('weekly student off-campus', 'N/A', 'n/a')
col3.metric('weekly staff new case', f'{int(stafCase_new)}', f'{int(stafCase_change)}', 'inverse')
col4.metric('weekly staff off-campus', 'N/A', 'n/a')

    ## -- MAP MSD SECTION -- ##
left, right = st.columns(2)
with left:
    plot_map = px.scatter_mapbox(
        df_curr, 
        lat="lat", lon="long", 
        hover_name="school",
        size = 'total_new_case',
        hover_data={'total_new_case':True, 'stu_newPos':True, 'staff_newPos':True, 'lat':False, 'long':False},
        color_discrete_sequence=["firebrick"], 
        zoom=11)
    plot_map.update_layout(mapbox_style="open-street-map",
                       margin={"r":10,"t":65,"l":10,"b":10},
                       height=300, width=400,
                       title=dict(
                           text='Map of Current Week Case',
                           x=0.02, y=0.9))
    st.plotly_chart(plot_map)
with right:
    plot_week = go.Figure(data=[go.Line(
        name = 'Weekly Student New Case',
        x = df_weekSum.index,
        y = df_weekSum.stu_newPos.values),
                                go.Line(
        name = 'Weekly Staff New Case',
        x = df_weekSum.index,
        y = df_weekSum.staff_newPos)])
    plot_week.update_layout(LINECHART_LAYOUT)
    plot_week.update_xaxes(showgrid=True, ticks='outside', tickson='boundaries', ticklen=5)
    plot_week.update_yaxes(tick0=0, dtick=50, title_text='Count')
    st.plotly_chart(plot_week)

    ## -- SELECTED SCHOOL STUDENT CASE TRACKING -- ##
plot_stud = go.Figure(data=[go.Bar(
    name = 'Student New Case',
    x = df_schl.date,
    y = df_schl.stu_newPos.values
   )#,
    #                    go.Bar(
    # name = 'Student off Campus',
    # x = df_schl.date,
    # y = df_schl.stu_offCampus
   # )
])
plot_stud.update_layout(BARCHART_LAYOUT,
                        title=dict(
                           text=f'{df_schl.school.unique()[0]} Student Case Tracking - Last Updated {str(df_curr.date.unique()[0])[:10]}',
                           x=0.01, y=0.9))
plot_stud.update_xaxes(showgrid=True, ticks='outside', tickson='boundaries', ticklen=5)
plot_stud.update_yaxes(tick0=0, dtick=2, title_text='Count')
st.plotly_chart(plot_stud)

    ## -- SELECTED SCHOOL STUDENT CASE TRACKING --
plot_staf = go.Figure(data=[go.Bar(
    name = 'Staff New Case',
    x = df_schl.date,
    y = df_schl.staff_newPos.values
    )#,
#                        go.Bar(
#     name = 'Staff off Campus',
#     x = df_schl.date,
#     y = df_schl.staff_offCampus)
]
                      )

plot_staf.update_layout(BARCHART_LAYOUT,
                        title=dict(
                           text=f'{df_schl.school.unique()[0]} Staff Case Tracking - Last Updated {str(df_curr.date.unique()[0])[:10]}',
                           x=0.01, y=0.9))
plot_staf.update_xaxes(showgrid=True, ticks='outside', tickson='boundaries', ticklen=5)
plot_staf.update_yaxes(tick0=0, dtick=2, title_text='Count')
st.plotly_chart(plot_staf)

st.markdown('----')

st.markdown('''
         **Disclaimer**: I am a data scientist, and am not an infectious disease expert or
         epidemiologist. Any question related to COVID-19, please consult your physician or medical expert. This dashboard was created with the intention to enable people
         living in the Melhville School District to see updated numbers of COVID-19 confirmed cases
         by school each week. The data is sourced from the Melhville School District Covid-19 website
         [HERE](https://mehlvilleschooldistrict.com/about_us/departments/student_services/covid-19/c_o_v_i_d-19_data_dashboard). 
         ''')
st.markdown('Check the newly updated school district COVID-19 health and safety procedure [HERE](https://mehlvilleschooldistrict.com/about_us/departments/student_services/covid-19).')

st.markdown('''I will try my best to keep the dashboard up to date each week, but know
            that this is pure out of personal spare time so there is no guarantee.
            I hope y'all have a happy and healthy year of 2022!''')