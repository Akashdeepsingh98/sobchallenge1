from typing import Dict, List, Set, Tuple

WEIGHT_LIM = 4000000


class MempoolTransaction():
    def __init__(self, txid: str, fee: int, weight: int, parents=[]) -> None:
        self.txid: str = txid
        self.fee: int = fee
        self.weight: int = weight
        self.parents: List[str] = parents  # list of direct parents
        self.children: List[str] = []  # list of direct children
        self.selected: bool = False  # was going to use this but did not

    def __str__(self) -> str:  # just a string representation for sake of debugging
        res: str = 'Txid: ${} \n Fee: {} \n Weight: {} \n Parents: {} \n Children: {}'.format(
            self.txid, self.fee, self.weight, self.parents, self.children)
        return res

    # get all the parents of this transaction in order
    def getParentGraph(self) -> List[str]:
        txidlist: List[str] = []  # list of parents topologically sorted
        # visited transactions must not be visited again
        visited: Set[str] = set()
        self.getParentGraphUtil(visited, txidlist)
        return txidlist

    def getParentGraphUtil(self, visited: Set[str], txidlist: List[str]) -> None:
        visited.add(self.txid)
        txidlist.append(self.txid)
        for i in range(len(self.parents)):  # go through all the parents
            if not self.parents[i] in visited:
                data[self.parents[i]].getParentGraphUtil(visited, txidlist)


# dictionary with txid as key and transactions as value
data: Dict[str, MempoolTransaction] = {}


def main():

    # read file into data dictionary
    with open('mempool.csv') as f:
        f.readline()  # get rid of first line
        while True:  # read file until EOF
            line = f.readline()
            if not line:
                break
            # get rid of surrounding whitespaces, commas and then split on commas within line
            line = line.strip().strip(',').split(',')
            parents = []
            if len(line) == 4:
                # if there are 4 elements in line list, there is at least one parent and parents are separated by semicolon
                parents = line[3].strip().split(';')

            if line[0] in data:  # if a current txid already exists due to following for loop then we need to update the provided temporary weight and fees
                data[line[0]].fee = int(line[1])
                data[line[0]].weight = int(line[2])
                data[line[0]].parents = parents
            else: # if it does not exist then just make a new object for transaction
                data[line[0]] = MempoolTransaction(
                    line[0], int(line[1]), int(line[2]), parents)

            for i in range(len(parents)): # go through the parents on this line and set the children it has
                if not parents[i] in data:
                    data[parents[i]] = MempoolTransaction(parents[i], 0, 0)
                data[parents[i]].children.append(line[0])

    candidates: Dict[str, List[Tuple[int, int, str]]] = {} # the candidate directed acyclic graphs 
    # each key is a root, it has no parent
    # each value is a list of topologically sorted transactions with prefix sum of fees and weight
    
    for txid in data.keys(): # prepare the candidates dictionary 
        txidlist = data[txid].getParentGraph()
        txidlist.reverse()
        candidates[txidlist[0]] = [
            [
                data[txidlist[0]].fee,
                data[txidlist[0]].weight,
                txidlist[0]
            ]
        ]
        for i in range(1, len(txidlist)):
            candidates[txidlist[0]].append([
                data[txidlist[i]].fee + candidates[txidlist[0]][-1][0],
                data[txidlist[i]].weight + candidates[txidlist[0]][-1][1],
                txidlist[i]
            ])

    curweight: int = 0  # it will store weight of currently selected transactions

    # the result array just stores a list with candidate graph root txid and the final index upto which transactions are included from candidates dictionary
    result: List[Tuple[str, int]] = []
    # the final index was quite unnecessary for this approach and could have been useful for another one I had in mind

    # go through each candidate
    for cand in candidates.keys():

        # exclude graphs whose weight is greater than the limit
        if candidates[cand][-1][1] > WEIGHT_LIM:
            continue

        # check if weight of graph can fit into result
        if candidates[cand][-1][1] <= WEIGHT_LIM-curweight:
            result.append([cand, len(candidates[cand])-1])
            curweight += candidates[cand][-1][1]
            result.sort(
                key=lambda x: candidates[x[0]][x[1]][1])
        # if cannot fit then replace other graphs with lesser fees with this current graph
        else:
            end = 0
            curfee = 0
            curweight2 = 0
            # get all graphs whose total fees is less than current candidate's fees
            while True:
                if end >= len(result) or curfee+candidates[result[end][0]][-1][0] > candidates[cand][-1][0]:
                    break
                curfee += candidates[result[end][0]][result[end][1]][0]
                curweight2 += candidates[result[end][0]][result[end][1]][1]
                end += 1
            end -= 1
            if end != -1:
                result = result[end+1:]
                curweight -= curweight2 # update weight by subtracting removed graph weights and adding new graph weight
                curweight += candidates[cand][-1][1]
                result.append([cand, len(candidates[cand])-1])
                result.sort(key=lambda x: candidates[x[0]][x[1]][1])

    with open('block.txt', 'w') as f:
        for cand in result:
            for i in range(cand[1]+1):
                f.write(candidates[cand[0]][i][2]+'\n')


if __name__ == '__main__':
    main()
