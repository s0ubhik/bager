from requests import get, post
from flask import Flask, request, Response, stream_with_context
import os
import json

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

print("Loading Station Code Names....")
with open("traintime/stn_codes.json") as fp:
	stn_code = json.load(fp)

tele = {}
print("Loading Telegram Download Links...")
with open('download/telegram.txt') as fp:
	lines = fp.read().split("\n")
	for line in lines:
		line = line.strip()
		if line == '': continue
		p = line.split(" ")
		tele.update({p[0]: [*p[1:]]})

drive = {}
print("Loading Goofle Drive Download Links...")
with open('download/drive.txt') as fp:
	lines = fp.read().split("\n")
	for line in lines:
		line = line.strip()
		if line == '': continue
		p = line.split(" ")
		drive.update({p[0]: [*p[1:]]})
		
def get_tele_file_chunks(info):
	p = int(info[1])
	for i in range(1, int(info[0])+1):
		download_link = f"https://api.telegram.org/file/bot{TOKEN}/documents/file_{p}.{i}"
		r = get(download_link, stream = True)
		for chunk in r.iter_content(chunk_size=1024):
			yield chunk
		p += 1

def get_file_chunks(link):
	r = get(link, stream = True)
	for chunk in r.iter_content(chunk_size=1024):
		yield chunk
			
app = Flask("app")

@app.route("/code/")
def code():
	with open("tmp/code.bat") as fp:
		return fp.read()

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

	html = style + header + table
	return html

@app.route('/download/tele/<filename>')
def donwload_tele(filename):
	if filename not in tele.keys():
		return "404 File not found"

	info = tele[filename]

	return Response(
        stream_with_context(get_tele_file_chunks(info)),
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        },
        mimetype=info[2],
    )


@app.route('/download/drive/<filename>')
def donwload_drive(filename):
	if filename not in drive:
		return "404 File not found"

	info = drive[filename]

	return Response(
        stream_with_context(get_file_chunks(info[1])),
        headers={
            'Content-Disposition': f'attachment; filename={filename}'
        },
        mimetype=info[2],
    )


