import pandas as pd

df_News = pd.read_excel("News_sort.xlsx", index_col=0)

df_News = df_News.drop_duplicates(['Title'], keep='first')
print(df_News['Title'])

df_News.to_excel('News_sort_editted.xlsx', encoding='utf-8', sheet_name='News')