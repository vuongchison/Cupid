import numpy as np 
import scipy.optimize as opt
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import jaccard_score
from numpy import flip
from app import db
from functools import lru_cache
from flask import current_app
from sqlalchemy import text

# @lru_cache(maxsize=1)
def recommend(user_id):
    # print(current_app.config)
    sql = current_app.config['SQL_QUERY_GET_ALL_FOLLOW_DATA'] % (user_id, user_id, user_id)
    with db.engine.connect() as connection:
        data = connection.execute(text(sql))
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

        score = jaccard_score(y_test, yhat)

        if score > 0.7:
            
            # tìm ng mà chưa từng ghé thăm
            # user id, height, weight, age
            sql = current_app.config['SQL_QUERY_GET_ALL_STRANGER'] % (user_id, user_id)
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




