import numpy as np

class Agent:

    def __init__(self, n_inputs, n_outputs):
        self.dense1 = FullyConnected(n_inputs, n_outputs)
        self.activation = Tanh()
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.score = 0
    
    def __call__(self, x):
        return self.activation(self.dense1(x))

class FullyConnected:
    
    def __init__(self, in_size, out_size):
        self.W = np.random.normal(
            scale=1, size=(out_size, in_size)) * np.sqrt(2 / (in_size + out_size))
        self.b = np.random.normal(
            scale=1, size=(out_size)) * np.sqrt(2 / (out_size))
    
    def __call__(self, x):
        return (np.dot(self.W, x) + self.b)
    
class Tanh:
    def __call__(self, x):
        return (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))

if __name__ == '__main__':
    agent = Agent(3, 1)
    x = np.array([123, 40, 110], dtype=np.float32)
    y = agent(x)
    print(y)