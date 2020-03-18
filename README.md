# Google Maps Visualization

This summer while travelling I discovered the Google Timeline, a history of your location recorded by your phone's GPS. While it would show you individual days, your routes, and points of interest on Google Maps, I wanted to see everywhere I've been on the face of this earth up to this point. Using Google's takeout feature, you can actually export your location history which is what were going to be using for our data visualization. This project introduced my to GIS software, I tried using ArcGIS as this is the most commonly used software used for spatial analysis. While trying to learn ArcGIS as I go, I ran into some issues which required me to switch to something I'm more comfortable with for certain tasks, which is Python scripting. This is how I did it



### Download your Location History using Google Takeout

Google Takeout can be found [here](https://takeout.google.com/settings/takeout ). It takes about 12 hours for Google to process your request until they send your takeout through email. You can download only your location history if you've accumulated a large amount of data. Your location history will be JSON formation

![Capture](C:\Users\Alex\Desktop\GIS post\Capture.PNG)



### Converting Location History JSON into GIS Shapefiles

The JSON format of our data seems to be in a format only readable by Google Maps. In order to read your data into ArcGIS it must be converted into shapefiles (.shp). For this I found a python script  on Github called [android_location_converter](https://github.com/iboates/android_location_converter)

![](C:\Users\Alex\Desktop\GIS post\Capture2.PNG)Our data is a series of points with a longitude, latitude, and timestamp. For me there was about 1,500,000+ points along Eastern Ontario from Toronto to Montreal, with most of the points being in my hometown Kingston.

### Reducing the Data

So even with my own desktop with a fancy CPU and GPU, this amount of data turned ArcGIS into a slideshow, which gets old very quick while trying to learn to use the software. I decided to reduce the data to only points within Kingston for my sanity. I've also gone ahead and downloaded Shapefiles for the map of Kingston, conveniently provided to the public on the [City of Kingston website](https://opendatakingston.cityofkingston.ca/explore/dataset/road-segments/information/?disjunctive.orn_class&disjunctive.gis_class)

![Capture1](C:\Users\Alex\Desktop\GIS post\Capture1.PNG)

We can see the map of Kingston, our location history, a boundary I created to include only the points within.

![](C:\Users\Alex\Desktop\GIS post\Capture4.PNG)

Still over 1,000,000 points but still much better.



### First attempting at created Routes

In an attempt to make a path similar to what is seen in the Google Timeline I decided to connect each point in a line based of off date. This was an absolute mess.

![Capture5](C:\Users\Alex\Desktop\GIS post\Capture5.PNG)

The line join feature is unaware of the underlying map layer and joins the points in straight lines. I originally thought this may be due to our GPS not fitting to the roads due inaccuracy so I tried snapping each point to the lines on the map layer

![](C:\Users\Alex\Desktop\GIS post\Capture3.PNG)While this did clean up the map a little, the resulting lines were almost identical to the previously generated mess.



### Attempting to create routes using ArcGIS's Network Analysts Plugin

So the version of ArcGIS provided by my school includes all of the licensed ArcGIS plugins including a routing engine found in the Network Analyst plugin. The idea was to create a route for each unique date, in the order of time for each point. First we have to convert out map layer into a Network Model which is a series of edges and nodes or in this case streets and intersections.

![](C:\Users\Alex\Desktop\GIS post\Capture8.PNG)

Using the Network analysist plugin I found no way to created routes based off of date or at least not without doing it manually one by one for each of the 1000+ days of routes. My next attempt was to used ArcMaps Model Builder, this tools lets you string together different geoprocessing tools inputs and outputs to automate the processing of data. I tried to do it iteratively for each of the routes.

![](C:\Users\Alex\Desktop\GIS post\Capture10.PNG) 

After spending a day trying to get the model to work I gave up. After doing some research on Reddit a simpler and more powerful option is Python scripting within ArcMaps. You can either control your current ArcMaps session with a python terminal or you can use all of the ArcGIS functionality with their APIs and Python plugin ArcPy.



### Creating Routes using Python

##### (1) Reducing the Data

After some research I came across a routing engine called [GraphHopper](https://github.com/graphhopper/graphhopper). This the API used to created routes in the OpenStreetMap website. Once again I am going to have to transform the Google data into a form easily parsable by Python and create some extra scripts to call the APIs and transform out data into a GIS readable format. For this I will use another script found on Github called [location-history-json-converter](https://github.com/Scarygami/location-history-json-converter). I am going to convert the data into CSV format, a table format where each row is a point having a latitude, longitude, and timestamp. 

After inspecting the data I decided that the data will have to be reduced. The ~1,000,000 points is a point approximately every 5 minutes for 8 years, and much of these points are consecutively in the same place, this make routing much more time consuming and redundant.  The pandas library is very powerful and quick tool for parsing large amounts of data. I used this to create a python script to reduce our points to only one necessary for routing.

All of the code for this project is also on my [Github](https://github.com/AlexPerrin/Google-Maps-Data-Visulaization)

```python
import pandas as pd

#Read Google data CSV into a pandas object
coordinates = pd.read_csv('locations.csv', parse_dates=['Time'])
coordinates['Date'] = coordinates['Time'].dt.date
coordinates['Time'] = coordinates['Time'].dt.time
coordinates = coordinates.reindex(columns = ['Latitude', 'Longitude', 'Date', 'Time'])

#Conditions for removing points
#detete points that have not moved atleast greater than 250m form the previous point (still plenty of points to used for routing)
#but do not delete points at the same location if they are on different days, need these points as start and end point
#delete points outside of the boundary of Kingston 
sameDay = coordinates['Date'] == coordinates['Date'].shift()
latitudeThresh = (abs(coordinates['Latitude'] - coordinates['Latitude'].shift()) < 0.0025) & sameDay
longitudeThresh = (abs(coordinates['Longitude'] - coordinates['Longitude'].shift()) < 0.0025) & sameDay
latitudeBoundry = (44.202942 < coordinates['Latitude']) & (coordinates['Latitude'] < 44.294006)
longitudeBoundry = (-76.622925 < coordinates['Longitude']) & (coordinates['Longitude'] < -76.432312)

#delete points
coordinates.drop(coordinates[latitudeThresh & longitudeThresh | ~latitudeBoundry | ~longitudeBoundry].index, inplace = True)

#delete any points where there is only one for a particular day (need atleast 2 to form a route)
dupes = coordinates[coordinates.duplicated('Date', keep = False)]

#export to csv
dupes.to_csv (r'export_dataframe_250m.csv', index = False, header = True)
```



##### (2) Calling the GraphHopper API

[GraphHopper](https://github.com/graphhopper/graphhopper) is a java application which can be interacted with through HTTP request with localhost. An instance of Graphhopper must be started with an OpenStreetMap file (.OSM) for routing. For this I used a map of Ontario from [Geofabrik](http://download.geofabrik.de/north-america/canada.html). I created a Windows Batch script for starting Graphhopper

```
java -Xmx2g -Xms2g -jar graphhopper-web-0.9.0-with-dep.jar jetty.resourcebase=webapp config=config-example.properties datareader.file=ontario-latest.osm.pbf
```

GraphHopper calls are actually just URLs. The API calling Python script parses each of the points in our reduced data set and creates concatenated string for each URL. GraphHopper outputs each route as a GPX file, a commonly used GPS format. These are a series of points evenly spaced along the route with the excepted time for each point. These points should be much connect to a line much better than or unrouted points. 

```python
import pandas as pd
import urllib.request

# path to your csv file with the endpoint coordinates
coordinates = pd.read_csv('export_dataframe_250m_Dupes.csv')

# graphhopper API call building blocks. Check Graphhopper documentation how to modify these. 
urlStart = 'http://localhost:8989/route?'
point = 'point='
urlEnd = 'type=gpx&gpx.route=false&instructions=false&vehicle=car'
separator = '%2C'

compare = '2013-10-22'
c = 0
address = ""

for i in range(len(coordinates)-1):
    if coordinates.loc[i, 'Date'] == compare:
        address = address + (point + str(round(coordinates.loc[i, 'Latitude'],8)) + separator + str(round(coordinates.loc[i, 'Longitude'], 8)) + '&')
        
    else:
        c += 1
        print("\n" + "Processing Route: " + str(c) + " Line: " + str(i) + "\n" + address + "\n")
        
        try:
            req = urlStart + address + urlEnd
            resp = urllib.request.urlopen(req)
            gpxData  = str(resp.read(),'utf-8')
            fileName = 'kingston_' + str(c)
            saveFile = open('gpx_files/{0}.gpx'.format(fileName), 'w')
            saveFile.write(gpxData)
            saveFile.close()
        except: 
            print('bad request on index ' + str(c))
            pass

        compare = coordinates.loc[i, 'Date']
        address = point + str(round(coordinates.loc[i, 'Latitude'],8)) + separator + str(round(coordinates.loc[i, 'Longitude'], 8)) + '&'
```



##### (3) Merging the GPX files

Now that we have a GPX file for each of the routes were going to be importing this all back into ArcMap. Now I'm going to have to do this literately for each file and collect each route into a single feature layer. For this I created yet another model in Model Builder, this time one that worked as intended.

![capture11](C:\Users\Alex\Desktop\GIS post\capture11.PNG)

The resulting feature overlayed on our map of Kingston layer looks like this.

![](C:\Users\Alex\Desktop\GIS post\Capture12.PNG)

ArcMaps does not include any sort of image processing functionality. After some more research a better solution for the visualization is going to be QGIS; an open source GIS program. After exporting the routes feature as a shapefile and importing into QGIS, I used the addition blending mode to highlight areas on the map where I had been more frequently. 

![](C:\Users\Alex\Desktop\GIS post\output.png)

A full resolution image [here](https://i.imgur.com/DweeyAZ.png)



### What I Learned

##### ArcGIS

- Features (points, lines, polygons, rasters)
- Manipulating features (using attribute tables, points to line, near function to snap to line, exclude outside polygon)
- Network Analysis Plugin (Creating routes)
- Model Builder (Iterators, creating model parameters)

##### Python

- Pandas library for parsing and data manipulation
- Integrating GraphHopper API



### In The Future

This was a great introduction to GIS for me, this project taught me the basic of ArcMap but there's much more to learn. I would like to learn the ArcPy library as it allows you do use all the functionality of ArcMap in a Python Script, allowing you to create really efficient and modular computations. With my solid foundation in Python and knowledge of computer science fields like algorithms this could be very powerful tool.

I would also like to use my new knowledge of GIS to complete the visualization with the full data set. I may also be able to generate animations for routes using QGIS.
