import numpy as np
from amadeus import Flights
import pandas as pd
import random
import datetime
import time
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


def choose_countries(origin, number_countries, number_continents):
    DATA_PATH = 'static/custom.csv'
    airport_code = pd.read_csv(DATA_PATH, keep_default_na=False)
    list_cities = list(airport_code.city)
    list_continents = list(airport_code.continent)
    list_countries = list(airport_code.country)
    list_codes = list(airport_code.code)
    tmp = list(range(len(list_cities)))
    index = random.sample(tmp, number_countries)
    num_countries = len(set([list_countries[x] for x in index]))
    num_continents = len(set([list_continents[x] for x in index]))
    while num_continents != number_continents and num_countries != number_countries:
        index = random.sample(range(len(list_cities)), num_countries)
        num_countries = len(set([list_countries[x] for x in index]))
        num_continents = len(set([list_continents[x] for x in index]))
    return [origin] + [list_codes[x] for x in index]


def find_best_travel(list_airports=None, days=None, num_countries=None,
                     departure_date=None):
    flights = Flights('rTgACcDGGTOrYi9vGotfQOM2wfHAGly8')
    if departure_date == None:
        departure_date = time.time()

    days_per_city = int(days / num_countries)
    distance_matrix = np.zeros((len(list_airports), len(list_airports)))
    for i, airport_departure in enumerate(list_airports):
        print(airport_departure)
        for j, airport_arrival in enumerate(list_airports):
            print(airport_arrival)
            if airport_arrival == airport_departure:
                distance_matrix[i, j] = 0
            else:
                prices_list = []
                for duration in range(0, 40, days_per_city):
                    print(duration)
                    date = datetime.datetime.fromtimestamp(departure_date + duration * 24 * 3600).strftime('%Y-%m-%d')
                    print(date)
                    resp = flights.low_fare_search(
                        origin=airport_departure,
                        destination=airport_arrival,
                        departure_date=date,
                        duration='1')
                    try:
                        price = resp['results'][0]['fare']['total_price']
                    except:
                        continue

                    print(price)
                    prices_list.append(float(price))
                if prices_list == []:
                    distance_matrix[i, j] = 10e6
                else:
                    distance_matrix[i, j] = np.mean(prices_list)
    return distance_matrix


def compute_optimal_tour(matrix, list_airports):
    # Distance callback
    class CreateDistanceCallback(object):
        """Create callback to calculate distances between points."""

        def __init__(self, matrix):
            """Array of distances between points."""
            self.matrix = matrix

        def Distance(self, from_node, to_node):
            return int(self.matrix[from_node][to_node])

    # Cities
    city_names = list_airports
    tsp_size = len(list_airports)
    num_routes = 1  # The number of routes, which is 1 in the TSP.
    # Nodes are indexed from 0 to tsp_size - 1. The depot is the starting node of the route.
    depot = 0

    # Create routing model
    if tsp_size > 0:
        routing = pywrapcp.RoutingModel(tsp_size, num_routes, depot)
        search_parameters = routing.DefaultSearchParameters()

        # Create the distance callback, which takes two arguments (the from and to node indices)
        # and returns the distance between these nodes.
        dist_between_nodes = CreateDistanceCallback(matrix)
        dist_callback = dist_between_nodes.Distance

        routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)
        # Solve, returns a solution if any.
        assignment = routing.SolveWithParameters(search_parameters)

        if assignment:
            # Solution cost.
            print ("Total duration: " + str(np.round(assignment.ObjectiveValue(), 3)) + " $\n")
            cost = np.round(assignment.ObjectiveValue(), 3)
            # Inspect solution.
            # Only one route here; otherwise iterate from 0 to routing.vehicles() - 1
            route_number = 0
            index = routing.Start(route_number)  # Index of the variable for the starting node.
            route = ''
            list_cities = []
            while not routing.IsEnd(index):
                # Convert variable indices to node indices in the displayed route.
                route += str(city_names[routing.IndexToNode(index)]) + ' -> '
                list_cities.append(city_names[routing.IndexToNode(index)])
                index = assignment.Value(routing.NextVar(index))
            route += str(city_names[routing.IndexToNode(index)])

            print ("Route:\n\n" + route)
        else:
            print ('No solution found.')
    else:
        print ('Specify an instance greater than 0.')

    return list_cities, cost
