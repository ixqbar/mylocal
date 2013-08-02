package com.bi.core;

import java.io.IOException;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;

public interface Handler {
	void execute(Selector selector, SelectionKey key) throws IOException;  
}
