#!/usr/bin/perl
# SCRIPT: rblcheck
# AUTHOR: Peter Elsner <peter.elsner@cpanel.net>
# PURPOSE: Check an IP address against various RBL's (Realtime Blackhole Lists)
# CREATED 8/9/2015
#

use strict;
use Geo::IP::PurePerl;
use Net::IP;
use Socket;
use CGI qw(:standard);
$| = 1;

my $version = "1.0.07";
my @RBLS = qw( 
   0spam.fusionzero.com
   0spam-killlist.fusionzero.com
   0spamurl.fusionzero.com
   88.blocklist.zap
   abuse.rfc-clueless.org
   access.redhawk.org
   admin.bl.kundenserver.de
   all.rbl.jp
   all.s5h.net
   all.spamrats.com
   aspews.ext.sorbs.net
   backscatter.spameatingmonkey.net
   badconf.rhsbl.sorbs.net
   badhost.stopspam.org
   badnets.spameatingmonkey.net
   b.barracudacentral.org
   bb.barracudacentral.org
   blacklist.mail.ops.asp.att.net
   blacklist.mailrelay.att.net
   blacklist.netcore.co.in
   blacklist.sci.kun.nl
   blacklist.sequoia.ops.asp.att.net
   blacklist.woody.ch
   bl.blocklist.de
   bl.drmx.org
   bl.emailbasura.org
   bl.ipv6.spameatingmonkey.net
   bl.konstant.no
   bl.mailspike.net
   bl.mav.com.br
   bl.mipspace.com
   bl.nszones.com
   block.dnsbl.sorbs.net
   block.stopspam.org
   bl.scientificspam.net
   bl.score.senderscore.com
   bl.spamcannibal.org
   bl.spamcop.net
   bl.spameatingmonkey.net
   bl.spamstinks.com
   bl.suomispam.net
   bl.tiopan.com
   bogons.cymru.com
   bogusmx.rfc-clueless.org
   bsb.empty.us
   bsb.spamlookup.net
   cbl.abuseat.org
   cbl.anti-spam.org.cn
   cblless.anti-spam.org.cn
   cblplus.anti-spam.org.cn
   cdl.anti-spam.org.cn
   cidr.bl.mcafee.com
   combined.rbl.msrbl.net
   dbl.tiopan.com
   db.wpbl.info
   dnsbl-0.uceprotect.net
   dnsbl1.dnsbl.borderware.com
   dnsbl-1.uceprotect.net
   dnsbl2.dnsbl.borderware.com
   dnsbl-2.uceprotect.net
   dnsbl3.dnsbl.borderware.com
   dnsbl-3.uceprotect.net
   dnsbl6.anticaptcha.net
   dnsbl.anticaptcha.net
   dnsbl.aspnet.hu
   dnsbl.burnt-tech.com
   dnsblchile.org
   dnsbl.cobion.com
   dnsbl.cyberlogic.net
   dnsbl.dronebl.org
   dnsbl.forefront.microsoft.com
   dnsbl.inps.de
   dnsbl.justspam.org
   dnsbl.kempt.net
   dnsbl.madavi.de
   dnsbl.mcu.edu.tw
   dnsbl.net.ua
   dnsbl.openresolvers.org
   dnsbl.othello.ch
   dnsbl.proxybl.org
   dnsbl.rizon.net
   dnsbl.rv-soft.info
   dnsbl.rymsho.ru
   dnsbl.sorbs.net
   dnsbl.spam-champuru.livedoor.com
   dnsbl.stopspam.org
   dnsbl.tornevall.org
   dnsbl.webequipped.com
   dnsbl.zapbl.net
   dnsrbl.org
   dnsrbl.swinog.ch
   dob.sibl.support-intelligence.net
   dsn.rfc-clueless.org
   dul.blackhole.cantv.net
   dul.dnsbl.borderware.com
   dul.dnsbl.sorbs.net
   dul.pacifier.net
   dunk.dnsbl.tuxad.de
   dyna.spamrats.com
   dyndns.rbl.jp
   dynip.rothen.com
   dyn.nszones.com
   elitist.rfc-clueless.org
   escalations.dnsbl.sorbs.net
   ex.dnsbl.org
   exitnodes.tor.dnsbl.sectoor.de
   feb.spamlab.com
   fnrbl.fast.net
   forbidden.icm.edu.pl
   free.v4bl.org
   fresh10.spameatingmonkey.net
   fresh15.spameatingmonkey.net
   fresh.spameatingmonkey.net
   fulldom.rfc-clueless.org
   gl.suomispam.net
   hartkore.dnsbl.tuxad.de
   hil.habeas.com
   hog.blackhole.cantv.net
   http.dnsbl.sorbs.net
   images.rbl.msrbl.net
   in.dnsbl.org
   ipbl.zeustracker.abuse.ch
   ips.backscatterer.org
   ip.v4bl.org
   ipv6.blacklist.woody.ch
   ipv6.rbl.choon.net
   ix.dnsbl.manitu.net
   korea.services.net
   l1.apews.org
   l1.bbfh.ext.sorbs.net
   l2.apews.org
   l2.bbfh.ext.sorbs.net
   l3.bbfh.ext.sorbs.net
   l4.bbfh.ext.sorbs.net
   list.bbfh.org
   list.blogspambl.com
   lookup.dnsbl.iip.lu
   mail-abuse.blacklist.jippg.org
   misc.dnsbl.sorbs.net
   multi.surbl.org
   netblockbl.spamgrouper.to
   netbl.spameatingmonkey.net
   netscan.rbl.blockedservers.com
   new.spam.dnsbl.sorbs.net
   nomail.rhsbl.sorbs.net
   no-more-funn.moensted.dk
   noptr.spamrats.com
   old.spam.dnsbl.sorbs.net
   orvedb.aupads.org
   pbl.spamhaus.org
   phishing.rbl.msrbl.net
   pofon.foobar.hu
   postmaster.rfc-clueless.org
   problems.dnsbl.sorbs.net
   proxies.dnsbl.sorbs.net
   psbl.surriel.com
   public.sarbl.org
   q.mail-abuse.com
   query.senderbase.org
   rbl2.triumf.ca
   rbl.abuse.ro
   rbl.blakjak.net
   rbl.blockedservers.com
   rbl.choon.net
   rbl.dns-servicios.com
   rbl.efnet.org
   rbl.efnetrbl.org
   rbl.fasthosts.co.uk
   rbl.interserver.net
   rbl.iprange.net
   rbl.lugh.ch
   rbl.megarbl.net
   rbl.rbldns.ru
   rbl.schulte.org
   rbl.spamlab.com
   rbl.talkactive.net
   rbl.tdk.net
   rbl.zenon.net
   recent.spam.dnsbl.sorbs.net
   relays.bl.kundenserver.de
   relays.dnsbl.sorbs.net
   relays.nether.net
   rhsbl.blackhole.cantv.net
   rhsbl.rymsho.ru
   rhsbl.scientificspam.net
   rhsbl.sorbs.net
   rhsbl.zapbl.net
   r.mail-abuse.com
   rot.blackhole.cantv.net
   rsbl.aupads.org
   safe.dnsbl.prs.proofpoint.com
   safe.dnsbl.sorbs.net
   sbl.nszones.com
   sbl.spamhaus.org
   sbl-xbl.spamhaus.org
   schizo-bl.kundenserver.de
   service.mailblacklist.com
   short.rbl.jp
   singlebl.spamgrouper.com
   singular.ttk.pte.hu
   smtp.dnsbl.sorbs.net
   socks.dnsbl.sorbs.net
   spam.blackhole.cantv.net
   spamblock.kundenserver.de
   spam.dnsbl.anonmails.de
   spam.dnsbl.sorbs.net
   spamguard.leadmon.net
   spamlist.or.kr
   spam.pedantic.org
   spam.rbl.blockedservers.com
   Spam-RBL.fr
   spamrbl.imp.ch
   spam.rbl.msrbl.net
   spamsources.fabel.dk
   spam.spamrats.com
   st.technovision.dk
   tor.dnsbl.sectoor.de
   tor.efnet.org
   torexit.dan.me.uk
   truncate.gbudb.net
   ubl.nszones.com
   ubl.unsubscore.com
   unsure.nether.net
   uribl.abuse.ro
   uri.blacklist.woody.ch
   uribl.pofon.foobar.hu
   uribl.spameatingmonkey.net
   uribl.swinog.ch
   uribl.zeustracker.abuse.ch
   urired.spameatingmonkey.net
   url.rbl.jp
   v4.fullbogons.cymru.com
   v6.fullbogons.cymru.com
   virbl.dnsbl.bit.nl
   virus.rbl.jp
   virus.rbl.msrbl.net
   vote.drbl.caravan.ru
   vote.drbldf.dsbl.ru
   vote.drbl.gremlin.ru
   web.dnsbl.sorbs.net
   web.rbl.msrbl.net
   whois.rfc-clueless.org
   work.drbl.caravan.ru
   work.drbldf.dsbl.ru
   work.drbl.gremlin.ru
   wormrbl.imp.ch
   worms-bl.kundenserver.de
   xbl.spamhaus.org
   zen.spamhaus.org
   z.mailspike.net
   zombie.dnsbl.sorbs.net
   zz.countries.nerd.dk
);

