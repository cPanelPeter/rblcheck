#!/usr/bin/perl
# There are better ways of doing this, but I have kept it as simple as possible so that
# you can easily understand the process.

system("clear");
print "Installing the RBLCheck WHM Plugin...\n";

# Check for and install if missing the Net::IP and Geo::IP Perl modules from CPAN.
&module_sanity_check;

# Create the directory for the plugin
system( "mkdir /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck" );

# Obtain the plugin from Github
system( "curl https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/whmplugin/rblcheck.cgi > /root/rblcheck.cgi" );
system( "curl https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/whmplugin/rblcheck.jpg > /root/rblcheck.jpg" );
system( "curl https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/whmplugin/rblcheck.conf > /root/rblcheck.conf" );

# Copy the rblcheck.jpg (Icon) image file to /usr/local/cpanel/whostmgr/docroot/addon_plugins
system( "cp -fv /root/rblcheck.jpg /usr/local/cpanel/whostmgr/docroot/addon_plugins" );

# Copy the rblcheck.cgi file to /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck
system( "cp -fv /root/rblcheck.cgi /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck" );

# Set execute permissions on the script
system( "chmod 0755 /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck/rblcheck.cgi" );

# Register the plugin
system( "/usr/local/cpanel/bin/register_appconfig /root/rblcheck.conf" );

print "\nRBLCheck WHM Plugin installed!\n";
exit;

# sub routines
sub module_sanity_check {
   @modules_to_install = qw( Net::IP Geo::IP );
   foreach $module(@modules_to_install) {
      chomp($module);
      eval("use $module;");
      if ($@) {
         print "WARNING: Perl Module $module not installed!\n";
         print "Installing now - Please stand by.\n";
         system("/usr/local/cpanel/bin/cpanm --force $module");
      }
   }
   return;
}
