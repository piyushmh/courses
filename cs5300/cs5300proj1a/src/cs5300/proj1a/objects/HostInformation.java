package cs5300.proj1a.objects;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.Enumeration;
import java.util.logging.Logger;

import cs5300.proj1a.daemons.RPCServerInitializer;

//Author - Piyush

public class HostInformation {
	
	private Logger LOGGER = Logger.getLogger(HostInformation.class.getName());

	private String ipAddress = "";

	public String getIPAddress(){

		if( "".equals(this.ipAddress)){
			try {
				findLocalIPAdrress();
			} catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

		return this.ipAddress;
	}

	private void findEC2IPAddress() throws Exception{
		Runtime rt = Runtime.getRuntime();
		Process proc = rt.exec("/opt/aws/bin/ec2-metadata --public-ipv4");
		InputStream s = proc.getInputStream();
		BufferedReader b = new BufferedReader(new InputStreamReader(s));
		String line = b.readLine();
		String [] lines = line.split(":");
		LOGGER.info(lines[1].trim());
		this.ipAddress = lines[1].trim();
		return;
	}

	private void findLocalIPAdrress(){

		try {
			String ip;
			Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
			while (interfaces.hasMoreElements()) {
				NetworkInterface iface = interfaces.nextElement();
				// filters out 127.0.0.1 and inactive interfaces
				if (iface.isLoopback() || !iface.isUp())
					continue;

				Enumeration<InetAddress> addresses = iface.getInetAddresses();
				while(addresses.hasMoreElements()) {
					InetAddress addr = addresses.nextElement();
					ip = addr.getHostAddress();
					if( isValidIP4Address(ip)){
						LOGGER.info(ip);
						this.ipAddress = ip;
						return;
					}
				}
			}
		} catch (SocketException e) {
			throw new RuntimeException(e);
		}
	}

	/*This is to prune IPv6 on local boxes, we are dealing with only ipv4*/
	public static boolean isValidIP4Address(String ipAddress) {
		if (ipAddress.matches("^(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})$")) {
			String[] groups = ipAddress.split("\\.");

			for (int i = 0; i <= 3; i++) {
				String segment = groups[i];
				if (segment == null || segment.length() <= 0) {
					return false;
				}
				int value = 0;
				try {
					value = Integer.parseInt(segment);
				} catch (NumberFormatException e) {
					return false;
				}
				if (value > 255) {
					return false;
				}
			}
			return true;
		}
		return false;
	}

}
