from enum import Enum

class State(Enum):
    START = 1
    NAME = 2
    START_NAME = 3
    END_NAME = 4
    EXPECTATION_END_TAG = 5
    CONTENT = 6
    EXCLAMATION = 7
    EXPECTATION_WHITESPACE = 8
    EXPECTATION_QUOTE = 9
    ATTRIBUTE = 10
    ATTRIBUTE_VALUE = 11
    EXPECTATION_DASH = 12
    COMMENT = 13
    FIRST_DASH = 14
    SECOND_DASH = 15

class Error:
 
    def __init__(self, error, line):
        self.error = error
        self.line = line
 
    def __str__(self):
        return 'Error on line ' + str(self.line) + ': "' + self.error + '"'

class Tag:
 
    def __init__(self, type, name, value, attachment, is_on_new_line):
        self.type = type
        self.name = name
        self.value = value
        self.attachment = attachment
        self.is_on_new_line = is_on_new_line
    
    def __str__(self):
        return "{" + self.type + "; " + self.name + "; " + self.value + "; " + str(self.attachment) + "; " + str(self.is_on_new_line) + "}"


unclosing_tag_list = ['area','base','br','br ','col','embed','hr','img','input','link','meta','param','source','track','wbr','command','keygen','menuitem']
class StateStatus:

    def __init__(self):
        self.new_line = False
        self.state = State.START
        self.name = ''
        self.tag_type = ''
        self.quote = ''
        self.attribute = ''
        self.attibute_value = ''
        self.attachment = 0
        self.data = ''
        

    def set_state(self,new_state):
            self.state = new_state

    def get_state(self):
        return self.state

    def get_name(self):
        return self.name

    def get_tag_type(self):
        return self.tag_type

    def increase_attachment(self):
        self.attachment += 1

    def decrease_attachment(self):
        self.attachment -= 1
        
    def add_ch(self,ch): #TODO rename to append_name_symbol
            self.name += ch

    def set_new_line(self,value):
            self.new_line = value

    def set_name(self,name):
            self.name = name

    def set_tag_type(self, tag_type):
            self.tag_type = tag_type


    def set_attribute(self,attribute):
            self.attribute = attribute

    def set_data(self,data):
            self.data = data

    def get_data(self):
            return self.data
    
    def delete_last_char_from_data(self):
            self.data = self.data[:-1]

    def delete_last_line_from_data(self):
        cbl = self.data.splitlines()
        cbl.pop()
        self.data = '\n'.join(cbl)
    def add_ch_to_attr(self,ch):
            self.attribute += ch

    def add_ch_to_value(self,ch):
            self.data += ch

    def set_quote(self,quote):
        self.quote = quote

    def get_quote(self):
        return self.quote

    def tag_genarate(self, type = 'tag'):
        if type == 'tag':
            
            return Tag(self.tag_type,
                    self.name,            
                    self.data,
                    self.attachment,
                    self.new_line)
        elif type == 'attribute':
            return Tag(type,
                    self.attribute,            
                    self.data,
                    self.attachment,
                    self.new_line)
        else:
            return Tag(type,
                    type,            
                    self.data,
                    self.attachment,
                    self.new_line)
       

    def tag_generate_tag(self, oppened_tags, index):
       
        if self.tag_type == 'doctype':
                    if self.name == '!DOCTYPE':
                        return self.tag_genarate('doctype')
                    else:
                        return Error('Expected !DOCTYPE tag',index)
        elif self.tag_type == 'closing':
            if len(oppened_tags) and oppened_tags[-1] == self.name:
                oppened_tags.pop()
                self.decrease_attachment()
                result = self.tag_genarate()
                
            else:
                return Error("Unmached closed tag " + self.name, index)
        else:
            result = self.tag_genarate()
            self.increase_attachment()
            oppened_tags.append(self.name)
            
        return result