my $totrbls=@RBLS;
my $ENTEREDIP;
my $TXT;

# Check for NAT configuration
my $HASNAT=0;
$HASNAT=&check_for_nat();

# Get mainip 
open(MAINIP,"/var/cpanel/mainip");
my $mainip = <MAINIP>;
close(MAINIP);

if ($HASNAT) { 
	$mainip=&replace_mainIP($mainip);
}

my ($country_code,$country_code3,$country_name,$region,$city,$postal_code,$latitude,$longitude)="";

# Check for additional IP's in /etc/ips file
my $IPALIASLINE;
my $IPALIAS;
open(ALIASES,"/etc/ips");
my @ALIASES=<ALIASES>;
close(ALIASES);
my @NEWALIASES=undef;
foreach $IPALIASLINE(@ALIASES) { 
	chomp($IPALIASLINE);
	($IPALIAS)=(split(/:/,$IPALIASLINE))[0];
	if ($HASNAT) { 
		$IPALIAS=&replace_with_natip($IPALIAS);
	}
	push(@NEWALIASES, "<form action='rblcheck.cgi'>\n");
	push(@NEWALIASES, "<li>$IPALIAS <input type='hidden' name='ipaddr' value='$IPALIAS'><input type='submit' value='Check'></li>\n");
	push(@NEWALIASES, "</form>");
}

