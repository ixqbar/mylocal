<?php
/**
 *
 * usage like php cli.php "request_uri=/index-1-2.html"
 *
 */
define('APP_PATH', dirname(__FILE__));
$app = new Yaf_Application(APP_PATH . "/conf/application.ini");
$app->bootstrap()->getDispatcher()->dispatch(new Yaf_Request_Simple());