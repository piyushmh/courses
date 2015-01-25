package cs5300.proj1a.daemons;

import java.util.logging.Logger;

import cs5300.proj1a.servelets.WebServer;

//Author - Piyush
public class GossipDaemon implements Runnable{

	private Logger LOGGER = Logger.getLogger(GossipDaemon.class.getName());
	
	private static final int GOSSIP_INTERVAL_SEC = 60;
	
	@Override
	public void run() {
		
		LOGGER.info("Starting gossip thread");
		WebServer.viewManager.addSelfToBootStrapServer();
		
		while(true){
			
			try {
				WebServer.viewManager.initiateViewGossip();
				int interval = (int) (GOSSIP_INTERVAL_SEC/2 + 
						(Math.random()* GOSSIP_INTERVAL_SEC) );
				
				LOGGER.info("Next gossip interval is :" + interval);
				Thread.sleep(interval * 1000);
				
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
		
	}

}
