# Subway Status Alert Service


### Overview

This web service alerts users if a subway line gets delayed or recovers from being delayed. Every 30 seconds, the service will alert the user if there are any changes in subway statuses.

Additionally the service includes two endpoints, '/status' and '/uptime', which allow the user to check if a specific line is delayed and get the uptime of a line respectively.

The subway data is obtained from: http://web.mta.info/status/ServiceStatusSubway.xml

Assumptions/Simplifications:
* For the purposes of this assignment, a subway line is either delayed or running as normal i.e. if a line is not delayed, it is considered to be running as normal.
* The 'SIR' train is denoted as 'SI' in the XML file, so it is also displayed as 'SI' in this service. If the user checks the status for 'SIR', it is converted to 'SI' first.


### Technologies Used:
* Python 3.8
* Flask
* APScheduler 
* XML
* Urllib
* time


### How to Run
1. Make sure Flask is installed.
2. In terminal, navigate to the project directory and run the command 'python subway_status.py'.
3. Navigate to the given link http://127.0.0.1:5000 in a browser.
4. The web service will start running, and you will start seeing alerts in your console for train delays and recoveries.

To check the status of a line, append '/status?line=<line_you_want_to_check>' to the end of the above link.
E.g. http://127.0.0.1:5000/status?line=1

Similarly, to check the uptime of a line, append '/uptime?line=<line_you_want_to_check>' to the end of the above link.
E.g. http://127.0.0.1:5000/uptime?line=A

Invalid subway names (lines not included in the ServiceStatusSubway.xml file) will return an 400 Bad Request error.
**Note**: For subway lines denoted by letters, capitalized and uncapitalized subway line names work fine.


### Design Decisions:
* I added a dictionary 'total_delay_times' to keep track of how long each subway line has been delayed (in seconds) since the start of the program. This is an estimate, since monitor_delays runs every 'refresh_time' seconds.
* Since there may be multiple AffectedVehicleJourney nodes listed under one PtSituationElement (with repetitions), I iterate through those nodes, adding to the 'current_delays' set variable before printing out any messages to the console, in order to avoid repetitions.

### Known Issues
* There are some delays/discrepancies between the MTA's ServiceStatusSubway.xml and the MTA dashboard. E.g. a summary of 'Slow Speeds' in the XML file shows up as 'Delays' in the dashboard. In most cases, however, the discrepancies eventually resolve within a few minutes or so.
* Subway lines S, S_f and S_r are not found in the XML ServiceStatusSubway.xml LineRef tags, so they are not checked in this service.


### Style Conventions
* Python PEP Guidelines


### Tutorials/Resources Used
* Subway Realtime Data: http://web.mta.info/status/ServiceStatusSubway.xml
* Learning Flask: https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask#lesson-goals
