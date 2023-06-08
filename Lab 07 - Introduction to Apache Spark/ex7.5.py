import sys
import string
from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name


def wordsRDD(line):
    for character in string.punctuation:
        line = line.replace(character, '')
    return line.lower().strip().split()

# define the top5 function
def top5(records):
    # sort the records by the second element of the tuple (count)
    sorted_records = sorted(records, key=lambda x: x[1], reverse=True)
    # return the top 5 records
    return sorted_records[:5]

if __name__ == "__main__":
    # Check the number of arguments
    if len(sys.argv) != 2:
        print("Usage: wordcount <file>", file=sys.stderr)
        exit(-1)

    # Set a name for the application
    appName = "PythonWordCount"

    # Set the input folder location to the firsta rgument of the application
    # NB! sys.argv[0] is the path/name of the script file
    input_folder = sys.argv[1]

    # Create a new Spark application and get the Spark session object
    spark = SparkSession.builder.appName(appName).getOrCreate()

    # Get the spark context object.
    sc = spark.sparkContext

    # Load input RDD from the data folder
    lines = spark.read.text(input_folder).select(input_file_name(), "value").rdd.map(tuple)


    # Take 5 records from the RDD and print them out
    records = lines.take(5)
    for record in records:
        print(record)

    # Apply RDD operations to compute WordCount
    # lines RDD contains lines from the input files.
    # Lets split the lines into words and use flatMap operation to generate an RDD of words.
    words = lines.flatMapValues(wordsRDD)

    # Transform words into (word, 1) Key & Value tuples
    pairs = words.map(lambda word: ((word[0], word[1]), 1))

    # Apply reduceBy key to group pairs by key/word and apply sum operation on the list of values inside each group
    # Apply our of customSum function as the aggregation function, but we could also have used "lambda x,y: x+y" function
    counts = pairs.reduceByKey(lambda x, y: x + y)

    # map each tuple to (file_name, (word, count))
    words_with_counts = counts.map(lambda x: (x[0][0], (x[0][1], x[1])))

    # group by file_name
    grouped = words_with_counts.groupByKey()

    # apply the top5 function to each group
    result = grouped.mapValues(top5)

    # save the output to multiple text files
    result.saveAsTextFile("ex7.5 output")

    # Read the data out of counts RDD
    # Output is a Python list (of (key, value) tuples)
    output = result.collect()

    # Print each key and value tuple inside output list
    for (word, count) in output:
        print(word, count)


    # Stop Spark session. It is not required when running locally through PyCharm.
    # spark.sparkContext.stop()
    # spark.stop()