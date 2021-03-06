import arcpy 
import requests
import xml.etree.ElementTree as ET

arcpy.env.workspace = r"C:\Users\Daewoong\Documents\ArcGIS\Projects\pm_API\Default.gdb"
arcpy.env.overwriteOutput = True
table_name = "airquality_table"

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

 # creates feature class to store required data    
def createFeatureClass():
    arcpy.management.CreateFeatureclass(arcpy.env.workspace, table_name, "POINT", spatial_reference=4326)
    # add fields for created feature class
    arcpy.management.AddField(table_name, "station", "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "latitude", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "longitude", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "pm25Grade1h", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "pm25Grade1h", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "pm10Value24", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "so2Value", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "pm10Grade1h", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "pm10Value", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "o3Grade", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "khaiGrade", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "pm25Value", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "mangName", "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "no2Value", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "so2Grade", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "khaiValue", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "coValue", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "pm25Value24", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "no2Grade", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "coGrade", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "dataTime", "DATE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "pm10Grade", "LONG", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.AddField(table_name, "o3Value", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

# update featture class with required data 
def updateFeatureClass(fulldata):
    # creates feature class before update 
    createFeatureClass()
    airQuality_table = table_name
    data_list = []
    with arcpy.da.InsertCursor(table_name, ['station', 'latitude', 'longitude', 'pm25Grade1h','pm10Value24','so2Value','pm10Grade1h','pm10Value',
                                            'o3Grade','khaiGrade','pm25Value','mangName','no2Value','so2Grade','khaiValue','coValue',
                                            'pm25Value24','no2Grade','coGrade','dataTime','pm10Grade','o3Value', 'SHAPE@XY']) as iCursor:                                  
                                    for data in fulldata:
                                        data_list.append(data)
                                        data_list.append(fulldata.get(data)[0][0])
                                        data_list.append(fulldata.get(data)[0][1])
                                        for i in range(19):
                                            if fulldata.get(data)[1][i] == '-':
                                                data_list.append(None)
                                            else:
                                                data_list.append(fulldata.get(data)[1][i])
                                        data_list.append(arcpy.Point(fulldata.get(data)[0][1], fulldata.get(data)[0][0]))
                                        iCursor.insertRow((tuple(data_list)))
                                        
                                        data_list.clear()  

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
    print(fullData)
    arcpy.AddMessage("Updating Feature Class...")
    # update featture class with required data
    updateFeatureClass(fullData)
    arcpy.AddMessage("Completed")

if __name__ == "__main__":
    # calling main function
    main()

     

