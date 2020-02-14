import subprocess as sub
import xml.etree.ElementTree as ET
import pandas as pd
import datetime
#from datetime import timedelta

def xml2df(xml_data, tag_path):
	root = ET.XML(xml_data) # element tree
	all_records = []
	
	#必要なログの選別
	with open(tag_path, 'r') as f:
		tag_list = f.read().splitlines()
	
	#XMLパース
	for log in root.iter('log'):
		for entry in log.iter('entry'):
			record = {}
			for subchild in entry:
				#ログ選別
				if subchild.tag in tag_list:
					record[subchild.tag] = subchild.text
			all_records.append(record)
		df = pd.DataFrame(all_records)
	return df

def get_df(log_category, query = None):
	filepath = log_category + '_xml' + get_date() + '.xml'
	nlogs = '100'
	
	#APIコール
	if query is None:
		sub.call("panxapi.py -t apitest -x --log '" + log_category + "' --nlogs " + nlogs + " > " + filepath,shell=True)
	else:
		sub.call("panxapi.py -t apitest -x --log '" + log_category + "' --nlogs " + nlogs + " --filter '" + query + "' > " + filepath,shell=True)
	#xmlをパースしてdata frame型へ
	with open(filepath, 'r') as f:
		print(f.read())
		df = xml2df(f.read(),log_category + '_tag')
	#一時的に生成したxmlを削除
	sub.call("rm -f" + filepath)
	return df

def get_date(date_format='%Y%m%d'):
	now = datetime.datetime.now()
	now = now.strftime(date_format)
	return now

def make_date_query():
	today = get_date('%Y/%m/%d')
	return '(receive_time geq "' + today + ' 22:00:00") and (receive_time leq "' + today + ' 22:59:59")'
	
def main():
	traffic_df = get_df(log_category='traffic',query=make_date_query() + ' and (subcategory-of-app eq file-sharing)')
	traffic_df.to_csv('traffic_log.csv')
	wildfire_df = get_df(log_category='wildfire' ,query=make_date_query())
	wildfire_df.to_csv('wildfire_log.csv')
	threat_df = get_df(log_category='wildfire' ,query=make_date_query())
	threat_df.to_csv('wildfire_log.csv')
	
	'''
    logcategory
    ・threat
    ・wildfire
    ・subcategory-of-app
    '''
	
if __name__ == "__main__":
	main()
