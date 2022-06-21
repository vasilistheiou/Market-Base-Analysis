# -*- coding: utf-8 -*-
"""
Created on Tue May  4 13:59:23 2021
@author: ΜΕΝΕΛΑΟΣ
"""
# import the libraries
import PySimpleGUI as sg
import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
from mlxtend.preprocessing import TransactionEncoder


# convert the output of the apriori,and association_rules to list

def convert2ListLift(output_column):
    output_list = []

    for i in range(len(output_column)):
        output_list.append(output_column[i])

    return output_list


def convert2List(output_column):
    output_list = []

    for i in range(len(output_column)):
        x, = output_column[i]
        output_list.append(x)

    return output_list


def convert2ListSupport(output_column):
    output_list = []

    for i in range(output_column.size):
        x, = output_column[i]
        output_list.append(x)

    return output_list


# create a user friendly output
def create_output(a_list, c_list, l_list):
    final_list = []
    i = 0

    # step is 2 to get rid of duplicates
    while i < len(a_list):
        final_list.append(
            a_list[i] + " -> " + c_list[i] + " with connection measurement at: " + str(round(l_list[i], 2)))
        i = i + 2

    return final_list


def Apriori(path):
    df = pd.read_csv(path, header=None)

    data = df.iloc[0]

    row = []

    dataset = []

    # create an array of strings where each row is a .csv row

    for i in range(df.shape[0]):

        data = df.iloc[i]

        for j in range(data.size):
            if str(data[j]) != 'nan':
                row.append(data[j])

        dataset.append(row)

        row = []

    # create an output with True if the item exists in the transaction and False if it doesnt

    te = TransactionEncoder()

    te_ary = te.fit(dataset).transform(dataset)

    df = pd.DataFrame(te_ary, columns=te.columns_)

    frequent_itemsets = apriori(df, min_support=0.02, use_colnames=True)

    # create an new column that contains the length of the relationship
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))

    # to get the most popular items set length to 1
    output = frequent_itemsets[(frequent_itemsets['length'] == 1) & (frequent_itemsets['support'] >= 0.02)]

    # sort the items from the most popular to the least popular
    output1 = output.sort_values(by="support", ascending=False)

    # convert to list to be easier to print in the GUI
    popular_items = convert2ListSupport(output1.itemsets.values)

    # find the relations with lift > 1
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

    # sort from the biggest lift to the smaller lift
    rules1 = rules.sort_values(by="lift", ascending=False)

    antecedents_list = convert2List(rules1.antecedents.values)

    consequents_list = convert2List(rules1.consequents.values)

    lift_list = convert2ListLift(rules1.lift.values)

    return antecedents_list, consequents_list, lift_list, popular_items


sg.theme("DarkTanBlue")

options = [[sg.Frame('Choose CSV file', [[
    sg.In(size=(25, 1), enable_events=True, key="-CSV-"),
    sg.FileBrowse(), ]], border_width=10)],
           [sg.Frame('Choose Action', [[sg.Checkbox('View popular items', key='Popular'),
                                        sg.Checkbox('View relationships between items', key='Relationship'),
                                        ]], title_location='ne')]]
choices = [[sg.Frame('Insert the data and pick the action', layout=options)]]

items_chosen = [[sg.Text('The results will popup in a new window')],
                [sg.Text('The results are in descending order')],
                [sg.Text('Pick at least one of the actions')], ]

# Create layout with two columns using precreated frames
layout = [[sg.Column(choices, element_justification='c'), sg.Column(items_chosen, element_justification='c')]]

# Define Window
window = sg.Window("Market Basket Analysis", layout)
# Read  values entered by user

while True:
    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "-CSV-":  # A file was chosen from the listbox
        if (values["-CSV-"] == ""):
            continue

        a_list, c_list, l_list, p_list = Apriori(values["-CSV-"])

        final_list = create_output(a_list, c_list, l_list)

        # use popups to print the final results
        if (values["Popular"] and values["Relationship"]):
            s = '\n\n '.join([str(i) for i in p_list])  # pass the string instead of an array.

            sg.PopupScrolled("Algorithm completed", f"The most popular items are: \n", f"{s}", non_blocking=True)

            s = '\n\n '.join([str(i) for i in final_list])  # pass the string instead of an array.

            sg.PopupScrolled("Algorithm completed", f"The following relationships found: \n", f"{s}",
                             non_blocking=False)

        elif (values["Relationship"]):
            s = '\n\n '.join([str(i) for i in final_list])  # pass the string instead of an array.

            sg.PopupScrolled("Algorithm completed", f"The following relationships found: \n", f"{s}",
                             non_blocking=False)

        elif (values["Popular"]):
            s = '\n\n '.join([str(i) for i in p_list])  # pass the string instead of an array.

            sg.PopupScrolled("Algorithm completed", f"The most popular items are: \n", f"{s}", non_blocking=False)
window.close()