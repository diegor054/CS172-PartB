import sys
import json

def fix_json_format(input_file):
    output_file = input_file.replace('.json', '_fixed.json')

    with open(input_file, 'r') as file:
        lines = file.readlines()

    fixed_json = '[' + ','.join(lines) + ']'

    with open(output_file, 'w') as file:
        file.write(fixed_json)

if len(sys.argv) < 2:
    print("Please provide the input file name as a command-line argument!")
    sys.exit(1)

input_file = sys.argv[1]

fix_json_format(input_file)