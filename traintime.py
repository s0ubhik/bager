from requests import get
from flask import Flask, request
import json

print("Loading Station Code Names....")
with open("stn_codes.json") as fp:
	stn_code = json.load(fp)

app = Flask("TTH")

@app.route("/traintime/")
def traintime():
 	global stn_code
 	m = ""
 	html = """
	<style type="text/css">
	#header {
	    font-size: 20px;
	    text-align: center;
	    margin-bottom: 10px;
	}
	table {
	    border-collapse: collapse;
	    width: 100%;
	}
	  
	th, td {
	    text-align: left;
	    padding: 2px;
	}
	  
	tr:nth-child(even) {
	    background-color: Khaki;
	}
	</style>"""
 	for key, value in stn_code.items():
 		m += '<option value="'+key+'">'+key+" "+value[0]+'</option>'
 	html += """<div id="header">Train Timetable</div><label for="from">From Station:</label><select name="from" form="frm" id="from">"""
 	html += m
 	html += "</select><br>"
 	html += """<label for="to">To Station:</label><select name="to" form="frm" id="to">"""
 	html += m
 	html += "</select>"

 	html += """
 	<form id="frm" action="ft/">
  		<input type="submit" value="Search">
	</form>
	<a href="ft/?from=BP&to=KDH">Braccakpore → Khardha</a><br>
	<a href="ft/?from=KDH&to=BP">Khardha → Braccakpore</a><br>
 	"""
 	return html

@app.route("/traintime/ft/")
def traintimeft():
	global stn_code
	_from = request.args.get("from")

	_to = request.args.get("to")
	_from = _from.upper()

	_to = _to.upper()
	if _from not in stn_code.keys(): return "No such from station"
	if _to not in stn_code.keys(): return "No such to station"
	f_name = stn_code[_from][0]
	t_name = stn_code[_to][0]
	x = get("http://164.52.197.129:3000/timetable/trains_between_stns_with_pf?from_stn="+_from+"&to_stn="+_to)
	resp = x.json()
	style = """
	<style type="text/css">
	#header {
	    font-size: 20px;
	    text-align: center;
	    margin-bottom: 10px;
	}
	table {
	    border-collapse: collapse;
	    width: 100%;
	}
	  
	th, td {
	    text-align: left;
	    padding: 2px;
	}
	  
	tr:nth-child(even) {
	    background-color: Khaki;
	}
	</style>"""

	header = '<div id="header">Time Table<br>'+f_name+' → '+t_name+'</div>'
	table = """
	<table>
	<tr>
		<th>Train</th>
		<th>Dept</th>
		<th>Arvl</th>
		<th>Days</th>
	</tr>"""

	for rsp in resp:
		from_stn_dep = rsp['from_stn_dep'][:-3]
		to_stn_arr = rsp['to_stn_arr'][:-3]
		datas = [rsp['train_no'], from_stn_dep, to_stn_arr, rsp['days_of_run']]
		for i in range(len(datas)):
			if datas[i] == None: datas[i] = ""
		datas[0] = "<a href=\"?train="+datas[0]+"\">"+datas[0]+"</a>"
		table += "<tr><td>"+datas[0]+"</td><td>"+datas[1]+"</td><td>"+datas[2]+"</td><td>"+datas[3]+"</td></tr>"
	table += "</table>"

	html = style+header + table
	return html

app.run()