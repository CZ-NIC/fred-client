<?php
$size = 60; // size of inputs
$indent_data=50; // indent column of data

$exec_path = ''; // Here you can write path to the app
// $exec_path = 'python /home/zdenek/enum/epp_client/trunk/'; // TEST

// Here you define where exe saves PHP code with answer data:
$php_module_name = '/tmp/fred_client.php';

$command_options = ''; // here you can type some options. For more see ./fred_client.py --help
// $command_options = '-s andromeda -f /home/zdenek/.fred_client.conf'; // TEST

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
    $cmdline = $exec_path.'fred_client.py -V';
    $ar_retval = array();
    exec($cmdline, $ar_retval);
    $retval = join('\n',$ar_retval);
    // See, what looks command line:
    // echo "<div class='output'><p class='command'>$cmdline</p> <p class='retval'>$retval</p></div>".CRLF;
    if(!preg_match('/FredClient \d+/',$retval)) $errors[] = 'fred_client.py not instaled properly. See help or set prefix of path.';
    if($errors) {
        echo '<h2 class="msg-error">Error:<br />'.join('<br />',$errors).'</h2>';
        if(!preg_match('/invalid_?(\w*)/',$command)) break;
    }

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
    if($_POST['output']=='html') {
        //--- HTML ---------------------------------
        $cmdline = $exec_path."fred_client.py ".$command_options." -x -v $_POST[verbose] -o html -d '$fred_command'";
        // See, what looks command line:
        // echo "<div class='output'><p class='command'>$cmdline</p></div>".CRLF;
        echo '<div id="fred_output">'.CRLF;
        passthru($cmdline);
        echo '</div>'.CRLF;
        //-----------------------------------------
    } else {
        //--- PHP ---------------------------------
        $cmdline = $exec_path."fred_client.py ".$command_options." -x -v $_POST[verbose] -o php -d '$fred_command' > $php_module_name";
        // See, what looks command line:
        if($TEST) echo "<br/>Command:<div class='output'><p class='command'>$cmdline</p></div>".CRLF;

        // reset output:
        @unlink($php_module_name);

        passthru($cmdline); // output is redirect into file

        // If everything went ok, we have prepared PHP data in module $php_module_name:
        include($php_module_name);
        
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

        //--- FOR EXAMPLE ONLY: --------------------
        echo '<hr />'.CRLF;
        echo "<h3>DUMP OF: $php_module_name</h3>".CRLF;
        echo '<pre class="fred_source">'.CRLF;
        $fp = fopen($php_module_name,'r');
        if($fp) {
            while(!feof($fp)) {
                echo htmlspecialchars(fgets($fp, 4096));
            }
            fclose($fp);
        }
        echo '</pre>'.CRLF;
        //-----------------------------------------
    }
    
    break;
}

?>
</body>
</html>
