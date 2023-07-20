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
    "response_length"
]

# Read CSV file
with open("FriPa.csv") as fp:
    reader = csv.reader(fp, delimiter=",", quotechar='"')
    csv_FriPa = [row for row in reader]
    # print(csv_FriPa)

with open("qt30.csv") as fp:
    reader = csv.reader(fp, delimiter=",", quotechar='"')
    csv_qt30 = [row for row in reader]
    # print(csv_qt30)


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
    pattern = r'id="node(\d+_\d+)"'
    matches = re.findall(pattern, s)
    return matches


for i in csv_FriPa[2:]:
    date_fripa = "cutietestrun" + i[0].lower()
    question_number = i[1]
    answer_number = i[4]
    answer_speaker = i[5]
    response_json_ID = ""
    response_text = i[6]
    response_length = len(response_text)
    true_nodes = []  # list for filtered L nodes (locutions)
    if i[8] == "":
        continue
    answer_part = i[8].replace(" ", "").split(",")  # this is response_part
    # looking for corpus in qt30 map
    date_indexes_qt30 = find_indexes(csv_qt30, date_fripa)
    for d in date_indexes_qt30:
        for a in answer_part:
            if csv_qt30[d][9] == a or csv_qt30[d][9] == "part " + a:
                if len(csv_qt30[d][11]) <= 6:  # there are texts instead of corpus numbers sometimes in the column
                    json_corpus = csv_qt30[d][11]
                    response_json_ID = json_corpus
                    try:
                        with open("jsons/" + json_corpus + ".json", encoding='utf-8-sig') as f:
                            json_data = json.load(f)
                            # print("OPENED " + json_corpus)
                    except FileNotFoundError:
                        print("File " + json_corpus + " does not exist.")
                    json_corpus_text = json_data["text"]  # extracted the whole text from json file
                    nodelist = extract_node_ids(json_corpus_text)  # extracted all nodes referring to text
                    for n in nodelist:
                        for j in json_data["AIF"]["nodes"]:
                            if j["nodeID"] == n and answer_speaker in j["text"]:
                                true_nodes.append(n)
    with open('output.csv', 'a', encoding='utf-8') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(HEADER_ROW)
        csv_writer.writerow([
            date_fripa,
            question_number,  # this is question type
            "SKIP",  # question json ID
            "SKIP",  # question part
            answer_number,
            response_json_ID,
            answer_part,
            response_text,
            true_nodes,
            response_length
        ])

        # the loop searches for answer_part in every row even after finding all. The code can be improved
