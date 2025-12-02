import numpy as np
import heapq as hq

class Node:

    def __init__(self, w: np.ndarray, label: np.ndarray, action: np.ndarray, parent: Node):
        self.w = w # 96 by 3 where cols= y, x, weight --> represent 8 x 12 grid
        self.label = label # vector length 96 --> represent each label on 8 x12 grid
        self.action = action # vector of [y1, x1, y2, x2]
        self.parent = parent # the node in which it came from 
        if action is not None: self.cost = abs(action[0] - action[2]) + abs(action[1] + action[3]) # cost of action to get to this node
        self.score = imbalance_score(w)
        

    def __eq__(self, other: Node):
        return np.array.equal(self.w, other.w) and np.array.equal(self.label == other.label)

    
    def __hash__(self):
        self.w.writeable = False
        self.label.writeable = False
        return hash((self.w.tobytes(), self.label.tobytes()))


def imbalance_score(w):
    mask = w[:, 1] <= 6
    return abs(np.sum(w[mask, 2]) - np.sum(w[~mask, 2]))    


def heuristic():
    pass

# define possible actions & return all neighbor states
def neighbors():
    pass

def a_star(X : np.ndarray):
    start = Node(np.int64(X[:, 0:3]), X[:, 3], None, None) 
    print(start.score)

if __name__ == '__main__':
    FOLDER_PATH = './data/'
    FILE_NAME = 'ShipCase6.txt'
    X = np.loadtxt(FOLDER_PATH+FILE_NAME, dtype=str, delimiter=',')
    X[:, 0] = np.char.strip(X[:, 0], "[")
    X[:, 1] = np.char.strip(X[:, 1], "]")
    X[:, 2] = np.char.strip(X[:, 2], "{} ")
    X[:, 3] = np.char.strip(X[:, 3], " ")
    
    a_star(X)


