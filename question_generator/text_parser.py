"""
text_parser.py
"""
import os, sys
import nltk



in_file = '/Users/law826/Calibre Library/Stern, Eric J_/Chest Radiology_ The Essentials (14)/cr.txt'



with open(in_file, 'r') as f:
    raw = f.readlines()

    ch1_range = (264, 847)
    ch2_range = (848, 1711)
    ch3_range = (1712, 2373)
    ch4_range = (2374, 2733)
    ch5_range = (2734, 3381)
    ch6_range = (3382, 3945)
    ch7_range = (3946, 4459)
    ch8_range = (4460, 5261)
    ch9_range = (5262, 5923)
    ch10_range = (5924, 7167)
    ch11_range = (7168, 7529)
    ch12_range = (7530, 7807)
    ch13_range = (7808, 8951)
    ch14_range = (8952, 9143)
    ch15_range = (9144, 9711)
    ch16_range = (9712, 9939)
    ch17_range = (9940, 10333)
    ch18_range = (10334, 11229)
    ch19_range = (11230, 11463)
    ch20_range = (11464, 15215)

    ranges = [ch1_range, ch2_range, ch3_range, ch4_range, ch5_range, ch6_range, 
                ch7_range, ch8_range, ch9_range, ch10_range, ch11_range, ch12_range, 
                ch13_range, ch14_range, ch15_range, ch16_range, ch17_range, 
                ch18_range, ch19_range, ch20_range]


    for i, range in enumerate(ranges):
        ch_raw = raw[range[0]: range[1]]

        # Get rid of blank spaces.
        pp = [line for line in ch_raw if line != '\n']

        # Get rid of references at the end of the chapter. 
        ref_start_index = next(index for index, line in enumerate(pp) if line == 'References\n')
        pp1 = pp[:ref_start_index]

        # Get rid of figure captions.
        pp2 = [line for line in pp1 if line[0:7] != 'FIGURE ']

        # Get rid of lines that don't have periods at the end (takes care of beginnings of chapters.)
        pp3 = [line for line in pp2 if (line[-2:] == '.\n') or (line[-2:] == '!\n') or (line[-2:] == '?\n')]

        out_file = '/Users/law826/Dropbox/question_generator/ch%s.txt' %str(i+1)
        out_string = ''.join(pp3)

        # Print to file
        with open(out_file, 'w') as o:
            o.write(out_string)