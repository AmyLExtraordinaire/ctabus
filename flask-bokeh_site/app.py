import subprocess
import atexit
from flask import Flask, render_template, request
from bokeh.embed import autoload_server
from bokeh.client import pull_session
from forms import RouteSelectForm

app = Flask(__name__)
app.config.from_object('config')

bokeh_process = subprocess.Popen(
    ['bokeh', 'serve','--allow-websocket-origin=localhost:5006','--allow-websocket-origin=localhost:5000', 'transit_planner.py'], stdout=subprocess.PIPE)

@atexit.register
def kill_server():
    bokeh_process.kill()

# Index page
@app.route("/transit_planner", methods=['GET', 'POST'])
def index():
	current_route = 55
	form = RouteSelectForm()
	if form.validate_on_submit():
		current_route = form.route.data

	script = autoload_server(None, url="http://127.0.0.1:5006/transit_planner")

	# https://github.com/bokeh/bokeh/issues/5992
	script_list = script.split("\n")
	script_list[2] = script_list[2][:-1]

	script_list[2] = script_list[2] + "&route={}".format(current_route) + '"'
	script = "\n".join(script_list)
	return render_template("index.html", script=script, form=form, route=current_route)

# With debug=True, Flask server will auto-reload 
# when there are code changes
if __name__ == '__main__':
	app.run(port=5000, debug=True)
