rblcheck - a simple command line script to check your main IP and any ipaliases against a list
of RBL's (Realtime Blackhole Lists).  

A WHM plugin was also created with this code to be used in a walkthrough.  

https://forums.cpanel.net/threads/how-to-create-a-plugin-whm-cpanel.516681/

How to use this from the command line: 

Either download the code from github.com: 

# curl -s https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/rblcheck > /root/rblcheck

or set up an alias: 

alias rblcheck="/usr/bin/perl <(curl -s https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/rblcheck)"

Call it with the following options: 

-bash-4.1# ./rblcheck 
rblcheck
   --main checks the main IP address.
   --allips checks all IP addresses on the server.
   --listips lists all IP addresses on the server.
   --listedonly only displays information if an IP address is listed in an RBL.
   --checkip [IP ADDRESS] - checks an IP address not associated with this server
   --help (you're looking at it!)

So to check the servers main IP address to see if it's listed on any RBL's you might enter: 

-bash-4.1# ./rblcheck --main --listedonly
Checking IP 208.74.121.106

cbl.abuseat.org: [LISTED] (127.0.0.2)
Reason: "Blocked - see http://www.abuseat.org/lookup.cgi?ip=208.74.121.106"
cidr.bl.mcafee.com: [LISTED] (127.0.0.4)
Reason: "https://www.spamhaus.org/query/ip/208.74.121.106"
rbl.rbldns.ru: [LISTED] (127.0.0.2)
Reason: "RBLDNS Server v1.0. Author VDV [ Site: WWW.RBLDNS.RU ]"
zz.countries.nerd.dk: [LISTED] (127.0.3.72)
Reason: "us"

Checked 248 Realtime Blackhole Lists (RBL's) & found 208.74.121.106 listed in 4 of them.

