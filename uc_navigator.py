## ================================================================================================================ ##
## ================================================================================================================ ##
##                                                                                                                  ##
##     _______________    _______________    _______________    ____          __     ____     __            __      ##
##    _______________    _______________    _______________    / /\ \        / /    / /\ \    \ \          / /      ##
##         ___          / /                / /                / /  \ \      / /    / /  \ \    \ \        / /       ##
##        ___          / /________        / /                / /    \ \    / /    / / __ \ \    \ \      / /        ##
##       ___          / /                / /                / /      \ \  / /    / /      \ \    \ \    / /         ##
##      ___          _______________    _______________    / /        \ \/ /    / /        \ \    \ \__/ /          ##
##     ___          _______________    _______________    / /          \ \/    / /          \ \    \____/           ##
##                                                                                                                  ##
## ================================================================================================================ ##
## ================================================================================================================ ##

### IMPORTS
# Data Management
import numpy as np
import pandas as pd
import pickle
# Utils
import ast
import argparse
import logging
import pprint
from datetime import datetime, timedelta
from random import choice
from time import sleep


class TecNav:

    def __init__(self, df, clinics_info, model, code_ratio=0):
        """Instantiate necessary data structures required for application."""

        self.df = df
        self.clinics_info = clinics_info
        self.model = model
        if code_ratio == None:
            self.code_ratio = 0
        else:
            self.code_ratio = code_ratio

        self.movements = []
        self.current_num_techs_col = []
        self.moves_within_hour = 0
        self.stag = 0
        self.potential_move = 0

        # Scheduled starting technician count at each location
        denver_start = df[df.visit_location == 'denver'].iloc[0]['new_num_techs']
        wheatridge_start = df[df.visit_location == 'wheatridge'].iloc[0]['new_num_techs']
        edgewater_start = df[df.visit_location == 'edgewater'].iloc[0]['new_num_techs']
        rino_start = df[df.visit_location == 'rino'].iloc[0]['new_num_techs']
        lakewood_start = df[df.visit_location == 'lakewood'].iloc[0]['new_num_techs']

        self.tracker = {
            'denver': {'checkin_time': None, 'num_techs': denver_start,'needed_techs': 0, 'flag': 0, 'available_techs': 0, 'rolling_code': 0, 'timestamp_recent_move': None},
            'edgewater': {'checkin_time': None, 'num_techs': edgewater_start,'needed_techs': 0, 'flag': 0, 'available_techs': 0, 'rolling_code': 0, 'timestamp_recent_move': None},
            'wheatridge': {'checkin_time': None, 'num_techs': wheatridge_start,'needed_techs': 0, 'flag': 0, 'available_techs': 0, 'rolling_code': 0, 'timestamp_recent_move': None},
            'rino': {'checkin_time': None, 'num_techs': rino_start,'needed_techs': 0, 'flag': 0, 'available_techs': 0, 'rolling_code': 0, 'timestamp_recent_move': None},
            'lakewood': {'checkin_time': None, 'num_techs': lakewood_start,'needed_techs': 0, 'flag': 0, 'available_techs': 0, 'rolling_code': 0, 'timestamp_recent_move': None}
            }


    def update_tracker(self, indx, row):
        """Update tracker dictionary with current iteration's patient check-in record information."""

        # Save information from the streamed patient check-in record (current iteration of row)
        self.indx = indx
        self.location = row['visit_location']
        self.checkin_time = row['checkin_time']
        self.num_techs = self.tracker[self.location]['num_techs']
        self.needed_techs = row['needed_num_techs']

        # Update dynamic dictionary (tracker) with current record's data
        self.tracker[self.location]['checkin_time'] = self.checkin_time
        self.current_num_techs = self.tracker[self.location]['num_techs']
        self.current_num_techs_col.append(self.current_num_techs)
        self.tracker[self.location]['needed_techs'] = self.needed_techs
        self.available_techs = self.tracker[self.location]['num_techs'] - self.tracker[self.location]['needed_techs']
        self.tracker[self.location]['available_techs'] = self.available_techs
        self.tracker[self.location]['rolling_code'] = row['rolling_code']

        return

    def check_flag_is_one(self):
        """Checks flag status in tracker for the currently streaming record's location."""

        return self.tracker[self.location]['flag'] == 1

    def should_flag_be_one(self):
        """Checks if flag status should be one for the currently streaming record's location."""

        return self.tracker[self.location]['num_techs'] == self.tracker[self.location]['needed_techs']

    def set_flag(self):
        """Marks flag status in tracker for the curently streaming record's location."""

        self.tracker[self.location]['flag'] = 1

    def reset_flag(self):
        """Resets flag status in tracker for the currently streaming record's location."""

        self.tracker[self.location]['flag'] = 0

    def do_we_navigate(self):
        """Called upon if flag was already marked, to check if more technicians are needed."""

        bool = (self.tracker[self.location]['num_techs'] < self.tracker[self.location]['needed_techs'])  \
            & (self.tracker[self.location]['rolling_code'] >= self.code_ratio)

        return bool

    def check_availability(self):
        """Called upon if we should navigate, to check the availability of nearby clinics."""

        available = []
        for clinic in self.clinics_info.loc[self.location, 'nearby_clinics']:
            avail_techs = self.tracker[clinic[0]]['available_techs']
            if avail_techs > 0:
                available.append(clinic)
        return available

    def find_pull_from(self, available):

        while len(available) > 0:

            pull_from = available[0][0]
            print(f'- Assessing if {pull_from.capitalize()} is a feasible location to pull technician from.')
            num_avail = self.tracker[pull_from]['available_techs']

            if num_avail != 1:
                return pull_from

            elif num_avail == 1:
                print(f'  {pull_from.capitalize()} only has 1 technician available \n  Deploy ML model to assess if transfer is feasible:')
                test_set = self.df[['denver', 'edgewater', 'wheatridge', 'rino', 'lakewood', 'weekend', 'hour']].copy()
                needed_num_techs_pred = self.model.predict(test_set[test_set.index == self.indx])[0]
                print(f"    - Predicted amount needed = {int(needed_num_techs_pred)} | Current amount needed = {self.tracker[pull_from]['needed_techs']}")

                if needed_num_techs_pred < self.tracker[pull_from]['needed_techs']:
                    print(f'  Model anticipates {pull_from.capitalize()} clinic to become less busy; feasible to pull from this location.')
                    return pull_from

                elif needed_num_techs_pred >= self.tracker[pull_from]['needed_techs']:
                    print(f"        - ML model recommends no transfer from {pull_from.capitalize()}")
                    available.pop(0)
        return None

    def pull_technician(self, pull_from):
        """Conduct navigation based on location to pull from."""
        print(f"- Pull technician from nearest clinic: {pull_from.capitalize()}, {self.tracker[pull_from]['available_techs']} available")

        departure_time = datetime.strptime(str(self.checkin_time), '%H:%M:%S') + timedelta(minutes=2, seconds=choice([i for i in range(60)]))

        # EVALUATION PURPOSES: Track instances where clinic who transferred a tech, needed one within next hour
        if self.tracker[self.location]['timestamp_recent_move'] != None:
            if departure_time + timedelta(minutes=60) < self.tracker[self.location]['timestamp_recent_move']:
                self.moves_within_hour += 1

        self.tracker[pull_from]['timestamp_recent_move'] = departure_time

        print(f'- Technician from {pull_from.capitalize()} left at {departure_time.time()}')

        # Update tracker dict by subtracting 1 tech from pull_from
        self.tracker[pull_from]['num_techs'] += -1

        # Update tracker dict by adding 1 to location
        self.tracker[self.location]['num_techs'] += 1

        travel_time = int(self.clinics_info.loc[pull_from, 'to_'+self.location]) + choice([0, 2, 3, 4, 5, 6])
        arrival_time = departure_time + timedelta(minutes=int(travel_time), seconds=choice([i for i in range(60)]))
        print(f"- Technician from {pull_from.capitalize()} arrived at {self.location.capitalize()} at {arrival_time.time()}")
        print(f'- {self.location.capitalize()}: before count = {self.num_techs} | after count = {self.tracker[self.location]["num_techs"]}')
        print(f'- {pull_from.capitalize()}: before count = {self.tracker[pull_from]["num_techs"]+1} | after count = {self.tracker[pull_from]["num_techs"]}')
        print()
        self.movements.append((pull_from, self.location))
        return

    def execute_navigation(self):
        """Calls upon the necessary class methods to stream patient records one-by-one and conduct navigation when needed."""

        # Simulate streaming by reading in each individual patient record chronologically
        for indx, row in self.df.iterrows():

            # Update dynamic tracker dict with new corresponding values based on current iteration of record
            self.update_tracker(indx, row)

            # Check if location of current record was already flagged
            if self.check_flag_is_one() == False:

                # If location was unflagged, check if it should be flagged based on current record
                if self.should_flag_be_one() == True:
                    # If location should be flagged, update tracker dict
                    self.set_flag()

            elif self.check_flag_is_one() == True:

                # If location was previously flagged, check if navigation should be attempted
                if self.do_we_navigate() == True:
                    print(f"{self.checkin_time} - {self.location.capitalize()} Clinic needs a technician")
                    self.potential_move += 1

                    # Check which clinics have available technicians
                    available = self.check_availability()
                    print("- Availability: ", [i[0].capitalize() for i in available])

                    # Determined which of the available clinics we should pull from (utilize ML model if needed)
                    pull_from = self.find_pull_from(available)

                    # If there is no location where its feasible to pull an available technician from, print notice
                    if pull_from == None:
                        self.stag += 1
                        print('No movement at this time; all clinics are busy.\n')
                        # track the count of how many times this occurs??

                    # If there is a location to pull from, pull tech from that location
                    elif pull_from != None:
                        self.pull_technician(pull_from)

                        # Reset flag after technician was pulled
                        self.reset_flag()

        return


