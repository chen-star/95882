import csv

users = []
tags = {}


def train(username):
    # read data from csv
    read_csv()

    # nearest users
    distances = computeNearestNeighbor(username)
    recommendations = {}
    count = 0
    for (distance, user) in distances:
        if count >= 3:
            break
        if distance == -1:
            continue
        recommendations[user] = common_tags(username, user)
        count += 1

    print(tags)
    print(recommendations)
    return recommendations


def read_csv():
    # read data from csv
    with open('stats.csv') as f:
        f_csv = csv.reader(f)
        for row in f_csv:
            users.append(row[0])
            tmp = {}
            for tag in row[1:]:
                if tag in tmp:
                    tmp[tag] = tmp[tag] + 1
                else:
                    tmp[tag] = 1
            tags[row[0]] = tmp


def manhattan(rate1, rate2):
    distance = 0
    commonRating = False
    for key in rate1:
        if key in rate2:
            distance += abs(rate1[key] - rate2[key])
            commonRating = True
    if commonRating:
        return distance
    else:
        return -1


def computeNearestNeighbor(username):
    distances = []
    for key in tags:
        if key != username:
            distance = manhattan(tags[username], tags[key])
            distances.append((distance, key))
    distances.sort()
    return distances


def common_tags(u1, u2):
    d1 = tags[u1]
    d2 = tags[u2]
    l1 = []
    l2 = []
    for key in d1:
        l1.append(key)
    for key in d2:
        l2.append(key)

    result = []
    for k1 in l1:
        if k1 in l2:
            result.append(k1)

    return result
