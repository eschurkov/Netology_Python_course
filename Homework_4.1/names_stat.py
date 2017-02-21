import pandas
import os
source_directory = 'names'
# years_list = [1880]
years_list = [1900, 1950, 2000]

data = pandas.DataFrame()
for year in years_list:
    files_path = os.path.join(source_directory, 'yob%s.txt' % str(year))

    year_data = pandas.read_csv(files_path, names=['name', 'sex', 'count'])

    data = data.append(year_data, ignore_index=True)

data = data.groupby(by=['name', 'sex']).aggregate(sum)
data = data.sort_values(by='count', ascending=False)[:3]

print(data)

