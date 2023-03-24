
import matplotlib.pyplot as plt
import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
import requests
import os
import shutil
import subprocess
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, Point
from folium.plugins import Draw

import folium



headers = {
    'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
}
        

st.header("It's great to see you again, please choose your desired operation.")
choice = st.radio(
    "pick your choice",
    ('conversion in file format', 
     'get the centeroids and the shortest route between them', 
     'downloading the intersection, union and difference between two layers',
     "risk asessment"))

if choice == "conversion in file format":
        
        st.text('please upload your geojson file')
        fileConversion = st.file_uploader("upload file point",type="geojson")
        if fileConversion:
            st.success("you uploaded your file successfully")
            fileReading = gpd.read_file(fileConversion)
            option = st.selectbox(
                    'which format would you like to convert your file to?',
                    ('shapefile', 'geopackage'))
            if (option == "shapefile"):
                    
                    #lazem n-create folder 34an l shp files btb2a kaza file m4 file wa7ed
                    os.makedirs(f"{fileConversion.name}-ShpFiles")
                    fileReading.to_file(f"{fileConversion.name}-ShpFiles/{fileConversion.name}.shp")
                    shutil.make_archive(f"{fileConversion.name}", "zip", f"{fileConversion.name}-ShpFiles")
                    with open(f"{fileConversion.name}.zip", "rb") as shpFile:
                     st.download_button(
                            label = 'convert file to shp file ',
                            file_name = f"{fileConversion.name}ShpFile.zip",
                            data = shpFile                           
                        )

                    #nms7 l folder w l zip file elly et-caryto fe l file path, 34an lw 3mlna nfs l file mara tanya fa maygb4 error n l file already mawgod
                    shutil.rmtree(f"{fileConversion.name}-ShpFiles")
                    os.remove(f"{fileConversion.name}.zip")


            else:
                fileReading.to_file(f"geoPackage.gpkg" )
                with open(f"geoPackage.gpkg", "rb") as gpkgFile:
                    st.download_button(
                        label = 'convert file to Geopackage ',
                        file_name = f"{fileConversion.name}.gpkg",
                        data = gpkgFile
                    )

                os.remove("geoPackage.gpkg")

elif choice =="get the centeroids and the shortest route between them":
    

    fileAnalysis = st.file_uploader("please upload your feature geojson file",type="geojson")
    if fileAnalysis:
        st.success("your file was uploaded successfully")
        file_Read = gpd.read_file(fileAnalysis).to_crs("EPSG:4326")
        centroids = file_Read.centroid.apply(lambda x: Point(x.x, x.y))
        st.subheader("Here you would get the centroids of the shaps you enter")
        st.subheader("By hovering over the point you'd get the number of the point and then you would choose the start and end point of the route you wish to make")
        
        #hn3ml 2 list le kol dropdown list
        startPoint = []
        counterPointDisplay =1
        lengthOfCoords = 0
        for item in centroids:
            mycoords = (f"Point no. {counterPointDisplay}){item.x}, {item.y}")
            startPoint.append(mycoords)
            counterPointDisplay +=1
        firstPoint = st.selectbox('please enter your start point',startPoint)


        endPoints =[]
        count =1
        for item in centroids:
            mycoords = (f"Point no. {count}){item.x}, {item.y}")
            endPoints.append(mycoords)
            count +=1
        secondPoint = st.selectbox('please enter your end point',endPoints)

        #n3ml l popup msgs bel raqam w da elly hykon mawgod fe l dropdown list fo2
        popup_msgs = (f"{i}"for i in range(1,len(centroids)+1))

        #n3ml l points w n7ot l popup beta3ha bel geometry elly gaya mn l centroids fo2
        points_gdf = gpd.GeoDataFrame(geometry=centroids, crs="EPSG:4326", data={"point no.": popup_msgs})
        route_style = {
            "stroke":True,
            "color" : "red",
            "weight" : 5
        }
        m = leafmap.Map()
        #nzod l points w l features
        m.add_gdf(file_Read)
        m.add_gdf(points_gdf) 


        #34an my3ml4 route mn nfs l point le nafsaha
        if firstPoint == secondPoint:
            st.error("please don't choose the same point as ending and start point to be able to get the route")

             
        #lw das 3al button w l 2 points mo5tlfeen fa ynady 3al api, w ya5od l value l tanya mn l dropdown list bma n elly gowaha 3obara 3n tupple fa ya5od l coordinate bs
        if st.button("get me the route") and firstPoint != secondPoint:        
            call = requests.get(f'https://api.openrouteservice.org/v2/directions/driving-car?api_key=5b3ce3597851110001cf6248c9ee9bd765a84956a2f95235ab20013b&start=%20%20%20%20%20%20%20%20%20%20{firstPoint.split(")")[1]}&end=%20%20%20%20%20%20%20%20%20%20{secondPoint.split(")")[1]}', headers=headers)
            df =gpd.read_file(call.text)
            m.add_gdf(df, style = route_style)

        m.to_streamlit(height=500)

