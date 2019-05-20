import numpy as np 
import scipy.optimize as opt
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import jaccard_similarity_score
from numpy import flip
from app import db
from functools import lru_cache

@lru_cache(maxsize=10)
def recommend(user_id):
    sql = """   select users.id, users.height, users.weight, cast(strftime('%%Y.%%m%%d', 'now') - strftime('%%Y.%%m%%d', users.birthday) as int) as age, 1 as prob
                from users, follow
                where users.id = follow.followed_id and follow.follower_id=%d
                union
                select users.id, users.height, users.weight, cast(strftime('%%Y.%%m%%d', 'now') - strftime('%%Y.%%m%%d', users.birthday) as int) as age, 0 as prob
                from users, views
                where users.id = views.user_id and views.viewer_id=%d and views.user_id not in (select users.id from users, follow where users.id = follow.followed_id and follow.follower_id=%d); 
                """ % (user_id, user_id, user_id)
    data = db.engine.execute(sql)
    data = [r for r in data]
    if len(data) <= 30:
        return list()
    data = np.array(data)
    X = data[:,1:4]
    y = data[:, 4]

    X = preprocessing.StandardScaler().fit(X).transform(X)


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=4)


    LR = LogisticRegression(C=0.01, solver='liblinear').fit(X_train, y_train)

    yhat = LR.predict(X_test)

    yhat_prob = LR.predict_proba(X_test)

    score = jaccard_similarity_score(y_test, yhat)

    if score > 0.7:
        
        # tìm ng mà chưa từng ghé thăm
        # user id, height, weight, age
        sql = """   select users.id, users.height, users.weight, cast(strftime('%%Y.%%m%%d', 'now') - strftime('%%Y.%%m%%d', users.birthday) as int) as age
                    from users
                    where id != %d and gender_id = 2 and id not in (select user_id from views where viewer_id = %d);
        """ % (user_id, user_id)
        res = db.engine.execute(sql)
        res = [r for r in res]
        users = np.array(res)
        
        yhat = LR.predict_proba(users[:, 1:])[:,1]
        users = users.tolist()
        res = []
        for i in range(len(users)):
            res.append((users[i][0], yhat[i]))
        res = sorted(res, key=lambda i: i[1], reverse=True)
        return res


    else:
        return None




