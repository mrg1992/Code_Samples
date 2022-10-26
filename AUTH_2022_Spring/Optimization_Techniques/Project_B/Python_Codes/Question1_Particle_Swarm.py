import random
import copy
import numpy as np
import matplotlib.pyplot as plt


###### Simply, run this code  #######

###### Problem Initializations ##########
function_select = 0       # zero (0) : first function        &        # one (1) :  second function
if function_select == 0:
    D = 2 #dimension
    boundary = [-10, 10]    #setting the symmetrical boundary
    true_solution = [0] * D
    true_solution_value = 0    #value of the objective function at true solution
else:
    D = 2
    boundary = [-10, 10]
    true_solution = [1, 3]
    true_solution_value = 0


# Setting the number of particles
if D == 2:
    num_of_particles = 30
elif D >= 10:
    num_of_particles = 4 * D + 1


max_iter = 10000
epsilon = 10**(-6)
initial_velocity = [0] * D
theta_max = 0.9
theta_min = 0.4
c1 = 2
c2 = 2



######### Functions ###########
def function1(X):     #Sphere Function
    total = 0
    for x in X:
        total = total + x**2
    return total

def function2(X):     #Booth Function
    return (X[0] + 2*X[1] - 7)**2 + (2*X[0] + X[1] -5)**2

def func(X):          #Objective function ==> returns eaither function1 or function2 based on function_select variable.
    if function_select == 0:
        return function1(X)
    else:
        return function2(X)
        
def F(f):       #Maximization Objective Function
    return 1/(0.1 + f)

def globalBest(particles):     #Returns the Global Best
    local_best_list = []
    for i in range(len(particles)):
        particle = copy.deepcopy(particles[i])
        local_best_list.append(particle['value'])
    max_value = max(local_best_list)
    max_index = local_best_list.index(max_value)
    return [particles[max_index]['position'], max_value]

def euclideanDist(vector1, vector2):     #Returns the euclidean distance between two vectors.
    result = 0
    for i in range(len(vector1)):
        result = result + (vector1[i] - vector2[i])**2
    return np.sqrt(result)


def main():
    final_solution = []
    particles = [] #this list will include dictionaries that contain particles' information
    for i in range(num_of_particles):      #initializing the particles
        #temp_dict is a dictionary that contains:
        #position of the particle, value of the (Maximization) objective function F, local_best point, value of the objective function F at local best point, and velocity
        temp_dict = {'position': [], 'value': 10000000, 'local_best': [], 'local_best_value': 10000000, 'velocity': initial_velocity}
        for j in range(D):
            temp_dict['position'].append(random.uniform(boundary[0], boundary[1]))
        temp_dict['value'] = F(func(temp_dict['position']))
        temp_dict['local_best'] = copy.deepcopy(temp_dict['position'])
        temp_dict['local_best_value'] = copy.deepcopy(temp_dict['value'])
        particles.append(temp_dict)    #temp_dict is added to the particles list.
        
    initial_particles = copy.deepcopy(particles)
    
    global_best = [globalBest(particles)]    #a list of all the global bests per particle, per step, throughout the algorithm. 
    #Note: global_best is NOT the original global best list per each step. It may contain several items per each step.
    
    global_update_tracker = copy.deepcopy(global_best)   #a list of all the global bests per iteration.
    #This is the original list of global bests at the end of each step.
    
    k = -1 # step_count
    
    #main loop
    while k < max_iter - 1:
        k = k + 1
        
        #checking the termination criteria. There are two modes for temination criteria:
        #default: The difference between the value of the objective function at the global best point 
        #         and the value of the objective funcion at the true solution is less than epsilon
        if np.abs(func(global_best[-1][0]) - true_solution_value) < epsilon:
            final_solution = global_best[-1]
            break
        #alternative: the euclidean distance between the global best point and the true solution is less than epsilon
        #Note: to activate the alternative, comment the "if statement above" and uncomment the "if statement below"
        '''if euclideanDist(global_best[-1][0], true_solution) < epsilon:
            final_solution = global_best[-1]
            break'''
        theta = theta_max - ((theta_max - theta_min)/(max_iter))*k    #defining the inertia for the current step.
        
        for i in range(len(particles)):
            particle = copy.deepcopy(particles[i])   #particle a dictionary that contains/updates a single particle's information
            r1 = random.uniform(0, 1)                #randomly assigning r1 and r2 values
            r2 = random.uniform(0, 1)
            velocity = []
            for j in range(D):
                #updating j-th element of velocity vector for particle i at step k
                velocity.append(theta * particle['velocity'][j] + c1*r1*(particle['local_best'][j] - particle['position'][j]) + c2*r2*(global_best[-1][0][j] - particle['position'][j]))
            for j in range(D):
                temp_position = particle['position'][j] + velocity[j]   #updating j-th element of position vector of particle i at step k
                
                if boundary[0] > temp_position:         #implementing absorbing walls
                    temp_position = boundary[0]
                elif boundary[1] < temp_position:
                    temp_position = boundary[1]
                particle['position'][j] = temp_position
            particle['value'] = F(func(particle['position']))    #updating the value of the (Maximization) objective function (F) at new position.
            
            if particle['value'] > particle['local_best_value']:    #updating local best
                particle['local_best'] = copy.deepcopy(particle['position'])
                particle['local_best_value'] = copy.deepcopy(particle['value'])
                if particle['local_best_value'] > global_best[-1][1]:   #updating running global best (not the original one)
                    global_best.append([particle['local_best'], particle['local_best_value']])
            
            particle['velocity'] = copy.deepcopy(velocity)
            
            particles[i] = copy.deepcopy(particle)
            
        global_update_tracker.append(global_best[-1])    #updating global best at the end of each step
    
    optimal_function_value = func(global_best[-1][0])   #optimal value of the original objective funcion (f)
    
    
    #printing the results log:
    print("###### Function number {}".format(function_select + 1))
    print("\nDimension: {}".format(D))
    print("\nSymetrical Boundary: {}".format(boundary))
    print("\nNumber of Particles: {}".format(num_of_particles))
    print("\nMaximum Number of Steps: {}".format(max_iter))
    print("\n\n################## Results ##################")
    print("\nNumber of Steps: {}".format(len(global_update_tracker)))
    print("\nOptimal X vector:\n{}".format(global_best[-1][0]))
    print("\nOptimal Function Value: {}".format(optimal_function_value))
    print("\nDifference between Found Optimal Value and True Optimal Value: {}".format(np.abs(func(global_best[-1][0]) - true_solution_value)))
    print("\nEuclidean Distance from True Solution: {}".format(euclideanDist(global_best[-1][0], true_solution)))
    
    
    #Plotting the global best values at each step
    plot_x = []
    plot_y = []
    for i in range(len(global_update_tracker)):
        plot_x.append(i + 1)
        plot_y.append(func(global_update_tracker[i][0]))
            
    #fig = plt.figure()
    plt.plot(plot_x, plot_y)
    plt.xlabel("Iterations")
    plt.ylabel("Global Best Value")
    title = "Global Best Value at each iteration for function #{} ; Dimension = {} ; Symmetrical Boundary = {}".format(function_select + 1, D, boundary)
    plt.title(title)
    plt.grid()
    plt.show()
    
main()        
