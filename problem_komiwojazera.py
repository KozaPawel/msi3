# Imports 
import numpy as np
import random
import PySimpleGUI as sg
from faker import Faker
fake = Faker()
import time
import _thread

from datetime import datetime

# sg.Window(title="Problem komiwojażera", layout=[[]], margins=(800,600)).read()
sg.theme('Python')
  
control_col = sg.Column([
    [sg.Text('Wprowadź dane'), sg.Button('Wyczyść')],
    [sg.Output(size=(80,12), key="_output_")],
    [sg.Text('Ilość miast', size =(20, 1)), sg.Slider(range=(10, 99), resolution=10, size =(40, 20), orientation="h", key="_ilosc_")],
    [sg.Text('Wielkość populacji', size =(20, 1)), sg.Slider(range=(150, 1000), resolution=10, size =(40, 20), orientation="h", key="_wielkosc_")],
    [sg.Text('Tempo mutacji', size =(20, 1)), sg.Slider(range=(0.1, 1.0), resolution=0.1, size =(40, 20), orientation="h",key="_tempo_")],
    [sg.Text('Ilość rund', size =(20, 1)), sg.Slider(range=(100, 10000), resolution=50, size =(40, 20), orientation="h",key="_rundy_")],
    [sg.Button('Start'), sg.Button('Wyjdź')]
], vertical_alignment='top')

info_col = sg.Column([
    [sg.Text('Koordynaty miast:'), sg.Multiline('', size =(40, 12), key="_koordynaty_miast_")],
    [sg.Text('Numer najlepszego rozwiązania:'), sg.Text('', size =(20, 1), key="_rozwiazanie_")],
    [sg.Text('Odległość:'), sg.Text('', size =(20, 1), key="_odleglosc_")],
    [sg.Text('Kolejność miast:'), sg.Multiline('', size =(40, 12), key="_miasta_")],
], vertical_alignment='top')

layout = [[control_col, sg.VSeparator(), info_col]]

window = sg.Window('Problem komiwojażera', layout)

while True:
    event, values = window.read()

    if event in (None, 'Wyjdź'):
        break

    if event == 'Start':
        window['_miasta_'].update('')
        window['_rozwiazanie_'].update('')
        window['_odleglosc_'].update('')

        n_cities = int(values['_ilosc_'])
        n_population = int(values['_wielkosc_'])
        mutation_rate = float(values['_tempo_'])
        rounds = int(values['_rundy_'])

        # Generating a list of coordenades representing each city
        coordinates_list = [[x,y] for x,y in zip(np.random.randint(0,100,n_cities),np.random.randint(0,100,n_cities))]

        names_list = np.array(['Warsaw'])
        for i in range(n_cities-1):
            names_list = np.append(names_list, fake.city())

        cities_dict = { x:y for x,y in zip(names_list,coordinates_list)}

        # Function to compute the distance between two points
        def compute_city_distance_coordinates(a,b):
            return ((a[0]-b[0])**2+(a[1]-b[1])**2)**0.5

        def compute_city_distance_names(city_a, city_b, cities_dict):
            return compute_city_distance_coordinates(cities_dict[city_a], cities_dict[city_b])

        window['_koordynaty_miast_'].update(cities_dict)

        # First step: Create the first population set
        def genesis(city_list, n_population):

            population_set = []
            for i in range(n_population):
                #Randomly generating a new solution
                sol_i = city_list[np.random.choice(list(range(n_cities)), n_cities, replace=False)]
                population_set.append(sol_i)
            return np.array(population_set)

        population_set = genesis(names_list, n_population)
        population_set

        def fitness_eval(city_list, cities_dict):
            total = 0
            for i in range(n_cities-1):
                a = city_list[i]
                b = city_list[i+1]
                total += compute_city_distance_names(a,b, cities_dict)
            return total
        def get_all_fitnes(population_set, cities_dict):
            fitnes_list = np.zeros(n_population)

            #Looping over all solutions computing the fitness for each solution
            for i in  range(n_population):
                fitnes_list[i] = fitness_eval(population_set[i], cities_dict)

            return fitnes_list

        fitnes_list = get_all_fitnes(population_set,cities_dict)
        fitnes_list

        def progenitor_selection(population_set,fitnes_list):
            total_fit = fitnes_list.sum()
            prob_list = fitnes_list/total_fit
            
            #Notice there is the chance that a progenitor. mates with oneself
            progenitor_list_a = np.random.choice(list(range(len(population_set))), len(population_set),p=prob_list, replace=True)
            progenitor_list_b = np.random.choice(list(range(len(population_set))), len(population_set),p=prob_list, replace=True)
            
            progenitor_list_a = population_set[progenitor_list_a]
            progenitor_list_b = population_set[progenitor_list_b]
            
            
            return np.array([progenitor_list_a,progenitor_list_b])


        progenitor_list = progenitor_selection(population_set,fitnes_list)
        progenitor_list[0][2]

        def mate_progenitors(prog_a, prog_b):
            offspring = prog_a[0:5]

            for city in prog_b:

                if not city in offspring:
                    offspring = np.concatenate((offspring,[city]))

            return offspring
                    
        def mate_population(progenitor_list):
            new_population_set = []
            for i in range(progenitor_list.shape[1]):
                prog_a, prog_b = progenitor_list[0][i], progenitor_list[1][i]
                offspring = mate_progenitors(prog_a, prog_b)
                new_population_set.append(offspring)
                
            return new_population_set

        new_population_set = mate_population(progenitor_list)
        new_population_set[0]

        def mutate_offspring(offspring):
            for q in range(int(n_cities*mutation_rate)):
                a = np.random.randint(0,n_cities)
                b = np.random.randint(0,n_cities)

                offspring[a], offspring[b] = offspring[b], offspring[a]

            return offspring
            
        def mutate_population(new_population_set):
            mutated_pop = []
            for offspring in new_population_set:
                mutated_pop.append(mutate_offspring(offspring))
            return mutated_pop

        mutated_pop = mutate_population(new_population_set)
        mutated_pop[0]

        best_solution = [-1,np.inf,np.array([])]
        for i in range(rounds):
            print(i, fitnes_list.min(), fitnes_list.mean(), datetime.now().strftime("%H:%M:%S"))
            window.Refresh()
            fitnes_list = get_all_fitnes(mutated_pop,cities_dict)
            
            #Saving the best solution
            if fitnes_list.min() < best_solution[1]:
                best_solution[0] = i+1
                best_solution[1] = fitnes_list.min()
                best_solution[2] = np.array(mutated_pop)[fitnes_list.min() == fitnes_list]
            
            progenitor_list = progenitor_selection(population_set,fitnes_list)
            new_population_set = mate_population(progenitor_list)
            
            mutated_pop = mutate_population(new_population_set)

        window['_odleglosc_'].update(best_solution[1])
        window['_rozwiazanie_'].update(best_solution[0])
        window['_miasta_'].update(best_solution[2])

    if event == "Wyczyść":
        window['_output_'].update('')
        window['_odleglosc_'].update('')
        window['_rozwiazanie_'].update('')
        window['_miasta_'].update('')
        window['_koordynaty_miast_'].update('')
        
window.close()