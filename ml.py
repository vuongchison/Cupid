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
    res = db.engine.execute(sql)
    res = [r for r in res]
    # print(res)
    # return None
    data = np.array(res)
    # user id, height, weight, age, pro
    # print(data)
    # return None
    X = data[:,1:4]
    y = data[:, 4]

    X = preprocessing.StandardScaler().fit(X).transform(X)


    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=4)


    LR = LogisticRegression(C=0.01, solver='liblinear').fit(X_train, y_train)

    yhat = LR.predict(X_test)

    yhat_prob = LR.predict_proba(X_test)
    # print(y_test, yhat)

    score = jaccard_similarity_score(y_test, yhat)
    print(score)
    # return None
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
        # print(yhat.shape)
        # yhat = yhat.reshape((yhat.shape[0], 1))
        # prob = np.zeros((yhat.shape[0], 1), dtype=float)
        # users = np.append(res, prob, axis=1)
        # users = users.view('i8,i8,i8,i8')
        # users[:,4] = yhat[:,0]
        users = users.tolist()
        res = []
        for i in range(len(users)):
            res.append((users[i][0], yhat[i]))
            # users[i].append(yhat[i])
        # print(users[0:5], yhat[0:5])
        res = sorted(res, key=lambda i: i[1], reverse=True)
        dtype = [('id', int), ('height', int), ('weight', int), ('age', int), ('prob', float)]
        # res = np.append(users, yhat, axis=1)
        # res = res.view('i8,i8,i8,i8,f8')
        # res.sort(order=['prob'], axis=0)
        # res = flip(res, axis=0)
        # print(res)
        # res.sort(order=['prob'])
        print(res[:10])
        return res


    else:
        return None




