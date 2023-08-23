import json
import re
import csv
# import gensim

QUESTION_TYPES = ['Pure Questioning', 'Rhetorical Questioning', 'Assertive Questioning']

discourse_markers = [
    'about',
    'accordingly',
    'additionaly',
    'after',
    'afterward',
    'afterwards',
    'albeit',
    'also',
    'alternatively',
    'although',
    'and',
    'as',
    'because',
    'before',
    'besides',
    'beyond',
    'both',
    'but',
    'by',
    'consequently',
    'conversely',
    'despite',
    'earlier',
    'else',
    'except',
    'finally',
    'for',
    'from',
    'further',
    'furthermore',
    'given',
    'hence',
    'however',
    'if',
    'in',  # I am not sure if that is considered a discourse marker. Double-check
    'indeed',
    'instead',
    'later',
    'lest',
    'like',
    'likewise',
    'meantime',
    'meanwhile',
    'moreover',
    'nevertheless',
    'next',
    'nonetheless',
    'nor',
    'on',  # not a discourse marker in phrasal verbs such as "get on"
    'once',
    'only',
    'or',
    'plus',
    'previously',
    'rather',
    'regardless',
    'separately',
    'similarly',
    'simultaneously',
    'since',
    'so',
    'specifically',
    'still',
    'subsequently',
    'then',
    'thereafter',
    'thereby',
    'though',
    'thus',
    'till',
    'ultimately',
    'unless',
    'until',
    'upon',
    'whatever',
    'when',
    'whenever',
    'where',
    'whereas',
    'whether',
    'while',
    'with',
    'without',
    'yet'
]

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


