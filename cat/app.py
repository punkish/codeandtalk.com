from flask import Flask, render_template, redirect, abort, request, url_for, Response, jsonify
import os
import json
import re

catapp = Flask(__name__)
root = os.path.dirname((os.path.dirname(os.path.realpath(__file__))))


@catapp.route("/videos")
def videos():
	term = _term()
	videos = _read_json(root + '/html/videos.json')
	results = []
	if term != '':
		for v in videos:
			if term in v['title']:
				results.append(v)
				continue
			if term in v['short_description']:
				results.append(v)
				continue
			if 'tags' in v:
				tags = [x['link'] for x in v['tags']]
				if term in tags:
					results.append(v)
					continue

	return render_template('videos.html',
		title            = 'Tech videos worth watching', 
		h1               = 'Videos',
		number_of_videos = len(videos),
		term             = term,
		videos           = results,
	)


@catapp.route("/people")
def people():
	term = _term()
	ppl = _read_json(root + '/html/people.json')
	result = {}
	if term != '':
		for nickname in ppl.keys():
			if re.search(term, ppl[nickname]['name'].lower()):
				result[nickname] = ppl[nickname]
			elif re.search(term, ppl[nickname].get('location', '').lower()):
				result[nickname] = ppl[nickname]
			elif re.search(term, ppl[nickname].get('topics', '').lower()):
				result[nickname] = ppl[nickname]
			elif 'tags' in ppl[nickname] and term in ppl[nickname]['tags']:
				result[nickname] = ppl[nickname]

	return render_template('people.html',
		title            = 'People who talk at conferences or in podcasts', 
		h1               = 'People who talk',
		number_of_people = len(ppl.keys()),
		term             = term,
		people           = result,
		people_ids       = sorted(result.keys()),
	)

@catapp.route("/series")
def series():
	data = _read_json(root + '/html/series.json')
	return render_template('series.html',
		h1     = 'Event Series',
		title  = 'Event Series',
		series = data,
	)

### static page for the time of transition
@catapp.route("/")
@catapp.route("/<filename>")
def static_file(filename = None):
	#index.html  redirect

	if not filename:
		filename  = 'index.html'
	mime = 'text/html'
	content = _read(root + '/html/' + filename)
	if filename[-4:] == '.css':
		mime = 'text/css'
	elif filename[-5:] == '.json':
		mime = 'application/javascript'
	elif filename[-3:] == '.js':
		mime = 'application/javascript'
	elif filename[-4:] == '.xml':
		mime = 'text/xml'
	elif filename[-4:] == '.ico':
		mime = 'image/x-icon'
	return Response(content, mimetype=mime)

@catapp.route("/v/<event>/<video>")
def video(event = None, video = None):
	path = root + '/html/v/{}/{}'.format(event, video)
	#html_file = path + '.html'
	data = json.loads(open(path + '.json').read())

	#os.path.exists(html_file):
	#	data['description'] = open(html_file).read()
	return render_template('video.html',
        h1          = data['title'],
        title       = data['title'],
        video       = data,
        blasters    = data.get('blasters'),
	)

@catapp.route("/p/<person>")
def person(person = None):
	path = root + '/html/p/{}'.format(person)
	data = json.load(open(path + '.json'))
	return render_template('person.html',
        h1          = data['info']['name'],
        title       = 'Presentations and podcasts by ' + data['info']['name'],
        person      = data,
        id          = person,
	)

@catapp.route("/t/<tag>")
@catapp.route("/e/<event>")
@catapp.route("/l/<location>")
@catapp.route("/s/<source>")
@catapp.route("/blaster/<blaster>")
def html(event = None, source = None, tag = None, location = None, blaster = None):
	if blaster:
		return _read(root + '/html/blaster/' + blaster)
	if location:
		return _read(root + '/html/l/' + location)
	if source:
		return _read(root + '/html/s/' + source)
	if event:
		return _read(root + '/html/e/' + event)
	if tag:
		return _read(root + '/html/t/' + tag)

###### Helper functions

def _read(filename):
	try:
		return open(filename).read()
	except Exception:
		return open(root + '/html/404.html').read()
		
def _term():
	term = request.args.get('term', '')
	term = term.lower()
	term = re.sub(r'^\s*(.*?)\s*$', r'\1', term)
	return term

def _read_json(filename):
	catapp.logger.debug("Reading '{}'".format(filename))
	try:
		with open(filename) as fh:
			search_data = json.loads(fh.read())
	except Exception as e:
		catapp.logger.error("Reading '{}' {}".format(search_file, e))
		search_data = {}
		pass
	return search_data

