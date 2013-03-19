<?php
/**
 * @name ErrorController
 * @desc 错误控制器, 在发生未捕获的异常时刻被调用
 * @see http://www.php.net/manual/en/yaf-dispatcher.catchexception.php
 * @author venkman
 */
class ErrorController extends Yaf_Controller_Abstract {
    
	public function errorAction(Exception $exception) {
        //如果要在view显示，这句一定要否则其他Controller抛出的错误且使用了disableView时本action无法在view显示
        Yaf_Dispatcher::getInstance()->enableView();
		$this->getView()->assign("exception", $exception);
	}

}