def analyze_code(file_name):
    errors = list()
    tags = list()
    oppened_tags = list()
    index = 1
    cur_state = StateStatus()
    file = open(file_name)
    source = file.read()
    indicator = False

    for ch in source:

        if ch == '\n':
            cur_state.set_new_line(True)
            index += 1

        #START STATE
        if cur_state.get_state() == State.START:
            if ch == '<':
                indicator = False
                cur_state.set_state(State.START_NAME)
            elif not indicator and ch == '\n':
                cur_state.set_new_line(True)
                indicator = True
            else:
                indicator = False
                cur_state.add_ch_to_value(ch)
                cur_state.set_state(State.CONTENT)

        #START_NAME STATE
        elif cur_state.get_state() == State.START_NAME:
            cur_state.set_name('')
            cur_state.set_tag_type('opening')
            if ch == ' ' or ch == '\t':
                continue
            elif ch == '\n':
                cur_state.set_new_line(True)
                continue
            elif ch == '!':
                cur_state.set_state(State.EXCLAMATION)
            elif ch == '/':
                cur_state.set_tag_type('closing')
                cur_state.set_state(State.NAME)
            elif ch.isalpha() or ch == '_':
                cur_state.add_ch(ch)
                cur_state.set_state(State.NAME)
            else:
                errors.append(Error("Invalid tag name", index))

        #NAME STATE
        elif cur_state.get_state() == State.NAME:
            if ch.isalpha() or ch.isdigit():
                cur_state.add_ch(ch)
                continue
            elif ch == ' ' or ch == '\t':
                cur_state.set_state(State.END_NAME)
                res = cur_state.tag_generate_tag(oppened_tags,index)
                if type(res) == Error:
                    errors.append(res)
                else:
                    tags.append(res)
                    cur_state.set_new_line(False)
            elif ch == '\n':
                cur_state.set_new_line(True)
                res = cur_state.tag_generate_tag(oppened_tags,index)
                if type(res) == Error:
                    errors.append(res)
                else:
                    tags.append(res)
                
            elif ch == '/':
                cur_state.set_state(State.EXPECTATION_END_TAG)
                if cur_state.get_tag_type() == 'opening':
                    cur_state.set_tag_type('single')
                    tags.append(cur_state.tag_genarate())
                    cur_state.decrease_attachment()
                    cur_state.set_new_line(False)
                    cur_state.set_state(State.EXPECTATION_END_TAG)
                else:
                    errors.append(Error("Invalid tag name", index))
            elif ch == '>':
                cur_state.set_state(State.START)
                cur_state.set_data('')
                
                if cur_state.get_name() in unclosing_tag_list:   
                    cur_state.set_tag_type('single')
                    tags.append(cur_state.tag_genarate())
                else:
                    res = cur_state.tag_generate_tag(oppened_tags,index)
                if type(res) == Error:
                    errors.append(res)
                else:
                    tags.append(res)
                    cur_state.set_new_line(False)


        #END_NAME STATE 
        elif cur_state.get_state() == State.END_NAME:
            if ch.isalpha() or ch =='_':
                cur_state.set_attribute('')
                cur_state.set_state(State.ATTRIBUTE)
                cur_state.add_ch_to_attr(ch)
            elif ch == ' ' or ch == '\t':
                continue
            elif ch == '\n':
                cur_state.set_new_line(True)
                continue
            elif ch == '/':
                cur_state.set_state(State.EXPECTATION_END_TAG)
                if cur_state.get_tag_type() == 'opening':
                    cur_state.set_tag_type('single')
                    cur_state.set_state(State.EXPECTATION_END_TAG)
                else:
                    errors.append(Error("Invalid tag name", index))
            elif ch == '>':
                if cur_state.get_name() in unclosing_tag_list:   
                    cur_state.set_tag_type('single')
                    if oppened_tags[-1] == cur_state.get_name(): 
                        oppened_tags.pop()
                    tags.append(cur_state.tag_genarate())
                    cur_state.decrease_attachment()


                cur_state.set_state(State.START)
                cur_state.set_data('')
            elif ch == '<':
                errors.append(Error("Unclosed tag", index))
                cur_state.set_state(State.START_NAME)
        
        #ATTRIBUTE STATE
        elif cur_state.get_state() == State.ATTRIBUTE:
            if ch.isalpha() or ch.isdigit() or ch =='_' or ch == '-':
                cur_state.add_ch_to_attr(ch)
                continue
            elif ch == '>':
                if cur_state.get_name() in unclosing_tag_list:   
                    cur_state.set_tag_type('single')
                    if oppened_tags[-1] == cur_state.get_name(): 
                        oppened_tags.pop()
                    tags.append(cur_state.tag_genarate())
                    cur_state.decrease_attachment()


                cur_state.set_state(State.START)
                cur_state.set_data('')
                if cur_state.get_tag_type() != 'doctype':
                    errors.append(Error("Invalid attribute value", index))
            elif ch == '=':
                cur_state.set_state(State.EXPECTATION_QUOTE)
        
        #EXPECTATION_QUOTE STATE 
        elif cur_state.get_state() == State.EXPECTATION_QUOTE:
            if ch == ' ' or ch == '\t':
                continue
            elif ch == '\n':
                cur_state.set_new_line(True)
                continue
            elif ch == '"' or ch == "'":
                cur_state.set_quote(ch)
                cur_state.set_data('')
                cur_state.set_state(State.ATTRIBUTE_VALUE)
            else:
                cur_state.set_quote(None)
                cur_state.set_data(ch)
                cur_state.set_state(State.ATTRIBUTE_VALUE)
                errors.append(Error("Quote is expected", index))
                
        #ATTRIBUTE_VALUE STATE
        elif cur_state.get_state() == State.ATTRIBUTE_VALUE:
            if ch == cur_state.get_quote():
                cur_state.set_state(State.EXPECTATION_WHITESPACE)
                tags.append(cur_state.tag_genarate('attribute'))
                cur_state.set_new_line(False)
            else:
                if not cur_state.get_quote():
                    if ch == '>':
                        tags.append(cur_state.tag_genarate('attribute'))
                        cur_state.set_new_line(False)
                        if cur_state.get_name() in unclosing_tag_list: 
                            cur_state.set_tag_type('single')
                            if oppened_tags[-1] == cur_state.get_name(): 
                                oppened_tags.pop()
                            tags.append(cur_state.tag_genarate())
                            cur_state.decrease_attachment()

                        cur_state.set_state(State.START)
                        cur_state.set_data('')
                    elif ch == ' ' or ch == '\t' or ch == '\n':
                        tags.append(cur_state.tag_genarate('attribute'))
                        cur_state.set_new_line(False)
                        cur_state.set_state(State.EXPECTATION_WHITESPACE)
                    else:
                        cur_state.add_ch_to_value(ch)
                else:
                    cur_state.add_ch_to_value(ch)

        #EXPECTATION_WHITESPACE STATE       
        elif cur_state.get_state() == State.EXPECTATION_WHITESPACE:
            if ch == ' ' or ch =='\t' or ch == '\n':
                #TODO save code structure ???
                cur_state.set_state(State.END_NAME)
            elif ch == '>':
                if cur_state.get_name() in unclosing_tag_list: 
                    cur_state.set_tag_type('single')
                    if oppened_tags[-1] == cur_state.get_name(): 
                        oppened_tags.pop()
                    tags.append(cur_state.tag_genarate())
                    cur_state.decrease_attachment()


                cur_state.set_data('')
                cur_state.set_state(State.START)
            elif cur_state =='/':
                if cur_state.set_tag_type('opening'):
                    cur_state.set_tag_type('single')
                    cur_state.set_state(State.EXPECTATION_END_TAG)
                else:
                    errors.append(Error("Invalid tag", index))
        
        #CONTENT STATE 
        elif cur_state.get_state() == State.CONTENT:
            if ch == '<':
                cbl = cur_state.get_data().splitlines()
                content_last = cbl[-1]
                is_data_in_last = False
                for ch in content_last:
                    if ch != ' ' and ch != '\t':
                        is_data_in_last = True

                if cur_state.get_data()[-1] == '\n':
                    cur_state.delete_last_char_from_data()
                    tags.append(cur_state.tag_genarate('content'))
                    cur_state.set_new_line(True)
                elif not is_data_in_last:
                    
                    cur_state.delete_last_line_from_data()
                    if len(cbl) > 1:
                        tags.append(cur_state.tag_genarate('content'))
                    cur_state.set_new_line(True)
                else:
                    tags.append(cur_state.tag_genarate('content'))
                    cur_state.set_new_line(False)

                cur_state.set_data('')
                cur_state.set_state(State.START_NAME)
            else:
                cur_state.add_ch_to_value(ch)


        #EXPECTATION_END_TAG STATE 
        elif cur_state.get_state() == State.EXPECTATION_END_TAG:
            if ch == '>':
                if cur_state.get_name() in unclosing_tag_list: 
                    cur_state.set_tag_type('single')
                    if oppened_tags[-1] == cur_state.get_name(): 
                        oppened_tags.pop()
                    tags.append(cur_state.tag_genarate())
                    cur_state.decrease_attachment()
                    cur_state.set_state(State.START)

                else:
                    if oppened_tags[-1] == cur_state.get_name(): 
                        oppened_tags.pop()
                    tags.append(cur_state.tag_genarate())

                    if cur_state.get_tag_type() == 'single':
                        cur_state.decrease_attachment()
                    cur_state.set_data('')
                    cur_state.set_state(State.START)
                    cur_state.set_new_line(False)
            else:
                errors.append(Error('Closing tag was expected', index))

        #EXCLAMATION STATE 
        elif cur_state.get_state() == State.EXCLAMATION:
            if ch == 'D':
                cur_state.set_state(State.NAME)
                cur_state.add_ch('!' + ch)
                cur_state.set_tag_type('doctype')
            elif ch == '-':
                cur_state.set_state(State.EXPECTATION_DASH)
                cur_state.set_tag_type('comment')
            else:
                errors.append(Error('Invalid tag name',index))

        #EXPECTATION DASH STATE
        elif cur_state.get_state() == State.EXPECTATION_DASH:
            if ch == '-':
                cur_state.set_state(State.COMMENT)
            else:
                errors.append(Error('invalid tag name',index))

        #COMMENT STATE
        elif cur_state.get_state() == State.COMMENT:
            if ch == '-':
                cur_state.set_state(State.FIRST_DASH)
            else:
                cur_state.add_ch_to_value(ch)

        #FIRST_DASH STATE
        elif cur_state.get_state() == State.FIRST_DASH:
            if ch == '-':
                cur_state.set_state(State.SECOND_DASH)
            else:
                cur_state.set_state(State.COMMENT)
                cur_state.add_ch_to_value('-' + ch)

        #SECOND_DASH STATE
        elif cur_state.get_state() == State.SECOND_DASH:
            if ch == '>':
                cur_state.set_state(State.START)
                tags.append(cur_state.tag_genarate('comment'))
                cur_state.set_data('')
                cur_state.set_new_line(False)
            elif ch == '-':
                cur_state.add_ch_to_value(ch)
                continue
            else:
                cur_state.add_ch_to_value('--' + ch)
                cur_state.set_state(State.COMMENT)
    if cur_state.get_state() != State.CONTENT and cur_state.get_state() != State.START:
        errors.append(Error("HTML is not valid",0))
    return tags, errors
