father = []
dx = [0, -1, -1, -1, 0, 1, 1, 1]
dy = [1, 1, 0, -1, -1, -1, 0, 1]
size = []


def find_father(x: int):
    if x != father[x]:
        father[x] = find_father(father[x])
    return father[x]


def union(x: int, y: int):
    x = find_father(x)
    y = find_father(y)
    if x != y:
        father[x] = y
        size[y] += size[x]


def adjacent(t1: tuple, t2: tuple):
    for (x, y) in zip(dx, dy):
        if t1[0] == t2[0] + x and t1[1] == t2[1] + y:
            return True
    return False


def run(l: list):
    for i in range(len(l)):
        father.append(i)
        size.append(1)
    for i in range(1, len(l)):
        for j in range(i - 1, -1, -1):
            if adjacent(l[i], l[j]):
                union(i, j)
                break
    return size

if __name__ == '__main__':
    run([(0, 0), (11, 1), (1, 1), (2, 2), (3, 3), (7, 2), (8, 3), (4, 4), (5, 0), (6, 1), (10, 0), (12, 2)])
    print(size)
