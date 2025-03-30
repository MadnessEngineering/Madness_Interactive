MachineLearningMastery.com
Making developers awesome at machine learning

Click to take the FREE Beginner's Guide to Data Science Crash-Course
Get Started
Blog
Topics
eBooks
FAQ
About
Contact
10 Python One-Liners That Will Boost Your Data Preparation Workflow
By Cornellius Yudha Wijaya on March 15, 2025 in Data Science 10
 Post Share
10 Python One-Liners That Will Boost Your Data Preparation Workflow
10 Python One-Liners That Will Boost Your Data Preparation Workflow
Image by Editor | Midjourney

Data preparation is a step within the data project lifecycle where we prepare the raw data for subsequent processes, such as data analysis and machine learning modeling. Data preparation can quite literally make or break your data project, as inadequate preparation will produce lousy output.

Given the importance of data preparation, we need a proper methodology for it. That’s why this article will explore how a simple one-liner Python code can boost your data preparation workflow.

1. Chain Transformation with Pipe
Data preparation often involves multiple transformations that are chained together in sequences. For example, not only must we filter rows, rename columns, and sort data, we must do so in that exact sequence for this specific project.

Multiple data transformations often make it messy as several codes must be processed in a cascade.

However, the Pandas

pipe()
function can make the transformation chain cleaner and readable. This eliminates the need for intermediate variables and allows the pipeline to process custom functions in an easily predefined order.

We can use the following one-liner to chain multiple functions for data preparation.

df = df.pipe(lambda d: d.rename(columns={'old_name': 'new_name'})).pipe(lambda d: d.query('new_name > 10'))
The code above shows how pipe facilitated function chaining with multiple custom functions and performed data transformation efficiently.

2. Pivot Data with Multiple Aggregation
Data pivot is a process of rearranging data into easier forms for the user to analyze and understand. The pivot is generally performed by transforming the data rows into columns and vice versa, with data aggregation of specific dimensions.

Sometimes the data preparations involve multiple aggregations within the data pivot depending on the analysis needs. This could become messy if we initiate and access an intermediate variable to do that.

Luckily, multiple aggregations can be easily performed in single line of Python using Pandas, once the pre-existing data has been created, of course. Let have a look.

Let’s say you have the following sample dataset with multiple columns, dimensions, and values.

import pandas as pd
import numpy as np
 
data = {
    'category': ['A', 'A', 'B', 'B', 'C', 'C'],
    'sub_category': ['X', 'Y', 'X', 'Y', 'X', 'Y'],
    'value': [10, 20, 30, 40, 50, 60]
}
df = pd.DataFrame(data)
Then, we want to prepare the data containing aggregation statistics, such as the average and sum for each category. To do that, we can use the following code.

pivot_df = df.pivot_table(index='category', columns='sub_category', values='value', aggfunc={'value': [np.mean, np.sum]})
Using the pivot table combined with the aggregation function, we can easily prepare our data without needing to execute multiple lines of code.

3. Time Series Resampling with Multiple Aggregation
Multiple aggregation is not only applicable to standard tabular data, but it’s also possible with the time series data, especially after data resampling. Time series data resampling is a method of data summarization in a time-frequent manner we want, such as daily, weekly, monthly, etc.

Once we resample the data, we should have multiple aggregations for the dataset to prepare them for any subsequent activity. To do all of the above, we can use the following one-liner.

df_resampled = df.set_index('timestamp').resample('D').agg({'value': ['mean', 'max'], 'count': 'sum'}).reset_index()
Simple replace the column name, like value() or count(), with the one you want. You can select any kind of aggregations you need as well.

4. Conditional Selection For Assigning Values
When working with raw data, we often need to create new features. For example, we may want to group employee salaries into three distinct values.

We could accomplish this by using multiple conditional if-else statements or a form of looping. But it’s also possible to simplify this to a one-liner by using NumPy.

Let’s initiate a sample employee dataset using the following code:

import pandas as pd
import numpy as np
 
data = {
    'employee_id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'salary': [3500, 5000, 2500, 8000, 1000]
}
df = pd.DataFrame(data)
Then, we can divide the salary into three bins by using the following one-liner (spread across multiple lines for readability).

