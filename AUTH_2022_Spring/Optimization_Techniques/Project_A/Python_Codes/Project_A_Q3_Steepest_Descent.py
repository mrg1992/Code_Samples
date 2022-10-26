from sympy import symbols, Matrix, sqrt, pprint
import copy
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import xlsxwriter
import random

#######For interactive 3D Plots in JuPyter environment, uncomment the following line
#%matplotlib notebook


##### Question Data #####

x1, x2, x3 = symbols('x1 x2 x3')
symbol_list = [x1, x2, x3]
X = Matrix(3, 1, [x1, x2, x3])

Q1 = Matrix([[1, 0, 0], [0, 5, 0], [0, 0, 25]])
b1 = Matrix(3, 1, [-1, -1, -1])

Q2 = Matrix([[-1, 0, 0], [0, 5, 0], [0, 0, 25]])
b2 = Matrix(3, 1, [-1, -1, -1])

formula = 1       #selecting which of the 2 functions to optimize
if formula == 1:
    Q = Q1
    b = b1
else:
    Q = Q2
    b = b2



alpha_constant = -100             #if alpha_constant is not positive then the algorithm will calculate the values for alpha in each step.
#alpha_constant = 0.05



f = ((1/2)*(X.T)*Q*X - (b.T)*X)[0]
print("\n###### Optimization problem ######\n")
print("Matrix Q:")
pprint(Q)
print("\nVector b:")
pprint(b)
print("\nFunction:\n")
pprint(f)

print("\nValue for ending critera (Epsilon):")
epsilon = 10**(-5)
print(epsilon)

#setting a flag to determine whether the user has assigned a valid constant alpha. If not, the algorithm will calculate the value of alpha at each iteration.
if alpha_constant <= 0:
    user_alpha_flag = 0
else:
    user_alpha_flag = 1
    print("\nThe value of alpha is defined by user:\nalpha = {}".format(alpha_constant))

print("\nMaximum number of allowed iterations:")
N_max = 1000       #Maximum number of iterations
print(N_max)


##### Solution #####
def main():
    #calculating the gradient vector
    gradient = []
    for element in symbol_list:
        gradient.append(f.diff(element))
    gradient = Matrix(len(symbol_list), 1, gradient)
    print("\nGradient of the function:\n")
    pprint(gradient)
    
    X_0 = [1, 1, 1]     #initial point
    X_k = Matrix(len(symbol_list), 1, X_0)
    X_vals = []         #keeping track of the iterations
    
    print("\n\nInitial point X_0:\n")
    pprint(X_k)
    print("\n\n")
    
    optimizer = []
    for i in range(N_max):
        if i == 0:
            gradient_k = gradient.subs({'x1': X_k[0,0], 'x2': X_k[1,0], 'x3': X_k[2,0]})
            grad_k_norm = sqrt(((gradient_k.T)*gradient_k)[0])
            X_vals = [[list(X_k.T), grad_k_norm, f.subs({'x1': X_k[0,0], 'x2': X_k[1,0], 'x3': X_k[2,0]})]]
            
        if grad_k_norm < epsilon:
            optimizer = [X_k, grad_k_norm, f.subs({'x1': X_k[0,0], 'x2': X_k[1,0], 'x3': X_k[2,0]})]
            break
        else:
            if user_alpha_flag == 0:
                alpha_k = (((gradient_k.T)*gradient_k))[0]/(((gradient_k.T)*Q*gradient_k)[0])
            else:
                alpha_k = alpha_constant
            X_k1 = X_k - alpha_k*gradient_k       #updating X(k+1)
            gradient_k1 = gradient.subs({'x1': X_k1[0,0], 'x2': X_k1[1,0], 'x3': X_k1[2,0]})
            grad_k1_norm = sqrt(((gradient_k1.T)*gradient_k1)[0])
            X_vals.append([list(X_k1.T), grad_k1_norm, f.subs({'x1': X_k1[0,0], 'x2': X_k1[1,0], 'x3': X_k1[2,0]})])
            X_k = copy.deepcopy(X_k1)
            gradient_k = copy.deepcopy(gradient_k1)
            grad_k_norm = copy.deepcopy(grad_k1_norm)
    
    print("\n\n#$#$#$ Solution $#$#$#\n")
    if optimizer == []:
        print("The algorithm failed to find the optimal point.")
    else:
        print("The algorith found a MINIMIZER:\n")
        print("X = [{}, {}, {}]\nThe value of the function at point X = {}\nThe norm of the gradient vector at point X = {}".format(optimizer[0][0], optimizer[0][1], optimizer[0][2], optimizer[2], optimizer[1]))
        print("\nThe algorithm took {} iterations to find the solution.\n".format(len(X_vals)))
        print("\n\nThe steps are summarized below:\n\n")
        
        #writing the details of each iteration into an excel file
        #a random file_name is generated to avoid problems in case a previously generated file is still open.
        file_name = "supplementary_Q3_{}.xlsx".format(random.randint(1, 200))
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet()
        worksheet.set_column(0, 5, 20)
        worksheet.write(0, 0, "Function")
        worksheet.write(0, 1, formula)
        worksheet.write(1, 0, "Alpha")
        if user_alpha_flag == 0:
            worksheet.write(1, 1, "Not Defined by User")
        else:
            worksheet.write(1, 1, "Defined by User")
            worksheet.write(1, 2, alpha_constant)
        worksheet.write(3, 0, "Initial X vector")
        worksheet.write(4, 0, "Initial X1")
        worksheet.write(4, 1, X_0[0])
        worksheet.write(5, 0, "Initial X2")
        worksheet.write(5, 1, X_0[1])
        worksheet.write(6, 0, "Initial X3")
        worksheet.write(6, 1, X_0[2])
        worksheet.write(9, 0, "k")
        worksheet.write(9, 1, "X1")
        worksheet.write(9, 2, "X2")
        worksheet.write(9, 3, "X3")
        worksheet.write(9, 4, "Gradient Norm")
        worksheet.write(9, 5, "Function Value")
        row = 10
        col = 0
        for k in range(len(X_vals)):
            print("\nk = {}\tX_{} = {}\t\t\tgrad(f(X_{})) = {}\t\tValue of f(X_{}) = {}".format(k, k, X_vals[k][0], k, X_vals[k][1], k, X_vals[k][2]))
            worksheet.write(row + k, 0, k)
            worksheet.write(row + k, 1, X_vals[k][0][0])
            worksheet.write(row + k, 2, X_vals[k][0][1])
            worksheet.write(row + k, 3, X_vals[k][0][2])
            worksheet.write(row + k, 4, X_vals[k][1])
            worksheet.write(row + k, 5, X_vals[k][2])
        workbook.close()
    
    #Plottings
    x, y, z = [], [], []
    for i in range(len(X_vals)):
        x.append(X_vals[i][0][0])
        y.append(X_vals[i][0][1])
        z.append(X_vals[i][0][2])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x, y, z)
    ax.set_xlabel("X1")
    ax.set_ylabel("X2")
    ax.set_zlabel("X3")
    plt.show()    
    
main()
