import flask
from flask import request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import xml.etree.ElementTree as ET 
from urllib.request import urlopen
import time


app = flask.Flask(__name__)

# Prefix dictionary for XML nodes
ns = {'siri': 'http://www.siri.org.uk/siri'}

# Time (in seconds) when the app starts running.
start_time = 0.0

# Time (in seconds) between subsequent calls of monitor_delays().
refresh_time = 30

# Set to keep track of subway lines that are delayed.
delays = set()

# Dictionary to keep track of how long each subway line has been delayed since start of program.
total_delay_times = {
  '1': 0,
  '2': 0,
  '3': 0,
  '4': 0,
  '5': 0,
  '6': 0,
  '7': 0,
  'A': 0,
  'B': 0,
  'C': 0,
  'D': 0,
  'E': 0,
  'F': 0,
  'G': 0,
  'J': 0,
  'L': 0,
  'M': 0,
  'N': 0,
  'Q': 0,
  'R': 0,
  'SI': 0,
  'W': 0,
  'Z': 0,
}


def monitor_delays():
  """Check for train delays and recoveries"""
  global delays
  with app.app_context():
    data_url = 'http://web.mta.info/status/ServiceStatusSubway.xml'
    content = urlopen(data_url)
    tree = ET.parse(content)
    root = tree.getroot()

    # Iterate over XML nodes for all trains.
    path_to_train_nodes = 'siri:ServiceDelivery/siri:SituationExchangeDelivery/siri:Situations/siri:PtSituationElement'
    path_to_affected_vehicles = 'siri:Affects/siri:VehicleJourneys/siri:AffectedVehicleJourney'

    # Get all the subway lines that are currently delayed.
    current_delays = set()      
    for item in root.findall(path_to_train_nodes, ns):
        summary = item.find('siri:Summary', ns)
        if summary.text == 'Delays':
          # Get the names of all affected subway lines.
          affected_subways = item.findall(path_to_affected_vehicles, ns)
          for subway in affected_subways:
            subway_string = subway.find('siri:LineRef', ns)
            subway_line = subway_string.text.replace('MTA NYCT_', '').strip() 
            # Check for valid input.
            if subway_line and (subway_line in total_delay_times):
              current_delays.add(subway_line)

    new_delays = current_delays - delays
    for line in new_delays:
      print('Line {} is experiencing delays.'.format(line))

    recoveries = delays - current_delays
    for line in recoveries:
      print('Line {} is now recovered.'.format(line))

    # Add time elapsed for delayed trains.
    for line in delays:
      total_delay_times[line] += refresh_time
    delays = current_delays

        
@app.before_first_request
def initialize():
  """Schedule monitor_delays() to run every refresh_time seconds"""
  global start_time
  apsched = BackgroundScheduler()
  apsched.start()
  apsched.add_job(monitor_delays, 'interval', seconds=refresh_time)
  monitor_delays()
  start_time = time.time()


@app.route('/', methods=['GET'])
def show_started():
  """Display to user that app has started running"""
  return 'Monitoring subway delays. Check console for alerts.'


@app.route('/status', methods=['GET'])
def is_delayed():
  """Given arg 'line', return status of subway line"""
  query_parameters = request.args
  subway_line = query_parameters.get('line')

  if not subway_line:
    return 'ERROR: No subway line specified', 400
  subway_line = subway_line.upper()

  # Special case for SIR.
  if subway_line == 'SIR':
    subway_line = 'SI'

  # If subway line valid, return True if delayed.
  if subway_line not in total_delay_times:
    return 'ERROR: Invalid subway line', 400
  else:
    return str(subway_line in delays)


@app.route('/uptime', methods=['GET'])
def get_uptime():
  """Given arg 'line', return uptime of subway line"""
  query_parameters = request.args
  subway_line = query_parameters.get('line')

  if not subway_line:
    return 'ERROR: No subway line specified', 400
  subway_line = subway_line.upper()

  # Special case for SIR.
  if subway_line == 'SIR':
    subway_line = 'SI'

  # If subway line valid, return uptime.
  if subway_line not in total_delay_times:
    return 'ERROR: Invalid subway line', 400
  else:
    total_time = time.time() - start_time
    uptime = 1 - (total_delay_times[subway_line] / total_time)
    return str(uptime)


app.run()
