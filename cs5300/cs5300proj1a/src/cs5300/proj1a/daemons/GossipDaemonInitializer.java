package cs5300.proj1a.daemons;

import java.util.logging.Logger;

import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;
import javax.servlet.annotation.WebListener;


//Author - Piyush

@WebListener
public class GossipDaemonInitializer implements ServletContextListener{

	private Logger LOGGER = Logger.getLogger(GossipDaemonInitializer.class.getName());
	
	@Override
	public void contextDestroyed(ServletContextEvent arg0) {
		// TODO Auto-generated method stub
		
	}
	@Override
	public void contextInitialized(ServletContextEvent arg0) {
		LOGGER.info("Starting gossip daemon initializer");
		Thread t = new Thread(new GossipDaemon());
		t.start();
	}

}
