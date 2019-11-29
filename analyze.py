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
        return "Type: " + self.type + "\n" + "Name: " + self.name + "\n" + "Value: " + self.value + "\n"+ "Attachment: " + str(self.attachment) + "\n"+ "New line: " + str(self.is_on_new_line) + "\n"    
class StateStatus:

    def __init__(self):
        self.next_line = False
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
                    self.next_line)
        elif type == 'attribute':
            return Tag('attribute',
                    self.attribute,            
                    self.data,
                    self.attachment,
                    self.next_line)
        elif type == 'content':
            return Tag('content',
                    'content',            
                    self.data,
                    self.attachment,
                    self.next_line)
        elif type == 'comment':
            return Tag('comment',
                       'comment',
                       self.data,
                       self.attachment,
                       self.next_line
                       )
        elif type == 'doctype':
            return Tag('doctype',
                       'doctype',
                        self.data,
                        self.attachment,
                        self.next_line
                        )
        else:
            pass

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
            else:
                return Error("Unmached closed tag " + self.name, index)
        else:
            self.increase_attachment()
            oppened_tags.append(self.name)
            
        return self.tag_genarate()

def analyze_code(file_name):
    errors = list()
    tags = list()
    oppened_tags = list()
    index = 1
    cur_state = StateStatus()
    file = open(file_name)
    source = file.read()
    for ch in source:

        if ch == '\n':
            index += 1

        #START STATE
        if cur_state.get_state() == State.START:
            if ch == '<':
                cur_state.set_state(State.START_NAME)
            else:
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
                error.append(Error("Invalid tag name", index))

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
                    cur_state.set_state(State.EXPECTATION_END_TAG)
                else:
                    errors.append(Error("Invalid tag name", index))
            elif ch == '>':
                cur_state.set_state(State.CONTENT)
                cur_state.set_data('')
                res = cur_state.tag_generate_tag(oppened_tags,index)
                if type(res) == Error:
                    errors.append(res)
                else:
                    tags.append(res)


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
                cur_state.set_state(State.CONTENT)
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
                cur_state.set_state(State.CONTENT)
                cur_state.set_data('')
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
                cur_state.set_data('')
                cur_state.set_state(State.ATTRIBUTE_VALUE)
                errors.append(Error("Quote is expected", index))
                
        #ATTRIBUTE_VALUE STATE
        elif cur_state.get_state() == State.ATTRIBUTE_VALUE:
            if ch == cur_state.get_quote():
                cur_state.set_state(State.EXPECTATION_WHITESPACE)
                tags.append(cur_state.tag_genarate('attribute'))
            else:
                if not cur_state.get_quote():
                    if ch == '>':
                        tags.append(cur_state.tag_genarate('attribute'))
                        cur_state.set_state(State.CONTENT)
                        cur_state.set_data('')
                    elif ch == ' ' or ch == '\t' or ch == '\n':
                        tags.append(cur_state.tag_genarate('attribute'))
                        cur_state.set_state(State.EXPECTATION_WHITESPACE)
                else:
                    cur_state.add_ch_to_value(ch)

        #EXPECTATION_WHITESPACE STATE       
        elif cur_state.get_state() == State.EXPECTATION_WHITESPACE:
            if ch == ' ' or ch =='\t' or ch == '\n':
                #TODO save code structure ???
                cur_state.set_state(State.END_NAME)
            elif ch == '>':
                cur_state.set_data('')
                cur_state.set_state(State.CONTENT)
            elif cur_state =='/':
                if cur_state.set_tag_type('opening'):
                    cur_state.set_tag_type('single')
                    cur_state.set_state(State.EXPECTATION_END_TAG)
                else:
                    errors.append(Error("Invalid tag", index))
        
        #CONTENT STATE 
        elif cur_state.get_state() == State.CONTENT:
            #ToDo CONTENT
            if ch == '<':
                tags.append(cur_state.tag_genarate('content'))
                cur_state.set_data('')
                cur_state.set_state(State.START_NAME)
            else:
                cur_state.add_ch_to_value(ch)


        #EXPECTATION_END_TAG STATE 
        elif cur_state.get_state() == State.EXPECTATION_END_TAG:
            if ch == '>':
                cur_state.set_data('')
                cur_state.set_state(State.CONTENT)
                if oppened_tags[-1] == cur_state.get_name(): 
                    oppened_tags.pop()
                tags.append(cur_state.tag_genarate())
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
            elif ch == '-':
                cur_state.add_ch_to_value(ch)
                continue
            else:
                cur_state.add_ch_to_value('--' + ch)
                cur_state.set_state(State.COMMENT)
    return tags, errors
