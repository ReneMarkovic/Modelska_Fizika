import numpy as np


def inputfunct(x):
    #return 0.25*(np.cos(2*np.pi*x*x)+2.0)*np.exp(-0.1*x)
    return 0.25*(np.sin(2*np.pi*x*x)+2.0)-0.5


def get_weights(net):
    nn_weights={}
    for w in net.layers:
        if w.name not in ["Activation","Hiden weights"]:
            ww=np.squeeze(w.weights).tolist()
            nn_weights[w.name]=ww
    return nn_weights

def convert_pred_to_list(xx):
    return np.squeeze(xx).tolist()

def print_size(label,data):
    print(f"{label} ima obliko {data.shape}")

# loss function and its derivative
def mse(y_true, y_pred):
    return np.mean(np.power(y_true-y_pred, 2))

def mse_prime(y_true, y_pred):
    return 2*(y_pred-y_true)/y_true.size

# activation function and its derivative
def tanh(x):
    return np.tanh(x)

def tanh_prime(x):
    return 1-np.tanh(x)**2
# inherit from base class Layer
# Base class
class Layer:
    def __init__(self):
        self.input = None
        self.output = None

    # computes the output Y of a layer for a given input X
    def forward_propagation(self, input):
        raise NotImplementedError

    # computes dE/dX for a given dE/dY (and update parameters if any)
    def backward_propagation(self, output_error, learning_rate):
        raise NotImplementedError

# inherit from base class Layer
class ActivationLayer(Layer):
    def __init__(self, activation, activation_prime):
        self.name="Activation"
        self.activation = activation
        self.activation_prime = activation_prime

    # returns the activated input
    def forward_propagation(self, input_data):
        self.input = input_data
        self.output = self.activation(self.input)
        return self.output

    # Returns input_error=dE/dX for a given output_error=dE/dY.
    # learning_rate is not used because there is no "learnable" parameters.
    def backward_propagation(self, output_error, learning_rate):
        return self.activation_prime(self.input) * output_error

class FCLayer(Layer):
    # input_size = number of input neurons
    # output_size = number of output neurons
    def __init__(self,input_size,output_size,name):
        self.name=name
        self.weights = np.random.rand(input_size, output_size) - 0.5
        self.bias = np.random.rand(1, output_size) - 0.5
        self.shape=self.weights.shape
        print(f"Leyer {self.name} -> {self.shape}")
    # returns output for a given input
    def forward_propagation(self, input_data):
        self.input = input_data
        self.output = np.dot(self.input, self.weights) + self.bias
        return self.output
    # computes dE/dW, dE/dB for a given output_error=dE/dY. Returns input_error=dE/dX.
    def backward_propagation(self, output_error, learning_rate):
        input_error = np.dot(output_error, self.weights.T)
        weights_error = np.dot(self.input.T, output_error)
        # dBias = output_error

        # update parameters
        self.weights -= learning_rate * weights_error
        self.bias -= learning_rate * output_error
        return input_error

class Network:
    def __init__(self):
        self.layers = []
        self.loss = None
        self.loss_prime = None

    # add layer to network
    def add(self, layer):
        self.layers.append(layer)

    # set loss to use
    def use(self, loss, loss_prime):
        self.loss = loss
        self.loss_prime = loss_prime

    # predict output for given input
    def predict(self, input_data):
        # sample dimension first
        samples = len(input_data)
        result = []

        # run network over all samples
        for i in range(samples):
            # forward propagation
            output = input_data[i]
            for layer in self.layers:
                output = layer.forward_propagation(output)
            result.append(output)

        return result

    # train the network
    def fit(self, x_train, y_train, epochs, learning_rate,show=False):
        # sample dimension first
        samples = len(x_train)

        # training loop
        err = 0
        for i in range(epochs):
            err = 0
            for j in range(samples):
                # forward propagation
                output = x_train[j]
                for layer in self.layers:
                    output = layer.forward_propagation(output)

                # compute loss (for display purpose only)
                err += self.loss(y_train[j], output)

                # backward propagation
                error = self.loss_prime(y_train[j], output)
                for layer in reversed(self.layers):
                    error = layer.backward_propagation(error, learning_rate)

            # calculate average error on all samples
            err /= samples
            if show:
                print(f'\repoch {i+1}/{epochs}   error={err:.5f}',end="")
        #print(f'\repoch {epochs}   error={err:.5f}',end="")
        return err

def initialize_neural_net(arh,n_layer):
    net = Network()
    net.add(FCLayer(arh[0], arh[1],0))
    net.add(ActivationLayer(tanh, tanh_prime))

    if len(arh)==2:
        pass

    elif len(arh)==3:
        net.add(FCLayer(arh[n_layer-2], arh[n_layer-2],1))
        net.add(ActivationLayer(tanh, tanh_prime))

    else:
        for l in range(1,n_layer-2,1):
            net.add(FCLayer(arh[l], arh[l+1],l))
            net.add(ActivationLayer(tanh, tanh_prime))
        net.add(FCLayer(arh[n_layer-2], arh[n_layer-2],n_layer-2))
        net.add(ActivationLayer(tanh, tanh_prime))
    net.add(FCLayer(arh[n_layer-2], arh[n_layer-1],n_layer-1))
    net.add(ActivationLayer(tanh, tanh_prime))
    return net