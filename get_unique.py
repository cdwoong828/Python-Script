from typing_extensions import final
from numpy import unique
import pandas as pd

pd.set_option('display.max_rows', None)
data = pd.read_csv('/Users/daewoong/Downloads/unique/postgre_dep.txt',
                   sep="=>",
                   names=['1열','2열'],
                   engine='python')

text_file = open('/Users/daewoong/Downloads/unique/unique.txt', "w")
slash_directory = []
unique_dict = []
for ind in data.index:
    if data['2열'][ind] is None:
        if data['1열'][ind] not in slash_directory:
            slash_directory.append(data['1열'][ind])
            text_file.write(data['1열'][ind])
            text_file.write("\n")
            data.drop(ind, inplace= True)

    elif data['1열'][ind] not in unique_dict:
        unique_dict.append(data['1열'][ind])
        text_file.write(data['1열'][ind])
        text_file.write("=>")
        text_file.write(data['2열'][ind])
        text_file.write("\n")
text_file.close()








