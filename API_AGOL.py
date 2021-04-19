import arcpy 
import requests
import xml.etree.ElementTree as ET
from arcgis.gis import GIS
import copy

arcpy.env.workspace = r"C:\Users\Daewoong\Documents\ArcGIS\Projects\pm_API\Default.gdb"
arcpy.env.overwriteOutput = True
table_name = "airquality_table"

url = "https://www.arcgis.com"
username = "daewoongc_gbs"
password = "Qw8946qw!!"
gis = GIS(url, username, password)
mask_layer = gis.content.search('title:airquality_table owner:daewoongc_gbs', item_type='Feature Layer')[0].layers[0]
mask_layer.delete_features(where="objectid > 0")
print(mask_layer)
def parseXML(requestURL):
    res = requests.get(requestURL)
    results = ET.ElementTree(ET.fromstring(res.text))
    root = results.getroot()
    # empty dictionary to append required values
    station_dict = {}
    # find required values in xml
    for row in root.findall("body/items/item"):
        latitude = row.find("dmX").text
        longitude = row.find("dmY").text
        address = row.find("addr").text
        stationName = row.find("stationName").text
        # find first word in string
        first_word_address = address.split()[0]
        if first_word_address == '경상남도':
            first_word_address = '경남'
        elif first_word_address == '울산광역시':
            first_word_address = '울산'
        elif first_word_address == '광주광역시':
            first_word_address = '광주'
        elif first_word_address == '전라북도':
            first_word_address = '전북'
        elif first_word_address == '전라남도':
            first_word_address = '전남'
        elif first_word_address == '경상북도':
            first_word_address = '경북'
        elif first_word_address == '경기도':
            first_word_address = '경기'
        elif first_word_address == '서울특별시':
            first_word_address = '서울'
        elif first_word_address == '세종특별자치시':
            first_word_address = '세종'
        elif first_word_address == '제주특별자치도':
            first_word_address = '제주'
        elif first_word_address == '대구광역시':
            first_word_address = '대구'
        elif first_word_address == '대전광역시':
            first_word_address = '대전'
        elif first_word_address == '충청북도':
            first_word_address = '충북'
        elif first_word_address == '충청남도':
            first_word_address = '충남'
        elif first_word_address == '인천광역시':
            first_word_address = '인천'
        elif first_word_address == '강원도':
            first_word_address = '강원'
        # append required values to dictionary
        fullAddress = first_word_address + stationName
        station_dict[fullAddress] = (latitude, longitude)

    return station_dict

def parseAirqualityXML():
    sido = ['서울', '세종', '제주', '인천', '대전', '대구', '부산', '울산', '광주', '경기', '충북', '충남', '강원', '경북', '경남', '전북', '전남']
    serviceKey = 'F8ai3etU0Wdu4eDYVes2B8YQjGU2aaR55dthAmTHvKV0t1%2FF8PCm7igUtV3pFvlDiOY%2BHpzs7Ja4m0OtkNSMYA%3D%3D'
    url = 'http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty'
    # empty dictionary to store required value
    airquality_dict = {}
    # for loop to get url with all sido 
    for sidoname in sido:
        airquality_urlFull = f'{url}?sidoName={sidoname}&pageNo=1&numOfRows=200&returnType=xml&serviceKey={serviceKey}&ver=1.3'
        res = requests.get(airquality_urlFull)
        results = ET.ElementTree(ET.fromstring(res.text))
        root = results.getroot()
        # find required values in xml
        for row in root.findall("body/items/item"):
            pm25Grade1h = row.find("pm25Grade1h").text
            pm10Value24 = row.find("pm10Value24").text
            so2Value = row.find("so2Value").text
            pm10Grade1h = row.find("pm10Grade1h").text
            pm10Value = row.find("pm10Value").text
            o3Grade = row.find("o3Grade").text
            khaiGrade = row.find("khaiGrade").text
            pm25Value = row.find("pm25Value").text
            mangName = row.find("mangName").text
            stationName = row.find("stationName").text
            no2Value = row.find("no2Value").text
            so2Grade = row.find("so2Grade").text
            khaiValue = row.find("khaiValue").text
            coValue = row.find("coValue").text
            sidoName = row.find("sidoName").text
            pm25Value24 = row.find("pm25Value24").text
            no2Grade = row.find("no2Grade").text
            coGrade = row.find("coGrade").text
            dataTime = row.find("dataTime").text
            pm10Grade = row.find("pm10Grade").text
            o3Value = row.find("o3Value").text
            # put required values in a dictionary
            airquality_dict[sidoName + stationName] = (pm25Grade1h,pm10Value24,so2Value,pm10Grade1h,pm10Value,o3Grade,
                                                        khaiGrade,pm25Value,mangName,no2Value,so2Grade,khaiValue,
                                                        coValue,pm25Value24,no2Grade,coGrade,dataTime,
                                                        pm10Grade,o3Value)

    return airquality_dict

