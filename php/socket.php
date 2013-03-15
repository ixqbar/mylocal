<?php
$sock = socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
if (!is_resource($sock)) {
    die('socket_create for error: '. socket_strerror(socket_last_error()) . PHP_EOL);
}
socket_set_option($sock, SOL_SOCKET, SO_REUSEADDR, 1);
socket_bind($sock,'0.0.0.0',10086);
socket_listen($sock,10);


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

    while(true) {
        //todo
    }

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

