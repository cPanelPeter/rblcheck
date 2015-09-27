#!/usr/bin/perl

system("clear");
print "Installing the RBLCheck WHM Plugin...\n";

# Check for and install if missing the Net::IP and Geo::IP Perl modules from CPAN.
&module_sanity_check;

# Create the directory for the plugin
mkdir(0755, "/usr/local/cpanel/whostmgr/docroot/cgi/rblcheck");

# Obtain the plugin from Github
system( "curl -o /root/rblcheck.tar.gz https://github.com/cPanelPeter/rblcheck/blob/master/whmplugin/rblcheck.tar.gz" );

# Extract the tarball
system( "tar xvzf rblcheck.tar.gz" );

# Copy the rblcheck.jpg (Icon) image file to /usr/local/cpanel/whostmgr/docroot/addon_plugins
system( "cp -fv /root/rblcheck/rblcheck.jpg /usr/local/cpanel/whostmgr/docroot/addon_plugins" );

# Copy the rblcheck.cgi file to /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck
system( "cp -fv /root/rblcheck/rblcheck.cgi /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck" );

# Register the plugin
system( "/usr/local/cpanel/bin/register_appconfig /root/rblcheck/rblcheck.conf" );

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
