import pandas as pd

#Read Google data CSV into a pandas object
coordinates = pd.read_csv('locations.csv', parse_dates=['Time'])
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
coordinates = coordinates[coordinates.duplicated('Date', keep = False)]

#export to csv
coordinates.to_csv (r'export_dataframe_250m.csv', index = False, header = True)
