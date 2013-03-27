<?php
$sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if (!is_resource($sock)) {
    die('socket_create for error: '. socket_strerror(socket_last_error()) . PHP_EOL);
}
socket_set_option($sock, SOL_SOCKET, SO_REUSEADDR, 1);
socket_bind($sock,'0.0.0.0',9090);
socket_listen($sock,10);

/**
 * @param $client_sock
 * @return array
 */
function read_client_msg($client_sock, $buf_len=6, $is_header=True) {
    $total_len = $buf_len;
    $buf       = "";
    while (true) {
        $tmp_buf = socket_read($client_sock, $buf_len, PHP_BINARY_READ);
        if (false === $tmp_buf) {
            return array(1, socket_strerror(socket_last_error()));
        }
        if (0 == strlen($tmp_buf)) {
            break;
        }
        if ($is_header && !is_numeric($tmp_buf)) {
            return array(1, "buf header must be numeric");
        }
        $buf_len -= strlen($tmp_buf);
        $buf     .= $tmp_buf;
        if (0 == $buf_len) {
            break;
        }
    }

    if ($buf_len != 0 || strlen($buf) != $total_len) {
        return strlen($buf) ? array(1, "error buf `" . $buf . "`") : array(1, "client disconnected");
    }

    if (false == $is_header) {
        if (substr($buf, -2) != "|>") {
            return array(1, "error body buf end flag `" . $buf . "`");
        }
        $cli_request_msg = json_decode(substr($buf, 0, -2), true);
        if (!is_array($cli_request_msg)
            || !isset($cli_request_msg['cli'])
            || !isset($cli_request_msg['data'])) {
            return array(1, "error body buf format `" . $buf . "`");
        }

        return array(0, $cli_request_msg);
    }

    return read_client_msg($client_sock, (int)$buf + 2, false);
}

/**
 * @param object $client_sock
 * @param array $msg
 */
function write_client_msg($client_sock, $msg) {
    $msg      = is_array($msg) ? json_encode($msg) : $msg;
    $msg      = str_pad(strlen($msg), 6, 0, STR_PAD_LEFT) . $msg . "|>";
    $body_len = strlen($msg);
    $start    = 0;
    $len      = $body_len;

    while (true) {
        $tmp_len = socket_write($client_sock, substr($msg, $start), $len);
        if (false === $tmp_len) {
            return array(1, socket_strerror(socket_last_error()));
        }

        if ($tmp_len == $len) {
            break;
        }

        $start += $tmp_len;
        $len    = $body_len - $start;
    }

    return array(0, "");
}

/**
 * @param array $msg array("cli" => "", "uid" => "", "rid" => "", "data" => array())
 * @return string "result|pull|clifd|uid|rid|ext_data"
 */
function process_client_msg($msg) {
    return sprintf("%d|%s|%s|%s|%s|%s", 0, "pull", $msg['cli'], $msg['uid'], $msg['rid'], "php servcie data");
}

function to_read($sock, $events, $arg) {
    try {
         $client_msg = read_client_msg($sock);
         print_r($client_msg);
         if (0 == $client_msg[0]) {
             try {
                $client_msg = process_client_msg($client_msg[1]);
                var_dump($client_msg);
                $result = write_client_msg($sock, $client_msg);
                print_r($result);
             } catch (Exception $e) {
                 write_client_msg($sock, json_encode(array(0, "exception " . $e->getMessage() . " in " . $e->getFile() . ",at " . $e->getLine())));
             }
         } else {
             event_base_loopexit($arg[1]);
         }
     }catch (Exception $e) {
         echo "exception " . $e->getMessage() . " in " . $e->getFile() . ",at " . $e->getLine() . PHP_EOL;
         event_base_loopexit($arg[1]);
     }
}

for ($i = 0; $i < 10; $i++) {

    $pid = pcntl_fork();
    if ($pid == 0) {
        break;
    }
}
if ($pid == 0) {
child:
    //accept connection
    $client_sock = socket_accept($sock);
    if (false === $client_sock) {
        echo "socket_accept for error:" . socket_strerror(socket_last_error()) . PHP_EOL;
        exit;
    }

    if (socket_getpeername($client_sock, $addr, $port)) {
        echo "connect at:" . $addr . ":" . $port . PHP_EOL;
    }

//    while(true) {
//        try {
//            $client_msg = read_client_msg($client_sock);
//            print_r($client_msg);
//            if (0 == $client_msg[0]) {
//                try {
//                   $client_msg = process_client_msg($client_msg[1]);
//                   var_dump($client_msg);
//                   $result = write_client_msg($client_sock, $client_msg);
//                   print_r($result);
//                } catch (Exception $e) {
//                    write_client_msg($client_sock, json_encode(array(0, "exception " . $e->getMessage() . " in " . $e->getFile() . ",at " . $e->getLine())));
//                }
//            } else {
//                break;
//            }
//        }catch (Exception $e) {
//            echo "exception " . $e->getMessage() . " in " . $e->getFile() . ",at " . $e->getLine() . PHP_EOL;
//        }
//    }
//
//    socket_close($client_sock);

    $base = event_base_new();
    $event = event_new();
    // set event flags
    event_set($event, $client_sock, EV_READ | EV_PERSIST, "to_read", array($event, $base));
    // set event base
    event_base_set($event, $base);
    // enable event
    event_add($event);
    // start event loop
    event_base_loop($base);
    //close
    socket_close($client_sock);
    exit;
}

while (true) {
    $pid = pcntl_fork();
    if ($pid == 0) {
        //child
        goto child;
    }
    //parent
    $child_pid = pcntl_wait($status);
    //error
    if ($child_pid == -1) {
        break;
    }
    echo "child exit " . $child_pid . " \n";
}
