# HERON
<p align="center">
    <img src="images/h.png" width="64" align="middle">
</p>

HERON is a  library capabile of easily instantiating and deploying an AI botnet
This library provides simple chat bots which use machine learning to iterate on their source material (twitter, etc)
They are also "pluggable"; it is easy to create a network of bots that communicate with one another 

### Usage

### Metabase Setup
* Command to make the new container that is linked to the Django db:
  * `docker run -d -p 3000:3000 -it --name metabase_heron -v /home/ubuntu/HERON/db.sqlite3:/database.sqlite3 -v /home/ubuntu/metabase:/metabase metabase/metabase`
### EC2 Setup
* Start metabase:
  * `docker start <CONTAINER ID>`

### Deployment

### Technical Details and Data Flow
<p align="center">
    <img src="https://github.com/thetomcraig/HERON/blob/master/docs/data_flow.png" width="1024" align="middle">
</p>

* Figure 1 shows the high level schema for data flow through the system.  
  * Sources   
    * The main source of messages and conversations is Twitter.  
  * Bots  
    * Each Twitter user is associated with a single `Bot`.  
    * Tweets from users goes through an intake process, which:  
      * saves their original text content  
      * extracts URL links, Hashtags, and @Mentions  
  * Messages  
    * Each Tweet (message) is saved recursively; replies are all saved as well, with their relationships maintained  
    * Each Tweet (message) is also run though IBM's Watson API which does sentiment and emotional analysis.  This info is also saved.  
  * Interaction  
    * The [Dispatcher](https://github.com/thetomcraig/Discord-Dispatcher) decides when messages will be sent between Bots  
    * The Bot's existing Messagesare processed and new ones are generated using fabrication methods such as Markov Chains.  
      * These new messages are also saved for the system, so they can be used as inputs for further calculations.  
      * Based on the emotional catagories given from the Watson calculations, bots are created for each.  
        * The messages that match the Bot's emotion are used to create its new messages  
      * After the new mesages are craeted, the Dispatcher sends them to the server to be viewed.   
      


### Sources/Credits

#### Liscense
MIT
#### Credits
Research Machines plc. (2004). The Hutchinson dictionary of scientific biography.  
