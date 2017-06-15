#!/usr/local/cpanel/3rdparty/bin/perl
# SCRIPT: rblcheck
# AUTHOR: Peter Elsner <peter.elsner@cpanel.net>
# PURPOSE: Check an IP address against various RBL's (Realtime Blackhole Lists)
# CREATED 8/9/2015
#

BEGIN {
    unshift @INC, '/usr/local/cpanel';
    unshift @INC, '/usr/local/cpanel/scripts';
    unshift @INC, '/usr/local/cpanel/bin';
    unshift @INC, '/usr/local/share/perl5';
}

use strict;
use warnings;
use Geo::IP::PurePerl;
use Net::IP;
use Data::Validate::IP qw(is_ip);
use Socket;
use Cpanel::Config::LoadWwwAcctConf ();
use CGI qw(:standard);
$| = 1;
use lib '/usr/local/cpanel/';
use Cpanel::Template;
use Whostmgr::HTMLInterface ();
Whostmgr::HTMLInterface::defheader('RBL Check');

my $version = "1.0.14";
my @RBLS = qx[ curl -s https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/rbllist.txt ];
my @SHORTRBLS = qx[ curl -s https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/shortlist.txt ];
my $totrbls=@RBLS;
my $ENTEREDIP;
my $TXT;
my $NUMLISTED=0;
my $LOOKUPHOST;

# Check for NAT configuration
my $HASNAT=0;
$HASNAT=&check_for_nat();

# Get servers_mainip for /etc/wwwacct.conf file.
my $wwwacct = Cpanel::Config::LoadWwwAcctConf::loadwwwacctconf();
my $servers_mainip = $wwwacct->{'ADDR'};
my $cpnatline;
my $PrivateIP;
my $PublicIP;
my @IPALIASES;
my @NEWALIASES;
my $IPALIAS;

if ($HASNAT) {
   open(CPNAT,"/var/cpanel/cpnat");
   my @CPNATDATA=<CPNAT>;
   close(CPNAT);
   foreach $cpnatline(@CPNATDATA) {
      chomp($cpnatline);
      ($PrivateIP,$PublicIP)=(split(/\s+/,$cpnatline));
      if ($PrivateIP eq $servers_mainip) {
         $servers_mainip=$PublicIP;
         next;
      }
      push(@IPALIASES,$PublicIP);
   }
}
else {
   open(IPS,"/etc/ips");
   my @EXTRAIPS=<IPS>;
   close(IPS);
   my $extraIP;
   foreach $extraIP (@EXTRAIPS) {
      ($PublicIP)=(split(/:/,$extraIP))[0];
      push(@IPALIASES,$PublicIP);
   }
}

my ($country_code,$country_code3,$country_name,$region,$city,$postal_code,$latitude,$longitude)="";

foreach $IPALIAS(@IPALIASES) { 
	chomp($IPALIAS);
	push(@NEWALIASES, "<li>$IPALIAS</li>\n");
}

my $aliascnt=@NEWALIASES;

