#/bin/sh

#You can usage like java -jar HttpServer.jar Options
#Options Detail:
#	--address                 default 0.0.0.0
#	--port                    default 2011
#	--biLogPath               default /var/logs
#	--httpLogPath             default /var/logs
#	--biLogToCompress         like 0 or 1 default 1
#	--httpLogTocompress       like 0 or 1 default 0
#	--delBiLogAfterCompress   like 0 or 1 default 1
#	--delHttpLogAfterCompress like 0 or 1 default 0
#	--biPerLogMaxNum          default 10000
#	--httpPerLogMaxNum        default 10000
#	--serverLogToFile         default 0
#	
java -jar HttpServer.jar --address=127.0.0.1 --port=8080 --biLogPath=/Users/venkman/Desktop/HttpServer/logs --httpLogPath=/Users/venkman/Desktop/HttpServer/logs
