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
        var_dump($this->getRequest()->getParams());

        throw new Exception('ttt');
	}
}
