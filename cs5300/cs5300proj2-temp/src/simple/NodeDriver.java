package simple;


import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * Simple MapReduce Over Nodes
 * 
 */

public class NodeDriver {

	// use a hadoop counter to track the total residual error so we can compute
	// the average at the end
	public static enum ProjectCounters {
		RESIDUAL_ERROR
	};

	public static final int totalNodes = 685230; // total # of nodes in the
													// input set
	public static final int precision = 10000; // this allows us to store the
												// residual error value in the
												// counter as a long
	
	private static final int NUM_ITERATIONS = 6; // # of iterations to run

	public static void main(String[] args) throws Exception {

		System.out.println(args[0]);
		System.out.println(args[1]);

		if (args.length != 2) {
			System.err
					.println("Usage (no trailing slashes): project2.NodeDriver s3n://<in filename> s3n://<out bucket>");
			System.exit(2);
		}
		String inputFile = args[0];
		String outputPath = args[1];

		for (int i = 0; i < NUM_ITERATIONS; i++) {
			Job job = new Job();
			// Set a unique job name
			job.setJobName("pagerank_" + (i + 1));
			job.setJarByClass(simple.NodeDriver.class);

			// Set Mapper and Reducer class
			job.setMapperClass(simple.LeMapper.class);
			job.setReducerClass(simple.LeReducer.class);

			// set the classes for output key and value
			job.setOutputKeyClass(Text.class);
			job.setOutputValueClass(Text.class);

			// on the initial pass, use the preprocessed input file
			// note that we use the default input format which is
			// TextInputFormat (each record is a line of input)
			if (i == 0) {
				FileInputFormat.addInputPath(job, new Path(inputFile));
				// otherwise use the output of the last pass as our input
			} else {
				FileInputFormat.addInputPath(job, new Path(outputPath + "/temp"
						+ i));
			}
			// set the output file path
			FileOutputFormat.setOutputPath(job, new Path(outputPath + "/temp"
					+ (i + 1)));

			// execute the job and wait for completion before starting the next
			// pass
			job.waitForCompletion(true);

			// before starting the next pass, compute the avg residual error for
			// this pass and print it out
			float residualErrorAvg = job.getCounters()
					.findCounter(ProjectCounters.RESIDUAL_ERROR).getValue();
			residualErrorAvg = (residualErrorAvg / precision) / totalNodes;
			String residualErrorString = String
					.format("%.4f", residualErrorAvg);
			System.out.println("Residual error for iteration " + i + ": "
					+ residualErrorString);

			// reset the counter for the next round
			job.getCounters().findCounter(ProjectCounters.RESIDUAL_ERROR)
					.setValue(0L);
		}

	}

}
