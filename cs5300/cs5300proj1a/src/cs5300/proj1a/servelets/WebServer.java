package cs5300.proj1a.servelets;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.Date;
import java.util.ArrayList;
import java.util.logging.Logger;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import cs5300.proj1a.objects.HostInformation;
import cs5300.proj1a.objects.Metadata;
import cs5300.proj1a.objects.SessionObject;
import cs5300.proj1a.sessiontable.SessionTable;
import cs5300.proj1a.utils.Utils;
import cs5300.proj1b.managers.CookieManager;
import cs5300.proj1b.managers.RPCCommunicationManager;
import cs5300.proj1b.managers.ServerViewManager;
import cs5300.proj1b.managers.SessionManager;
import cs5300.proj1b.managers.SimpleDBInteractionManager;

/**
 * Servlet implementation class SessionManager
 * Author - Piyush
 */
@WebServlet("/SessionManager")
public class WebServer extends HttpServlet {
	
	private Logger LOGGER = Logger.getLogger(WebServer.class.getName());
	
	private static final long serialVersionUID = 1L;

	/*String used to represent parameter*/
	private static final String PARAM_STRING = "param";

	/*Cookie*/
	private static final String COOKIE_STRING = "CS5300PROJ1SESSIONPM489";

	private static final String PAGE_LOAD = "pageload";

	private static final String REFRESH = "refresh";

	private static final String REPLACE = "replace";

	private static final String LOGOUT = "logout";
	
	private static String MESSAGE = "This is a default CS 5300 message";

	private static int COOKIE_AGE = 60*5;

	public static SessionTable sessionTable = new SessionTable();

	public static HostInformation hostInfo  = new HostInformation();

	public static ServerViewManager viewManager = new ServerViewManager();

	public static RPCCommunicationManager rpcManager = new RPCCommunicationManager();

	public static SessionManager sessionManager = new SessionManager();

	public static CookieManager cookieManager = new CookieManager();
	
	public static SimpleDBInteractionManager simpleDBManager = new SimpleDBInteractionManager();

	public WebServer() {
		super();
	}

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

		response.setContentType("text/html");
		PrintWriter responsewriter = response.getWriter();
		String param = request.getParameter(PARAM_STRING);
		String cookiecontent = null;
		Cookie [] cookies = request.getCookies();
		for( Cookie cookie : cookies){
			if( cookie.getName().equals(COOKIE_STRING)){
				cookiecontent = cookie.getValue();
				break;
			}
		}
		LOGGER.info("Size of the session table is :" + sessionTable.getSize());
		LOGGER.info("Cookie content from the browser cookie is : " + cookiecontent);
		LOGGER.info("Parameter received from the browser is :"  + param);
		String servermessage = "";
		long newTime = Utils.getCurrentTimeInMillis() + COOKIE_AGE * 1000;
		int newcookieAge = COOKIE_AGE; 
		Metadata metadataobject = sessionManager.fetchSession(cookiecontent, rpcManager, viewManager, cookieManager, sessionTable, hostInfo);
		
		SessionObject sessionobject = null;
		int servernum = -1;
		
		if( metadataobject!= null){
			sessionobject = metadataobject.getSessionObject();
			servernum = metadataobject.getServernum();
		}else{
			assert(false);
		}
		
		//ArrayList<String> replicatedServers = metadataobject.getReplicatedServers();
		
		LOGGER.info("Retrieved session from session table : " + sessionobject);
		if( sessionobject!= null){
			if ( Utils.hasSessionExpired(sessionobject.getExpirationTime())){
				sessionManager.deleteSession(sessionobject.getSessionId(), sessionTable);
				sessionobject = null;
				servermessage = "SESSIONTIMEDOUT";
			}
		}else{
			if( cookiecontent!= null){
				servermessage = "SESSIONTIMEDOUT";
			}
		}

		if( sessionobject != null){

			if( param.equalsIgnoreCase(PAGE_LOAD)){

				LOGGER.info("Inside page load");		
				sessionobject.incrementVersionNumber();
				sessionobject.setExpirationTime(newTime);

			}else if (param.equalsIgnoreCase(REFRESH)){

				LOGGER.info("Inside page refresh");
				sessionobject.incrementVersionNumber();
				sessionobject.setExpirationTime(newTime);

			}else if (param.equalsIgnoreCase(REPLACE)){

				LOGGER.info("Inside replace");
				sessionobject.incrementVersionNumber();
				sessionobject.setExpirationTime(newTime);
				String replacementmessage = request.getParameter("message");
				sessionobject.setMessage(replacementmessage);
			
			}else if (param.equalsIgnoreCase(LOGOUT)){
				LOGGER.info("Inside logout");
				sessionManager.deleteSession(sessionobject.getSessionId(), sessionTable);
				newcookieAge = 0;
			}else{
				LOGGER.info("Shouldn't be here");
			}
			
		}else{
			
			if( ! param.equalsIgnoreCase(LOGOUT)){
				sessionobject = new SessionObject(MESSAGE, newTime, hostInfo);
				LOGGER.info("Constructed new session object with session id : " 
						+ sessionobject.getSessionId());
			}
		}
		
		if( param == null || !param.equalsIgnoreCase(LOGOUT)){
			
			assert(sessionobject!=null);
			ArrayList<String> replicatedservers = sessionManager.storeSessionWithReplication(
					sessionobject, sessionTable, hostInfo, viewManager, rpcManager);
		
			String cookiestring = cookieManager.generateCookieString(sessionobject, replicatedservers);
			Cookie c = new Cookie(COOKIE_STRING, cookiestring);
			c.setMaxAge(newcookieAge);
			response.addCookie(c);
			
			LOGGER.info("Replicated Servers : " + Utils.generateDelimitedStringFromList(',', replicatedservers));
			String retstring = sessionobject.getMessage() 
					+ "|" + sessionobject.getExpirationTime().toString() 
					+ "|" + new Date(sessionobject.getExpirationTimeMilliSecond()+ SessionManager.DELTA_MILLI_SECONDS ).toString() 
					+ "|" + sessionobject.getVersion()
					+ "|" + hostInfo.getIPAddress() + "|" + Utils.generateDelimitedStringFromList(',', replicatedservers)
					+ "|" + Utils.generateDelimitedStringFromList(',', new ArrayList<String>(viewManager.getServerViewList())) 
					+ "|" + servernum + "|" + servermessage;
			
			responsewriter.write(retstring);
			
			LOGGER.info(retstring);
		}

}// end of doGet

/**
 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
 */
protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
	// TODO Auto-generated method stub
}

}
