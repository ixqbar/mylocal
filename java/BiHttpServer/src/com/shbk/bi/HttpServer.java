package com.shbk.bi;

import java.io.IOException;

import com.shbk.bi.core.*;

public class HttpServer {

	/**
	 * @param args
	 */
	public static void main(String[] args) throws IOException {
		System.out.println("running .....");
		TcpServer.run(8080);
		System.out.println("end");
	}

}
