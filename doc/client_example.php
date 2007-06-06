<?php
$size = 60; // size of inputs
$indent_data=50; // indent column of data

define('CRLF', "\r\n");
define('BR', "<br />\r\n");

?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="cs" xml:lang="cs">
<head>
    <title>CZ.NIC - Example of using Fred</title>
    <meta http-equiv="Content-Language" content="cs" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="Keywords" content="Domény, Domains, Registrátoři, Registrators, Registrace domén, CZ.NIC, WHOIS, DNS, ENUM, Doména .eu, zájmové sdružení právnických osob, Top level domain, Domény nejvyšší urovně" />

<style type="text/css">
body {
    font-family:Verdana, Tahoma, Arial, sans-serif;
}
/*******************************

    FredClient output HTML

*******************************/
.fred_output {
    /* main block of fred_client output */
    font:size:9pt;
}

.fred_errors {
    /* errors during send/receive process */
    color:#f00;
    font-weight:bold;
}

.fred_messages {
    /* messages during connection process */
    color:#888;
}

.fred_source {
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
table.fred_data  { 
    border-collapse:collapse;
    border:solid 2px #8FBCBF;
    margin:6px 0;
}
.fred_data table { vertical-align:top; }
.fred_data th, 
.fred_data td {
    border-right:solid 1px #7eafc0;
    border-bottom:solid 1px #7eafc0;
    padding:4px 8px;
}
.fred_data th {
    text-align:left;
    border-left:solid 1px #7eafc0;
    background-color:#F5F5F5;
}
.fred_data tr:hover {
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
.note {
    color:#888;
    font-size:80%;
}
</style>
</head>
<body>

<h1>Example of using fred_client.</h1>

<p style="font-size:80%"><i>Note:</i> For running this example:</p>
<ul style="font-size:80%">
<li>Place this example to your www folder.</li>
<li>You have to install <strong>fred_client</strong> properly or use <strong>Eexec path</strong> entry.</li>
<li>Your configuration file must be in <strong>/etc</strong> or use <strong>Command options</strong> entry.</li>
</ul>


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

    <?php
    if($_REQUEST['display_command_line']) $checked=' checked="checked"'; else $checked='';
    echo "<input type='checkbox' name='display_command_line'$checked /> Display command line (for TEST only).".CRLF;
    ?>
    
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
    <input class="btn" type="submit" name="send[list_contacts]" value="List contacts" /><br />
    <input class="btn" type="submit" name="send[list_nssets]" value="List NSSETs" /><br />
    <input class="btn" type="submit" name="send[list_domains]" value="List domains" /><br />
    </td>

    <td class="tb-top">
    TEST (ERRORS)<br/>
    <input class="btn" type="submit" name="send[invalid]" value="Invalid command" /><br />
    <input class="btn" type="submit" name="send[invalid_handle_missing]" value="info_contact Handle missing" /><br />
    <input class="btn" type="submit" name="send[invalid_login]" value="Invalid login" /><br />
    <input class="btn" type="submit" name="send[invalid_cert]" value="Invalid certificate" /><br />
    <input class="btn" type="submit" name="send[invalid_invalidhost]" value="Invalid host" /><br />
    </td>

    </tr>
    </table>

    </td>
</tr>

<tr>
    <th>Output</th>
    <td><?php
    $ar_output = array('html'=>'Simple HTML', 'php'=>'PHP code');
    if(!$_POST['output']) $_POST['output'] = key($ar_output);
    foreach($ar_output as $k => $v) {
        if($_POST['output'] == $k) $checked = 'checked="checked"'; else $checked = '';
        echo "<input type='radio' name='output' value='$k' $checked /> $v".CRLF;
    }
    ?><br />
    <span class='note'>
<i>Explanation:</i><br />
Mode <strong>Simple HTML</strong> outputs HTML code directly into this web page.<br />
Mode <strong>PHP code</strong> generates PHP code what we redicert into file and subsequently we include into page.
    </span>
    </td>
</tr>

<tr>
    <th>Command options</th>
    <td>
    <input name="command_options" value="<?php echo htmlspecialchars(stripslashes($_POST['command_options'])); ?>" size="<?php echo $size; ?>" /> 
    <span class="note">
    (use if <strong>fred_client</strong> is not installed)<br/>
    <i>Example:</i> -s curlew -f /home/zdenek/.fred_client.conf<br/>
    <i>For mode see README or</i> $ fred_client --help</span>
    </td>
</tr>

<tr>
    <th>Exec path</th>
    <td>
    <input name="exec_path" value="<?php echo htmlspecialchars(stripslashes($_POST['exec_path'])); ?>" size="<?php echo $size; ?>" />
    <span class="note">
    (use if <strong>fred_client</strong> is not installed)<br/>
    <i>Example:</i> /home/zdenek/enum/epp_client/trunk/
    </span>
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
    // check if fred_client exist
    $cmdline = $_POST['exec_path'].'fred_client -V';
    $ar_retval = array();
    exec($cmdline, $ar_retval);
    $retval = join('\n',$ar_retval);
    // See, what looks command line:
    // echo "<div class='output'><p class='command'>$cmdline</p> <p class='retval'>$retval</p></div>".CRLF;
    if(!preg_match('/FredClient \d+/',$retval)) $errors[] = 'fred_client not instaled properly. See help or set prefix of path.';
    if($errors) {
        echo '<h2 class="msg-error">Error:<br />'.join('<br />',$errors).'</h2>';
        if(!preg_match('/invalid_?(\w*)/',$command)) break;
    }

    $command_options = $_POST['command_options'];
    $TEST = 0;
    if(preg_match('/invalid_?(\w*)/',$command, $match)) {
            $TEST = 1;
            $command = $match[1];
            if($command=='login') $command_options .= ' -w invalidpassw';
            elseif($command=='cert') { $command = 'login'; $command_options .= ' -c invalid_cert.pem'; }
            elseif($command=='invalidhost') { $command = 'login'; $command_options .= ' -h invalidhost'; }
            elseif($command=='handle_missing') { $command = 'info_contact'; $handle = ''; }
    }

    if(in_array($command,$ar_no_handler))
         $fred_command = $command;
    else $fred_command = "$command $handle";
    $command_python = 'python ';
    if($_POST['output']=='html') {
        //--- HTML ---------------------------------
        $cmdline = $command_python.$_POST['exec_path']."fred_client ".$command_options." -v $_POST[verbose] -o html -d '$fred_command'";
        // See, what looks command line:
        if($TEST or $_REQUEST['display_command_line']) echo "<br/>HTML Command line:<div class='output'><p class='command'>$cmdline</p></div>".CRLF;
        echo '<div id="fred_output">'.CRLF;
        passthru($cmdline);
        echo '</div>'.CRLF;
        //-----------------------------------------
    } else {
        //--- PHP ---------------------------------
        $cmdline = $command_python.$_POST['exec_path']."fred_client ".$command_options." -v $_POST[verbose] -o php -d '$fred_command'";
        // See, what looks command line:
        if($TEST or $_REQUEST['display_command_line']) echo "<br/>PHP Command line:<div class='output'><p class='command'>$cmdline</p></div>".CRLF;

        $output = array();
        exec($cmdline, $output, $retval);

        if($retval == 0) {
            array_shift($output); // remove sign of the PHP beginnig: <[question mark]php
            array_pop($output); // remove sign of the PHP end: [question mark]>
            // We need implode by cause of the multiline variables.
            $data = implode("\n",$output);
            // echo '<pre>'.htmlspecialchars($data).'</pre>'.CRLF; // TEST
            eval($data);
        }

        echo "<h3>PHP CODE:</h3>".CRLF;
        echo '<pre>'.CRLF;

        echo "<strong>\$fred_client_notes</strong>:".CRLF;
        print_r($fred_client_notes);
        echo "<strong>\$fred_client_errors</strong>:".CRLF;
        print_r($fred_client_errors);
        echo CRLF;

        echo '<strong>'.str_pad('$fred_encoding',$indent_data)."</strong>$fred_encoding".CRLF;
        echo '<strong>'.str_pad('$fred_command',$indent_data)."</strong>$fred_command".CRLF;
        echo '<strong>'.str_pad('$fred_code',$indent_data)."</strong>$fred_code".CRLF;
        echo '<strong>'.str_pad('$fred_reason',$indent_data)."</strong>$fred_reason".CRLF;
        echo CRLF;

        echo "<strong>\$fred_reason_errors</strong>:".CRLF;
        print_r($fred_reason_errors);
        if($fred_error_create_name)  echo "<strong>\$fred_error_create_name</strong>: $fred_error_create_name".CRLF;
        if($fred_error_create_value) echo "<strong>\$fred_error_create_value</strong>: $fred_error_create_value".CRLF;
        echo CRLF;

        $label = str_pad('$fred_labels $fred_data[KEY]:',$indent_data);
        echo "<strong>$label\$fred_data</strong>".CRLF.CRLF;
        if(is_array($fred_data)) {
            foreach($fred_data as $key => $value) {
                echo str_pad("$fred_labels[$key] [$key]:", $indent_data);
                print_r($value);
                if(!is_array($value)) echo CRLF;
            }
        }
        echo "<i>Third verbose level:</i>".BR;
        echo "<strong>\$fred_source_command</strong>:".BR;
        echo htmlspecialchars($fred_source_command).BR;
        echo "<strong>\$fred_source_answer</strong>:".BR;
        echo htmlspecialchars($fred_source_answer).BR;
        echo '</pre>'.CRLF;

    }
    
    break;
}

?>
</body>
</html>
