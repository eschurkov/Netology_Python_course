import pandas
import os


def top3_names(years_list):
    source_directory = 'names'
    data = pandas.DataFrame()
    for year in years_list:
        files_path = os.path.join(source_directory, 'yob%s.txt' % str(year))

        year_data = pandas.read_csv(files_path, names=['name', 'sex', 'count'])

        data = data.append(year_data, ignore_index=True)

    data = data.groupby(by=['name', 'sex']).aggregate(sum).reset_index()
    data = data.sort_values(by='count', ascending=False)[:3]

    print(list(data['name']))

# years = [1880]
years = [1900, 1950, 2000]
top3_names(years)
