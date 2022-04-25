cd crawl/crawl-ref/source/
./crawl -name aiagent -rc .rcs/aiagent.rc -macro ./rcs/aiagent.macro -morgue ./rcs/aiagent -sprint -webtiles-socket ./rcs/aiagent:test.sock -await-connection

./crawl -name midca -rc .rcs/midca.rc -macro ./rcs/midca.macro -morgue ./rcs/midca -sprint -webtiles-socket ./rcs/midca:crawl.sock -await-connection