my $aliascnt=@NEWALIASES;

my $enteredipaddr = param('ipaddr');
if ($enteredipaddr) { 
	# Get GEO IP data for $mainip
	my $gi = Geo::IP::PurePerl->new("/usr/local/share/GeoIP/GeoLiteCity.dat", GEOIP_STANDARD);
	($country_code,$country_code3,$country_name,$region,$city,$postal_code,$latitude,$longitude) = $gi->get_city_record($enteredipaddr);
	print "Content-Type: text/html; charset=iso-8859-1\n\n";
	print "Checking $enteredipaddr...<br>\n";
	if ($country_name) { 
		print "Country: $country_name ( $country_code / $country_code3 )<br>\n";
		print "Region: $region / City: $city / Postal Code: $postal_code<br>\n";
		print "Latitude: $latitude / Longitude: $longitude<br>\n";
	}
	print "<hr>\n";
	&checkit($enteredipaddr);
	print <<END;
<p>
Please note that neither your provider or datacenter or cPanel, Inc. have any control over<br>
the blacklists.  Each RBL has their own criteria for listing an IP address.  You will need<br>
to personally visit each RBL where your IP is listed and check with them on what their removal<br>
process is.<p>  
Don't just request to have your IP delisted without fixing the problem.  If you do that, <br>
you will most likely just get listed again and next time it will be more difficult to get<br>
removed.  Make sure that your network and mail server are properly configured and that your <br>
workstations/servers are free from viruses and other malware.  
<p>
Follow the steps outlined in the RBL removal process. Once you have solved the problem that <br>
got you listed, go back and attempt removal. Many of them have a self-service removal process.
<br>You should also not need to pay to be removed. These should all be professional RBL's and<br>
they are not out to extort you. Their goal is to have a cleaner, faster and better<br> 
Internet experience for everyone. 

<a href="rblcheck.cgi">Return</a>

END
}
else { 
	print <<END;
Content-Type: text/html; charset=iso-8859-1

<!DOCTYPE html>
<html>
	<head>
		<title>RBL Check</title>
	</head>
	<body>
	RBL Check...<p>
   Q: What is an RBL?<p>
   A: RBL stands for Realtime Blackhole List. These are spam blocking lists that allow a <br>
   system administrator to block email from being sent out that have a history of sending spam<br>
   or are infected with something that is doing the spamming.  Once your IP Address is on an <br>
   RBL, any other server that subscribes to that RBL will refuse email from your server. <p>
   Check your servers IP's now (or any IP) to see if it is listed. 
   <p>
	<form action="rblcheck.cgi">
	The servers main ip is: $mainip <input type="hidden" name="ipaddr" value="$mainip"><input type="submit" value="Check"><br>
	</form>
END
	if ($aliascnt > 1) { 
		print "These are the additional IP's (aliases): <p>\n";
	}
	print <<END;
	<ul>
	@NEWALIASES
	</ul>
	<p>
	<form action="rblcheck.cgi">
	<div>Enter an IP Address to check: <input name="ipaddr" size="20"></div>
	<div><input type="submit" value=" Check "></div>
	</form>
END
}

