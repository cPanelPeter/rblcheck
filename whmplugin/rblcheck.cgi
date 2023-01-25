#!/usr/local/cpanel/3rdparty/bin/perl
# SCRIPT: rblcheck
# AUTHOR: Peter Elsner <peter.elsner@cpanel.net>
# PURPOSE: Check an IP address against various RBL's (Realtime Blackhole Lists)
# CREATED 8/9/2015
#

#BEGIN { unshift @INC, '/usr/local/share/perl5'}
#BEGIN { unshift @INC, '/usr/local/cpanel' }

use strict;
use warnings;
use Cpanel::GeoIPfree ();
use Net::DNS;
use Net::IP;
use Time::Piece;
use Time::Seconds;
use Data::Validate::IP qw(is_ip);
use Socket;
use Cpanel::Config::LoadWwwAcctConf ();
use Cpanel::SafeRun::Timed          ();
use constant { PLUGIN_PATH => '/cgi/rblcheck' };
use Term::ANSIColor qw(:constants);
$Term::ANSIColor::AUTORESET = 1;
use CGI qw(:standard);
$| = 1;
use lib '/usr/local/cpanel/';
use Cpanel::Template;
use Whostmgr::HTMLInterface ();
print "Content-type: text/html\r\n\r\n";

Cpanel::Template::process_template('whostmgr', {
    'print' => 1,
    'template_file' => '_defheader.tmpl',
    'theme' => "yui",
    'skipheader' => 0,
    'breadcrumbdata' => {
        'name' => 'RBL Check',
        'url' => PLUGIN_PATH . '/rblcheck.cgi',
        'previous' => [{
                'name' => 'Home',
                'url' => "/scripts/command?PFILE=main",
            }, {
                'name' => "Plugins",
                'url' => "/scripts/command?PFILE=Plugins",
        }],
    },
});

my $version = "1.0.15";
my $RBLS = Cpanel::SafeRun::Timed::timedsaferun( 6, 'curl', '-s', 'https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/rbllist.txt' );
my @RBLS = split /\n/, $RBLS;
my $SHORTRBLS = Cpanel::SafeRun::Timed::timedsaferun( 6, 'curl', '-s', 'https://raw.githubusercontent.com/cPanelPeter/rblcheck/master/shortlist.txt' );
my @SHORTRBLS = split /\n/, $SHORTRBLS;
my $totrbls=@RBLS;
my $ENTEREDIP;
my $TXT;
my $NUMLISTED=0;
my $NUMTIMEDOUT=0;
my $LOOKUPHOST;

# Get servers_mainip for /etc/wwwacct.conf file.
my $wwwacct = Cpanel::Config::LoadWwwAcctConf::loadwwwacctconf();
my $servers_mainip = $wwwacct->{'ADDR'};
my $cpnatline;
my $PrivateIP;
my $PublicIP;
my @IPALIASES;
#my @NEWALIASES;
my @server_ips;
my $IPALIAS;

my $ListIPsJSON = get_whmapi1('listips');
my $main_ip_address;
for my $ListOfIPs ( @{ $ListIPsJSON->{data}->{ip} } ) {
    if ( $ListOfIPs->{mainaddr} ) {
		$main_ip_address = $ListOfIPs->{public_ip};
	}
	push @server_ips, $ListOfIPs->{public_ip};
}

my ($country_code,$country_name)="";
my $aliascnt=@server_ips;

