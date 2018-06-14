#!/user/bin/env python
# coding=utf-8
import email
import os
import sys
from html_stripper import strip_html

TARGET = "processed"    

def get_character_set(msg):
    if msg.get_content_charset() is None :
        return "utf-8"
    else:
        charset = msg.get_content_charset()
        try:
            unicode("123", "utf-8").encode(charset)
            return charset
        except:
            return "utf-8"


def select_body_part(msg):
    if msg.is_multipart():
        candidate_list = []
        # 优先在当前级别选择文本类型
        for part in msg.get_payload():
            if ("text" == part.get_content_maintype()):
                return part
            else:
                candidate_list.append(part)
        # 然后选择 alternative 和 mixed
        for candidate in candidate_list:
            if ("alternative" == part.get_content_subtype() or "mixed" == part.get_content_subtype()):
                selected = select_body_part(part)
                if selected is not None:
                    return selected

        # 最后处理剩下的， 如果仍然没有找到
        for candidate in candidate_list:
            return select_body_part(candidate)

        # 真的是没有找到
        return None
    else:
        return msg


def read_body(filename):
    fd = open(filename)
    msg = email.message_from_file(fd)
    fd.close()
    body_part = select_body_part(msg)
    if body_part is not None:
        try:
            body = unicode(body_part.get_payload(decode=True), \
                        str(get_character_set(body_part)), \
                        'ignore') \
            .encode('utf-8', 'replace')

            if ("html" == body_part.get_content_subtype().lower()):
                body = strip_html(body)
            return body
        except:
            return "utf-8"
    else:
        return None


def save(file, body):
    fd = open(file, "w")
    fd.write(body)
    fd.close()


def run(DIR):
    counter = 1
    for file in os.listdir(DIR):
        filename = os.path.join(DIR, file)
        if len(filename) < 5 or not os.path.isfile(filename):
            continue
        sys.stdout.write("\r%d...%s" % (counter, file))
        counter = counter + 1

        body = read_body(filename)
        if body is not None:
            target_dir = os.path.join("processed", os.path.basename(DIR))
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            save(os.path.join(target_dir, file), body)
    sys.stdout.write("\r%d files processed.\n" % (counter))


if __name__ == "__main__":
    for file in os.listdir("./data"):
        target_dir = os.path.join("data", file)
        if os.path.isdir(target_dir):
            print("process emails in %s" % (target_dir))
            run(target_dir)
