from functools import cmp_to_key
import heapq
import queue
from typing import Dict, List, Set, Tuple

WEIGHT_LIM = 4000000


class MempoolTransaction():
    def __init__(self, txid: str, fee: int, weight: int, parents=[]) -> None:
        self.txid: str = txid
        self.fee: int = fee
        self.weight: int = weight
        self.parents: List[str] = parents
        self.children: List[str] = []
        self.selected: bool = False

    def __lt__(self, other: 'MempoolTransaction') -> bool:
        return self.fee < other.fee

    def __str__(self) -> str:
        res: str = 'Txid: ${} \n Fee: {} \n Weight: {} \n Parents: {} \n Children: {}'.format(
            self.txid, self.fee, self.weight, self.parents, self.children)
        return res

    def getParentGraph(self) -> Tuple[int, int, List[str]]:
        txidlist: List[str] = []
        totalfee: int = 0
        visited: Set[str] = set()
        totalfee, totalweight = self.getParentGraphUtil(visited, txidlist)
        return totalfee, totalweight, txidlist

    def getParentGraphUtil(self, visited: Set[str], txidlist: List[str]) -> Tuple[int, int]:
        totalfee: int = 0
        totalweight: int = 0
        totalfee += self.fee
        totalweight += self.weight
        visited.add(self.txid)
        txidlist.append(self.txid)
        for i in range(len(self.parents)):
            if not self.parents[i] in visited:
                f, w = data[self.parents[i]].getParentGraphUtil(
                    visited, txidlist)
                totalfee += f
                totalweight += w
        return totalfee, totalweight


data: Dict[str, MempoolTransaction] = {}  # dictionary with txid as key


def main():

    curweight: int = 0

    # read file into data dictionary
    with open('mempool.csv') as f:
        f.readline()  # get rid of first line
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip().strip(',').split(',')
            parents = []
            if len(line) == 4:
                parents = line[3].strip().split(';')

            # print(line)
            # break

            if line[0] in data:
                data[line[0]].fee = int(line[1])
                data[line[0]].weight = int(line[2])
                data[line[0]].parents = parents
            else:
                data[line[0]] = MempoolTransaction(
                    line[0], int(line[1]), int(line[2]), parents)

            for i in range(len(parents)):
                if not parents[i] in data:
                    data[parents[i]] = MempoolTransaction(parents[i], 0, 0)
                data[parents[i]].children.append(line[0])
    print(len(data))
    # print(data['79c51c9d4124c5cbb37a85263748dcf44e182dff83561fa3087f0e9e43f41c33'])

    # store sum of each graph and nodes of each graph
    # ratio of fee by weight, fee, weight, txid list
    result: List[Tuple[int, int, int, List[str]]] = []
    for txid in data.keys():
        totalfee, totalweight, txidlist = data[txid].getParentGraph()
        # print(totalweight)
        if totalweight > WEIGHT_LIM:
            continue
        if totalweight <= WEIGHT_LIM-curweight:
            curweight += totalweight
            txidlist.reverse()
            result.append(
                [totalfee/totalweight, totalfee, totalweight, txidlist])
            result.sort(key=lambda x: x[1])
            # radix sort so that weight is the main criteria for and next is fee
            #result.sort(key=lambda x: x[0])
            #result.sort(key=lambda x: x[1])
        else:
            end = 0
            curfee = 0
            curweight2 = 0
            while True:
                if end >= len(result) or curfee+result[end][1] > totalfee:
                    break
                curfee += result[end][1]
                curweight2 += result[end][2]
                end += 1
            end -= 1
            if end == -1:
                pass
            else:
                result = result[end+1:]
                curweight -= curweight2
                curweight += totalweight
                result.append(
                    [totalfee/totalweight, totalfee, totalweight, txidlist])
                result.sort(key=lambda x: x[1])
        # print(len(result))

    with open('block.txt', 'w') as f:
        for item in result:
            if len(item[3]) > 1:
                print(item[3])
            for txid in item[3]:
                f.write(txid)
                f.write('\n')


if __name__ == '__main__':
    main()
