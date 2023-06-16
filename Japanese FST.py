import prettytable
import pynini

from prettytable import PrettyTable
from pynini import *


def A(s: str) -> Fst:
    return acceptor(s, token_type="utf8")


def T(upper: str, lower: str) -> Fst:
    return cross(A(upper), A(lower))


a = A("a")
zero = a - a
zero.optimize()


def newclass(letters: str):
    temp = zero
    for x in letters: temp = A(x) | temp
    return temp.optimize()


vowel = newclass("aiueoɯ̥i̥̥")
consonant = newclass("pbtdkgmnɲŋNszɸɕʑçhʦʣʨʥjwrɾ")
voiceless = newclass("ptksɸɕçhʦʨ")
stop = ("pbtdkg")

sigmaStar = (closure(vowel | consonant)).optimize()

###VOCABULARY###

# 20 RU-Verbs
testRUVerbs = ['tabeɾɯ', 'miɾɯ', 'neɾɯ', 'oɕieɾɯ', 'kiɾɯ', 'kotaeɾɯ', 'dekiɾɯ', 'okiɾɯ', 'kaNgaeɾɯ', 'ɕiNʥiɾɯ', 'deɾɯ',
               'kakeɾɯ', 'sɯteɾɯ', 'ɕiɾabeɾɯ', 'iɾɯ', 'kimeɾɯ', 'nigeɾɯ', 'jaseɾɯ', 'maʨigaeɾɯ', 'kataʥɯkeɾɯ']

# 20 U-Verbs
testUVerbs = ['kakɯ', 'ojogɯ', 'hanasɯ', 'maʦɯ', 'ɕinɯ', 'tobɯ', 'jomɯ', 'kiɾɯ', 'kaɯ', 'asobɯ', 'nomɯ', 'aɾɯ', 'noɾɯ',
              'kaeɾɯ', 'ɯtaɯ', 'kakaɾɯ', 'aɾɯkɯ', 'ʦɯkɯɾɯ', 'wakaɾɯ', 'owaɾɯ']

irregularVerbs = ['sɯɾɯ', 'kɯɾɯ']

sampleNouns = ['iNkɯ', 'teNpɯra', 'aNdi']

###USER INPUTS###
#Checks lists of words to find the word class
#word class is used to select correct suffixes
wordClass = ""
wordLoop = True
while wordLoop == True:
    print("Enter Word in IPA or type 'list' to see all available words:")
    userWord = input()
    #retrieves word list
    if userWord == "list" or userWord == "List":
        print("Printing list of all vocabulary...")
        wordLoop = False
    #RU Verb Class
    elif userWord in testRUVerbs:
        print("RU-Verb Selected")
        wordClass = "RU"
        wordLoop = False
    #U Verb Class
    elif userWord in testUVerbs:
        print("U-Verb Selected")
        wordClass = "U"
        wordLoop = False
    #Irregular Verb Class
    elif userWord in irregularVerbs:
        print("Irregular-Verb Selected")
        wordClass = "Irregular"
        wordLoop = False
    #Noun Verb Class
    elif userWord in sampleNouns:
        print("Noun Selected")
        wordClass = "Noun"
        wordLoop = False
    else:
        print("Word not found")

#Gathers information on the wanted tense/polarity of word if it's not a noun or list
mainLoop = True
tenseLoop = True
polarLoop = True
classes = ["RU", "U", "Irregular"]
#'Noun' and 'list' skip this section
while mainLoop == True and userWord in classes:
    #User choosing Present or Past Tense
    print("Choose Tense:\n1) Present\n2) Past")
    while tenseLoop == True:
        tenseInput = input()
        if tenseInput == "1":
            tenseInput = "Present"
            tenseLoop = False
        elif tenseInput == "2":
            tenseInput = "Past"
            tenseLoop = False
    #User choosing Affirmative or Negative form
    print("Choose Polarity:\n1) Affirmative\n2) Negative")
    while polarLoop == True:
        polarInput = input()
        if polarInput == "1":
            polarInput = "Affirmative"
            polarLoop = False
        elif polarInput == "2":
            polarInput = "Negative"
            polarLoop = False
    mainLoop = False

