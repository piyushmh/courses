package randomblock;

import java.io.IOException;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;

public class RandomPageRankBlockMapper extends Mapper<LongWritable, Text, Text, Text> {

	protected void map(LongWritable key, Text value, Context context)
			throws IOException, InterruptedException {

		// value is in the format['node','PageRank
		// Estimate','degrees(node)','outgoing edgelist'] delimiter = whitespace

		String line = value.toString();
		line = line.trim();
		String[] temp = line.split("\\s+");

		Integer node = new Integer(temp[0]);
		Float pageRank = new Float(temp[1]);
		Integer degree = 0;
		if( temp.length > 2){
			degree = new Integer(temp[2]);
		}
		
		// there may not be any outgoing edges
		String edgeList = "";
		if (temp.length > 3) {
			edgeList = temp[3];
		}
		
		// find the blockID for this node
		Integer blockID = new Integer(lookupBlockID(node));

		// for this node, value to pass is nodeID, previous pageRank and outgoing edgelist
		// map key:blockID value:PR nodeID pageRank <outgoing edgelist>
		Text mapperKey = new Text(blockID.toString());
		Text mapperValue = new Text("PR " + node.toString() + " " + String.valueOf(pageRank) + " "
				+ edgeList);
		context.write(mapperKey, mapperValue);

		// find the blockID for the outgoing edge
		// if the outgoing edge lies within a different block, we also need to send our
		// node's info to that block with a label of "BC" (boundary condition)
		if ( ! edgeList.equals("")) {
			String[] edgeListArray = edgeList.split(",");

			for (int i = 0; i < edgeListArray.length; i++) {
				Integer blockIDOut = new Integer(lookupBlockID(Integer.parseInt(edgeListArray[i])));
				mapperKey = new Text(blockIDOut.toString());
				// the 2 nodes are in the same block
				if (blockIDOut.equals(blockID)) {
					// map key:blockID value:BE node nodeOut
					mapperValue = new Text("BE " + node.toString() + " " + edgeListArray[i]);
				// this is an edge node - the incoming node is in another block
				} else {
					// the pageRankFactor is used by the reducer to calculate the new
					// pageRank for the outgoing edges
					Float pageRankFactor = new Float(pageRank / degree);
					String pageRankFactorString = String.valueOf(pageRankFactor);
					// map key:blockID value:BC node nodeOut pageRankFactor 
					mapperValue = new Text("BC " + node.toString() + " " + edgeListArray[i] + " " + pageRankFactorString);
				}
				context.write(mapperKey, mapperValue);
			}
		}
	}

	public static int lookupBlockID(long nodeID) {
        return (int) (hash(nodeID) % RandomPageRankBlock.totalBlocks);
    }
	
	
    public static final long hash(long nodeID){
        nodeID ^= (nodeID << 13);
        nodeID ^= (nodeID >>> 17);
        nodeID ^= (nodeID << 5);
        return nodeID;
    }
}
