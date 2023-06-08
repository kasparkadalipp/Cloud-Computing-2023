import sys
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler

if __name__ == "__main__":

    #check the number of arguments
    if len(sys.argv) != 2:
        print("Usage: dataframe_example.py <input folder> ")
        exit(-1)

    #Set a name for the application
    appName = "DataFrame Example"

    #Set the input folder location to the first argument of the application
    #NB! sys.argv[0] is the path/name of the script file
    input_folder = sys.argv[1]

    #create a new Spark application and get the Spark session object
    spark = SparkSession.builder.appName(appName).getOrCreate()

    #read in the CSV dataset as a DataFrame
    #inferSchema option forces Spark to automatically specify data column types
    #header option forces Spark to automatically fetch column names from the first line in the dataset files
    dataset = spark.read \
                  .option("inferSchema", True) \
                  .option("header", True) \
                  .csv(input_folder)

    #Show 10 rows without truncating lines.
    #review content might be a multi-line string.
    dataset.show(10, False)

    #Show dataset schema/structure with filed names and types
    dataset.printSchema()

    # Filter out outliers
    dataset = dataset.na.fill(0)\
        .filter("0 < `Wind Speed` and `Wind Speed` < 35")\
        .filter("0 < Humidity and  Humidity < 100")\
        .select("Humidity", "Wind Speed")

    # Create a vector assembler
    assembler = VectorAssembler(inputCols=["Humidity", "Wind Speed"], outputCol="features")

    # Transform the dataset to a vectorized form
    dataset = assembler.transform(dataset)

    # Fit KMeans model to the dataset
    model = KMeans(k=4, seed=42).fit(dataset)

    # Compute clusters
    dataset = model.transform(dataset).withColumnRenamed("prediction", "cluster id")

    # Convert Spark DataFrame to Pandas DataFrame
    pandas_df = dataset.toPandas()

    # Generate scatter plot
    colors = ["red", "green", "blue", "purple"]
    categorical_values = pandas_df["cluster id"].unique()
    pandas_df.plot.scatter(x="Humidity", y="Wind Speed",
                    c=pandas_df["cluster id"].apply(lambda x: colors[list(categorical_values).index(x)]))

    # Display the graph visually
    plt.title("Clusters")
    plt.show()

    # Display dataset
    dataset.show()

    #Stop Spark session
    #spark.stop()