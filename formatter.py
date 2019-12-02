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
        
        for t in tags:
            print(t)

        result = self.format(tags)
        

        print(result)

        #TODO write result to output_file
        file = open (output_file,mode = 'w')
        file.write(result)

    def format(self, tags):
        self.identation = ' '
        result = ''
        i = 0
        while i < len(tags):
            tag = tags[i]

            if tag.is_on_new_line:
                result += "\n" + self.get_indent(tag.attachment)

            if tag.type == 'opening':
                result +=  "<" + tag.name         
                i += 1
                while tags[i].type == 'attribute':
                    result += self.get_continuation_indent() + self.format_attribute(tags[i])
                    i += 1
                if tags[i].type == 'single':
                    result += "/" 
                else:
                    i -= 1 

                result += ">"
                tag = tags[i]

            if tag.type == 'closing':
                result += "</" + tag.name + ">"

            if tag.type == 'content':
                result += tag.value
            i += 1  
        
        result = result.expandtabs(self.prop_dict['tab_size'])

        return result

    def format_attribute(self, tag):
        return tag.name + "=" + '"' + tag.value + '"'

    def get_indent(self, attachment):
        return (self.prop_dict['indent'] * attachment) * self.identation

    def get_continuation_indent(self):
        if self.prop_dict['use_tab'] == 'True':
            tab_count = int(self.prop_dict['continuation_indent'] / self.prop_dict['tab_size'])
            space_count = self.prop_dict['continuation_indent'] - tab_count * self.prop_dict['tab_size']
            return "\t" * tab_count + ' '* space_count
        else:
            return self.prop_dict['continuation_indent'] * self.identation

formatter = Formatter('formatter.properties')
formatter.format_file('test.html', 'output.html')