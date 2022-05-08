import pandas as pd

#필요한 자료 다 가져오기
df_comment = pd.read_excel("comment.xlsx", index_col=0)
df_bad_words = open ("bad_words.txt", "r", encoding = "utf-8")

#bad_words 확인
for line in df_bad_words.readlines():
    #print(type(line))
    words = line.split(", ")    #bad_words를 words에 리스트로 저장
    #print(type(words))
    #print(words)
#print(words)

#bad_words가 댓글에 있으면 하트 이모티콘으로 바꾸기
for word in words:
    df_word = df_comment[df_comment['text'].str.contains(word)]
    #print(df_word)

    for idxcomment, text_word in df_word.iterrows():
        '''new_text = ''
        text_word = str(text_word[2]).split('\n')
        print(text_word)

        for line in text_word:
            print(idxcomment, word)
            print(line)
            line = line.replace(word, '🤍❣🧡💛')
            print(line, end='')
            new_text += line + ''
        new_text += '''

        text_word = str(text_word[2])
        #print(text_word)
        new_text = text_word.replace(word, '🤍❣🧡💛')
        #print(new_text)

        df_comment.at[idxcomment, 'text'] = new_text
        #print(df_comment.loc[idxcomment, 'text'], end='\n\n')


#print(df_comment['text'])

df_comment.to_csv('comment_filter.csv', encoding='utf-8')
df_comment.to_excel('comment_filter.xlsx', encoding='utf-8', sheet_name='comment')

'''for line in comment_text:
    print(line)
    print(line[3].replace(words,'♥'))'''