# Pair each nasal to its change depending on what stop is after.
coronalStop = A('t') | A('d')
coronoalAssimilation = cdrewrite(T('N', 'n'), '', coronalStop, sigmaStar)
velarStop = A('k') | A('g')
velarAssimilation = cdrewrite(T('N', 'ŋ'), '', velarStop, sigmaStar)
labialStop = A('p') | A('b')
labialAssimilation = cdrewrite(T('N', 'm'), '', labialStop, sigmaStar)
nasalAssimilation = (coronoalAssimilation @ velarAssimilation @ labialAssimilation)

devoicePairs = (T("i", "i̥̥") | T("ɯ", "ɯ̥")).optimize()
shiEnding = (T("s", "ɕ")).optimize()
tsuEnding = (T("ʦ", "ʨ")).optimize()

# devoice at end of word when preceded by voiceless / devoice between two voiceless consonants
devoicing = (cdrewrite(devoicePairs, voiceless, "[EOS]", sigmaStar)
             @ cdrewrite(devoicePairs, voiceless, voiceless, sigmaStar))

# these fix U-verb endings after suffixation
shiFix = (cdrewrite(shiEnding, "", "i", sigmaStar))
tsuFix = (cdrewrite(tsuEnding, "", "i", sigmaStar))
endingFixes = (shiFix @ tsuFix).optimize()

### RU/U Suffixation to stem ###
RUVerbBase = (sigmaStar + T("", "mas")).optimize()
UVerbBase = (sigmaStar + T("", "imas")).optimize()

### Japanese Suffixation ###
PresentVerb = (sigmaStar + T("", "ɯ")).optimize()
NegativeVerb = (sigmaStar + T("", "en")).optimize()
PastVerb = (sigmaStar + T("", "ita")).optimize()
PastNegativeVerb = (sigmaStar + T("", "deɕita")).optimize()

