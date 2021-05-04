import urllib.request
import json
import ssl
myssl = ssl.create_default_context()
myssl.check_hostname=False
myssl.verify_mode=ssl.CERT_NONE
ssl._create_default_https_context = ssl._create_unverified_context

# Tools to monitor. URLs are from server admin page
gptool_urls = "https://demo.gbs.kiwi/arcgis/admin/services/NIA/wifi_1620095929945.MapServer"


# token generation url
token_url = "https://demo.gbs.kiwi/portal/sharing/rest/generateToken"

# generate token
token_requestParams = dict(username="WABAdmin", password="building apps 4", client="referer", referer="https://demo.gbs.kiwi/portal", expiration="60", f="json")
resp = urllib.request.urlopen(token_url, urllib.parse.urlencode(token_requestParams).encode('utf-8')).read()
json_data = json.loads(resp)
token = json_data.get("token")

webtool_requestParams = dict(f="json", token=token)
resp = urllib.request.urlopen(gptool_urls, urllib.parse.urlencode(webtool_requestParams).encode('utf-8')).read()
webtool_query_result = json.loads(resp)
jobs = webtool_query_result.get("properties")
jobs["maxRecordCount"] = 25000
print(jobs)


# print("monitoring: {}".format(gptool_urls))
webtool_query_url = gptool_urls + "/edit"



webtool_requestParams = dict(service=webtool_query_result, runAsync="false", f="json", token=token)
resp = urllib.request.urlopen(webtool_query_url, urllib.parse.urlencode(webtool_requestParams).encode('utf-8')).read()
print(resp)
# webtool_query_result = json.loads(resp)
# jobs = webtool_query_result.get("properties")

# #jobs["maxRecordCount"] = 25000
# print(jobs)