elif choice == "downloading the intersection, union and difference between two layers":
    firstLayer = st.file_uploader("please upload your first input",type="geojson")
    secondLayer = st.file_uploader("please upload your second input",type="geojson")

    firstLayer_style = {
                "stroke":True,
                "color" : "#ede100",
                "weight" : 3,
                "fill" : True,
                "fillColor" : "#e6e075",
                "fillOpacity" : 0.5
            }
    secondLayer_style = {
                "stroke":True,
                "color" : "#ff0800",
                "weight" : 3,
                "fill" : True,
                "fillColor" : "#f5a29f",
                "fillOpacity" : 0.5
            }
    resultLayer_style = {
                "stroke":True,
                "color" : "#ff8000",
                "weight" : 3,
                "fill" : True,
                "fillColor" : "#f0b273",
                "fillOpacity" : 0.8
            }                            
            
    if firstLayer and secondLayer:
        st.subheader("your result is in orange")
        option = st.selectbox(
        'what do you want to do',
        ('intersection', 'erase', 'union'))
        #l user y5tar howa 3ayz intersection wla union wla erase ma ben 2 layers w n-download l output ka geojson zy ma 3mlnaha fe l conversion fo2
        if (option == "intersection"):
            polygon1_Read = gpd.read_file(firstLayer).to_crs("EPSG:3857")
            polygon2_Read = gpd.read_file(secondLayer).to_crs("EPSG:3857")
            intersection = gpd.overlay(polygon1_Read, polygon2_Read, how='intersection')
            intersection.to_file('intersection.geojson', driver='GeoJSON')
            with open(f"intersection.geojson", "rb") as interGeo:
                st.download_button(label='Download your Intersection',
                                data=interGeo,
                                file_name='intersection.geojson')
            os.remove(f"intersection.geojson")
            m = leafmap.Map()
            m.add_gdf(polygon1_Read, style = firstLayer_style)
            m.add_gdf(polygon2_Read, style = secondLayer_style)
            m.add_gdf(intersection, style = resultLayer_style)
            m.to_streamlit(height=500)

        elif (option == "union"):
            polygon1_Read = gpd.read_file(firstLayer).to_crs("EPSG:3857")
            polygon2_Read = gpd.read_file(secondLayer).to_crs("EPSG:3857")
            union = gpd.overlay(polygon1_Read, polygon2_Read, how='union')
            union.to_file('union.geojson', driver='GeoJSON')
            with open(f"union.geojson", "rb") as unionGeo:
                st.download_button(label='Download your Union',
                                data=unionGeo,
                                file_name='union.geojson')
            os.remove(f"union.geojson")
            m = leafmap.Map()
            m.add_gdf(polygon1_Read, style = firstLayer_style)
            m.add_gdf(polygon2_Read, style = secondLayer_style)            
            m.add_gdf(union, style = resultLayer_style)
            m.to_streamlit(height=500)
        else:
            polygon1_Read = gpd.read_file(firstLayer).to_crs("EPSG:3857")
            polygon2_Read = gpd.read_file(secondLayer).to_crs("EPSG:3857")
            erase = gpd.overlay(polygon1_Read, polygon2_Read, how='difference')
            erase.to_file('erase.geojson', driver='GeoJSON')
            with open(f"erase.geojson", "rb") as unionGeo:
                st.download_button(label='Download your Erase',
                                data=unionGeo,
                                file_name='erase.geojson')
            os.remove(f"erase.geojson")
            m = leafmap.Map()
            m.add_gdf(polygon1_Read, style = firstLayer_style)
            m.add_gdf(polygon2_Read, style = secondLayer_style)            
            m.add_gdf(erase, style = resultLayer_style)
            m.to_streamlit(height=500)            

elif choice == "risk asessment":
    st.header("Risk Assessment")
    st.subheader("In this analysis your first layer is the source of danger, your second input is the buffer range of its risk, and your third input is the tested area")
    st.subheader("You would get the intersection between the buffer(effect range) of the danger and your tested area. so you would be able to avoid the danger")

    riskSource = st.file_uploader("please upload your risk sources",type="geojson")
    radius = st.number_input("please enter your buffer radius in meter")
    testedArea = st.file_uploader("please upload your tested Area",type="geojson")

    if riskSource and radius and testedArea:
        intersection_style = {
                "stroke":True,
                "color" : "#ff0000",
                "weight" : 5,
                "fill" : True,
                "fillColor" : "red",
                "fillOpacity" : 0.75
            }
        buffer_style = {
                "stroke":True,
                "color" : "#855b03",
                "weight" : 2,
                "fill" : True,
                "fillColor" : "#ffb005",
                "fillOpacity" : 0.75
            }
        tested_style = {
                "stroke":True,
                "color" : "#125402",
                "weight" : 2,
                "fill" : True,
                "fillColor" : "#77d160",
                "fillOpacity" : 0.75
            }
        #ytl3 l buffer
        riskSource_Read = gpd.read_file(riskSource).to_crs("EPSG:3857")
        buffer_point = riskSource_Read['geometry'].buffer(radius)       #7atena geometry 34an y-access l field da bs
        buffer_gdf= gpd.GeoDataFrame(geometry=buffer_point)

        #ytl3 l intersection w ye3redo 3al 5areeta
        testedArea_Read = gpd.read_file(testedArea).to_crs("EPSG:3857")
        intersection = gpd.overlay(testedArea_Read, buffer_gdf, how='intersection')
        st.subheader("The indanger area is in red!")
        m = leafmap.Map()
        m.add_gdf(riskSource_Read)
        m.add_gdf(buffer_gdf, style = buffer_style)
        m.add_gdf(testedArea_Read, style = tested_style)
        m.add_gdf(intersection, style = intersection_style)

        #y-download l intersection
        intersection.to_file('intersection.geojson', driver='GeoJSON')
        with open(f"intersection.geojson", "rb") as interGeo:
            st.download_button(label='Download your Intersection',
                            data=interGeo,
                            file_name='risk.geojson')
        os.remove(f"intersection.geojson")
        m.to_streamlit(height=500)