df['salary_level'] = np.select(
    [
        df['salary'] < 3000,
        (df['salary'] >= 3000) & (df['salary'] < 6000),
        df['salary'] >= 6000
    ],
    ['Low', 'Medium', 'High']
)
The result will be a new column filled with a value determined by following the condition we laid out.

5. Conditional Replacement For Several Columns
There are times when we don’t want to filter out the data we select; instead, we want to replace it with another value suitable for our work.

Using NumPy, we can efficiently replace values from multiple columns with a single line of code.

For example, here is an example of how we can use a combination of the Pandas apply() method with the Numpy where() function to replace values within different columns.

df[['col1','col2']] = df[['col1','col2']].apply(lambda col: np.where(col > 0, col, np.nan))
You can easily replace the value with the required condition with the code above.

6. Multiple Columns Combination
When we work with data, sometimes we represent multiple columns as one feature instead of leaving them as they are.

For combining multiple columns, we can aggregate them with simple statistics such as average, sum, standard deviation, and many others. However, there are other ways to combine multiple columns into one, such as via string combination.

This does not necessarily work for numerical data, as the result might not be the best, but it’s sufficient for any text data, especially if the combination has meaning.

To do that, we can use the following code:

df['combined'] = df[['col1', 'col2', 'col3']].astype(str).agg('_'.join, axis=1)
The axis equal to 1 will join row-wise with ‘_’ as the separator. You can replace them with space, hyphen, or any other separator you deem appropriate.

7. Column Splitting
We have discussed combining columns into one, but sometimes it is much more beneficial to separate one feature into several different features.

The principle is the same as above, and you can easily use a Python one-liner to split.

df[['first', 'last']] = df['full_name'].str.split(' ', n=1, expand=True)
The code above will separate the first space of the text and split it into several columns, even if there are multiple spaces within the text.

You can change the separator you want to split on as appropriate.

8. Outlier Identification and Removal
Outliers sometimes need to be removed as they can distort our analysis and machine learning algorithms. It’s not always the case, but you can consider removing them after careful analysis.

There are many methods for outlier identification, but the easiest one is using percentiles.

For example, we defined the bottom and top 5% of data as outliers. To do that, we can use the following single line of code.

df['capped'] = df['value'].clip(lower=df['value'].quantile(0.05), upper=df['value'].quantile(0.95))
Using the code above, we can identify and cut the outliers we don’t want in our dataset.

9. Merge Multiple DataFrame with Reduce
Many times in our work, we end up with multiple datasets, and we may want to merge them.

In Pandas, you can easily do that using the merge() function. However, the complexity will increase with a larger dataset.

If this is the case, we can use the reduce() function, which allows us to merge a list of DataFrames without manually nesting multiple merge function calls.

For example, we have the following multiple datasets, which we make into a list.

import pandas as pd
from functools import reduce
 
df1 = pd.DataFrame({'key': [1, 2, 3], 'A': ['a1', 'a2', 'a3']})
df2 = pd.DataFrame({'key': [2, 3, 4], 'B': ['b2', 'b3', 'b4']})
df3 = pd.DataFrame({'key': [3, 4, 5], 'C': ['c3', 'c4', 'c5']})
 
list_of_dfs = [df1, df2, df3]
Using reduce(), we can merge multiple DataFrame with the following code.

df_merged = reduce(lambda left, right: pd.merge(left, right, on='key', how='outer'), list_of_dfs)
The result will depend on how you merge the DataFrame and the key you merge on, but it’s now easier than having to merge multiple datasets with intermediate variables.

10. DataFrame Query Optimization with Eval
Creating a new column based on a DataFrame calculation might take some time, especially if the data are large.

To optimize this process, we can use the Pandas eval() function. By using a procedure similar to the query() function, eval() can improve the execution time while reducing the need for an intermediate object.

df = df.eval("col3 = (col1 * 0.8 + col2 * 0.2) / col4", inplace=False)



Kai March 9, 2025 at 1:32 am #
Avoid the warning in point 02, replace w/”… aggfunc={‘value’: [“mean”, “sum”]})”
For readability and allowing straight copying into Jupyter (which is what most people do with tutorials like this) include things like “df.head(5)” in between and at the end. Last command in step 2 should be: “pivot_df.head(5)”, for example.
Otherwise, an informative post – just too many hick-ups (see (4) as well – post by Tom above)
