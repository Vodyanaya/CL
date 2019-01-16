import os
import nltk
import csv
from string import punctuation
from nltk.corpus import stopwords
from pymorphy2 import MorphAnalyzer

# Путь к директории (можно input сделать) и список папок в директории
d = "/Users/user/Documents/HSE_project/torture/Тексты/"
author_list = os.listdir(d)


# БЛОК измывательства над текстом
# разбивает текст (на входе) на предложения (на выходе список предложений (List of sentences))
def get_sentences(document):
    sentences = nltk.sent_tokenize(document)
    sentences = [i.replace('\ufeff', '') for i in sentences]
    sentences = [i.replace('\n', ' ') for i in sentences]
    # cnt = 0
    # for sent in sentences:
    #     cnt += 1
    #     print('{}. {}'.format(cnt, sent))
    # print(sentences)
    return sentences


# список предложений (на входе), на выходе список слов (List of words)
def get_words(sentences):
    punct = punctuation + '«»—…“”*№–'
    stop_words = stopwords.words('russian')
    words = [word for sent in sentences
             for word in nltk.word_tokenize(sent)
             if word not in stop_words
             and word.strip(punct) != '']
    return words


# список слов на входе, список тэгов на выходе
def get_words_tags(words):
    words = [word.lower() for word in words]
    morph = MorphAnalyzer()
    words_tags = [morph.parse(word)[0].tag.POS for word in words]
    return words_tags


# список предложений на входе, на выходе среднее колическтво слов в предложении
# (количество слов в предложении / количество предложений)
def preprocess_sents(sentences, words):
    sents = float('{:.4f}'.format(len(words) / len(sentences)))
    return sents


# на входе список слов, на выходе средняя длина слов (количесто букв / количество слов)
def preprocess_words(words):
    letters = sum(len(i) for i in words)
    wordlength = float('{:.4f}'.format(letters / len(words)))
    return wordlength


# на входе список слов, на выходе процент союзов (количество союзов / количество слов)
def preprocess_conj(words_tags, words):
    cnt_tags = 0
    for tag in words_tags:
        if tag == "CONJ":
            cnt_tags = cnt_tags + 1
    conj_percent = float('{:.4f}'.format(cnt_tags / len(words) * 100))
    return conj_percent


# на входе список слов, на выходе процент существительных (количество существительных / количество слов)
def preprocess_noun(words_tags, words):
    cnt_tags = 0
    for tag in words_tags:
        if tag == "NOUN":
            cnt_tags = cnt_tags + 1
    noun_percent = float('{:.4f}'.format(cnt_tags / len(words) * 100))
    return noun_percent


# на входе список слов, на выходе процент глаголов (количество глаголов / количество слов)
def preprocess_verb(words_tags, words):
    cnt_tags = 0
    for tag in words_tags:
        if tag == "VERB":
            cnt_tags = cnt_tags + 1
    verb_percent = float('{:.4f}'.format(cnt_tags / len(words) * 100))
    return verb_percent


# на входе список слов, на выходе процент деепричастий (количество деепричастий / количество слов)
def preprocess_grnd(words_tags, words):
    cnt_tags = 0
    for tag in words_tags:
        if tag == "GRND":
            cnt_tags = cnt_tags + 1
    grnd_percent = float('{:.4f}'.format(cnt_tags / len(words) * 100))
    return grnd_percent


# получение профиля документа: на входе текст,
# на выходе словарь: ключи - параметры, значения - собственно полученные значения
def get_profile(document):
    sentences = get_sentences(document)
    words = get_words(sentences)
    words_tags = get_words_tags(words)
    sents = preprocess_sents(sentences, words)
    wordlength = preprocess_words(words)
    conj = preprocess_conj(words_tags, words)
    noun = preprocess_noun(words_tags, words)
    verb = preprocess_verb(words_tags, words)
    grnd = preprocess_grnd(words_tags, words)
    imaginary_total = float('{:.4f}'.format((sents + wordlength + conj + noun + verb + grnd) / 6))
    profile = {'sent': sents, 'words': wordlength, 'conj': conj, 'noun': noun, 'verb': verb, 'grnd': grnd,
               'imaginary_total': imaginary_total}
    return profile


# БЛОК собственно работы с файлами

# Для Windows
# на входе список папок с авторами, в которых тексты, на выходе словарь:
# ключи - названия папок (авторы +- произведения и т.д), значения - словари профиля по имеющемуся в папке тексту
def get_dictionary(directory_list):
    dictionary = {}
    for i in directory_list:
        title = os.listdir(d + '/' + i)
        for n in title:
            with open(d + '/' + i + '/' + n, 'r', encoding='UTF-8') as out:
                document = out.read()
                profile = get_profile(document)
                dictionary[i] = profile
    return dictionary


# Для MacOS
# на входе список папок с авторами, в которых тексты, на выходе словарь:
# ключи - названия папок (авторы +- произведения и т.д), значения - словари профиля по имеющемуся в папке тексту
# def get_dictionary(author_list):
#     data = {}
#     for i in author_list:
#         if i != '.DS_Store':
#             title = os.listdir(d + '/' + i)
#             for n in title:
#                 if n != '.DS_Store':
#                     with open(d + '/' + i + '/' + n, 'r', encoding='UTF-8') as out:
#                         document = out.read()
#                         profile = get_profile(document)
#                         data[i] = profile
#     return data


# укладывание словаря в csv: на входе желаемое name.csv и словарь, на выходе таблица (RStudio её нормально читает)
def save_file(csvfile, dictionary):
    with open(csvfile, 'w', encoding="utf-8") as savefile:
        writer = csv.DictWriter(savefile, fieldnames=['Author', 'Words_in_Sent_Mean',
                                                      'Char_in_Words_Mean', 'Conj_PerCent',
                                                      'Noun_PerCent', 'Verb_PerCent',
                                                      'Grnd_PerCent', 'Gods_Know_What'])
        writer.writeheader()
        for i in dictionary.keys():
            strtowrite = [i, str(dictionary[i]['sent']), str(dictionary[i]['words']), str(dictionary[i]['conj']),
                          str(dictionary[i]['noun']), str(dictionary[i]['verb']), str(dictionary[i]['grnd']),
                          str(dictionary[i]['imaginary_total'])]
            # strtowrite = str(strtowrite)
            savefile.write(','.join(strtowrite))
            savefile.write('\n')


data = get_dictionary(author_list)
save_file('result.csv', data)
