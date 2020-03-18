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