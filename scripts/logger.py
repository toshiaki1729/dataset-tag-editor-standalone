from print_color import print

def write(content):
    print(content)

def profile(content):
    print(content, tag='PROF', tag_color='blue')

def warn(content):
    print(content, tag='WARNING', tag_color='yellow')

def error(content):
    print(content, tag='ERROR', tag_color='red')