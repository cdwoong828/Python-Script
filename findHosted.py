from arcgis.gis import GIS
import arcgis
# gis = GIS("home")
url = "https://beta.gbs.kiwi/arcgis"
username = "admin"
password = "gbskorea1"
gis = GIS(url, username, password, verify_cert=False)
# Search contents 
feature_layers = gis.content.search('owner:admin', item_type = 'feature layer')
# Empty list to store ids of the items
id_list = []
# read each item 
for item in feature_layers:
    # if hosted layer, enable delete protection
    if 'Hosted Layer' in item.typeKeywords:
        item.protect(enable=True)
