#!/usr/bin/perl
system("clear");
print "Installing the RBLCheck WHM Plugin...\n";

# Check for and install if missing any required Perl modules from CPAN.
&module_sanity_check;
use IO::Uncompress::Gunzip qw(gunzip $GunzipError);

# Create the directory for the plugin
print "Creating /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck directory... ";
mkdir "/usr/local/cpanel/whostmgr/docroot/cgi/rblcheck";
print " - Done\n";

# Obtain the plugin from Github
my $http = HTTP::Tiny->new();
print "Downloading rblcheck.cgi... ";
$http->mirror( 'https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/whmplugin/rblcheck.cgi', '/root/rblcheck.cgi' );
print " - Done\n";
print "Downloading rblcheck.jpg... ";
$http->mirror( 'https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/whmplugin/rblcheck.jpg', '/root/rblcheck.jpg' );
print " - Done\n";
print "Downloading rblcheck.conf... ";
$http->mirror( 'https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/whmplugin/rblcheck.conf', '/root/rblcheck.conf' );
print " - Done\n";

# Copy the rblcheck.jpg (Icon) image file to /usr/local/cpanel/whostmgr/docroot/addon_plugins
print "Copying rblcheck.jpg to /usr/local/cpanel/whostmgr/docroot/addon_plugins... ";
copy("/root/rblcheck.jpg","/usr/local/cpanel/whostmgr/docroot/addon_plugins") or die "Copy failed: $!";
print " - Done\n";

# Copy the rblcheck.cgi file to /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck
print "Copying rblcheck.cgi to /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck... ";
copy("/root/rblcheck.cgi","/usr/local/cpanel/whostmgr/docroot/cgi/rblcheck") or die "Copy failed: $!";
print " - Done\n";

# Set execute permissions on the rblcheck.cgi script
print "Setting permissions on /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck/rblcheck.cgi to 0755...";
chmod 0755, "/usr/local/cpanel/whostmgr/docroot/cgi/rblcheck/rblcheck.cgi";
print " - Done\n";

# Download the GeoLiteCity.dat file to /usr/local/share/GeoIP and gunzip it.
print "Creating directory /usr/local/share/GeoIP... ";
mkdir "/usr/local/share/GeoIP";
print " - Done\n";
print "Downloading GeoLiteCity.dat.gz... ";
$http->mirror( 'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz', '/usr/local/share/GeoIP/GeoLiteCity.dat.gz' );
print " - Done\n";
print "Uncompressing GeoLiteCity.dat.gz...";
my $input="/usr/local/share/GeoIP/GeoLiteCity.dat.gz";
my $output="/usr/local/share/GeoIP/GeoLiteCity.dat";
gunzip $input => $output or die "gunzip failed: $GunzipError\n";
print " - Done\n";

# Register the plugin
print "Registering plugin...";
system( "/usr/local/cpanel/bin/register_appconfig /root/rblcheck.conf" );
print " - Done\n";

print "\nRBL Check WHM Plugin installed!\n";
exit;

# sub routines
sub module_sanity_check {
   @modules_to_install = qw( Net::IP Geo::IP::PurePerl IO::Uncompress::Gunzip File::Copy HTTP::Tiny IO::Socket::SSL );
   foreach $module(@modules_to_install) {
      chomp($module);
      eval("use $module;");
      if ($@) {
         print "WARNING: Perl Module $module not installed!\n";
         print "Installing now - Please stand by.\n";
         system( "/usr/local/cpanel/bin/cpanm --force $module 2>&1" );
      }
   }
   return;
}
