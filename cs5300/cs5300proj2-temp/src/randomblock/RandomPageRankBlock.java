package randomblock;

import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;


// blocked version of pageRank calculations using MapReduce
public class RandomPageRankBlock {
	
	// use a hadoop counter to track the total residual error so we can compute the average at the end
	public static enum ProjectCounters {
	    RESIDUAL_ERROR,
	    AVERAGE_ITERATIONS
	};
	public static final int totalNodes = 685230;	// total # of nodes in the input set
	public static final int totalBlocks = 68;	// total # of blocks
	public static final int precision = 100000000;	// this allows us to store the residual error value in the counter as a long
	private static final Double thresholdError = 0.001;	// the threshold to determine whether or not we have converged
    
	public static void main(String[] args) throws Exception {
		
		String inputFile = "tmp/new_mapperinput.txt";
		String outputPath = "tmp/tmpoutput";
		int i = 0;
		double residualErrorAvg = 0.0;
		double averageIterations = 0.0;
		
		// iterate to convergence 
        do {
            Job job = new Job();
            // Set a unique job name
            job.setJobName("prBlock_"+ (i+1));
            job.setJarByClass(jacobi.PageRankBlock.class);

            // Set Mapper and Reducer class
            job.setMapperClass(randomblock.RandomPageRankBlockMapper.class);
            job.setReducerClass(randomblock.RandomPageRankBlockReducer.class);
            
            // set the classes for output key and value
            job.setOutputKeyClass(Text.class);
            job.setOutputValueClass(Text.class);
            
            // on the initial pass, use the preprocessed input file
            // note that we use the default input format which is TextInputFormat (each record is a line of input)
            if (i == 0) {
                FileInputFormat.addInputPath(job, new Path(inputFile)); 	
            // otherwise use the output of the last pass as our input
            } else {
            	FileInputFormat.addInputPath(job, new Path(outputPath + "/temp"+i)); 
            }
            // set the output file path
            FileOutputFormat.setOutputPath(job, new Path(outputPath + "/temp"+(i+1)));
            
            // execute the job and wait for completion before starting the next pass
            job.waitForCompletion(true);
            
            // before starting the next pass, compute the avg residual error and average iterations for this pass and print it out
            residualErrorAvg = (double) job.getCounters().findCounter(ProjectCounters.RESIDUAL_ERROR).getValue() / precision  / totalBlocks;
            //String residualErrorString = String.format("%.4f", residualErrorAvg);
            System.out.println("Residual error for iteration " + i + ": " + residualErrorAvg);
            
            averageIterations = (double) job.getCounters().findCounter(ProjectCounters.AVERAGE_ITERATIONS).getValue() / totalBlocks;
            //String averageIterationsString = String.format("%.f", averageIterations);
            System.out.println("Average number of in block iterations for interation " + i + ": "  + averageIterations);
            
            // reset the counter for the next round
            job.getCounters().findCounter(ProjectCounters.RESIDUAL_ERROR).setValue(0L);
            job.getCounters().findCounter(ProjectCounters.AVERAGE_ITERATIONS).setValue(0L);
            i++;
        } while (residualErrorAvg > thresholdError);
        
    }
}