my $enteredipaddr = param('ipaddr');
my @SelectedRBLs = multi_param('selectedItems');
my $totselected=@SelectedRBLs;
my $multiline;
if ($enteredipaddr) { 
	# Get GEO IP data for $servers_mainip
	my $gi = Geo::IP::PurePerl->new("/usr/local/share/GeoIP/GeoLiteCity.dat", GEOIP_STANDARD);
	($country_code,$country_code3,$country_name,$region,$city,$postal_code,$latitude,$longitude) = $gi->get_city_record($enteredipaddr);
	print "Checking $enteredipaddr...<br>\n";
	if ($country_name) { 
		print "Country: $country_name ( $country_code / $country_code3 )<br>\n";
		print "Region: $region / City: $city / Postal Code: $postal_code<br>\n";
		print "Latitude: $latitude / Longitude: $longitude<br>\n";
	}
	print "<hr>\n";
	&checkit($enteredipaddr);
	if ($NUMLISTED == 0) { 
		print "<p>Congratulations! - $ENTEREDIP is not currently listed in the $totselected RBL's checked!\n";
		print "<p><a href=\"rblcheck.cgi\">Return</a>\n";
	}
	else { 
		print <<END;
<p>
Please note that neither your provider or datacenter or cPanel, Inc. have any control over<br>
the blacklists.  Each RBL provider has their own criteria for listing an IP address.<br>
You will need to contact each RBL provider where your IP is listed and check with them on what<br>
their removal process is.<p>  
Don't just request to have your IP delisted without fixing the problem.  If you do that, <br>
you will most likely just get listed again and next time it will be much more difficult to get<br>
removed.  Make sure that your network and mail server are properly configured and that your <br>
workstations/servers are free from viruses and other malware.  
<p>
Follow the steps outlined in the RBL removal process. Once you have solved the problem that <br>
got you listed, go back and attempt removal. Many of them have a self-service removal process.
<br>Most of these RBL providers are professional and their goal is to have a cleaner, faster<br> 
and better Internet experience for everyone. 

<P>
<a href="rblcheck.cgi">Return</a>

</body>
</html>

END
	}
}
else { 
	print <<END;

<!DOCTYPE html>
<html>
	<head>
	<script type="text/javascript"> 

	function addItems() {
    	var ai = document.getElementById("availableItems");
    	var si = document.getElementById("selectedItems");
    	for (i=0;i<ai.options.length;i++) {
      		if (ai.options[i].selected) {
        		var opt = ai.options[i];
        		si.options[si.options.length] = new Option(opt.innerHTML, opt.value);
        		ai.options[i] = null; i = i - 1;
      		}
    	}
  	}

	function addAll() { 
    	var ai = document.getElementById("availableItems"); 
    	var si = document.getElementById("selectedItems"); 
    	for (i=0;i<ai.options.length;i++) { 
			var opt = ai.options[i]; 
			si.options[si.options.length] = new Option(opt.innerHTML, opt.value); 
		} 
		ai.options.length = 0; 
	} 

  function removeItems() {
    var ai = document.getElementById("availableItems"); 
    var si = document.getElementById("selectedItems"); 
    for (i=0;i<si.options.length;i++) { 
      if (si.options[i].selected) { 
        var opt = si.options[i]; 
        ai.options[ai.options.length] = new Option(opt.innerHTML, opt.value); 
        si.options[i] = null; i = i - 1; 
      } 
    } 
    sortAvailable(); 
  } 

  function removeAll() { 
    var ai = document.getElementById("availableItems"); 
    var si = document.getElementById("selectedItems"); 
    for (i=0;i<si.options.length;i++) { 
      var opt = si.options[i]; 
      ai.options[ai.options.length] = new Option(opt.innerHTML, opt.value); 
    } 
    si.options.length = 0; 
    sortAvailable(); 
  } 

  function sortAvailable() { 
    var ai = document.getElementById("availableItems"); 
    var tmp = ""; 
    for (i=0;i<ai.options.length;i++) { 
      if (tmp > "") tmp +=","; 
      tmp += ai.options[i].innerHTML + "~" + ai.options[i].value; 
    } 
    var atmp = tmp.split(",") atmp = atmp.sort(); 
    ai.options.length = 0;
    for (i=0;i<atmp.length;i++) { 
      var opt = atmp[i].split("~"); 
      ai.options[i] = new Option(opt[0],opt[1]); 
    } 
  } 

	function frmSubmit() {
		var si = document.getElementById("selectedItems"); 
		for (i=0;i<si.options.length;i++) { 
			si.options[i].selected = true; 
		} 
		document.form1.submit(); 
	} 
  </script> 

  <style type="text/css"> 
    .btn {width:90px;} 
  </style>
	<title>RBL Check</title>
	</head>
	<body>
	RBL Check (version $version)...<p>
   Q: What is an RBL?<p>
   A: RBL stands for Realtime Blackhole List. These are spam blocking lists that allow a <br>
   system administrator to block email from being sent out that have a history of sending spam<br>
   or are infected with something that is doing the spamming.  Once your IP Address is on an <br>
   RBL, any other server that subscribes to that RBL will refuse email from your server. <p>
   Check your servers IP's now (or any IP) to see if it is listed. 
   <p>
	Select the RBL's to use below. A minimum set has already been added for your convenience.<p>
	<form name="form1" id="form1" action="rblcheck.cgi">
	<div style="width:130px;float:left;"> 
	<select size="10" multiple name="availableItems" id="availableItems" style="width:120px;"> 
END
	my $rblavail;
	foreach $rblavail(@RBLS) { 
		chomp($rblavail);
		print "<option value=\"$rblavail\">$rblavail</option><br>\n";
	}
	print <<END;
	</select>
	</div>
	<div style="width:100px;float:left;"> 
	<script type="text/javascript"> 

	function frmSubmit() {
		var si = document.getElementById("selectedItems"); 
		for (i=0;i<si.options.length;i++) { 
			si.options[i].selected = true; 
		} 
		document.form1.submit(); 
	} 

	function addItems() {
    	var ai = document.getElementById("availableItems");
    	var si = document.getElementById("selectedItems");
    	for (i=0;i<ai.options.length;i++) {
      		if (ai.options[i].selected) {
        		var opt = ai.options[i];
        		si.options[si.options.length] = new Option(opt.innerHTML, opt.value);
        		ai.options[i] = null; i = i - 1;
      		}
    	}
  	}
	function addAll() { 
    	var ai = document.getElementById("availableItems"); 
    	var si = document.getElementById("selectedItems"); 
    	for (i=0;i<ai.options.length;i++) { 
			var opt = ai.options[i]; 
			si.options[si.options.length] = new Option(opt.innerHTML, opt.value); 
		} 
		ai.options.length = 0; 
	} 
  function removeItems() {
    var ai = document.getElementById("availableItems"); 
    var si = document.getElementById("selectedItems"); 
    for (i=0;i<si.options.length;i++) { 
      if (si.options[i].selected) { 
        var opt = si.options[i]; 
        ai.options[ai.options.length] = new Option(opt.innerHTML, opt.value); 
        si.options[i] = null; i = i - 1; 
      } 
    } 
    sortAvailable(); 
  } 
  function removeAll() { 
    var ai = document.getElementById("availableItems"); 
    var si = document.getElementById("selectedItems"); 
    for (i=0;i<si.options.length;i++) { 
      var opt = si.options[i]; 
      ai.options[ai.options.length] = new Option(opt.innerHTML, opt.value); 
    } 
    si.options.length = 0; 
    sortAvailable(); 
  } 
	</script>
	<input type="button" class="btn" value="Add" onclick="addItems();" /> 
	<input type="button" class="btn" value="Add All" onclick="addAll();" /> 
	<input type="button" class="btn" value="Remove" onclick="removeItems();" /> 
	<input type="button" class="btn" value="Remove All" onclick="removeAll();" /> 
	</div> 
	<div style="width:130px;float:left"> 
	<select size="10" multiple name="selectedItems" id="selectedItems" style="width:120px;"> 
END
	my $rblshort;
	foreach $rblshort(@SHORTRBLS) { 
		chomp($rblshort);
		print "<option value=\"$rblshort\">$rblshort</option><br>\n";
	}
	print <<END;
	</select> 
	</div> 
	<p>
	The servers main ip is: $servers_mainip 
END
	if ($aliascnt > 0) { 
		print "<p>These are the additional IP's (aliases): <p>\n";
	}
	print <<END;
	<ul>
	@NEWALIASES
	</ul>
	<p>
	<div>IP Address to check: <input name="ipaddr" size="20" value="$servers_mainip">
	<input type="submit" value=" Check " onclick="frmSubmit();"></div>
	</form>
END
}

