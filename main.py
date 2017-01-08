import random

V_SYL = None
VC_SYL = None
CV_SYL = None
CVC_SYL = None
LETTER_PAIRS = None

V_WEIGHT = 0.75
VC_WEIGHT = 0.25
CV_WEIGHT = 0.55
CVC_WEIGHT = 0.45

# Weight order: CV, CVC, V, VC
FIRST_SYL_WEIGHTS = [0.5, 0.37, 0.09, 0.03]

SPECIAL_CHARS = ['sh', 'ai', 'ay', 'th']
VOWELS = ['a', 'e', 'i', 'o', 'u']

OUTPUT_FILE = "gen_words.txt"


def main():
    global V_SYL
    global VC_SYL
    global CV_SYL
    global CVC_SYL
    global LETTER_PAIRS

    V_SYL = load_syl_file('v.txt')
    VC_SYL = load_syl_file('vc.txt')
    CV_SYL = load_syl_file('cv.txt')
    CVC_SYL = load_syl_file('cvc.txt')
    LETTER_PAIRS = load_legal_pairs('legal_pairs.txt')

    num_words = 20
    max_syl = 5

    out_file = open(OUTPUT_FILE, 'w')
    for num_syl in range(1, max_syl + 1):
        for i in range(num_words):
            out_file.write(get_word(num_syl) + '\n')
    out_file.close()


def load_syl_file(path: str) -> dict:
    """Loads a Syllable file expecting one syllable per line"""
    file = open(path, 'r')
    first_letter_to_syl = dict()
    for line in file:
        if line.strip() and len(line) > 0:
            first_letter = line[0]
            # Check if the first letter is really a special character
            if len(line) >= 2:
                if line[:2] in SPECIAL_CHARS:
                    first_letter = line[:2]
            # Construct the map of "letter" -> list of syllables
            if first_letter not in first_letter_to_syl:
                first_letter_to_syl[first_letter] = []
            first_letter_to_syl[first_letter].append(line.strip())
    file.close()

    return first_letter_to_syl


def load_legal_pairs(path: str) -> dict:
    """Loads legal letter pairings, comma separated lines where letter is followed by legal pairings"""
    file = open(path, 'r')

    letter_to_legal_letters = dict()
    for line in file:
        # Split the comma separated values
        split_line = line.split(',')
        # First value is the letter to match
        first_letter = split_line[0]
        letter_to_legal_letters[first_letter] = []
        # Following letters are the legal pairings
        for letter in split_line[1:]:
            letter_to_legal_letters[first_letter].append(letter.strip())
    file.close()

    return letter_to_legal_letters


def get_syl(previous_letter: str = None) -> str:
    """Chooses the next syllable from weighted distributions based on the previous letter if provided"""
    chosen_syl = None
    while chosen_syl is None:
        if previous_letter is not None:
            # Check if there is a valid list of letter pairings possible, break if not
            if previous_letter not in LETTER_PAIRS:
                raise ValueError('No letter pairing is possible!')

            # Choose a random valid letter pairing based on previous letter
            next_letter = random.choice(LETTER_PAIRS[previous_letter])
            if next_letter in VOWELS:
                # Weighted choice between V and VC list
                syl_group = random.choices([V_SYL, VC_SYL], [V_WEIGHT, VC_WEIGHT])[0]
            else:
                # Weighted choice between CV and CVC list
                syl_group = random.choices([CV_SYL, CVC_SYL], [CV_WEIGHT, CVC_WEIGHT])[0]

            # If the next letter is not in our syllable group, try again with a different group
            if next_letter not in syl_group:
                continue
            # Choose a random syllable from the group we've chosen
            chosen_syl = random.choice(syl_group[next_letter])
        else:
            # Weighted choice of all Syllable groups because no previous letter
            syl_group = random.choices([CV_SYL, CVC_SYL, V_SYL, VC_SYL], FIRST_SYL_WEIGHTS)[0]
            chosen_syl = random.choice(syl_group[random.choice(list(syl_group.keys()))])

    return chosen_syl


def get_word(num_syl: int) -> str:
    """Attempts to build a word with the number of given syllables"""

    # No previous letter, grab the first syllable randomly
    word = get_syl()

    for i in range(1, num_syl):
        # Previous letter might be a special character
        if word[-2:] in SPECIAL_CHARS:
            previous_letter = word[-2:]
        else:
            previous_letter = word[-1]
        try:
            word += get_syl(previous_letter)
        except ValueError:
            # The previous letter had no valid pairings, just return what we had
            return word

    return word


if __name__ == '__main__':
    main()
