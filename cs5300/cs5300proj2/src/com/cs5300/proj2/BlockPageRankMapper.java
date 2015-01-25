package com.cs5300.proj2;

import java.io.IOException;

import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.log4j.Logger;


public class BlockPageRankMapper extends Mapper<LongWritable, Text, Text, Text>{

	Logger logger = Logger.getLogger(BlockPageRankMapper.class);

	protected void map(LongWritable key, Text value, Context context)
			throws IOException, InterruptedException {

		//input format  : nodeid pagerank deg(nodeid) edgelist  [ everything is space separated]

		String line = value.toString();
		line = line.trim();
		String [] temp = line.split("\\s+");

		Integer nodeid = Integer.parseInt(temp[0].trim());
		Double pagerank  = Double.parseDouble(temp[1].trim());
		Integer degree = Integer.parseInt(temp[2].trim());
		Integer blockid = lookupBlockID(nodeid);
		String edgelist = ""; 

		if( temp.length == 4){
			edgelist = temp[3].trim();
		}

		Text mapperkey = new Text(blockid.toString());
		Text mappervalue = new Text("PR " + 
									nodeid.toString() +
									" " + 
									pagerank.toString() +
									" " + 
									edgelist
								);

		//this is the old page rank value and edge list for reconstructing the graph at reducer
		context.write(mapperkey, mappervalue); 

		if( ! edgelist.equals("")){	
			String [] edgelistarray = edgelist.split(",");
			
			for (String edge : edgelistarray) {
				Integer blockIdedge = new Integer( lookupBlockID(Integer.parseInt(edge)));				
				mapperkey = new Text(blockIdedge.toString());

				if( blockIdedge.equals(blockid)){ //same block

					mappervalue = new Text("BE " + nodeid.toString() + " " + edge );

				}else{

					Double pagerankratio = new Double( pagerank / degree);
					mappervalue = new Text("BC " + nodeid.toString() + " " + edge + 
							" " + pagerankratio.toString());

				}

				context.write(mapperkey, mappervalue);
			}

		}

	}


	// lookup the block ID in a hard coded list based on the node ID
	// this runs in O(1) since we have fixed the boundaries
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
