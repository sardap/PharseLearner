#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import argparse
import json
from random import shuffle
from difflib import SequenceMatcher
import random
import queue as Q
from operator import attrgetter
from datetime import datetime, timedelta
from dateutil import parser
import editdistance

_args = None

def update_phrases(phrases):
    with open(_args.filename, 'w', encoding='utf-8') as outfile:
        json.dump(phrases, outfile, indent=4, ensure_ascii=False)

def phrase_relearn(phrase):
	return parser.parse(phrase["log"][-1]["date"]) < datetime.today() - timedelta(days=10)

def get_new_phrases(phrases):
	new_phrases = []

	for phrase in phrases:
		if(
			(len(phrase["log"]) == 0) or phrase_relearn(phrase)):
			new_phrases.append(phrase)

	return new_phrases

def cull_phrase_list(phrases, old_phrases_n, new_phrases_n):
	active_phrases = []

	new_phrases = get_new_phrases(phrases)

	old_phrases = phrases.copy()

	for phrase in new_phrases:
		old_phrases.remove(phrase)

	shuffle(new_phrases)

	while len(active_phrases) < new_phrases_n and len(new_phrases) > 0:
		active_phrases.append(phrases.index(new_phrases.pop()))
	
	shuffle(old_phrases)

	while len(active_phrases) - old_phrases_n + new_phrases_n and len(old_phrases) > 0:
		active_phrases.append(phrases.index(old_phrases.pop())) 

	return active_phrases

def ask_question(phrase):
	print(phrase["phrase"])
	user_answer = input("Enter Answer:")

	lower_answers = [x.lower() for x in phrase["answers"]]

	edit_distance = editdistance.eval(min(lower_answers, key=lambda x:editdistance.eval(x, user_answer)), user_answer)

	result = edit_distance < 5

	phrase["log"].append({"provided answer" : user_answer, "date" : str(datetime.now()), "edit Distance" : edit_distance, "correct" : result})

	return result

def game_loop(phrases, active_phrases):
	completed_word_count = 0

	while completed_word_count < len(active_phrases):
		if(ask_question(phrases[active_phrases[0]])):
			completed_word_count += 1
			active_phrases.pop(0)
		else:
			shuffle(active_phrases)

		update_phrases(phrases)


def main():
	global _args

	parser = argparse.ArgumentParser()
	parser.add_argument('filename')
	parser.add_argument("-o", "--number_of_old_phrases", 
		type=int, default=10, 
		help="The number of old phrarses")
	parser.add_argument("-n", "--number_of_new_phrases", 
		type=int, default=1,
		help="The number of new phrarses")
	_args = parser.parse_args()

	with open(_args.filename, encoding='utf-8') as fh:
		phrases = json.load(fh)

	active_phrases = cull_phrase_list(phrases, _args.number_of_old_phrases, _args.number_of_new_phrases)

	shuffle(active_phrases)

	game_loop(phrases, active_phrases)

main()