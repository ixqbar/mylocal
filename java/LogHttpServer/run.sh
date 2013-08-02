#/bin/sh

#You can usage like java -jar HttpServer.jar Options
#Options Detail:
#	--address                 default 0.0.0.0
#	--port                    default 2011
#	--biLogPath               default /var/logs
#	--httpLogPath             default /var/logs
#	--serverLogIndexFile      default /var/logs/serverLogIndex.log
#	--biLogIndexFile          default /var/logs/biLogIndex.log
#	--biLogToCompress         like 0 or 1 default 1
#	--biLogFormat             like 0 or 1 default 1
#	--httpLogTocompress       like 0 or 1 default 0
#	--delBiLogAfterCompress   like 0 or 1 default 1
#	--delHttpLogAfterCompress like 0 or 1 default 0
#   --logFlushToFilePerNum    default 3600
#	--biLogMaxInterval        default 3600
#	--biPerLogMaxNum          default 10000
#	--httpPerLogMaxNum        default 10000
#	--serverLogToFile         default 0
#	--timeZone                default Asia/Shanghai
#	--httLogLevel             default all you can usage like debug,info,warn,error,except

java -jar LogHttpServer.jar --address=127.0.0.1 --port=2011 --biLogPath=/home/venkman/desktop/httpserver/logs --httpLogPath=/home/venkman/desktop/httpserver/logs --biLogIndexFile=/home/venkman/desktop/httpserver/biIndex.log --serverLogIndexFile=/home/venkman/desktop/httpserver/serverIndex.log --serverLogToFile=1
