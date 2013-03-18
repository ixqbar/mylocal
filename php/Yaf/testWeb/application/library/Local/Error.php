<?php

class Local_Error {

   /**
    *
    * @param int    $err_no   错误代码
    * @param string $err_msg  错误描述
    * @param string $err_file 所在文件
    * @param string $err_line 所在位置
    */
    public static function errorHandler($err_no, $err_msg, $err_file, $err_line) {
        die("[" . $err_no . "]" . $err_msg . " in " . $err_file . " at " . $err_line . " line");
    }

    /**
     *
     * @param Exception $e
     */
    public static function exceptionHandler($e) {
        die($e->getMessage() . " in " . $e->getFile() . " at " . $e->getLine() . " line");
    }

    /**
     *
     */
    public static function shutdownHandler() {
        $last_error = error_get_last();
        if ($last_error) {
            die("[" . $last_error['type'] . "]" . $last_error['message'] . " in " . $last_error['file'] . " at " . $last_error['line'] . " line");
        }
    }

}