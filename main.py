import json
import re
import csv

HEADER_ROW = [
    "Testrun",
    "question_number",
    "question_json_ID",
    "question_part",
    "response_number",
    "response_json_ID",
    "response_part",
    "response_text",
    "response_locutions",
    "response_length",
    "response_loc_count",  # number of locutions in the response
    "response_dm_count",  # number of discourse markers
    "response_em_count",  # number of epistemic markers
    "response_assertion_count",  # number of assertions
    "response_question_count",  # number of questions
    "response_MA_count",
    "response_RA_count",
    "response_CA_count",
    "response_unconnected_count",  # unconnected propositions in the answer
    "response_DefaultIlloc_count",
    "response_rs_count"  # reported speech count
]

# Read CSV file
with open("FriPa_new.csv") as fp:
    reader = csv.reader(fp, delimiter=",", quotechar='"')
    csv_FriPa = [row for row in reader]
    # print(csv_FriPa)

with open("qt30.csv") as fp:
    reader = csv.reader(fp, delimiter=",", quotechar='"')
    csv_qt30 = [row for row in reader]


def find_indexes(lst, target, current_indexes=[]):
    indexes = []
    for index, item in enumerate(lst):
        if isinstance(item, list):
            # If the item is a sublist, recursively call the function
            sub_indexes = find_indexes(item, target, current_indexes + [index])
            indexes.extend(sub_indexes)
        elif item == target:
            # If the item is the target string, add the current index
            indexes.append(current_indexes[-1])

    return list(set(indexes))


def extract_node_ids(s):
    pattern = r'id=\\"node(\d+_\d+)\\"'
    matches = re.findall(pattern, s)
    return matches


with open('output.csv', 'a', encoding='utf-8') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(HEADER_ROW)
    # used to write the header once and only once

for i in csv_FriPa[1:]:  # first two rows are examples (15.08.2023)
    resp_json = i[11]
    if resp_json == "":  # if no Resp_json exist, we skip it - the stance is different
        continue
    date_fripa = "cutietestrun" + i[0].lower()
    question_number = i[1]
    answer_number = i[3]
    answer_speaker = i[8]
    response_json_ID = ""
    question_json_ID = ""
    response_text = i[9]
    response_length = len(response_text)
    answer_part = i[4]
    question_part = i[2]
    node_list = []
    # looking for corpus in qt30 map
    date_indexes_qt30 = find_indexes(csv_qt30, date_fripa)
    for d in date_indexes_qt30:
        # search for json_ids using parts for answers
        if csv_qt30[d][9] == answer_part or csv_qt30[d][9] == "part " + answer_part:
            if len(csv_qt30[d][11]) <= 6:  # there are texts instead of corpus numbers sometimes in the column
                json_corpus = csv_qt30[d][11]
                response_json_ID = json_corpus  # writing to outer scope
                try:
                    with open("jsons/" + json_corpus + ".json", encoding='utf-8-sig') as f:
                        json_data = json.load(f)
                except FileNotFoundError:
                    print("File " + json_corpus + " does not exist.")
                node_list = extract_node_ids(resp_json)  # extracted all nodes referring to text
        # same search, but now for the questions
        if csv_qt30[d][9] == question_part or csv_qt30[d][9] == "part " + question_part:
            if len(csv_qt30[d][11]) <= 6:  # there are texts instead of corpus numbers sometimes in the column
                json_corpus = csv_qt30[d][11]
                question_json_ID = json_corpus  # writing to outer scope
    with open('output.csv', 'a', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([
            date_fripa,
            question_number,
            question_json_ID,
            question_part,
            answer_number,
            response_json_ID,
            answer_part,
            response_text,
            node_list,
            response_length
        ])