my $enteredipaddr = param('ipaddr');
my $onlylisted = param('onlylisted');
my @SelectedRBLs = multi_param('selectedItems');
my $totselected=@SelectedRBLs;
my $multiline;
if ($enteredipaddr) { 
    # Get Country via GEO IP free database for $servers_mainip
    my $geo = Cpanel::GeoIPfree->new();
    ($country_code,$country_name) = $geo->LookUp($enteredipaddr);
    print "Checking $enteredipaddr...<br>\n";
    if ($country_name) { 
        print "Country: $country_name ( $country_code )<br>\n";
    }
    print "<hr>\n";
    my $starttime = Time::Piece->new;
	print "Started: $starttime<br>\n";
	print "<hr>\n";
    checkit($enteredipaddr, $onlylisted);
    my $endtime = Time::Piece->new;
	print "<br>Completed: $endtime<br>\n";
    my $timediff = ( $endtime - $starttime );

    my $TotTime  = $timediff->pretty;
    $TotTime = $TotTime . "\n";
	print "Elapsed Time: $TotTime<br>\n";

    if ($NUMLISTED == 0) { 
        print "<p>Congratulations! - $ENTEREDIP is not currently listed in the $totselected RBL's checked!\n";
        print "<p><a href=\"rblcheck.cgi\">Return</a>\n";
    }
    else { 
        print <<END;
<p>
Please note that neither your provider or datacenter or cPanel, Inc. have any control over the blacklists.  Each RBL provider has their own criteria for listing an IP address.  You will need to contact each RBL provider where your IP is listed and check with them on what their removal process is.<p>  
Don't just request to have your IP delisted without fixing the problem.  If you do that, you will most likely just get listed again and next time it will be much more difficult to get removed.  Make sure that your network and mail server are properly configured and that your workstations/servers are free from viruses and other malware.  
<p>
Follow the steps outlined in the RBL removal process. Once you have solved the problem that got you listed, go back and attempt removal. Many of them have a self-service removal process.  Most of these RBL providers are professional and their goal is to have a cleaner, faster and better Internet experience for everyone. 
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
   A: RBL stands for Realtime Blackhole List. These are spam blocking lists that allow a system administrator to block email from being sent out that have a history of sending spam or are infected with something that is doing the spamming.  Once your IP Address is on an RBL, any other server that subscribes to that RBL will refuse email from your server. 
   <p>
   Check your servers IP's now (or any IP) to see if it is listed. 
   <p>
    Select the RBL's to use below. A minimum set has already been added for your convenience.
   <p>
    <form name="form1" id="form1" action="rblcheck.cgi">
    <div style="width:210px;float:left;"> 
    <select size="10" multiple name="availableItems" id="availableItems" style="width:200px;"> 
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
    <select size="10" multiple name="selectedItems" id="selectedItems" style="width:200px;">
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
	&nbsp;
	<p>
	&nbsp;
	<p>
	&nbsp;
	<p>
	&nbsp;
	<p>
	&nbsp;
	<p>
	&nbsp;
    <div>
    <input type="checkbox" name="onlylisted" value="1" > Show only when listed in an RBL<p>
    </div>
    <div>
END
    if ($aliascnt > 0) { 
        print "<p>Here are the $aliascnt IP's on this server: <p>\n";
		print "<SELECT name=\"selectedIP\" id=\"selectedIP\" size=10 style=\"width:200px;\" ondblclick=\"showSelected()\">";
		foreach my $ip (@server_ips) {
			chomp($ip);
			if ( $ip eq $servers_mainip ) {
				print "<option selected value=\"$ip\">$ip (main shared IP)</option>";
			}
			else {
				print "<option value=\"$ip\">$ip (dedicated)</option>";
			}
		}
		print "</select>\n";
    }
    print <<END;
	<script>
	function showSelected(){
    	var s=document.getElementById('selectedIP');          //refers to that select with all options
    	var selectText=s.options[s.selectedIndex].value   // takes the one which the user will select
		document.getElementById('field2').value = selectText;
	}
	</script>
	<p>
	Select an IP address above or enter an IP address NOT on this server: <input type="text" id="field2" name="ipaddr" size="20" value="">
    <input type="submit" value=" Check " onclick="frmSubmit();">
    </div>
    </form>
END
}

# RETURN TO MAIN MENU
Whostmgr::HTMLInterface::deffooter();
exit;

sub checkit {
    $ENTEREDIP=shift;
    my $LISTEDONLY=shift;
    my $LOOKUPHOST;
    my $EXPANDEDIP = new Net::IP ( $ENTEREDIP );
    if ( $ENTEREDIP =~ /:/ and $ENTEREDIP !~ /\./ ) {
        $LOOKUPHOST = join '.', reverse ( split '', $EXPANDEDIP->ip() );
        $LOOKUPHOST =~ s/\.:\././g;
    }
    elsif ( $ENTEREDIP =~ /\./ and $ENTEREDIP !~ /:/ ) {
        $LOOKUPHOST = join '.', reverse ( split /\./, $ENTEREDIP );
    }
    foreach my $BLACKLIST (@SelectedRBLs) {
		chomp($BLACKLIST);
        print $BLACKLIST . ": " unless( $LISTEDONLY );
        my $lookup = "$LOOKUPHOST.$BLACKLIST";
		my $RESULT;
		eval {
    		local $SIG{ALRM} = sub { die "alarm\n" }; # NB: \n required
    		alarm 3;
    		$RESULT = gethostbyname( $lookup );
    		alarm 0;
		};

		if ( $@ ) {
			print "<font color=\"CYAN\">[TIMED OUT]</font><BR>\n";
			$NUMTIMEDOUT++;
			next;
		}
		if ( ! defined $RESULT ) {
			print "<font color=\"GREEN\">[OK]</font><BR>\n" unless( $LISTEDONLY );
		}
		else {
			my $A=Cpanel::SafeRun::Timed::timedsaferun( 3, 'dig', $lookup, 'A', '+short' );
			print "<font color=\"RED\">[ LISTED - RESULT: $A ]</font>\n";
			my $TXT=Cpanel::SafeRun::Timed::timedsaferun( 3, 'dig', $lookup, 'TXT', '+short' );
			print "<font color=\"BLUE\"> - Additional Information: <font color=\"YELLOW\">$TXT</font><br>\n" if ( $TXT );
			$NUMLISTED++;
		}
    }
    print "<p>\n";
    print "<hr>\n";
    print "Checked $totrbls Realtime Blackhole Lists (RBL's).<BR>\n";
	print "$ENTEREDIP is listed in $NUMLISTED Real-Time Blackhole Lists<br>\n";
	print "$NUMTIMEDOUT Real-Time Blackhole Lists timed out.<br>\n";
}

sub get_json_from_command {
    my @cmd = @_;
    return Cpanel::JSON::Load(
        Cpanel::SafeRun::Timed::timedsaferun( 30, @cmd ) );
}

sub get_whmapi1 {
    return get_json_from_command( 'whmapi1', '--output=json', @_ );
}
