from formatter import Formatter
from analyze import analyze_code
import argparse
import os

parser = argparse.ArgumentParser(description='Fromatter for HTML files')
parser.add_argument('infile',
                   help='path to input file')
parser.add_argument('-p', '--params', default='formatter.properties',
                   help='template params for formatter (default = "formatter.properties")')
parser.add_argument('-o', '--outfile', default='output.html',
                   help='path to output file (default = "output.html")')
parser.add_argument('-e', '--errfile', default='error.txt',
                   help='path to output file (default = "error.txt")')
args = vars(parser.parse_args())

def format_file(input_file, output_file, param_file, error_file):
    
        f = Formatter(param_file)
        tags, errors = analyze_code(input_file)       
        result = f.format(tags)

        directory = os.path.dirname(output_file)
        if directory != '' and not os.path.exists(directory):
            os.makedirs(directory)
        file = open (output_file,mode = 'w')
        file.write(result)
        file.close()


        directory = os.path.dirname(error_file)
        if directory != '' and not os.path.exists(directory):
            os.makedirs(directory)
        file = open (error_file, mode = 'w')
        for e in errors:
            file.write(str(e) + "\n")
        file.close()

        print('HTML file succesfuly formatted and written to', output_file, '\nErrors in:',error_file)
        

format_file(args['infile'],args['outfile'],args['params'],args['errfile'])
