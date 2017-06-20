# slackelog

# Requirements
- Miniconda (currently running with 4.3.11
- slackclient  (pip install slackclient)
- pyyaml  (conda install pyyaml)
- elog.conf file  

# Usage
- Setup new Slack bot user and retrieve their BOT_ID for entry in the elog.conf file
- Invite the Slack bot user to your channel(s)
- Start up your Slack bot via the lsstelogbot script
- Any posts which mention your Slack bot user, will be handled by the Slack bot
  1. `@elog /get <entryNumber>`   Returns the XML entry in the elog
  2. `@elog /listcat`  Returns a list of all available categories defined in elog
  3. All other posts directed at the Slack bot will be handled as a post to elog.
      - Posts require one valid eLog category, otherwise the entry will be rejected:  
      `@elog /cat <categoryName> <post text>`
      - One tag may optionally be applied via `/tag <tagName>`
   
# To Do
- Modify the /tag command to #tag
- Handle image attachments
