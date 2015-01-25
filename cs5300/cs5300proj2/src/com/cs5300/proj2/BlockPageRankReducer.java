package com.cs5300.proj2;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;

import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.log4j.Logger;

import com.cs5300.proj2.BlockPageRank.ProjectCounters;

/**
 * This is the reducer implementation for the blocked page rank algorithm
 * 
 * @author piyush
 *
 */
public class BlockPageRankReducer extends Reducer<Text, Text, Text, Text> {

	Logger logger = Logger.getLogger(BlockPageRankReducer.class);

	//this is for storing the new page rank values
	private HashMap<String, Double> newPR = new HashMap<String, Double>();

	//this is for storing the mapping from node id to node object
	private HashMap<String, Node> nodeIdToNodeMap = new HashMap<String, Node>();

	//this is the mapping from node in the block to incoming edges within the reducer block
	private HashMap<String, ArrayList<String>> BE = new HashMap<String, ArrayList<String>>();

	//this is the mapping from nodes in the block to incoming edges from other blocks
	private HashMap<String, Double> BC = new HashMap<String, Double>();

	private ArrayList<String> vList = new ArrayList<String>();

	private double dampingFactor = 0.85;
	private double randomJumpFactor = (1.0 - dampingFactor) / Constants.TOTAL_NODES;
	private int maxIterations = 5;
	private Double threshold = 0.001; 

	//this is called once per block id 
	protected void reduce(Text key, Iterable<Text> values, Context context)
			throws IOException, InterruptedException {


		//this is because the same reducer instance can be used for multiple keys, so
		//we must clear them before reading values
		newPR.clear();
		nodeIdToNodeMap.clear();
		BE.clear();
		BC.clear();
		vList.clear();
		
		Integer maxnode = 0; //this is for keeping track of the max node in the block
		Iterator<Text> iter = values.iterator(); 

		while( iter.hasNext()){ //read all values one by one

			Text input = iter.next();
			String [] valuearray = input.toString().split("\\s+");

			if( "PR".equals(valuearray[0].trim())){

				//format is PR NodeID Pagerank edgelist
				Node node = new Node();
				node.setNodeID(valuearray[1].trim());
				node.setPageRank(Double.parseDouble(valuearray[2].trim()));
				vList.add(valuearray[1].trim());
				newPR.put(node.getNodeID(), node.getPageRank());

				if( valuearray.length == 4){
					node.setEdgeList(valuearray[3].trim());
					node.setDegrees(valuearray[3].trim().split(",").length);
				}

				nodeIdToNodeMap.put(node.getNodeID(), node);
				maxnode = Math.max(maxnode, Integer.parseInt(node.getNodeID()));

			}else if ("BE".equals(valuearray[0].trim())){

				//format is BE edge node 
				if( ! BE.containsKey(valuearray[2].trim())){
					BE.put(valuearray[2].trim(), new ArrayList<String>());
				}

				BE.get(valuearray[2].trim()).add(valuearray[1].trim());

			}else if ("BC".equals(valuearray[0].trim())){

				//format is BC edge Node EdgePagerank
				if ( ! BC.containsKey(valuearray[2].trim())){
					BC.put(valuearray[2].trim(), 0.0);
				}

				double tempVal =  BC.get(valuearray[2].trim()) + 
						Double.parseDouble(valuearray[3].trim()) ; 
				BC.put(valuearray[2].trim(), tempVal);
			}

		}

		assert(vList.size() == this.nodeIdToNodeMap.keySet().size());

		double residualerroriteration  = 0.0;
		for( int i = 0 ; i < maxIterations ; i++){

			residualerroriteration = iterateBlockOnce();

			if( residualerroriteration < threshold){
				break;
			}
		}


		double residualerror = 0.0;
		for( String node : this.nodeIdToNodeMap.keySet()){

			residualerror+= 
					Math.abs((newPR.get(node) - this.nodeIdToNodeMap.get(node).getPageRank())) 
					/ newPR.get(node);

		}

		residualerror = residualerror / this.nodeIdToNodeMap.keySet().size();

		long residualLong = (long)residualerror * Constants.RESIDUAL_OFFSET;
		context.getCounter(ProjectCounters.RESIDUAL_ERROR).increment(residualLong);

		for( String node : this.nodeIdToNodeMap.keySet()){
			String output = newPR.get(node) + " " + this.nodeIdToNodeMap.get(node)
					.getDegrees() + " " + this.nodeIdToNodeMap.get(node).getEdgeList();

			Text outputkey = new Text(node);
			Text outputtext = new Text(output);
			context.write(outputkey, outputtext);
			if (node.equals(maxnode.toString())) {
				//System.out.println("Block:" + key + " node:" + node + " pageRank:" + 
				//		newPR.get(node));
			}
		}

		cleanup(context);

	}


	private double iterateBlockOnce(){

		Set<String> nodeset = this.nodeIdToNodeMap.keySet();
		double residualError = 0.0;

		HashMap<String, Double> tempmap = new HashMap<String, Double>();
		for (String node : nodeset) {

			double oldpagerank = this.newPR.get(node);
			double newpagerank = 0.0;

			if( BE.containsKey(node)){
				ArrayList<String> edgelist = BE.get(node);

				for (String edge: edgelist) {
					newpagerank += ( this.newPR.get(edge) / this.nodeIdToNodeMap.get(edge).getDegrees());
				}
			}


			if( BC.containsKey(node)){
				newpagerank += BC.get(node);
			}

			newpagerank = (newpagerank* dampingFactor) + randomJumpFactor;

			//newPR.put(node, newpagerank);
			tempmap.put(node, newpagerank);
			residualError += Math.abs(newpagerank - oldpagerank) / newpagerank;
		}

		this.newPR = tempmap;
		residualError = residualError / nodeset.size();
		return residualError;

	}
	
	protected double IterateBlockOnce() {
		// used to iterate through the BE list of edges
		ArrayList<String> uList = new ArrayList<String>();
		// npr = current PageRank value of Node v
		double npr = 0.0f;
		// r = sum of PR[u]/deg[u] for boundary nodes pointing to v
		double r = 0.0f;
		// resErr = the avg residual error for this iteration
		double resErr = 0.0f;

		for (String v : vList) {
			npr = 0.0f;
			double prevPR = newPR.get(v);

			// calculate newPR using PR data from any BE nodes for this node
			if (BE.containsKey(v)) {
				uList = BE.get(v);
				for (String u : uList) {
					// npr += PR[u] / deg(u);
					Node uNode = this.nodeIdToNodeMap.get(u);
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
			newPR.put(v, npr);
			// track the sum of the residual errors
			resErr += Math.abs(prevPR - npr) / npr;
		}
		// calculate the average residual error and return it
		resErr = resErr / vList.size();
		return resErr;
	}

}