def main():
    """Instantiates necessary objects and executes TecNav on new patient data."""

    # Read in necessary data files and pre-constructed model object
    past_patients_df = pd.read_pickle('./pickled_objects/past_patients_df.pkl')
    new_patients_df = pd.read_pickle('./pickled_objects/new_patients_df.pkl')
    clinics_df = pd.read_csv('./fabricated_data/uc_clinics.csv', index_col='branch_name')
    clinics_df['nearby_clinics'] = clinics_df.nearby_clinics.apply(lambda x: ast.literal_eval(x))
    model = pickle.load(open('./pickled_objects/rf_model.pkl', 'rb'))

    # Setup parser for customized execution based on CLI arguments
    parser = argparse.ArgumentParser(description='Specify preferences for TecNav execution.')
    parser.add_argument('data_src', metavar='<source>', type=str, choices=['past', 'new'], help='Choose to execute TecNav with streamed data from "past" or "new" patient records.')
    parser.add_argument('-d', '--date', dest='specified_date', metavar='<date>', type=str, help='Specify a date of interest to stream patient records (OPTIONAL).')
    parser.add_argument('-s', '--starting', dest='specified_starting_ct', metavar='<start>', type=int, help='Specify a modified starting number of assigned technicians (OPTIONAL).')
    parser.add_argument('-r', '--ratio', dest='specified_ratio', metavar='<ratio>', type=int, help='Specify a threshold ratio of number of patients per technician (OPTIONAL).')
    parser.add_argument('-c', '--code', dest='specified_code', metavar='<code>', type=float, help='Specify a threshold average code to trigger moves (OPTIONAL).')

    args = parser.parse_args()

    # Conduct modifications based on user-provided specifications
    if args.data_src == 'past':
        df = past_patients_df.copy()
    elif args.data_src == 'new':
        df = new_patients_df.copy()
    if args.specified_date:
        df = df[df.visit_date.astype(str) == args.specified_date]

    staff_ratio = args.specified_ratio
    code_ratio = args.specified_code
    start_ct_modification = args.specified_starting_ct
    if staff_ratio != None:
        aggregated_df = df.groupby(['visit_date', 'visit_location']).max()[['rolling_ct']].reset_index(drop=False)
        aggregated_df['assigned_num_techs'] = aggregated_df['rolling_ct'].apply(lambda x: int(x/staff_ratio)+1 if x%staff_ratio != 0 else int(x/staff_ratio))
        schedule_zipper = zip(aggregated_df.visit_date, aggregated_df.visit_location, aggregated_df.assigned_num_techs)
        schedule_dict = {}
        for i in schedule_zipper:
            schedule_dict[(i[0], i[1])] = i[2]
        df['assigned_num_techs'] = df[['visit_date', 'visit_location']] \
            .apply(lambda x: (x[0], x[1]), axis=1) \
            .map(schedule_dict)

    if start_ct_modification != None:
        df['new_num_techs'] = df['assigned_num_techs'] + start_ct_modification

    # Instantiate navigator application class & feed in the necessary data
    nav = TecNav(df, clinics_df, model, code_ratio)
    nav.execute_navigation()
    df['current_num_techs'] = nav.current_num_techs_col
    df.to_csv('./uc_log.csv')

    return


if __name__ == '__main__':
    main()