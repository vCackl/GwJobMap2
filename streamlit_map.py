maps_api_key='AIzaSyB-dQj96htTup7ggxE_hNp8X-xvZzQgTS4'



from io import BytesIO
import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import folium
import base64
import os
import time
from streamlit_folium import st_folium


# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Eastern Fwy Graffiti Inspection - 09/02/2023")
#add the above as a title
cc1, cc2 = st.columns((1, 1))
with cc1:
        st.title("Eastern Fwy Graffiti Inspection - 09/02/2023")

with cc2:
    gw_logo = open("gw_logo.jpg", "rb")
    gw_logo_bytes = gw_logo.read()
    st.image(gw_logo_bytes, width=200, use_column_width=False, output_format="PNG", caption="")

# LOAD DATA ONCE
@st.experimental_singleton
def load_data_csv(ib, rows=10000):
    #READ data_ib.csv and data_ob.csv
    #phsyical_coordinate,type,path,coordinate,loc_name,sqm,is_day_job

    file ="data_ib.csv" if ib else "data_ob.csv"
    #ignore header row

    data = pd.read_csv(
        file,
        nrows=rows,
        names=[
            "physical_coordinate",
            "type",
            "path",
            "loc_name",
            "sqm",
            "is_day_job",
        ],
        skiprows=1,  # don't read header since names specified directly
    )
    



    data["physical_coordinate"] = data["physical_coordinate"].str.replace("(", "")
    data["physical_coordinate"] = data["physical_coordinate"].str.replace(")", "")
    #convert to floats
    data[["lat", "lon"]] = data["physical_coordinate"].str.split(",", expand=True).astype(float)
    #replace sqm nan with "N/A"
    data["sqm"] = data["sqm"].fillna("N/A")
    #replace -1 sqm with "N/A"
    data["sqm"] = data["sqm"].replace(-1, "N/A")

    
    


    return data





# CALCULATE MIDPOINT FOR GIVEN SET OF DATA
def mpoint(lat, lon):
    #ignore all incorrect values so you can average the rest
    return (np.nanmean(lat), np.nanmean(lon))






c3, c4 = st.columns((1, 1))
#switch box that allows you to switch between inbounds and outbounds
with c3:
    switch = st.selectbox("Select Inbound or Outbound", ["Inbound", "Outbound"])
switch2bool = {"Inbound": True, "Outbound": False}
data = load_data_csv(switch2bool[switch])
print(data["lat"], data["lon"])
midpoint = mpoint(data["lat"], data["lon"])

#create map functipon
@st.experimental_singleton
def create_map(data):
    m = folium.Map(location=[midpoint[0], midpoint[1]], zoom_start=12)
    featuregroup = folium.FeatureGroup(name="Jobs")
    for index, row in data.iterrows():
        featuregroup.add_child(folium.Marker(location=[row["lat"], row["lon"]]))
    return m, featuregroup



def show_vid(data):
    #turn data into a dict
    data = data.to_dict("records")[0]
    with c4:
        #add blank space
        st.write("")
        st.write("")
        st.write(f"""**{data['loc_name']}** | **sqm: {data['sqm']}** | **{"Day Job" if data['is_day_job'] else "Night Job"}** """)


    #display day job and sqm as metrics, place next to eachother withouyt using columns


    if data["type"]  in ("frame", "image"):
        #show image
        #bytes

        image_file = open(data["path"], "rb")
        image_bytes = image_file.read()
        #make it 2 percent smaller
        st.image(image_bytes)
        
    elif data["type"] == "video":
        #show video
        video_file = open(data["path"], "rb")
        video_bytes = video_file.read()
        st.video(video_bytes)
        #write the Loc_name in bold
    
    

 
#make sure maps only load once
m, featuregroup = create_map(data)





c1, c2 = st.columns(2)
#add session state to keep track of last clicked object

st.session_state["last_object_clicked"] = None
with c1:
    output = st_folium(m, feature_group_to_add=featuregroup, width=1000, height=500)
    st.session_state["clicked_object"] = output["last_object_clicked"]

with c2:
    if st.session_state["clicked_object"] is not None:
        if st.session_state["clicked_object"] != st.session_state["last_object_clicked"]:
            st.session_state["last_object_clicked"] = st.session_state["clicked_object"]
            lat = st.session_state["clicked_object"]['lat']
            lon = st.session_state["clicked_object"]["lng"]
            cur_job = data[(data["lat"] == lat) & (data["lon"] == lon)]
            show_vid(cur_job)    

#add footer
#show map


volition_logo = open("volition_logo.jpg", "rb")
volition_logo_bytes = volition_logo.read()


bot_right = st.columns(6)
bot_right[5].image(volition_logo_bytes, width=150, use_column_width=False, output_format="PNG", caption="")