#Suffix endings of RU Verbs based on tense and polarity.
if wordClass == "RU":
    #STEM + PRES || ex: taberu > tabe > tabe-mas-u
    if tenseInput == "Present" and polarInput == "Affirmative":
        RUSuffixation = (RUVerbBase @ PresentVerb).optimize()
    #STEM + NEG || ex: taberu > tabe > tabe-mas-en
    elif tenseInput == "Present" and polarInput == "Negative":
        RUSuffixation = (RUVerbBase @ NegativeVerb)
    #STEM + PAST || ex: taberu > tabe > tabe-mas-ita
    elif tenseInput == "Past" and polarInput == "Affirmative":
        RUSuffixation = (RUVerbBase @ PastVerb).optimize()
    #STEM + NEG + PASTNEG? || ex: taberu > tabe > tabe-mas-en-deshita
    else:
        RUSuffixation = (RUVerbBase @ NegativeVerb @ PastNegativeVerb).optimize()

    #Gives conjugated form of RU Verb
    def conjugateRUVerbs(stem: str):
        #removes 'ru' ending from verbs >> suffixing > phonological rules
        x = (A(stem[:-2]) @ RUSuffixation @ devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")
    print(conjugateRUVerbs(userWord))

#Suffix endings of U and Irregular Verbs based on tense and polarity.
if wordClass == "U" or wordClass == "Irregular":
    #STEM + PRES || ex: kaku > kak > kak-imas > kak-imas-u
    if tenseInput == "Present" and polarInput == "Affirmative":
        USuffixation = (UVerbBase @ PresentVerb).optimize()
    #STEM + PRES + NEG || ex: kaku > kak > kak-imas > kak-imas-en
    elif tenseInput == "Present" and polarInput == "Negative":
        USuffixation = (UVerbBase @ NegativeVerb).optimize()
    #STEM + PAST || ex: kaku > kak > kak-imas > kak-imas-ita
    elif tenseInput == "Past" and polarInput == "Affirmative":
        USuffixation = (UVerbBase @ PastVerb).optimize()
    #STEM + NEG + PAST-NEG? || ex: kaku > kak > kak-imas > kak-imas-en > kak-imas-en-deshita
    else:
        USuffixation = (UVerbBase @ NegativeVerb @ PastNegativeVerb).optimize()

    if wordClass == "U":
        #Gives conjugated form of U Verb
        def conjugateUVerbs(stem: str):
            # Removes 'U' ending from verbs > suffixing > phonological rules
            x = (A(stem[:-1]) @ USuffixation @ devoicing @ endingFixes @ nasalAssimilation).optimize()
            y = x.project("output")
            return y.string(token_type="utf8")
        print(conjugateUVerbs(userWord))

    else:
        #Gives conjugated form of Irregular verbs
        def conjugateIrregularVerbs(stem: str):
            x = (A(stem[:-3]) @ USuffixation @ devoicing @ endingFixes @ nasalAssimilation).optimize()
            y = x.project("output")
            return y.string(token_type="utf8")
        print(conjugateIrregularVerbs(userWord))

if wordClass == "Noun":
    #Nouns with phonological changes
    def applyNasalAssimilation(underlyingForm: str):
        x = (A(underlyingForm) @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")

    print(applyNasalAssimilation(userWord))

#Gives an ultimate list of all words available in program
#You can use this to check each specific conjugation/test new phono rules/different suffixations
if userWord == "list":
    print("RU-Verb List:\n", testRUVerbs)
    print("\nU-Verb List:\n", testUVerbs)
    print("\nIrregular Verb List:\n", irregularVerbs)
    print("\nNoun List:\n", sampleNouns, "\n")

    ###RU-VERB CHARTS###
    ###PRESENT RU-VERBS###
    def makeRUPresent(stem: str):
        # First removes 'ru' ending from verbs >> ORDER OF PHONO RULES (im not sure where nasal would be)
        x = (A(stem[:-2]) @ RUVerbBase @ PresentVerb @ devoicing @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table1 = PrettyTable()
    table1.field_names = ["Input", "Output"]

    for x in testRUVerbs:
        y = makeRUPresent(x)
        table1.add_row([x, y])

    print("************************************\n"
          "********RU-Verb Present Table*******\n"
          "************************************")
    print(table1)
    print("\n")


    ###PRESENT RU-VERBS NEGATIVE###
    def makeRUPresentNegative(stem: str):
        x = (A(stem[:-2]) @ RUVerbBase @ NegativeVerb @ devoicing @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table2 = PrettyTable()
    table2.field_names = ["Input", "Output"]

    for x in testRUVerbs:
        y = makeRUPresentNegative(x)
        table2.add_row([x, y])

    print("************************************\n"
          "***RU-Verb Present Negative Table***\n"
          "************************************")
    print(table2)
    print("\n")


    ###RU PAST TENSE###
    def makeRUPast(stem: str):
        x = (A(stem[:-2]) @ RUVerbBase @ PastVerb @ devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table3 = PrettyTable()
    table3.field_names = ["Input", "Output"]

    for x in testRUVerbs:
        y = makeRUPast(x)
        table3.add_row([x, y])

    print("************************************\n"
          "*********RU-Verb Past Table*********\n"
          "************************************")
    print(table3)
    print("\n")


    ###RU PAST TENSE NEGATIVE###
    def makeRUPastNegative(stem: str):
        x = (A(stem[:-2]) @ RUVerbBase @ PastNegativeVerb @ devoicing @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table4 = PrettyTable()
    table4.field_names = ["Input", "Output"]

    for x in testRUVerbs:
        y = makeRUPastNegative(x)
        table4.add_row([x, y])

    print("************************************\n"
          "****RU-Verb Past Negative Table*****\n"
          "************************************")
    print(table4)
    print("\n")

    ###U-Verb Charts###
    ###Present U-Verbs###
    def makeUPresent(stem: str):
        # Removes 'U' ending from verbs > phono rules > fix U-verb endings
        x = (A(stem[:-1]) @ UVerbBase @ PresentVerb @ devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table5 = PrettyTable()
    table5.field_names = ["Input", "Output"]

    for x in testUVerbs:
        y = makeUPresent(x)
        table5.add_row([x, y])

    print("************************************\n"
          "*********U-Verb Present Table*******\n"
          "************************************")
    print(table5)
    print("\n")


    ###Present Negative U-Verbs###
    def makeUPresentNegative(stem: str):
        x = (A(stem[:-1]) @ UVerbBase @ NegativeVerb @ devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table6 = PrettyTable()
    table6.field_names = ["Input", "Output"]

    for x in testUVerbs:
        y = makeUPresentNegative(x)
        table6.add_row([x, y])

    print("************************************\n"
          "***U-Verb Present Negative Table****\n"
          "************************************")
    print(table6)
    print("\n")


    ###Past U-Verbs###
    def makeUPast(stem: str):
        x = (A(stem[:-1]) @ UVerbBase @ PastVerb @ devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table7 = PrettyTable()
    table7.field_names = ["Input", "Output"]

    for x in testUVerbs:
        y = makeUPast(x)
        table7.add_row([x, y])

    print("************************************\n"
          "*********U-Verb Past Table**********\n"
          "************************************")
    print(table7)
    print("\n")


    ###Past Negative U-Verbs###
    def makeUPastNegative(stem: str):
        x = (A(stem[:-1]) @ UVerbBase @ PastNegativeVerb @ devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table8 = PrettyTable()
    table8.field_names = ["Input", "Output"]

    for x in testUVerbs:
        y = makeUPastNegative(x)
        table8.add_row([x, y])

    print("************************************\n"
          "*****U-Verb Past Negative Table*****\n"
          "************************************")
    print(table8)
    print("\n")


    ################################################################################################################################################################################

    ###Irregular Verb Charts###
    ###Present Irregular###
    def makeIrregularPresent(stem: str):
        x = (A(stem[:-3]) @ UVerbBase @ PresentVerb @ devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table9 = PrettyTable()
    table9.field_names = ["Input", "Output"]

    for x in irregularVerbs:
        y = makeIrregularPresent(x)
        table9.add_row([x, y])

    print("************************************\n"
          "*****Irregular Present Tense********\n"
          "************************************")
    print(table9)
    print("\n")


    ###Present Negative Irregular###
    def makeIrregularPresentNegative(stem: str):
        x = (A(stem[:-3]) @ UVerbBase @ NegativeVerb @ devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table10 = PrettyTable()
    table10.field_names = ["Input", "Output"]

    for x in irregularVerbs:
        y = makeIrregularPresentNegative(x)
        table10.add_row([x, y])

    print("************************************\n"
          "**Irregular Present Negative Tense**\n"
          "************************************")
    print(table10)
    print("\n")


    ###Past Irregular###
    def makeIrregularPast(stem: str):
        x = (A(stem[:-3]) @ UVerbBase @ PastVerb @devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table11 = PrettyTable()
    table11.field_names = ["Input", "Output"]

    for x in irregularVerbs:
        y = makeIrregularPast(x)
        table11.add_row([x, y])

    print("************************************\n"
          "*******Irregular Past Tense*********\n"
          "************************************")
    print(table11)
    print("\n")


    ###Past Negative Irregular###
    def makeIrregularPastNegative(stem: str):
        x = (A(stem[:-3]) @ UVerbBase @ PastNegativeVerb @ devoicing @ endingFixes @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    def applyNasalAssimilation(underlyingForm: str):
        x = (A(underlyingForm) @ nasalAssimilation).optimize()
        y = x.project("output")
        return y.string(token_type="utf8")


    table12 = PrettyTable()
    table12.field_names = ["Input", "Output"]

    for x in irregularVerbs:
        y = makeIrregularPastNegative(x)
        table12.add_row([x, y])

    print("************************************\n"
          "***Irregular Past Tense Negative****\n"
          "************************************")
    print(table12)
    print("\n")

    table13 = PrettyTable()
    table13.field_names = ["Input", "Output"]

    for x in sampleNouns:
        y = applyNasalAssimilation(x)
        table13.add_row([x, y])

    print("************************************\n"
          "***Nasal Place Assimilation Test****\n"
          "************************************")
    print(table13)
    print("\n")

# idea: take user input > ipa > match word > output w/e