# RETURN TO MAIN MENU
Whostmgr::HTMLInterface::deffooter();
exit;

sub checkit() { 
	$ENTEREDIP=$_[0];
	my $LOOKUPHOST;
	my $IS_IP_VALID = is_ip($ENTEREDIP);
	if (!($IS_IP_VALID)) { 
		print "FATAL - invalid entry \"$ENTEREDIP\"\n";
		print "<p><a href=\"rblcheck.cgi\">Return</a>\n";
		exit;
	}
	if ( $ENTEREDIP =~ /:/ and $ENTEREDIP !~ /\./ ) {
		my $EXPANDEDIP = new Net::IP ( $ENTEREDIP );
		$LOOKUPHOST = join '.', reverse ( split '', $EXPANDEDIP->ip() );
		$LOOKUPHOST =~ s/\.:\././g;
	} 
	elsif ( $ENTEREDIP =~ /\./ and $ENTEREDIP !~ /:/ ) {
		$LOOKUPHOST = join '.', reverse ( split /\./, $ENTEREDIP );
	} 
	foreach my $BLACKLIST (@SelectedRBLs) {
		print $BLACKLIST . ": ";
		my $lookup = "$LOOKUPHOST.$BLACKLIST";
		my $RESULT = gethostbyname ( $lookup );
		if ( ! defined $RESULT ) { 
			print "<font color=\"GREEN\">[OK]</font><BR>\n";
		}
		else { 
			$RESULT = inet_ntoa ( $RESULT );
			$TXT = qx[ dig $lookup TXT +short ];
			chomp($TXT);
			print "<font color=\"RED\">[LISTED]</font> ($RESULT)<BR>\n";
            if ($TXT) { 
               print "<font color=\"BLUE\">Reason: $TXT</font><BR>\n";
			}
			$NUMLISTED++;
		}
	}
	print "<p>\n";
	print "Checked $totrbls Realtime Blackhole Lists (RBL's) & found $ENTEREDIP listed in $NUMLISTED of them.\n";
}

sub check_for_nat() {
   return if (!(-e("/var/cpanel/cpnat")));
   return 1;
}

