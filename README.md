## MOF

This desk robot was designed to kep me (anyone) entertained when there is no one else in the office... 

### How to set up the service
These are the commands I use to make sure the service runs nice and smoothly (in terminal). After running these the bot should work without needing a monitor connected to it and the code should run on startup

systemctl --user daemon-reload               # after any changes to the .service file <br/>
systemctl --user restart assistant.service   # restart it <br/>
systemctl --user stop assistant.service      # stop it <br/>
systemctl --user enable assistant.service    # enable it to run on start-up <br/>
systemctl --user start assistant.service     # start it <br/>
systemctl --user status assistant.service    # check if it's running + recent logs <br/>

> [!NOTE]
> The service has already been setup (TODO: add the relevant files for the service setup)

> [!WARNING]
> Current bugs: the eyes crash out

### Virtual Environment
Set up a virtual environment with all required libraries
Use this in the terminal to activate the environment:

source env/bin/activate

> [!NOTE]
> TODO: make a list of these/requirements document.
