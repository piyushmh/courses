package jacobi;

import java.io.IOException;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;

public class PageRankBlockMapper extends Mapper<LongWritable, Text, Text, Text> {

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

	// lookup the block ID in a hardcoded list based on the node ID
	public static int lookupBlockID(int nodeID) {
		int partitionSize = 10000;
		int[] blockBoundaries = { 0, 10328, 20373, 30629, 40645,
				50462, 60841, 70591, 80118, 90497, 100501, 110567, 120945,
				130999, 140574, 150953, 161332, 171154, 181514, 191625, 202004,
				212383, 222762, 232593, 242878, 252938, 263149, 273210, 283473,
				293255, 303043, 313370, 323522, 333883, 343663, 353645, 363929,
				374236, 384554, 394929, 404712, 414617, 424747, 434707, 444489,
				454285, 464398, 474196, 484050, 493968, 503752, 514131, 524510,
				534709, 545088, 555467, 565846, 576225, 586604, 596585, 606367,
				616148, 626448, 636240, 646022, 655804, 665666, 675448, 685230 };

		int blockID = (int) Math.floor(nodeID / partitionSize);
		int testBoundary = blockBoundaries[blockID];
		if (nodeID < testBoundary) {
			blockID--;
		}
		
		return blockID;
	}
}
