rblcheck - a simple plugin created specifically for a walkthrough on how to create a Plugin
for WHM. 

https://forums.cpanel.net/resources/how-to-create-a-plugin-whm-cpanel.415/

Allows you to check your servers main IP and any ipaliases against a list of RBL's 
(Realtime Blackhole Lists).  

INSTALLATION: 

Download the rblcheck_install.pl script to /root and run it (as root).  
Once completed, you should have an rblcheck plugin under WHM => Plugins.

wget https://github.com/cPanelPeter/rblcheck/blob/master/whmplugin/rblcheck_install.pl
chmod 0755 rblcheck_install.pl
./rblcheck_install.pl


