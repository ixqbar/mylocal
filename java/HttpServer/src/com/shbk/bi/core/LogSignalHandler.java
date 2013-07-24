package com.shbk.bi.core;

import com.shbk.bi.HttpServer;

import sun.misc.Signal;
import sun.misc.SignalHandler;

public class LogSignalHandler implements SignalHandler {
	
	@Override
	public void handle(Signal signalName) {
		Logger.warn("catch signal `%s`", signalName);
		HttpServer.isStoped = true;
	}

}
