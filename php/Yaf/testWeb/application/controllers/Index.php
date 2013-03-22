<?php
/**
 * @name IndexController
 * @author venkman
 * @desc 默认控制器
 * @see http://www.php.net/manual/en/class.yaf-controller-abstract.php
 */
class IndexController extends Yaf_Controller_Abstract {

    /**
     *
     */
    public function init() {
        //
    }

	/**
     *
     */
	public function indexAction() {
        Yaf_Dispatcher::getInstance()->disableView();

        if ($this->getRequest()->isCli()) {
            print_r($this->getRequest()->getParams());
            print_r($_SERVER);
        } else {
            var_dump($this->getRequest()->getParams());
            var_dump($_SERVER);
        }
	}
}
