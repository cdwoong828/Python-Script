import urllib.request
import json
import ssl
myssl = ssl.create_default_context()
myssl.check_hostname=False
myssl.verify_mode=ssl.CERT_NONE
ssl._create_default_https_context = ssl._create_unverified_context

# Tools to monitor. URLs are from server admin page
id_url = "https://demo.gbs.kiwi/arcgis/admin/services/NIA/wifi_1620095929945.MapServer"


# token generation url
token_url = "https://demo.gbs.kiwi/portal/sharing/rest/generateToken"

# generate token
token_requestParams = dict(username="WABAdmin", password="building apps 4", client="referer", referer="https://demo.gbs.kiwi/portal", expiration="60", f="json")
resp = urllib.request.urlopen(token_url, urllib.parse.urlencode(token_requestParams).encode('utf-8')).read()
json_data = json.loads(resp)
token = json_data.get("token")

requestParams = dict(f="json", token=token)
resp = urllib.request.urlopen(id_url, urllib.parse.urlencode(requestParams).encode('utf-8')).read()
query_result = json.loads(resp)
jobs = query_result.get("properties")
jobs["maxRecordCount"] = 25000

# go to edit
query_url = id_url + "/edit"

# update query result 
requestParams = dict(service=query_result, runAsync="false", f="json", token=token)
resp = urllib.request.urlopen(query_url, urllib.parse.urlencode(requestParams).encode('utf-8')).read()

