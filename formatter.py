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
            if value == "False":
                value = False
            elif value == "True":
                value = True

            params[name] = value
        params_file.close()

        if not 'indent' in params or not 'use_tab' in params:
            raise Exception('Wrong params file')
        return params

    def __init__(self, params_file):
        self.prop_dict = self.parse_params(params_file)
        
    

    def format(self, tags):


        self.identation = ' '
        result = ''
        i = 0
        while i < len(tags):
            
            tag = tags[i]
            if tag.is_on_new_line:
                result += "\n" + self.get_indent(tag.attachment)
            if tag.type == 'doctype':
                result += "<!DOCTYPE html>\n"
            if tag.type == 'comment':
                result += "<!--" + tag.value + "-->"
            if tag.type == 'opening':
                result +=  "<" + self.format_space_in_tag() + tag.name         
                i += 1
                while tags[i].type == 'attribute':
                    if self.prop_dict['keep_line_breaks'] and tags[i].is_on_new_line:
                        result += "\n" + self.get_indent(tag.attachment) + self.format_attribute(tags[i])
                    else:
                        result += self.get_continuation_indent() + self.format_attribute(tags[i])
                    i += 1
                if tags[i].type == 'single':
                    result +=   self.format_space_in_tag() + "/" 
                else:
                    i -= 1 

                result +=  ">"
                tag = tags[i]

            if tag.type == 'closing':
                result += "</" + tag.name + self.format_space_in_tag() +">"

            if tag.type == 'content':
                result += self.format_content(tag.value)
            i += 1  
        
        result = result.expandtabs(self.prop_dict['tab_size'])

        return result

    def format_content(self,content):
        lines = content.splitlines()
        step1_result = ''
        for line in lines:
            is_has_data = False
            for ch in line:
                if ch != ' ' and ch != '\t':
                    is_has_data = True
            if not is_has_data and not self.prop_dict['keep_indents_on_empty_line']:
                line = ''  
            step1_result += "\n" + line 
        
        lines = step1_result.splitlines()
        blank_cnt = 0
        result = ''

        for line in lines:
            is_has_data = False
            for ch in line:
                if ch != ' ' and ch != '\t':
                    is_has_data = True
                
            if not is_has_data:
                blank_cnt += 1
            else:
                blank_cnt = 0
            if not is_has_data and blank_cnt > self.prop_dict['keep_blank_lines']:
                pass
            else:
                result += "\n" + line 


        if not self.prop_dict['keep_line_breaks_in_text']:
            result = result.replace("\n", "")
        return result


    def format_attribute(self, tag):
        if self.prop_dict['space_around_equal']:
            return tag.name + ' = "' + tag.value + '"'
        return tag.name + '="' + tag.value + '"'

    def get_indent(self, attachment):
        return (self.prop_dict['indent'] * attachment) * self.identation

    def get_continuation_indent(self):
        if self.prop_dict['use_tab'] == 'True':
            tab_count = int(self.prop_dict['continuation_indent'] / self.prop_dict['tab_size'])
            space_count = self.prop_dict['continuation_indent'] - tab_count * self.prop_dict['tab_size']
            return "\t" * tab_count + ' '* space_count
        else:
            print(self.prop_dict['continuation_indent'], self.identation)
            return self.prop_dict['continuation_indent'] * self.identation
    def format_space_in_tag(self):
        return ' ' if self.prop_dict['space_after_tag_name'] else ''
