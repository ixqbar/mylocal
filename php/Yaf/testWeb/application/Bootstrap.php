<?php
/**
 * @name Bootstrap
 * @author venkman
 * @desc 所有在Bootstrap类中, 以_init开头的方法, 都会被Yaf调用,
 * @see http://www.php.net/manual/en/class.yaf-bootstrap-abstract.php
 * 这些方法, 都接受一个参数:Yaf_Dispatcher $dispatcher
 * 调用的次序, 和申明的次序相同
 */
class Bootstrap extends Yaf_Bootstrap_Abstract {

    private $_config;

    /**
     *
     * @param Yaf_Dispatcher $dispatcher
     */
    public function _initBootstrap($dispatcher) {
        $this->_config = Yaf_Application::app()->getConfig();
    }

    /**
     *
     * @param Yaf_Dispatcher $dispatcher
     */
    protected function _initTimeZone($dispatcher) {
        if ($this->_config->application->timezone) {
            date_default_timezone_set($this->_config->application->timezone);
        }
    }

    /**
     *
     * @param Yaf_Dispatcher $dispatcher
     */
    public function _initErrors($dispatcher) {
        if ($this->_config->application->showErrors) {
            error_reporting (-1);
            ini_set('display_errors','On');
        }
    }

    /*
     * initIncludePath is only required because zend components have a shit load of
     * include_once calls everywhere. Other libraries could probably just use
     * the autoloader (see _initNamespaces below).
     */
    public function _initIncludePath($dispatcher) {
        set_include_path(get_include_path() . PATH_SEPARATOR . $this->_config->application->library);
    }

    /**
     *
     * @param Yaf_Dispatcher $dispatcher
     */
    public function _initPlugin($dispatcher) {
		$sample = new SamplePlugin();
		$dispatcher->registerPlugin($sample);
	}

    /**
     *
     * @param Yaf_Dispatcher $dispatcher
     */
    public function _initRoutes($dispatcher) {
        $route_handle = $dispatcher->getRouter();
        $route_handle->addRoute(
            "default",
            new Yaf_Route_Regex(
                "/index-(\w+)-(\w+).html/",
                array('controller' => "index"),
                array(1 => "p1", 2 => "p2")
            )
        );
    }
}
