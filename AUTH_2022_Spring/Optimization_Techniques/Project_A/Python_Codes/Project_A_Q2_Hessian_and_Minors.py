import numpy as np
from sympy import symbols, Eq, solve, zeros, Matrix, pprint
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#######For interactive 3D Plots in JuPyter environment, uncomment the following line
#%matplotlib notebook


#defining the variables
x1, x2 = symbols('x1 x2')
symbol_list = [x1, x2]

#defining the functions
f1 = 8*(x1**2) + 3*x1*x2 + 7*(x2**2) - 25*x1 + 31*x2
f2 = x1**2 - 2*x1*(x2**2) + x2**4 - x2**5
f3 = 100*((x2 - x1**2)**2) + (1-x1)**2


formula = 1   #selecting which of the 3 functions to optimize

if formula == 1:
    func = f1
    x = np.arange(-30, 30, 0.25)    #for 3D plotting
    y = np.arange(-30, 30, 0.25)    #for 3D plotting
    x, y = np.meshgrid(x, y)        #for 3D plotting
    z = 8*(x**2) + 3*x*y + 7*(y**2) - 25*x + 31*y     #for 3D plotting
    
elif formula == 2:
    func = f2
    x = np.arange(-30, 30, 0.25)
    y = np.arange(-30, 30, 0.25)
    x, y = np.meshgrid(x, y)
    z = x**2 - 2*x*(y**2) + y**4 - y**5

else:
    func = f3
    x = np.arange(-30, 30, 0.25)
    y = np.arange(-30, 30, 0.25)
    x, y = np.meshgrid(x, y)
    z = 100*((y - x**2)**2) + (1-x)**2
    
    

def main():
    print("\nFunction:")
    pprint(func)
    
    
    #calculating the gradient vector
    gradient = []
    for element in symbol_list:
        gradient.append(func.diff(element))
    
    print("\nGradient:")
    pprint(Matrix(gradient))
    
    #building the equations for for first necessary condition
    gradient_equations = []
    for expression in gradient:
        gradient_equations.append(Eq(expression, 0))
    
    #Solving the equation to calculate critical points
    x_star_set = solve(gradient_equations, symbol_list, dict=True)
    
    print("\nList of Points satisfying the necessary condition:")
    print(x_star_set)
    
    
    #building the Hessian Matrix
    hessian_mat = zeros(len(symbol_list), len(symbol_list))
    for i in range(len(symbol_list)):
        for j  in range(len(symbol_list)):
            hessian_mat[i,j] = func.diff(symbol_list[i]).diff(symbol_list[j])
    print("\nGeneral form of the Hessian Matrix:")
    pprint(hessian_mat)
    
    #calculating the Hessian Matrices for all of the critical points
    set_of_hessians = {}    
    for x_star in x_star_set:
        hessian_key = []
        for key in x_star:
            hessian_key.append(x_star[key])
        set_of_hessians[tuple(hessian_key)] = hessian_mat.subs(x_star)
    
    
    print("\n\n***** Methods: Minors of the Hessian Matrix & Eigenvalues of the Hessian Matrix *****\n\n")
    counter = 0
    for point in set_of_hessians:
        print("&&& Point number {} that satisfies the necessary condition:\n".format(counter+1))
        print("{}\n".format(point))
        print("The Hessian matrix at point {}:\n".format(point))
        hessian = set_of_hessians[point]
        pprint(hessian)
        #calculating Minors
        minors = []
        for i in range(len(symbol_list)):
            if i == 0:
                minors.append(hessian[0])
            else:
                minor_submatrix = hessian.extract(list(range(i+1)), list(range(i+1)))
                minors.append(minor_submatrix.det())
    
        print("\n### Method #1: Minors:")
        for i in range(len(minors)):
            print("Delta_{} = {}".format(i+1, minors[i]))
        
        
        #Analyzing the minors to determine whether the critical points are a local optimizer.
        #If yes, determining whether they are Minimizers or Maximizers.    
        sum_flag = 0
        for i in range(len(minors)):
            if minors[i] > 0:
                sum_flag = sum_flag + 1
            else:
                break
        if sum_flag == len(minors):
            print("Point {} is a LOCAL MINIMIZER and the value of the function at this point is: {}".format(point, float(func.subs({'x1':point[0], 'x2':point[1]}))))
        else:
            sum_flag = 0
            for i in range(len(minors)):
                if minors[i]*((-1)**(i+1)) < 0:
                    sum_flag = sum_flag + 1
                else:
                    break
            if sum_flag == len(minors):
                print("Point {} is a LOCAL MAXIMIZER and the value of the function at this point is: {}".format(point, float(func.subs({'x1':point[0], 'x2':point[1]}))))
            else:
                print("Point {} is NOT a local optimizer".format(point))
        
        print("\n### Method #2: Eigenvalues:")
        
        #calculating Eigenvalues
        eigenvalues = []
        eigenvalues = hessian.eigenvals(multiple=True)
        print("List of eigenvalues of the Hessian Matrix:\n{}".format(eigenvalues))
        #Analyzing the Eigenvalues to determine whether the critical points are local optimizers.
        #If yes, determining whether they are Minimizers or Maximizers.
        sum_flag = 0
        for ev in eigenvalues:
            if ev > 0:
                sum_flag = sum_flag + 1
            else:
                break
        if sum_flag == len(eigenvalues):
            print("Point {} is a LOCAL MINIMIZER and the value of the function at this point is: {}".format(point, float(func.subs({'x1':point[0], 'x2':point[1]}))))
        else:
            sum_flag = 0
            for ev in eigenvalues:
                if ev < 0:
                    sum_flag = sum_flag + 1
                else: break
            if sum_flag == len(eigenvalues):
                print("Point {} is a LOCAL MAXIMIZER and the value of the function at this point is: {}".format(point, float(func.subs({'x1':point[0], 'x2':point[1]}))))
            else:
                print("Point {} is NOT a local optimizer".format(point))
        print("\n----------------------------------------------\n")

    
    #Plottings
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(x,y,z)
    ax.scatter(point[0], point[1], float(func.subs({'x1':point[0], 'x2':point[1]})), s = 100, color = 'red')
    ax.set_xlabel("X1")
    ax.set_ylabel("X2")
    ax.set_zlabel("F(X1, X2)")
    plt.show()
    

main()













