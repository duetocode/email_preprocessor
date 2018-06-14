from HTMLParser import HTMLParser


class HTMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    
    def handle_data(self, d):
        self.fed.append(d)
    
    def get_text(self):
        return ''.join(self.fed)


def strip_html(body):
    stripper = HTMLStripper()
    stripper.feed(body)
    return stripper.get_text()


if __name__ == "__main__":
    print("%s" % (strip_html("<div>123<stong>abc</st></div>")))