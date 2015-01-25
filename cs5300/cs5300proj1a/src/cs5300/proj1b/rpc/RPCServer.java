package cs5300.proj1b.rpc;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.util.logging.Logger;

import cs5300.proj1b.managers.RPCCommunicationManager;


/*
	An RPC protocol is basically just an agreed-upon format for call and reply messages. 
	For example, a call message could consist of :- 
		   - a unique callID for the call 
		   - an operation code.
		   - zero or more arguments, whose format is determined by the operation code.

	A reply message could consist of
	- the callID of the call to which this is a reply.
	- zero or more results, whose format is determined by the operation code in the call.
 */
/**
 * @author adityagaitonde
 *
 */
public class RPCServer implements Runnable{

	private static final int MAX_PACKET_LENGTH = 512;
	private static final int PORT = 5300;
	private Logger logger = Logger.getLogger(RPCServer.class.getName());
	
	DatagramSocket rpcSocket;

	public RPCServer() throws SocketException{
		rpcSocket = new DatagramSocket(PORT);
	}

	@Override
	public void run() {
		
		logger.info("RPC Server starting");
		
		while(true){
			try { 
				logger.info("RPC Server loop beginning");
				byte[] inBuf = new byte[MAX_PACKET_LENGTH];
				DatagramPacket recvPkt = new DatagramPacket(inBuf, inBuf.length);
				rpcSocket.receive(recvPkt);
				InetAddress returnAddr = recvPkt.getAddress();
				int returnPort = recvPkt.getPort();
				logger.info("Packet received from : " + returnAddr.getHostAddress() 
						+ " : " + returnPort);

				String newString = new String(recvPkt.getData());
				logger.info("Received Packet : "+ newString);

				String resultdata  = new RPCCommunicationManager().replyToClient(newString);

				byte[] outBuf = new byte[512];
				outBuf = resultdata.getBytes();
				DatagramPacket pckt = new DatagramPacket(outBuf, outBuf.length, returnAddr, returnPort);
				rpcSocket.send(pckt);

			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}
}
