<?php

class Facebook {
    private $_proxy = '';
    private $_app_id = '';
    private $_app_secret = '';
    public $app_access_token = null;
    public $user_access_token = null;
    public $signed_request_data = '';

    /**
     *
     * @param string $app_id
     * @param string $app_secret
     * @param string $proxy
     */
    function __construct($app_id, $app_secret, $proxy = '') {
        if (empty($app_id) || empty($app_secret)) {
			//@TODO
        }
            
		$this->_app_id     = $app_id;
        $this->_app_secret = $app_secret;
        $this->_proxy      = $proxy;

        $this->app_access_token  = $this->get_app_access_token();
    }

    /**
     *
     * @param string $uid
     * @param string $fields
     * @return array
     */
    public function get_user_info($uid, $fields='id,first_name,last_name,gender,locale,email,location') {
        $url = 'https://graph.facebook.com/' . $uid . '/?fields='.$fields.'&access_token=' . $this->app_access_token;
        $result = $this->fetch_url($url);
        return json_decode($result, true);
    }

    /**
     *
     * @return array
     */
    public function get_player_full_info() {
        $this->get_user_access_token();
        $url = 'https://graph.facebook.com/me/?access_token=' . $this->user_access_token;
        $result = $this->fetch_url($url);
        return json_decode($result, true);
    }

    /**
     *
     * @param string $signed_request
     * @return array
     */
    public function parse_signed_request($signed_request) {
        list($encoded_sig, $payload) = explode('.', $signed_request, 2);

        // decode the data
        $sig = base64_decode(strtr($encoded_sig, '-_', '+/'));
        $data = json_decode(base64_decode(strtr($payload, '-_', '+/')), true);

        if (strtoupper($data['algorithm']) !== 'HMAC-SHA256') {
            return null;
        }

        // check sig
        $expected_sig = hash_hmac('sha256', $payload,  $this->_app_secret, true);
        if ($sig !== $expected_sig) {
            return null;
        }

        return $data;
    }

    /**
     *
     * @return array
     */
    public function get_signed_request_data() {
        if ($this->signed_request_data) {
            return $this->signed_request_data;
        }

        if (isset($_REQUEST['signed_request'])) {
            $this->signed_request_data = $this->parse_signed_request($_REQUEST['signed_request']);
        } else if (isset($_COOKIE['fbm_' . $this->_app_id])) {
            $this->signed_request_data = $this->parse_signed_request($_COOKIE['fbm_' . $this->_app_id]);
        }

        return $this->signed_request_data;
    }

    /**
     *
     * @return string
     */
    public function get_app_access_token() {
        if ($this->app_access_token) {
            return $this->app_access_token;
        }

        $this->app_access_token = $this->_app_id . '|' . $this->_app_secret;
        return $this->app_access_token;
    }

    /**
     *
     * @return string
     */
    public function get_user_access_token() {
        if ($this->user_access_token) {
            return $this->user_access_token;
        }

        $signed_request_data = $this->get_signed_request_data();
        if ($signed_request_data) {
            // apps.facebook.com hands the access_token in the signed_request
            if (isset($signed_request_data['oauth_token'])) {
                $this->user_access_token = $signed_request_data['oauth_token'];
                return $this->user_access_token;
            }

            // the JS SDK puts a code in with the redirect_uri of ''
            if (isset($signed_request_data['code'])) {
                $this->user_access_token = $this->get_access_token_from_code($signed_request_data['code'], '');
                return $this->user_access_token;
            }
        }

        return $this->user_access_token;
    }

    /**
     *
     * @param string $code
     * @param string $redirect_uri
     * @return string
     */
    public function get_access_token_from_code($code, $redirect_uri) {
        $url = 'https://graph.facebook.com/oauth/access_token?code=' . $code . '&client_id=' . $this->_app_id . '&client_secret=' . $this->_app_secret . '&redirect_uri=' . $redirect_uri;
        $result = $this->fetch_url($url);

        return $result;
    }

    /**
     *
     * @return array
     */
    public function get_app_friend_ids() {
        $friend_ids = array();
        $url = 'https://api.facebook.com/method/friends.getAppUsers?access_token=' . $this->get_user_access_token() . '&format=json';
        $result = $this->fetch_url($url);
        if ($result) {
            //fix 32BUG
            $result = preg_replace('/([0-9]+)/', '"$1"', $result);

            $result = json_decode($result, true);
            if ($result && is_array($result) && count($result)) {
                $friend_ids = $result;
            }
        }

        return $friend_ids;
    }

    /**
     *
     * @param $uids  array
     * @return array
     */
    public function get_credits($uids) {
        $url = 'https://api.facebook.com/method/users.getStandardinfo' .
                '?uids=' . (is_array($uids) ? json_encode($uids) : $uids) .
                '&fields=credit_balance&access_token=' . $this->app_access_token .
                '&format=json';
        $result = $this->fetch_url($url);
        $result = json_decode($result, true);
        return $result;
    }

    //params:   'ip:port'
    public function set_sock_proxy($proxy) {
        $this->_proxy = $proxy;
    }

    public function fetch_url($url) {
        $ch = curl_init();
        //curl_setopt($ch, CURLOPT_COOKIEJAR, "cookie.txt");
        //curl_setopt($ch, CURLOPT_COOKIEFILE, "cookie.txt");
        curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)");
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

        if ($this->_proxy) {
            curl_setopt($ch, CURLOPT_PROXY, $this->_proxy);
            curl_setopt($ch, CURLOPT_PROXYTYPE, CURLPROXY_SOCKS5);
        }

        //curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
        //curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        //curl_setopt($ch, CURLOPT_REFERER, $ref_url);
        //curl_setopt($ch, CURLOPT_HEADER, TRUE);
        //curl_setopt($ch, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, TRUE);
        //curl_setopt($ch, CURLOPT_POST, TRUE);
        //curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
        $result = curl_exec($ch); // execute the curl command
        curl_close($ch);
        return $result;
    }

    /**
     *
     * @param string $uid
     * @param string $request_id
     * @return boolean
     */
    public function delete_feed($uid, $request_id) {
        if (empty($uid) || empty($request_id)) {
            return false;
        }
        $url = "https://graph.facebook.com/".$request_id . "_" . $uid ."?access_token=".$this->app_access_token."&method=delete";

        return $this->fetch_url($url);
    }

    /**
     *
     * @param string $uid
     * @param string $request_id
     * @return array
     */
    public function get_request_detail($uid, $request_id) {
        $result =  $this->fetch_url("https://graph.facebook.com/" . $request_id . "_" . $uid . "?access_token=" . $this->app_access_token);
        $result = json_decode($result, true);
        return $result;
    }
}

