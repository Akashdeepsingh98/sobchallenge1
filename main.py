from functools import cmp_to_key
import heapq
import queue


class MempoolTransaction():
    def __init__(self, txid, fee, weight, parents=[]):
        self.txid = txid
        self.fee = fee
        self.weight = weight
        self.parents = parents
        self.children = []

    def __lt__(self, other):
        return self.fee < other.fee

    def __str__(self) -> str:
        return self.fee


def main():
    data = {}  # dictionary with txid as key
    curweight = 0

    with open('mempool.csv') as f:
        f.readline()
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip().split(',')
            if line[0] in data:
                data[line[0]].fee = int(line[1])
                data[line[0]].weight = int(line[2])
                data[line[0]].parents = line[3:]
            else:
                data[line[0]] = MempoolTransaction(
                    line[0], int(line[1]), int(line[2]), line[3:])
            for i in range(3, len(line)):
                if not line[i] in data:
                    data[line[i]] = MempoolTransaction(line[i], 0, 0)
                data[line[i]].children.append(line[0])
        print(len(data))

if __name__ == '__main__':
    main()
