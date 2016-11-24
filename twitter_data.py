class GetData(object):
    def __init__(self, cons_key, cons_secret, access_key, access_secret):
        self.__cons_key = cons_key
        self.__cons_secret = cons_secret
        self.__access_key = access_key
        self.__access_secret = access_secret
        self._json_file = 'all_tweets.json'

    def get_tweets(self, twitter_username, duration=7):
        import datetime
        import tweepy
        import json
        import tqdm as pbar

        auth = tweepy.OAuthHandler(self.__cons_key, self.__cons_secret)
        auth.set_access_token(self.__access_key, self.__access_secret)
        api = tweepy.API(auth)
        all_tweets = []
        try:
            new_tweets = (api.user_timeline(screen_name=twitter_username,
                                            count=20))
            oldest_id = new_tweets[-1].id - 1
            for i in pbar.tqdm(range(5)):
                all_tweets.extend(api.user_timeline(screen_name=twitter_username,
                                                    count=20, max_id=oldest_id))
                oldest_id = all_tweets[-1].id - 1

            earliest_tweet_date = (all_tweets[0].created_at).date()
            tweet_max_date = earliest_tweet_date + datetime.timedelta(days=duration)
            status_list = []
            for tweet in all_tweets:
                if (tweet.created_at).date() <= tweet_max_date:
                    status_list.append(tweet._json)

                with open(self._json_file, 'w') as json_data:
                    json.dump(status_list, json_data, indent=4)
        except tweepy.TweepError as e:
            # print(e)
            # err = json.loads(e.reason)
            # print(e[0])
            # # print(type(e[0]))
            if e.reason == "[{'message': 'Sorry, that page does not exist.', 'code': 34}]":
                print('Invalid twitter username, try again with a valid username')
            elif e.reason == 'Not authorized.':
                print('You are not authorized to view this person tweets!, (protected tweets)')
            else:
                print('Internet connection required, please connect and try again')
        return ''

    def word_list(self):
        import json
        import re
        from nltk.corpus import stopwords

        cachedStopWords = stopwords.words("english")
        cachedStopWords.append(')')
        cachedStopWords.append('-')
        cachedStopWords.append(',')
        tweet_list = []
        with open(self._json_file, 'r') as tweet_data:
            data = json.load(tweet_data)
        tweet_list.extend(data)
        # print(len(tweet_list))
        # pprint(tweet_list)
        unwanted_texts = re.compile('[@#-&()..."]')
        words = []
        for status in tweet_list:
            for word in status['text'].split():
                if unwanted_texts.match(word) or word.startswith('http')\
                    or word.startswith('http'):
                    continue
                else:
                    for word_members in (word.replace(':',' ').replace('.',' '
                                        ).replace('!',' ').replace('?',' '
                                        ).replace('"', ' ').replace('-',' '
                                        ).replace('/',' ').split()
                                        ):
                        if (word_members not in cachedStopWords) and\
                            (word_members != 'RT'):
                            words.append(str(word_members))
        return words

    def word_frequency(self):
        word_count = {}
        words = self.word_list()
        for word in words:
            try:
                word = int(word)
                try:
                    if word_count[word]:
                        word_count[word] += 1
                except KeyError:
                    word_count[word] = 1
            except ValueError:
                try:
                    if word_count[word]:
                        word_count[word] += 1
                except KeyError:
                    word_count[word] = 1
        return word_count

    def word_count_analysis(self):
        from operator import itemgetter
        from prettytable import PrettyTable

        word_count = self.word_frequency()
        sort = word_count.items()
        sorted_list =(sorted(sort, key=itemgetter(1)))
        count_sum = sum(word_count.values())
        count = -1
        tweet_table = PrettyTable(['Word', 'Count', 'Percent'])
        while count > -20:
            word, value = sorted_list[count]
            percent = (value/count_sum)*100
            percent1 = ('{:.2f}'.format(percent))
            tweet_table.add_row([word, value, percent1])
            count += -1
        print(tweet_table)

    def sentiment_analysis(self, all=True, sentiment=False, emotion=False):
        from watson_developer_cloud import AlchemyLanguageV1
        alchemyapi = AlchemyLanguageV1(api_key='0e1c5001c8047a3f0492469bf8449d40949f5d1f')

        words_list = ' '.join(self.word_list())

        self.__tweets_sentiment = alchemyapi.sentiment(text=words_list)
        self.__tweets_emotion = alchemyapi.emotion(text=words_list)
        if all:
            return (self.sentiment_table(), self.emotion_graph())
        if sentiment:
            return self.sentiment_table()
        if emotion:
            return self.emotion_graph()

    def emotion_graph(self):
        from ascii_graph import Pyasciigraph

        total_emotion_value = [(str(emotion).capitalize(), float(value)*100) for emotion,
                                value in self.__tweets_emotion['docEmotions'].items()]
        graph = Pyasciigraph()
        for line in graph.graph('Emotions Graph', total_emotion_value):
            print('         ', line)
        return

    def sentiment_table(self):
        from prettytable import PrettyTable

        sent_dict = self.__tweets_sentiment['docSentiment']
        sentiment_data = PrettyTable(['Sentiment Type', 'Score', 'if_mixed'])
        sentiment_data.add_row([sent_dict['type'], sent_dict['score'], sent_dict['mixed']])
        print('\n')
        print(sentiment_data)
        return

def main():
    from pprint import pprint
    cons_key = "qrRMCNNtOtWlN7YPAwllY4C9p"
    cons_secret = "WuA5sp6Do0Q3ohcyTztBjeF0Z8fRQaNFxJQzD0HAWXJpGEA46K"
    access_key = "765074739228471296-eQswENirBvmzVSI3LNSf7p7E3r4L32d"
    access_secret = "t2SuOHDGxO8T5EzaEcoM17mu6ug65F9TGdeo8L8NnT46a"
    data = GetData(cons_key, cons_secret, access_key, access_secret)
    #tweets = data.get_tweets('@realdonaldTrump')
    # data.word_count_analysis()
    for item in data.sentiment_analysis():
        pprint(item)

if __name__ == '__main__':main()



