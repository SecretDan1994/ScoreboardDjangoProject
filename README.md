# ScoreboardDjangoProject
This Project involves the transfer of JSON data from programs used in specific gameservers for a community named "ElevatedGamingNetwork".

The particular webpage from the server list that is actively being worked on is gs1.elevatedgaming.net's page: "elevatedgaming.net:82/servers/4/stats". 

This webpage will be linked with an active gameserver in a video-game named "Counter-Strike: Source". 

# NOTE: DO NOT BE ALARMED BY THE NAMES OF THE TEAMS, "COUNTER-TERRORISTS" AND "TERRORISTS", THESE ARE THE DEFAULT NAMES FOR TEAMS IN THIS SPECIFIC VIDEO GAME. 

In this particular server it will retrieve all the necessary information for all active players connected on the server and display them with two methods: 

1. A Scoreboard
2. Viewable logs, both of which will automatically update every time an event fires in the server.  

**********************
How it works 
**********************

A python program in the server records information every time an event happens on the server and stores it in python 
dictionaries. 

The information is then converted into JSON and is sent through daphne django websockets and connects with the webpage 
via client-side websocket and transfers the JSON to a JSONField in the model of the webpage.

Every time an event happens on the server, a serverlog object is created and the webpage updates the information displayed via the passed JSON and the automatic refresh of data is handled by the websockets. 

All data since the first round is cached via the views.py using redis and the server is run on nginx. 

The webpages are setup with html5, bootstrap css, and Javascript/JQuery for the frontend and Django Python handles all the backend. 

**********************
What is done at the moment?
**********************

- The webpage for "elevatedgaming.net:82/servers/4/stats" is already setup and is a responsive webpage
- What appears on the screen is a live representation of what is happening on the game server
- The caching and display of data has proven to work as intended 
- The websockets are completely operational and are connected correctly, one websocket for gameserver to webserver updating the database with information 
- Another websocket connects from the webserver to the client browser, updating the browser with information each time a message is passed from the game server to the webserver to the client
