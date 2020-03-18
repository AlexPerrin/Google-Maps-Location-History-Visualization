import pandas as pd

coordinates = pd.read_csv('locations.csv', parse_dates=['Time'])
coordinates['Date'] = coordinates['Time'].dt.date
coordinates['Time'] = coordinates['Time'].dt.time
coordinates = coordinates.reindex(columns = ['Latitude', 'Longitude', 'Date', 'Time'])

sameDay = coordinates['Date'] == coordinates['Date'].shift()
latitudeThresh = (abs(coordinates['Latitude'] - coordinates['Latitude'].shift()) < 0.0025) & sameDay
longitudeThresh = (abs(coordinates['Longitude'] - coordinates['Longitude'].shift()) < 0.0025) & sameDay
latitudeBoundry = (44.202942 < coordinates['Latitude']) & (coordinates['Latitude'] < 44.294006)
longitudeBoundry = (-76.622925 < coordinates['Longitude']) & (coordinates['Longitude'] < -76.432312)

coordinates.drop(coordinates[latitudeThresh & longitudeThresh | ~latitudeBoundry | ~longitudeBoundry].index, inplace = True)

#latitudeThreshDupes = (abs(coordinates['Latitude'] - coordinates['Latitude'].shift(2)) < 0.0025) & sameDay
#longitudeThreshDupes = (abs(coordinates['Longitude'] - coordinates['Longitude'].shift(2)) < 0.0025) & sameDay

#coordinates.drop(coordinates[latitudeThreshDupes | latitudeThreshDupes].index, inplace = True)
#coordinates.drop(coordinates[latitudeThresh | longitudeThresh].index, inplace = True)

dupes = coordinates[coordinates.duplicated('Date', keep = False)]

dupes.to_csv (r'export_dataframe_250m_Dupes.csv', index = False, header = True)