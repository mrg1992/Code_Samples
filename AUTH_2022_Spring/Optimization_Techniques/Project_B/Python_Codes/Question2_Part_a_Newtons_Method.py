import numpy as np
from sympy import symbols, zeros, Matrix, pprint, sqrt
import random
import copy
import time


#defining the variables
x1, x2 = symbols('x1 x2')
symbol_list = [x1, x2]

#defining the functions
f1 = (x1 + 2*x2 - 7)**2 + (2*x1 + x2 -5)**2    #Booth Function
f2 = 0.26*(x1**2 + x2**2) - 0.48*x1*x2         #Matyas Function
f3 = 2*(x1**2) - 1.05*(x1**4) + (x1**6)/6 + x1*x2 + x2**2     #Three-hump Camel Function

random_initiation = 0
formula = 1   #selecting which of the 3 functions to optimize

if formula == 1:
    func = f1
    boundary = [-4.5, 4.5]
    func_name = "Booth Function"
elif formula == 2:
    func = f2
    boundary = [-10, 10]
    func_name = "Matyas Function"
else:
    func = f3
    boundary = [-5, 5]
    func_name = "Three-hump Camel Function"

epsilon = 10**(-6)
print("\nValue for ending critera (Epsilon): {}".format(epsilon))
N_max = 10000
alpha = 1


start_time = time.time()
if random_initiation == 1:
    X_0 = [random.uniform(boundary[0], boundary[1]), random.uniform(boundary[0], boundary[1])]
else:
    X_0 = [-1, -1]
def main():
    print("\nFunction:")
    print(func_name)
    #pprint(func)
    
    
    #calculating the gradient vector
    gradient = []
    for element in symbol_list:
        gradient.append(func.diff(element))
    gradient = Matrix(len(symbol_list), 1, gradient)
    #print("\nGradient:")
    #pprint(Matrix(gradient))
    
    #building the Hessian Matrix
    hessian_mat = zeros(len(symbol_list), len(symbol_list))
    for i in range(len(symbol_list)):
        for j  in range(len(symbol_list)):
            hessian_mat[i,j] = func.diff(symbol_list[i]).diff(symbol_list[j])
    #print("\nGeneral form of the Hessian Matrix:")
    #pprint(hessian_mat)
    
    X_k = Matrix(len(symbol_list), 1, X_0)
    X_vals = []         #keeping track of the iterations
    
    print("\n\nInitial point X_0:\n")
    pprint(X_k)
    print("\n\n")
    
    optimizer = []
    
    for i in range(N_max):
        if i == 0:
            gradient_k = gradient.subs({'x1': X_k[0,0], 'x2': X_k[1,0]})
            hessian_mat_k = hessian_mat.subs({'x1': X_k[0,0], 'x2': X_k[1,0]})
            grad_k_norm = sqrt(((gradient_k.T)*gradient_k)[0])
            X_vals = [[list(X_k.T), grad_k_norm, func.subs({'x1': X_k[0,0], 'x2': X_k[1,0]})]]
            
        #print(grad_k_norm)
        if grad_k_norm < epsilon:
            optimizer = [X_k, grad_k_norm, func.subs({'x1': X_k[0,0], 'x2': X_k[1,0]})]
            break
        else:
            X_k1 = X_k - ((hessian_mat_k.inv()) * gradient_k)
            gradient_k1 = gradient.subs({'x1': X_k1[0,0], 'x2': X_k1[1,0]})
            grad_k1_norm = sqrt(((gradient_k1.T)*gradient_k1)[0])
            X_vals.append([list(X_k1.T), grad_k1_norm, func.subs({'x1': X_k1[0,0], 'x2': X_k1[1,0]})])
            X_k = copy.deepcopy(X_k1)
            gradient_k = copy.deepcopy(gradient_k1)
            grad_k_norm = copy.deepcopy(grad_k1_norm)
    
    print("\n\n#$#$#$ Solution $#$#$#\n")
    if optimizer == []:
        print("The algorithm failed to find the optimal point.")
    else:
        print("The algorith found a MINIMIZER:\n")
        print("X = [{}, {}]\nThe value of the function: {}\nThe norm of the gradient vector: {}".format(optimizer[0][0], optimizer[0][1], optimizer[2], optimizer[1]))
        print("\nThe algorithm took {} iterations to find the solution.\n".format(len(X_vals)))
        
        
main()

end_time = time.time()
runtime_sec = end_time - start_time

print("\nThe algorithm took {} minutes and {} seconds to run.".format(int(runtime_sec/60), runtime_sec % 60))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    