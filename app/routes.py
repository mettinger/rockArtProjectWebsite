
from flask import render_template, flash, redirect, request, url_for
from app import app
import sys
import os
import glob
import mammoth
import re
from bs4 import BeautifulSoup

# strip out private info, e.g. address, price for artifact
def stripInfo(soup, regExpList):
    for thisRegExp in regExpList:
        for elem in soup(text=re.compile(thisRegExp)):
            elem.parent.decompose()

# convert .docx to .html, strip private info, and check for annotations
def processDoc(documentPath, htmlDirectory):

    basename = os.path.basename(documentPath)[0:-5].replace(" ","_")
    goodDirectory = htmlDirectory + "goodFiles/"
    badDirectory = htmlDirectory + "badFiles/"

    try:
        with open(documentPath, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value

        soup = BeautifulSoup(html, 'html.parser')
        regExpList = [r'Coffman', r'149 Atlantic',r'Swampscott',r'\$\d*\.\d\d'] # strip dollar amounts, etc.
        stripInfo(soup, regExpList)
        html = str(soup)
        if "LC Class" in html:
            htmlPath = goodDirectory + basename + '.html'
        else:
            htmlPath = badDirectory + basename + '.html'

        with open(htmlPath,'w') as fp:
            fp.write(html)
    except:
        pass


# make html directories and convert .docx to .html
def setup(baseDataDirectory):

    htmlDirectory = "./app/static/html/"
    goodDirectory = htmlDirectory + "goodFiles/"
    badDirectory = htmlDirectory + "badFiles/"

    os.mkdir(htmlDirectory)
    os.mkdir(goodDirectory)
    os.mkdir(badDirectory)
    allWordFilesGlob = baseDataDirectory + "**/*.docx"
    docFileList = glob.glob(allWordFilesGlob, recursive=True)
    print("Number of .docx files found: " + str(len(docFileList)))
    for thisFile in docFileList:
        processDoc(thisFile, htmlDirectory)

@app.route('/')
@app.route('/index',methods=['GET', 'POST'])
def index():

    if sys.platform == 'linux': # aws ubuntu
        baseDataDirectory = "/home/ubuntu/data/rockArtProject/"
    else: # mac local
        baseDataDirectory = "/Users/mettinger/Desktop/rockArtProjectData/"

    htmlDirectory =  "./app/static/html/"
    goodDirectory = htmlDirectory + "goodFiles/"
    badDirectory = htmlDirectory + "badFiles/"

    # if the .docx files have not been converted to .html, do it now!
    # to start over, just delete ./app/static/html
    if not os.path.isdir(htmlDirectory):
        setup(baseDataDirectory)

    goodFilePairs =  [(url_for('static', filename = "html/goodFiles/"+ i), i) for i in os.listdir(goodDirectory)]
    badFilePairs = [(url_for('static', filename = "html/badFiles/"+ i),i) for i in os.listdir(badDirectory)]
    return render_template('index.html', goodFiles=goodFilePairs, badFiles=badFilePairs)
