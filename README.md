# Commerical-Real-Estate-Slayer
Toolkit to automate prospecting systems for agents/brokers.

Goals: Maximize the time/value of the prospecting process.  

Settings:
    - Pattern: [VARIABLE: Description...]
    - URL: The remote JSON source location.
    - USERNAME: Username or login for your JSON Request.
    - API_KEY: The API key for your JSON source.
    - TAG: Tag of the list you want to download. 
    - TIMER_1: The high number of seconds for the phone.
    - TIMER_2: The low number of seconds for the phone.
- Automate Cisco Jabber GUI desktop client (Windows 7+)
    - Identify and connect to the main Jabber GUI window.
    - Identify the active call window.
    - Place calls from a list of phone numbers. 
    - Mute calls from a list of phone numbers.
    - End calls from a list of phone numbers. 
- Download a list of contacts and phone numbers from a remote API
    - Parse JSON Data into contact name objects. 
    - Parse JSON Data into phone number objects.
    - Clean phone numbers into a uniform format. 
- Planned Development:
  - Automation:
    - Better call management.
    - Scheduled call sessions.
    - Start/Stop/Pause/Step the call sessions.  Hands-free mode. 
  - System:
    - Read TCP/SIP packets to parse transaction information.
    - Parse TCP packets to natural language text and associate with contact.
    - Request and parse a contact's property address and information from a remote source.
    - Use a CSV file instead of API request.
    - Implement Sqlite database.  
  - Application GUI:
    - GUI for list of contacts.
    - Threading during the call automation cycle.
    - Call charts and statistics. 
    - Start/Stop/Pause/Step buttons and hot-keys. 

