#!/bin/bash
echo "Uninstalling the RBL Check WHM Plugins..."

echo -n "Removing rblcheck.jpg from the /usr/local/cpanel/whostmgr/docroot/addon_plugins/ directory "
rm -f /usr/local/cpanel/whostmgr/docroot/addon_plugins/rblcheck.jpg
echo "Done"

echo -n "Removing rblcheck.cgi from the /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck/ directory "
rm -f /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck/rblcheck.cgi
echo "Done"

echo -n "Removing the rblcheck directory from the /usr/local/cpanel/whostmgr/docroot/cgi/ directory "
rmdir /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck
echo "Done"

echo -n "Removing the whmrblcheck.tar.gz file from the /root/ directory "
rm -f /root/whmrblcheck.tar.gz
echo "Done"

echo -n "Removing the rblcheck_install.pl file from the /root/ directory "
rm -f /root/rblcheck_install.pl
echo "Done"

echo -n "Removing the rblcheck.conf file from the /root/ directory "
rm -f /root/rblcheck.conf
echo "Done"

echo -n "Unregistering the appconfig... "
/usr/local/cpanel/bin/unregister_appconfig /var/cpanel/apps/rblcheck.conf
echo "Done"


echo "RBL Check WHM Plugin has been successfully removed."
rm -f /root/rblcheck_uninstall.sh
