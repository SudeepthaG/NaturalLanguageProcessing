### This program is a lemmatizer, which learns a lemmatization function from an annotated corpus. The function maps every word form
### attested in the training data to the most common lemma associated with that form. At test time, the program checks if a form is in
### the lookup table, and if so, it gives the associated lemma; if the form is not in the lookup table, it gives the form itself as the
### lemma (identity mapping).

### The program performs training and testing in one run: it reads the training data, learns the lookup table and keeps it in memory,
### then reads the test data, runs the testing, and reports the results.

### The program takes two command line arguments, which are the paths to the training and test files. Both files are assumed to be
### already tokenized, in Universal Dependencies format, that is: each token on a separate line, each line consisting of fields separated
### by tab characters, with word form in the second field, and lemma in the third field. Tab characters are assumed to occur only in
### lines corresponding to tokens; other lines are ignored.

import sys
import re

### Global variables

# Paths for data are read from command line
# train_file = sys.argv[1]
# test_file = sys.argv[2]

train_file = "UD_Hindi-HDTB-master/hi_hdtb-ud-train.conllu"
test_file = "UD_Hindi-HDTB-master/hi_hdtb-ud-test.conllu"

# Counters for lemmas in the training data: word form -> lemma -> count
lemma_count = {}

# Lookup table learned from the training data: word form -> lemma
lemma_max = {}

# Variables for reporting results
training_stats = ['Wordform types', 'Wordform tokens', 'Unambiguous types', 'Unambiguous tokens', 'Ambiguous types',
                  'Ambiguous tokens', 'Ambiguous most common tokens', 'Identity tokens']
training_counts = dict.fromkeys(training_stats, 0)

test_outcomes = ['Total test items', 'Found in lookup table', 'Lookup match', 'Lookup mismatch',
                 'Not found in lookup table', 'Identity match', 'Identity mismatch']
test_counts = dict.fromkeys(test_outcomes, 0)

accuracies = {}

### Training: read training data and populate lemma counters

train_data = open(train_file, 'r')

token_count=0
tokens={}
ambi=0
for line in train_data:

    # Tab character identifies lines containing tokens
    if re.search('\t', line):
        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')
        # print(field)
        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]
        # print(form+" "+lemma )
        token_count=token_count+1
        if form in tokens.keys() and form!='|':
            ambi=ambi+1

        tokens[lemma]=[form]

print("Wordform tokens: "+str(token_count))
print(len(tokens))
print(ambi)


#         ######################################################
#         ### Insert code for populating the lemma counts    ###
#         ######################################################

# building dictionary
ambi_types=0
lemma_count={}
train_data = open(train_file, 'r')
for line in train_data:

    # Tab character identifies lines containing tokens
    if re.search('\t', line):
        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')
        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]
        lemma_repeat=0                                         #updating number of times a lemma repeats for a word
        if form in lemma_count.keys():
            if lemma in lemma_count[form]:
                lemma_repeat=lemma_count[form][lemma]+1
                lemma_count[form][lemma]=lemma_repeat
            else:
                lemma_count[form][lemma]=1
                if len(lemma_count[form].keys())==2:     #form is ambigious if it has more than 2 lemmas
                    ambi_types = ambi_types + 1
        else:
            lemma_count[form]={lemma:1}

# print("lemma_count")
print("Wordform types: "+str(len(lemma_count)))
print("Ambiguous types: "+str(ambi_types))
print("Unambiguous types: "+str(len(lemma_count)-ambi_types))


# ######################################################
# ### Insert code for building the lookup table      ###
# ######################################################

# mapping to the most common lemma:
lemma_max={}
for form in lemma_count.keys():
    if len(lemma_count[form].keys()) >= 2:     #for ambiguos forms, choose most common lemma
        highest=0
        common_lemma=''
        for lemma in lemma_count[form]:
            if highest<lemma_count[form][lemma]:
                highest=lemma_count[form][lemma]
                common_lemma=lemma
        lemma_max[form]=common_lemma
    else:
        for lemma in lemma_count[form]:
            lemma_max[form]=lemma


print(len(lemma_max))
# print(lemma_max)

identity_tokens=0
for form in lemma_max.keys():
    if form==lemma_max[form]:
        identity_tokens=identity_tokens+1

print("Identity types: "+str(identity_tokens))

form=''
lemma=''
#
# ######################################################
# ### Insert code for populating the training counts ###
# ######################################################

### Calculate expected accuracy if we used lookup on all items ###
lookup_accuracy=0
train_data = open(train_file, 'r')
for line in train_data:

    # Tab character identifies lines containing tokens
    if re.search('\t', line):
        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')
        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]
        if lemma_max[form]==lemma:
            lookup_accuracy=lookup_accuracy+1

print("Expected lookup accuracy: "+str(lookup_accuracy/token_count))
#
accuracies['Expected lookup'] =  str(lookup_accuracy/token_count)

### Calculate expected accuracy if we used identity mapping on all items ###

identity_accuracy=0
train_data = open(train_file, 'r')
for line in train_data:
    # Tab character identifies lines containing tokens
    if re.search('\t', line):
        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')
        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]
        if form==lemma:
            identity_accuracy=identity_accuracy+1

print("Expected identity accuracy: "+str(identity_accuracy/token_count))

accuracies['Expected identity'] =  str(identity_accuracy/token_count)


### Testing: read test data, and compare lemmatizer output to actual lemma

test_data = open(test_file, 'r')
test_items_count=0
lookup_availability=0
lookup_match=0
lookup_mismatch=0
identity_match=0
identity_mismatch=0
identity_lemma_types=[]
for line in test_data:

    # Tab character identifies lines containing tokens
    if re.search('\t', line):
        # Tokens represented as tab-separated fields
        field = line.strip().split('\t')

        # Word form in second field, lemma in third field
        form = field[1]
        lemma = field[2]
        test_items_count=test_items_count+1
        if form in lemma_max:
            lookup_availability=lookup_availability+1
            if lemma_max[form]==lemma:
                lookup_match=lookup_match+1
        else:
            if lemma==form:
                identity_match = identity_match+1
            else:

                identity_mismatch=identity_mismatch+1


print(test_items_count)
print(lookup_availability)
print(lookup_match)
lookup_mismatch=lookup_availability-lookup_match
print(lookup_mismatch)
print(identity_match)
print(identity_mismatch)

# calculating accuracies
test_lookup_accuracy=lookup_match/lookup_availability
test_identity_accuracy=identity_match/(identity_match+identity_mismatch)
overall_accuracy=(lookup_match+identity_match)/test_items_count

print(test_lookup_accuracy)
print(test_identity_accuracy)
print(overall_accuracy)

        ######################################################
        ### Insert code for populating the test counts     ###
        ######################################################
#
accuracies['Lookup'] =  test_lookup_accuracy

accuracies['Identity'] = test_identity_accuracy
accuracies['Overall'] =  overall_accuracy

### Report training statistics and test results

output = open('lookup-output.txt', 'w')

output.write('Training statistics\n')

for stat in training_stats:
    output.write(stat + ': ' + str(training_counts[stat]) + '\n')

for model in ['Expected lookup', 'Expected identity']:
    output.write(model + ' accuracy: ' + str(accuracies[model]) + '\n')

output.write('Test results\n')

for outcome in test_outcomes:
    output.write(outcome + ': ' + str(test_counts[outcome]) + '\n')

for model in ['Lookup', 'Identity', 'Overall']:
    output.write(model + ' accuracy: ' + str(accuracies[model]) + '\n')

output.close
