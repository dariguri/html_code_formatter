import analyze

class Formatter:

    def parse_params(self, file):
        params_file = open(file)
        params = dict()
        for propLine in params_file:
            propDef= propLine.strip()
            if len(propDef) == 0:
                continue
            if propDef[0] in ( '!', '#' ):
                continue
            punctuation = [ propDef.find(c) for c in ':= ' ] + [ len(propDef) ]
            found = min( [ pos for pos in punctuation if pos != -1 ] )
            name = propDef[:found].rstrip()
            value = propDef[found:].lstrip(":= ").rstrip()
            if value.isdigit():
                value = int(value)
            params[name] = value
        params_file.close()
        return params

    def __init__(self, params_file):
        self.prop_dict = self.parse_params(params_file)
    

    def format_file(self, input_file, output_file):
        
        tags, errors = analyze.analyze_code(input_file)
        result = self.format(tags)
        for t in tags:
            print(t)

        print(result)

        #TODO write result to output_file
        file = open (output_file,mode = 'w')
        file.write(result)

    def format(self, tags):
        self.identation = ' '
        result = ''
        for i in range(len(tags)):
            tag = tags[i]
            if tag.type == 'opening':
                result += self.get_indent(tag.attachment) + "<" + tag.name 
                
                i += 1
                while tags[i].type == 'attribute':
                    if tags[i].is_on_new_line:
                        result += '\n' + self.get_indent(tag.attachment)
                    result += " " + self.format_attribute(tags[i])
                    i += 1
                tag = tags[i]

                if tag.type == 'single':
                    result += "/"
                    i += 1    
                result += ">"
                tag = tags[i]

            if tag.type == 'closing':
                result += self.get_indent(tag.attachment) + "</" + tag.name + ">"
                
            if tag.type == 'content':
                result += tag.value

            
            
        return result

    def format_attribute(self, tag):
        return tag.name + "=" + '"' + tag.value + '"'

    def get_indent(self, attachment):
        return (self.prop_dict['indent'] * attachment) * self.identation


formatter = Formatter('formatter.properties')
formatter.format_file('test.html', 'output.html')