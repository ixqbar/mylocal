package com.bi.core;

import com.bi.LogTcpServer;

import sun.misc.Signal;
import sun.misc.SignalHandler;

public class LogSignalHandler implements SignalHandler {
	
	@Override
	public void handle(Signal signalName) {
		Logger.warn("catch signal `%s`", signalName);
		LogTcpServer.isStoped = true;
	}

}
