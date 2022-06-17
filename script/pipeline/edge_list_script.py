import logging
import os
from datetime import time
import time
import yaml
import pandas

from hate_tweet_map.database import DataBase


def main():
    global db, query
    start = time.time()
    logging.basicConfig()

    with open("edge_list_script.config", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
        source_field = cfg['criteria']['source']
        target_field = cfg['criteria']['target']

    if source_field is None and target_field is None:
        raise ValueError("Specificare entrambi i parametri")

    if source_field != "author_username":
        raise ValueError("Attributo inserito non valido per il campo source")

    log = logging.getLogger("PIPELINE")
    log.setLevel(logging.INFO)

    db = DataBase('edge_list_script.config')

    if source_field == "author_username":
        if target_field == "user_mentioned":
            df1= pandas.DataFrame(db.extract_all_tweets())
            df1.to_csv('dict',index=False)
            query={}
            log.info("EXTRACT [MENTIONS]...")
            result = db.pipeline_mentions(query)
            log.info("UPDATE: {} TWEETS".format((result)))
            db.extract(query)
            df = pandas.DataFrame(db.extract(query))
            newdf = df.explode('target')
            newdf.to_csv('data.csv', index=False)
            log.info("TWEETS SAVED ON: {}".format(os.path.abspath('../../data.csv')))
            db.delete_collection()
            name = cfg['mongodb']['collection']
            db1=db.create_collection(name)
            data = df1.to_dict(orient="records")
            db1.insert_many(data)
            ABSOLUTE_PATH = os.path.abspath("dict")
            os.remove(ABSOLUTE_PATH)

    if source_field == "author_username":
        if target_field == "hashtag":
            df1 = pandas.DataFrame(db.extract_all_tweets())
            df1.to_csv('dict', index=False)
            query = {}
            log.info("EXTRACT [MENTIONS]...")
            result = db.pipeline_hashtags(query)
            log.info("UPDATE: {} TWEETS".format((result)))
            db.extract(query)
            df = pandas.DataFrame(db.extract(query))
            newdf= df.explode('target')
            newdf.to_csv('data.csv', index=False)
            log.info("TWEETS SAVED ON: {}".format(os.path.abspath('../../data.csv')))
            db.delete_collection()
            name = cfg['mongodb']['collection']
            db1 = db.create_collection(name)
            data = df1.to_dict(orient="records")
            db1.insert_many(data)
            ABSOLUTE_PATH=os.path.abspath("dict")
            os.remove(ABSOLUTE_PATH)

    end = time.time()
    log.info("DONE IN: {}".format(end - start))


if __name__ == "__main__":
    main()