# join station and airquality data 
def joinData(stationData, airqualityData):
    # empty dictionary to store joined data 
    dictionaryJoined = {}
    # for loop to find same keys 
    for stationkey in stationData.keys():
        for airqualitykey in airqualityData.keys():
            if stationkey == airqualitykey:
                # when find same keys, put both key and value into distionaryJoined dictionary
                dictionaryJoined[stationkey[2:]] = (stationData[stationkey], airqualityData[airqualitykey])
                # stop loop when find same keys
                break
    return dictionaryJoined  

def updateFeatureClass(fulldata):
    record_template = {
    "attributes": {}, 
    "geometry": {}
    }
    features_to_be_added = []

    for data in fulldata:
        new_record = copy.deepcopy(record_template)
        '''new_record['attributes']['station'] = data
        new_record['attributes']['latitude'] = fulldata.get(data)[0][0]
        new_record['attributes']['longitude'] = fulldata.get(data)[0][1]
        new_record['attributes']['pm25Grade1h'] = fulldata.get(data)[1][0]
        new_record['attributes']['pm10Value24'] = fulldata.get(data)[1][1]
        new_record['attributes']['so2Value'] = fulldata.get(data)[1][2]
        new_record['attributes']['pm10Grade1h'] = fulldata.get(data)[1][3]
        new_record['attributes']['pm10Value'] = fulldata.get(data)[1][4]
        new_record['attributes']['o3Grade'] = fulldata.get(data)[1][5]
        new_record['attributes']['khaiGrade'] = fulldata.get(data)[1][6]
        new_record['attributes']['pm25Value'] = fulldata.get(data)[1][7]
        new_record['attributes']['mangName'] = fulldata.get(data)[1][8]
        new_record['attributes']['no2Value'] = fulldata.get(data)[1][9]
        new_record['attributes']['so2Grade'] = fulldata.get(data)[1][10]
        new_record['attributes']['khaiValue'] = fulldata.get(data)[1][11]
        new_record['attributes']['coValue'] = fulldata.get(data)[1][12]
        new_record['attributes']['pm25Value24'] = fulldata.get(data)[1][13]
        new_record['attributes']['no2Grade'] = fulldata.get(data)[1][14]
        new_record['attributes']['coGrade'] = fulldata.get(data)[1][15]
        new_record['attributes']['dataTime'] = fulldata.get(data)[1][16]
        new_record['attributes']['pm10Grade'] = fulldata.get(data)[1][17]
        new_record['attributes']['o3Value'] = fulldata.get(data)[1][18]'''
        new_record['geometry']['x'] = float(fulldata.get(data)[0][1])
        new_record['geometry']['y'] = float(fulldata.get(data)[0][0])
        new_record['geometry']['spatialReference'] = {"wkid" : 4326}
        features_to_be_added.append(new_record)  
    print(features_to_be_added)       
    return features_to_be_added     

def main():
    station_Info_url = "http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getMsrstnList?addr=&stationName=&pageNo=1&numOfRows=600&&ServiceKey=gmE9dvrEbNf4qRUIiGAko71w7mjXn%2FWTMhg6V0PC%2BpEkjRACVHwM1ddRr%2FPANc1AKFhh0CTFFhC2q9erAIh8Dw%3D%3D"
    arcpy.AddMessage("Parsing Station Url...")
    # parse Station Info xml file
    stationData = parseXML(station_Info_url)
    arcpy.AddMessage("Parsing AirqualityInfo Url...")
    # parse Airquality Info xml file
    airqualityData = parseAirqualityXML()
    arcpy.AddMessage("Joining data...")
    # join station and airquality data
    fullData = joinData(stationData, airqualityData)
    features_to_be_added = updateFeatureClass(fullData)
    mask_layer.edit_features(adds = features_to_be_added)                            

    arcpy.AddMessage("Complete")

if __name__ == "__main__":
    # calling main function
    main()

     

