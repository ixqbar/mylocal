<?php

class Chat {
    static $inst = null;

    /**
     *
     * @return Break_Chat
     */
    public static function instance() {
        if (null == self::$inst) {
            self::$inst = new self();
        }

        return self::$inst;
    }

    private $_socket_handle = null;
    public $connected = false;

    /**
     *
     */
    public function __construct() {
        $this->_socket_handle = @socket_create(AF_INET, SOCK_STREAM, SOL_TCP);
        if (false !== $this->_socket_handle) {
            if (false !== @socket_connect($this->_socket_handle, "127.0.0.1", 8080)) {
                $this->login();
            } else {
                echo "Unable to connect socket " . socket_strerror(socket_last_error());
            }
        } else {
            echo "Unable to create socket " . socket_strerror(socket_last_error());
        }
    }

    /**
     *
     */
    public function __destruct() {
        if ($this->connected) {
            socket_close($this->_socket_handle);
        }
    }

    /**
     * @param object $socket
     * @param array $msg
     */
    private function write_socket_msg($socket, $msg) {
       $msg      = is_array($msg) ? json_encode($msg) : $msg;
       $msg      = str_pad(strlen($msg), 6, 0, STR_PAD_LEFT) . $msg . "|>";
       $body_len = strlen($msg);
       $start    = 0;
       $len      = $body_len;

       while (true) {
           $tmp_len = socket_write($socket, substr($msg, $start), $len);
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
     * @param $client_sock
     * @return array
     */
    private function read_socket_msg($socket, $buf_len=6, $is_header=True) {
        $total_len = $buf_len;
        $buf       = "";
        while (true) {
            $tmp_buf = socket_read($socket, $buf_len, PHP_BINARY_READ);
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
            return array(0, substr($buf, 0, -2));
        }

        return $this->read_socket_msg($socket, (int)$buf + 2, false);
    }

    /**
     *
     * @param string $message
     * @return boolean/array
     */
    private function send($message) {
        $result = $this->write_socket_msg($this->_socket_handle, $message);
        if ($result[0]) {
            echo "Unable to write socket msg " . $result[1];
            return false;
        }

        $result = $this->read_socket_msg($this->_socket_handle);
        if ($result[0]) {
            echo "Unable to read socket msg " . $result[1];
            return false;
        }

        if (substr($result[1], 0, 3) != "rep") {
            echo "Unable to get login response " . $result[1];
            return false;
        }

        $login_response_msg = json_decode(substr($result[1], 4), true);
        if (!is_array($login_response_msg) || !isset($login_response_msg['result']) || "ok" != $login_response_msg['result']) {
            echo "Unable to get login response " . $result[1];
            return false;
        }

        return $login_response_msg;
    }

    /**
     *
     */
    private function login() {
        $random    = mt_rand(1, 1000);
        $timestamp = time();
        $temp_uid  = "system" . $timestamp . $random;
        $login_msg = "login " . json_encode(array(
            "uid"       => $temp_uid,
            "name"      => "",
            "first"     => "",
            "last"      => "",
            "level"     => 0,
            "timestamp" => $timestamp,
            "random"    => $random,
            "sign"      => md5($temp_uid . $timestamp . $random)
        ));

        $this->connected = false !== $this->send($login_msg);
    }

    /**
     * 群聊公告
     *
     * @param string $message
     * @return boolean
     */
    public function send_golbal_notice($message) {
        if (!$this->connected) {
            return false;
        }

        $chat_msg = "chat " . json_encode(array(
            "type"  => 1,
            "guild" => 0,
            "msg"   => $message,
        ));

        return false !== $this->send($chat_msg);
    }

    /**
     * 公会公告
     *
     * @param int $guild_id
     * @param string $message
     * @return boolean
     */
    public function send_guild_notice($guild_id, $message) {
        if (!$this->connected) {
            return false;
        }

        $chat_msg = "chat " . json_encode(array(
            "type"  => 2,
            "guild" => $guild_id,
            "msg"   => $message,
        ));

        return false !== $this->send($chat_msg);
    }

    /**
     *
     * @param string $message
     * @param int $guild_id
     * @return boolean
     */
    public function send_notice($message, $guild_id=0) {
        if (!$this->connected) {
            return false;
        }

        return $guild_id ? $this->send_guild_notice($guild_id, $message) : $this->send_golbal_notice($message);
    }

    /**
     *
     * @param array $player_data
     * @return boolean
     */
    public function update_player_data($player_data) {
        if (!$this->connected) {
            return false;
        }

        $chat_msg = "update " . json_encode($player_data);
        return false !== $this->send($chat_msg);
    }

}

$chat = Chat::instance();
while($chat->connected) {
    $chat->send_notice("hello");
    sleep(3);
}