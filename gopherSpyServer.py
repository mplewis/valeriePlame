import os
import sys
import pickle
import flask
import htmlRenderUtils
import math
from loadConfig import loadConfig

# make sure config file exists
try:
	cfg = loadConfig()
except IOError, err:
	print 'Error reading config file:', err
	print '    (Maybe you didn\'t copy sampleConfig.yml to config.yml?)'
	sys.exit()

# read yaml config: server devel mode, port
develMode = cfg['server']['develMode']
serverPort = cfg['server']['port']

subjList = htmlRenderUtils.getSubjectsWithSvgFiles()
subjTriples = htmlRenderUtils.getSubjTriples()

app = flask.Flask(__name__)
app.debug = develMode # debug mode; reload on file change and provide interactive terminal

@app.route('/')
def index():
	return flask.render_template('index.html')

@app.route('/page/<int:pageNum>/')
def multipleSubjPage(pageNum):
	numPages = int(math.ceil(len(subjTriples) / 8) + 1)
	listOfThings = range(0, numPages)
	if pageNum > numPages or pageNum < 1:
		flask.abort(404)
	return flask.render_template('multipleSubjects.html', pageNum = pageNum, subjTriples = subjTriples[pageNum*8-8:pageNum*8-1])

@app.route('/<subjAbbr>/')
def singleSubjPage(subjAbbr):
	subjAbbr = subjAbbr.upper()
	if not subjAbbr in subjList:
		flask.abort(404)
	return flask.render_template('singleSubject.html', subjAbbr = subjAbbr)

@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
	if develMode: # debug mode; serve on localhost only
		app.run(port = serverPort)
	else: # production mode; serve on all interfaces
		app.run(host = '0.0.0.0', port = serverPort)
	app.add_url_rule('/favicon.ico', redirect_to = flask.url_for('static', filename='favicon.ico'))