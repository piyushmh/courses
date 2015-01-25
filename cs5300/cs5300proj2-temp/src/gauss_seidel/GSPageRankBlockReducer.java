package gauss_seidel;

import java.io.IOException;
import java.util.*;

import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import preprocess.NodeData;


public class GSPageRankBlockReducer extends Reducer<Text, Text, Text, Text> {

	private HashMap<String, Double> newPR = new HashMap<String, Double>();
	private HashMap<String, ArrayList<String>> BE = new HashMap<String, ArrayList<String>>();
	private HashMap<String, Double> BC = new HashMap<String, Double>();
	private HashMap<String, NodeData> nodeDataMap = new HashMap<String, NodeData>();
	private ArrayList<String> vList = new ArrayList<String>();
	private Double dampingFactor = (double) 0.85;
	private Double randomJumpFactor = (1 - dampingFactor) / GSPageRankBlock.totalNodes;
	//private int maxIterations = 5;
	private Double threshold = 0.001;
	
	protected void reduce(Text key, Iterable<Text> values, Context context)
			throws IOException, InterruptedException {
		
		Iterator<Text> itr = values.iterator();
		Text input = new Text();
		String[] inputTokens = null;
		
		// initialize/reset all variables
		Double pageRankOld =  0.0;
		Double residualError =  0.0;
		
		String output = "";
		Integer maxNode = 0;
		
		ArrayList<String> temp = new ArrayList<String>();
		Double tempBC = 0.0;
		vList.clear();
		newPR.clear();
		BE.clear();
		BC.clear();
		nodeDataMap.clear();	
		
		while (itr.hasNext()) {
			input = itr.next();
			inputTokens = input.toString().split(" ");			
			// if first element is PR, it is the node ID, previous pagerank and outgoing edgelist for this node
			if (inputTokens[0].equals("PR")) {
				String nodeID = inputTokens[1];
				pageRankOld = Double.parseDouble(inputTokens[2]);
				newPR.put(nodeID, pageRankOld);
				NodeData node = new NodeData();
				node.setNodeID(nodeID);
				node.setPageRank(pageRankOld);
				if (inputTokens.length == 4) {
					node.setEdgeList(inputTokens[3]);
					node.setDegrees(inputTokens[3].split(",").length);
				}
				vList.add(nodeID);
				nodeDataMap.put(nodeID, node);
				// keep track of the max nodeID for this block
				if (Integer.parseInt(nodeID) > maxNode) {
					maxNode = Integer.parseInt(nodeID);
				}
				
			// if BE, it is an in-block edge
			} else if (inputTokens[0].equals("BE")) {			
				
				if (BE.containsKey(inputTokens[2])) {
					//Initialize BC for this v
					temp = BE.get(inputTokens[2]);
				} else {
					temp = new ArrayList<String>();
				}
				temp.add(inputTokens[1]);
				BE.put(inputTokens[2], temp);
				
			// if BC, it is an incoming node from outside of the block
			} else if (inputTokens[0].equals("BC")) {
				if (BC.containsKey(inputTokens[2])) {
					//Initialize BC for this v
					tempBC = BC.get(inputTokens[2]);
				} else {
					tempBC = 0.0;
				}
				tempBC += Double.parseDouble(inputTokens[3]);
				BC.put(inputTokens[2], tempBC);
			}		
		}
		
		int i = 0;
		do {
			i++;
			residualError = IterateBlockOnce();
			//System.out.println("Block " + key + " pass " + i + " resError:" + residualError);
		} while (residualError > threshold);

		//i < maxIterations && 
				
		// compute the ultimate residual error for each node in this block
		residualError = 0.0;
		for (String v : vList) {
			NodeData node = nodeDataMap.get(v);
			residualError += Math.abs(node.getPageRank() - newPR.get(v)) / newPR.get(v);
		}
		residualError = residualError / vList.size();
		//System.out.println("Block " + key + " overall resError for iteration: " + residualError);
		
		// add the residual error to the counter that is tracking the overall sum (must be expressed as a long value)
		long residualAsLong = (long) Math.floor(residualError * GSPageRankBlock.precision);
		long numberOfIterations = (long) ( i);
		context.getCounter(GSPageRankBlock.ProjectCounters.RESIDUAL_ERROR).increment(residualAsLong);
		
		context.getCounter(GSPageRankBlock.ProjectCounters.AVERAGE_ITERATIONS).increment(numberOfIterations);
		
		// output should be 
		//	key:nodeID (for this node)
		//	value:<pageRankNew> <degrees> <comma-separated outgoing edgeList>
		for (String v : vList) {
			NodeData node = nodeDataMap.get(v);
			output = newPR.get(v) + " " + node.getDegrees() + " " + node.getEdgeList();
			Text outputText = new Text(output);
			Text outputKey = new Text(v);
			context.write(outputKey, outputText);
			if (v.equals(maxNode.toString())) {
				System.out.println("Block:" + key + " node:" + v + " pageRank:" + newPR.get(v));
			}
		}
			
		cleanup(context);
	}
	

	// v is all nodes within this block B
	// u is all nodes pointing to this set of v
	// some u are inside the block as well, those are in BE
	// some u are outside the block, those are in BC
	// BE = the Edges from Nodes in Block B
    // BC = the Boundary Conditions
	// NPR[v] = Next PageRank value of Node v
	protected double IterateBlockOnce() {
		// used to iterate through the BE list of edges
		ArrayList<String> uList = new ArrayList<String>();
		// npr = current PageRank value of Node v
		double npr = 0.0;
		// r = sum of PR[u]/deg[u] for boundary nodes pointing to v
		double r = 0.0;
		// resErr = the avg residual error for this iteration
		double resErr = 0.0;
		
		//HashMap<String, Double> tempmap = new HashMap<String, Double>();
		for (String v : vList) {
			npr = 0.0f;
			double prevPR = newPR.get(v);

			// calculate newPR using PR data from any BE nodes for this node
			if (BE.containsKey(v)) {
				uList = BE.get(v);
				for (String u : uList) {
					// npr += PR[u] / deg(u);
					NodeData uNode = nodeDataMap.get(u);
					npr += (newPR.get(u) / uNode.getDegrees());
				}
			}
			
			// add on any PR from nodes outside the block (BC)
			if (BC.containsKey(v)) {
				r = BC.get(v);
				npr += r;
			}
	
	        //NPR[v] = d*NPR[v] + (1-d)/N;
			npr = (dampingFactor * npr) + randomJumpFactor;
			// update the global newPR map
			//tempmap.put(v, npr);
			newPR.put(v, npr);
			// track the sum of the residual errors
			resErr += Math.abs(prevPR - npr) / npr;
		}
		// calculate the average residual error and return it
		//newPR = tempmap;
		resErr = resErr / vList.size();
		return resErr;
	}

}

