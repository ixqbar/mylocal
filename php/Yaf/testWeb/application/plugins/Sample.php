<?php
/**
 * Ap定义了如下的7个Hook,
 * 插件之间的执行顺序是先进先Call
 */
class SamplePlugin extends Yaf_Plugin_Abstract {

	public function routerStartup(Yaf_Request_Abstract $request, Yaf_Response_Abstract $response) {
		echo "Plugin routerStartup called <br/>\n";

		echo "Request with base uir:" . $request->getBaseUri() . "<br/>\n";

		echo "Request with request uri:" .$request->getRequestUri() . "<br/>\n";
	}

	public function routerShutdown(Yaf_Request_Abstract $request, Yaf_Response_Abstract $response) {
		echo "Plugin routerShutdown called <br/>\n";
		echo "Request routed result:" ;
		var_dump($request);
		echo "<br/>\n";
		echo "Functional route:" . Yaf_Dispatcher::getInstance()->getRouter()->getCurrentRoute();
		echo "<br/>\n";
	}

	public function dispatchLoopStartup(Yaf_Request_Abstract $request, Yaf_Response_Abstract $response) {
		echo "Plugin DispatchLoopStartup called <br/>\n";
	}

	public function preDispatch(Yaf_Request_Abstract $request, Yaf_Response_Abstract $response) {
		echo "Plugin PreDispatch called <br/>\n";
	}

	public function postDispatch(Yaf_Request_Abstract $request, Yaf_Response_Abstract $response) {
		echo "Plugin postDispatch called <br/>\n";
	}

	public function dispatchLoopShutdown(Yaf_Request_Abstract $request, Yaf_Response_Abstract $response) {
		echo "Plugin DispatchLoopShutdown called <br/>\n";
	}

	public function preResponse(Yaf_Request_Abstract $request, Yaf_Response_Abstract $response) {
		echo "Plugin PreResponse called <br/>\n";
		echo "Response is ready to send<br/>\n";
	}

}