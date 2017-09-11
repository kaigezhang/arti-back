# -*- coding: UTF-8 -*-
# import subprocess
import app.config as config
from subprocess import check_call, CalledProcessError
import codecs


def splitBetween(s, s1, s2):
    return s.split(s1)[1].split(s1)[0]


def pdf2html(pdf_path):
    fn = pdf_path.split('/')[-1].replace('.pdf', '')

    props = [
        '--fit-width=800',
        '--embed-font=1',
        '--embed-css=0',
        '--embed-image=1',
        '--embed-javascript=0',
        '--embed-outline=0',
        '--process-outline=0',
        '--heps=1',
        '--optimize-text=1',
        '--css-filename=%s.css' % fn,
        '--dest-dir=%s' % config.HTML_DIR,
        '%s' % pdf_path,
        '%s.html' % fn
    ]
    try:
        res = check_call(['pdf2htmlEX'] + props)
    except CalledProcessError:
        res = 1
    return res


def extract_html_css(filename):
    html = str(config.HTML_DIR + '/' + filename + '.html')
    css = str(config.HTML_DIR + '/' + filename + '.css')
    # 防止编码问题
    with codecs.open(html, 'r', 'utf-8') as f:
        html_content = f.read()
    with codecs.open(css, 'r', 'utf-8') as c:
        css_content = c.read()
    html_split = splitBetween(
        str(html_content),
        '<div id="page-container">\n',
        '\n<div class="loading-indicator">'
    )
    return {
        'html': html_split,
        'css': css_content
    }
