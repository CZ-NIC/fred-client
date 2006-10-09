<?php
$size = 60; // size of inputs

$path = ''; // Here you can write path to the app
// $path = '/home/zdenek/enum/epp_client/trunk/'; // TEST

$command_options = ''; // here you can type some options. For more see ./ccreg_client.py --help
// $command_options = '-s curlew'; // TEST

define('CRLF', "\r\n");

?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="cs" xml:lang="cs">
<head>
    <title>CZ.NIC - Example of using ccReg</title>
    <meta http-equiv="Content-Language" content="cs" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="Keywords" content="Domény, Domains, Registrátoři, Registrators, Registrace domén, CZ.NIC, WHOIS, DNS, ENUM, Doména .eu, zájmové sdružení právnických osob, Top level domain, Domény nejvyšší urovně" />

<style type="text/css">
body {
    font-family:Verdana, Tahoma, Arial, sans-serif;
}
/*******************************

    ccRegClient output HTML

*******************************/
.ccreg_output {
    /* main block of ccreg_client output */
    font:size:9pt;
}

.ccreg_errors {
    /* errors during send/receive process */
    color:#f00;
    font-weight:bold;
}

.ccreg_messages {
    /* messages during connection process */
    color:#888;
}

.ccreg_source {
    /* display sources in verbose mode 3 */
    color:#00f;
}

.command_success {
    /* appears if code has value 1000 */
    color:#008000;
}
.command_done {
    /* appears if code has not value 1000 */
    color:#808000;
}

/* ------------------------------

    DATA/REASON table

------------------------------*/
table.ccreg_data  { 
    border-collapse:collapse;
    border:solid 2px #8FBCBF;
    margin:6px 0;
}
.ccreg_data table { vertical-align:top; }
.ccreg_data th, 
.ccreg_data td {
    border-right:solid 1px #7eafc0;
    border-bottom:solid 1px #7eafc0;
    padding:4px 8px;
}
.ccreg_data th {
    text-align:left;
    border-left:solid 1px #7eafc0;
    background-color:#F5F5F5;
}
.ccreg_data tr:hover {
    background-color:#F5F5DC;
}

/******************************

    Input table tags

******************************/
table#command  { border-collapse: collapse; }
#command table { border-collapse: collapse; background-color:#FFF8DC; }
#command tr { vertical-align:top; }
#command th, 
#command td {
    border-right:solid 1px #7eafc0;
    border-bottom:solid 1px #7eafc0;
    padding:8px;
}
#command th {
    border-left:solid 1px #7eafc0;
}
.tb-top {
    border-top:solid 1px #7eafc0;
}
.btn {
    width:100%;
}
.msg-error { color:#f00; }
.output {
    /* TEST only */
    background-color:#fafafa;
    border:dotted 1px #a9a9a9;
    padding:0 10px;
}
.command {
    color:#00f;
}
.retval {
    color:#a80;
}
</style>
</head>
<body>

<h1>Example of using cceg_client.</h1>

<form method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>">

<table id="command">
<tr>
    <th class="tb-top">Handle</th>
    <td class="tb-top"><input name="handle" value="<?php echo htmlspecialchars(stripslashes($_POST['handle'])); ?>" size="<?php echo $size; ?>" /></td>
</tr>
<tr>
    <th>verbose</th>
    <td><select name='verbose'>
    <?php
    // list of verbose levels:
    for($i=1; $i < 4; $i++) {
        if($i == ($_POST['verbose']+0)) $sel=' selected="selected"'; else $sel = '';
        echo "<option value='$i'$sel>$i</option>".CRLF;
    }
    ?>
    </select>
    </td>
</tr>

<tr>
    <th>&nbsp;</th>
    <td>

    <table>
    <tr>
    <th class="tb-top">
    <input class="btn" type="submit" name="reset" value="Reset" /><br />
    <input class="btn" type="submit" name="send[hello]" value="Hello" />
    <input class="btn" type="submit" name="send[poll]" value="Poll" />
    </th>

    <td class="tb-top">
    <input class="btn" type="submit" name="send[check_contact]" value="Check contact" /><br />
    <input class="btn" type="submit" name="send[check_nsset]" value="Check NSSET" /><br />
    <input class="btn" type="submit" name="send[check_domain]" value="Check domain" /><br />
    </td>

    <td class="tb-top">
    <input class="btn" type="submit" name="send[info_contact]" value="Info contact" /><br />
    <input class="btn" type="submit" name="send[info_nsset]" value="Info NSSET" /><br />
    <input class="btn" type="submit" name="send[info_domain]" value="Info domain" /><br />
    </td>

    <td class="tb-top">
    <input class="btn" type="submit" name="send[list_contact]" value="List contact" /><br />
    <input class="btn" type="submit" name="send[list_nsset]" value="List NSSET" /><br />
    <input class="btn" type="submit" name="send[list_domain]" value="List domain" /><br />
    </td>

    </tr>
    </table>

    </td>
</tr>
</table>
</form>
<?php

// Here are commands that don't need handler:
$ar_no_handler = array('hello','list_contact','list_nsset','list_domain');

while(is_array($_POST['send'])) {
    $errors = array();
    $command = key($_POST['send']);
    $handle = strtr(trim($_POST['handle']), "'",'"');

    if(!$handle and !in_array($command,$ar_no_handler)) $errors[] = 'Handle missing.';
    // check if ccreg_client exist
    $cmdline = 'python '.$path.'ccreg_client.py -V';
    $ar_retval = array();
    exec($cmdline, $ar_retval);
    $retval = join('\n',$ar_retval);
    // See, what looks command line:
    // echo "<div class='output'><p class='command'>$cmdline</p> <p class='retval'>$retval</p></div>".CRLF;
    if(!preg_match('/ccRegClient \d+/',$retval)) $errors[] = 'ccreg_client.py not instaled properly. See help or set prefix of path.';
    if($errors) {
        echo '<h2 class="msg-error">Error:<br />'.join('<br />',$errors).'</h2>';
        break;
    }
    if(in_array($command,$ar_no_handler))
         $ccreg_command = $command;
    else $ccreg_command = "$command $handle";
    $cmdline = 'python '.$path."ccreg_client.py ".$command_options." -x -v $_POST[verbose] -o html -d '$ccreg_command'";
    // See, what looks command line:
    // echo "<div class='output'><p class='command'>$cmdline</p></div>".CRLF;
    echo '<div id="ccreg_output">'.CRLF;
    passthru($cmdline);
    echo '</div>'.CRLF;
    break;
}

?>
</body>
</html>