# RETURN TO MAIN MENU
exit;

sub checkit() { 
	$ENTEREDIP=$_[0];
	my $NUMLISTED=0;
	my $LOOKUPHOST;
	if ( $ENTEREDIP =~ /:/ and $ENTEREDIP !~ /\./ ) {
      # IPV6
		my $EXPANDEDIP = new Net::IP ( $ENTEREDIP );
		$LOOKUPHOST = join '.', reverse ( split '', $EXPANDEDIP->ip() );
		$LOOKUPHOST =~ s/\.:\././g;
	} 
	elsif ( $ENTEREDIP =~ /\./ and $ENTEREDIP !~ /:/ ) {
      # IPV4 
		$LOOKUPHOST = join '.', reverse ( split /\./, $ENTEREDIP );
	} 
	else {
      # IP is not valid
		die "FATAL - invalid host \"$ENTEREDIP\"\n";
	}
	foreach my $BLACKLIST (@RBLS) {
		#print "List: ". $BLACKLIST . ": $ENTEREDIP is ";
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
			$NUMLISTED++ unless($BLACKLIST =~ m/uribl.com/);
		}
	}
	print "<p>\n";
	print "Checked $totrbls Realtime Blackhole Lists (RBL's) & found $ENTEREDIP listed in $NUMLISTED of them.\n";
}

sub check_for_nat() { 
	return if (!(-e("/var/cpanel/cpnat")));
	my $NATFOUND=0;
	$NATFOUND=1;
	return $NATFOUND;;
}

sub replace_with_natip { 
	my $privateIP=$_[0];
	my $outsideIP;
	my $insideIP;
	open(CPNAT,"/var/cpanel/cpnat");
	my @CPNAT=<CPNAT>;
	close(CPNAT);
	my $cpnat;
	foreach $cpnat(@CPNAT) {
		chomp($cpnat);
		($outsideIP,$insideIP)=(split(/\s+/,$cpnat));
		chomp($outsideIP);
		chomp($insideIP);
		if ($insideIP eq $privateIP) { 
			return $outsideIP;
		}
		else {
			return $insideIP;
		}
	}
}

sub replace_mainIP { 
	my $privateIP=$_[0];
	my $outsideIP;
	my $insideIP;
	open(CPNAT,"/var/cpanel/cpnat");
	my @CPNAT=<CPNAT>;
	close(CPNAT);
	my $cpnat;
	foreach $cpnat(@CPNAT) {
		chomp($cpnat);
		($outsideIP,$insideIP)=(split(/\s+/,$cpnat));
		chomp($outsideIP);
		chomp($insideIP);
		if ($outsideIP eq $privateIP) { 
			return $outsideIP;
		}
	}
}

sub getGeoData {
   my $ip2chk=$_[0];
   return;   
}
