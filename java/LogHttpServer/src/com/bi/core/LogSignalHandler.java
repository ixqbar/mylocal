package com.bi.core;

import com.bi.LogHttpServer;

import sun.misc.Signal;
import sun.misc.SignalHandler;

public class LogSignalHandler implements SignalHandler {
	
	@Override
	public void handle(Signal signalName) {
		Logger.warn("catch signal `%s`", signalName);
		LogHttpServer.isStoped = true;
	}

}
