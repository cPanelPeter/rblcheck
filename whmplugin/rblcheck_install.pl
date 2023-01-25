#!/usr/local/cpanel/3rdparty/bin/perl

use Net::IP;
use IO::Uncompress::Gunzip qw(gunzip $GunzipError);
use File::Copy;
use Archive::Tar;
use Cpanel::SafeRun::Timed ();
use Cpanel::SafeRun::Errors();
use Term::ANSIColor qw(:constants);
$Term::ANSIColor::AUTORESET = 1;

system("clear");
print GREEN "Installing the RBLCheck WHM Plugin...\n";

# Create the directory for the plugin
print YELLOW "Creating /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck directory... ";
mkdir "/usr/local/cpanel/whostmgr/docroot/cgi/rblcheck";
print CYAN " - Done\n";

# Obtain the plugin from Github
print YELLOW "Downloading whmrblcheck.tar.gz... ";
Cpanel::SafeRun::Timed::timedsaferun( 4, 'wget', '-O', '/root/whmrblcheck.tar.gz', '-o', '/dev/null', "https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/whmplugin/whmrblcheck.tar.gz" );
print CYAN " - Done\n";

# Uncompress whmrblcheck.tar.gz
print YELLOW "Extracting whmrblcheck.tar.gz... ";
my $tar = Archive::Tar->new;
$tar->read("/root/whmrblcheck.tar.gz");
$tar->extract();
print CYAN " - Done\n";

# Copy the rblcheck.jpg (Icon) image file to /usr/local/cpanel/whostmgr/docroot/addon_plugins
print YELLOW "Copying rblcheck.jpg to /usr/local/cpanel/whostmgr/docroot/addon_plugins... ";
copy("/root/rblcheck.jpg","/usr/local/cpanel/whostmgr/docroot/addon_plugins") or die "Copy failed: $!";
print CYAN " - Done\n";

# Copy the rblcheck.cgi file to /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck
print YELLOW "Copying rblcheck.cgi to /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck... ";
copy("/root/rblcheck.cgi","/usr/local/cpanel/whostmgr/docroot/cgi/rblcheck") or die "Copy failed: $!";
print CYAN " - Done\n";

# Set execute permissions on the rblcheck.cgi script
print YELLOW "Setting permissions on /usr/local/cpanel/whostmgr/docroot/cgi/rblcheck/rblcheck.cgi to 0755...";
chmod 0755, "/usr/local/cpanel/whostmgr/docroot/cgi/rblcheck/rblcheck.cgi";
print CYAN " - Done\n";

# Register the plugin
print YELLOW "Registering plugin...";
system( "/usr/local/cpanel/bin/register_appconfig /root/rblcheck.conf" );

print GREEN "\nRBL Check WHM Plugin installed!\n";
exit;
