<?php

define('APP_PATH', dirname(__FILE__));

try {
    $application = new Yaf_Application(APP_PATH . "/conf/application.ini");
    $application->bootstrap()->run();
} catch (Exception $e) {
    echo $e->getMessage();
}