def get_statistics(text):
    # words = gensim.utils.simple_preprocess(str(text), deacc=True, min_len=1)
    # above is legacy code. Use when the text contains spans
    words = text.split()
    # Number of discourse indicators
    discourse_markers_count = 0
    epistemic_markers_count = []
    for word in words:
        if word in discourse_markers:
            discourse_markers_count += 1
    # Count epistemic expressions
    epistemic_markers_count.extend(re.findall(  # really know and that may mean - are those EM?
        r'(?:I|We|we|One|one)?(?:\s\w+)?(?:\s\w+)?\s(?:believes?|think|thinks|means?|worry|worries|know|guesse?s?|assumes?|wonders?|feels?)\b(?:that)?',
        text))
    epistemic_markers_count.extend(re.findall(
        r'(?:I|We|we|One|one)\s(?:don\'t|\sdoesn\'t\sdo\snot|\sdoes\snot)\s(?:believe|think|mean|worry|know|guess|assume|wonder|feel)\b(?:that)?',
        text))
    epistemic_markers_count.extend(
        re.findall(r'(?:It|it)\sis\s(?:believed|known|assumed|thought)\b(?:that)?', text))
    epistemic_markers_count.extend(
        re.findall(r'(?:I|We|we)\s(?:am|are|was|were)(?:\sjust)?\s(?:thinking|guessing|wondering)\b(?:that)?',
                   text))
    epistemic_markers_count.extend(
        re.findall(r'(?:I\'m|[Ww]e\'re)(?:\sjust)?\s(?:thinking|guessing|wondering)\b(?:that)?', text))
    epistemic_markers_count.extend(
        re.findall(r'(?:I|We|we|One|one)(?:\s\w+)?\s(?:do|does)\snot\s(?:believe?|think|know)\b(?:that)?',
                   text))
    epistemic_markers_count.extend(
        re.findall(r'(?:I|We|we|One|one)\swould(?:\s\w+)?(?:\snot)?\ssay\b(?:that)?', text))
    epistemic_markers_count.extend(
        re.findall(r'(?:I\sam|I\'m|We\sare|We\'re)(?:\s\w+)?\s(?:afraid|sure|confident)\b(?:that)?', text))
    epistemic_markers_count.extend(re.findall(
        r'(?:My|my|Our|our)\s(?:personal\s)?(?:experience|opinion|belief|view|knowledge|worry|worries|concerns?|guesse?s?|position|perception)(?:\son\s\w+)?\s(?:is|are)\b(?:that)?',
        text))
    epistemic_markers_count.extend(re.findall(r'[Ii]n\s(?:my|our)(?:\s\w+)?\s(?:view|opinion)\b', text))
    epistemic_markers_count.extend(re.findall(r'[Fr]rom\s(?:my|our)\s(?:point\sof\sview|perspective)\b', text))
    epistemic_markers_count.extend(re.findall(r'As\sfar\sas\s(?:I|We|we)\s(?:am|are)\sconcerned', text))
    epistemic_markers_count.extend(
        re.findall(r'(?:I|We|we|One|one)\s(?:can|could|may|might)(?:\s\w+)?\sconclude\b(?:that)?', text))
    epistemic_markers_count.extend(re.findall(r'I\s(?:am\swilling\sto|must)\ssay\b(?:that)?', text))
    epistemic_markers_count.extend(re.findall(r'"One\s(?:can|could|may|might)\ssay\b(?:that)?', text))
    epistemic_markers_count.extend(re.findall(r'[Oo]ne\s(?:can|could|may|might)\ssay\b(?:that)?', text))
    epistemic_markers_count.extend(re.findall(r'[Ii]t\sis\s(?:obvious|(?:un)?clear)\b', text))
    epistemic_markers_count.extend(re.findall(r'[Ii]t(?:\sjust)?\s(?:seems|feels|looks)', text))
    epistemic_markers_count.extend(re.findall(r'[Pp]ersonally\s(?:for\sme|speaking)', text))
    epistemic_markers_count.extend(re.findall(r'[Ff]rankly|[Hh]onestly|[Cc]learly', text))
    return discourse_markers_count, len(epistemic_markers_count)


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
    statistics = get_statistics(response_text)
    response_dm_count = statistics[0]
    response_em_count = statistics[1]
    response_length = len(response_text.split())  # count the ammount of words
    answer_part = i[4]
    question_part = i[2]
    node_list = []
    response_loc_count = 0
    response_assertion_count = 0
    response_question_count = 0
    response_MA_count = 0
    response_RA_count = 0
    response_CA_count = 0
    response_unconnected_count = 0
    response_DefaultIlloc_count = 0
    response_rs_count = 0
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
                response_loc_count = len(node_list)
                nodes_YA_from_locutions = []
                #  First, we collect all the edges that contain our locution nodes in their fromID
                for edge in json_data['AIF']['edges']:
                    fromID = edge["fromID"]
                    toID = edge["toID"]
                    if fromID in node_list:
                        nodes_YA_from_locutions.append(toID)
                #  Now, we find all nodes where our edges are going to, to check if it is Assertion
                for node in json_data["AIF"]["nodes"]:
                    if node["nodeID"] in nodes_YA_from_locutions and node["type"] != "YA":
                        nodes_YA_from_locutions.remove(node["nodeID"])
                    if node["text"] == "Asserting" and node["nodeID"] in nodes_YA_from_locutions:
                        response_assertion_count += 1
                    if node["text"] in QUESTION_TYPES and node["nodeID"] in nodes_YA_from_locutions:
                        response_question_count += 1
                #  creating a search for I-nodes to later find connected CA, MA and RA nodes
                nodes_I_from_YA = []
                for edge in json_data['AIF']['edges']:
                    fromID = edge["fromID"]
                    toID = edge["toID"]
                    if fromID in nodes_YA_from_locutions:
                        nodes_I_from_YA.append(toID)
                for node in json_data["AIF"]["nodes"]:
                    if node["nodeID"] in nodes_I_from_YA and node["type"] != "I":
                        nodes_I_from_YA.remove(node["nodeID"])
                        #  searching for reported speech assuming that L to L situations are unique
                        if node["type"] == "L":
                            response_rs_count += 1
                nodes_MA_from_I = []
                nodes_RA_from_I = []
                nodes_CA_from_I = []
                end_nodes = []
                unconnected_nodes = nodes_I_from_YA.copy()
                #  searching nodes and those with types RA, MA, CA are appended to an array
                for edge in json_data['AIF']['edges']:
                    fromID = edge["fromID"]
                    toID = edge["toID"]
                    if fromID in nodes_I_from_YA:
                        end_nodes.append(toID)
                        if fromID in unconnected_nodes:
                            unconnected_nodes.remove(fromID)
                unconnected_nodes_total = unconnected_nodes.copy()
                for node in unconnected_nodes_total:
                    counter_to = 0
                    for edge in json_data['AIF']['edges']:
                        if node == edge["toID"]:
                            counter_to += 1
                    if counter_to != 1:
                        unconnected_nodes.remove(node)
                response_unconnected_count = len(unconnected_nodes)
                for node in json_data["AIF"]["nodes"]:
                    if node["nodeID"] in end_nodes:
                        if node["type"] == "MA":
                            nodes_MA_from_I.append(node["nodeID"])
                        elif node["type"] == "RA":
                            nodes_RA_from_I.append(node["nodeID"])
                        elif node["type"] == "CA":
                            nodes_CA_from_I.append(node["nodeID"])
                response_MA_count = len(nodes_MA_from_I)
                response_RA_count = len(nodes_RA_from_I)
                response_CA_count = len(nodes_CA_from_I)
                #  search for all incoming edges in I-nodes to filter for Default Illocutings
                nodes_to_MA = []
                default_illocutings_nodes = []
                for edge in json_data['AIF']['edges']:
                    fromID = edge["fromID"]
                    toID = edge["toID"]
                    if toID in nodes_MA_from_I:
                        nodes_to_MA.append(fromID)
                for node in json_data["AIF"]["nodes"]:
                    if node["nodeID"] in nodes_to_MA and node["text"] == "Default Illocuting":
                        default_illocutings_nodes.append(node)
                response_DefaultIlloc_count = len(default_illocutings_nodes)
        # same search for json ID in qt30 file, but now for the questions
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
            response_length,
            response_loc_count,
            response_dm_count,
            response_em_count,
            response_assertion_count,
            response_question_count,
            response_MA_count,
            response_RA_count,
            response_CA_count,
            response_unconnected_count,
            response_DefaultIlloc_count,
            response_rs_count
        ])
