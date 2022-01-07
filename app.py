from flask import Flask, request, abort, send_from_directory, send_file, render_template, jsonify, make_response
import os
import numpy as np
import pandas as pd
import json
import csv
import minecart
import json
from stuff import *
import requests

#response = make_response(render_template('index.html', foo=42)), response.headers.add('Access-Control-Allow-Origin', '*')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
dlfolder = app.config['UPLOAD_FOLDER'] + '/out/'

@app.route("/")
def index():
    response = make_response(render_template('index.html'))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/write")
def write():
    file = open(app.config["UPLOAD_FOLDER"] + "/text.txt", "w")
    file.write("dadadadada\n")
    file.write("blksdlkslkj fklj asfj klasf jklajsf \n")
    file.write("jlkajflksajlkfasjkljsl\n")
    return "done"

@app.route("/read")
def read():
    file = open(app.config["UPLOAD_FOLDER"] + "/text.txt", "r")
    content = file.read()
    print(content)
    return content

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
        global plan
        global celljson
        files = request.files
        # print(str(files))
        files['pdffile'].save(dlfolder + 'pdf.pdf')
        files['jsonfile'].save(dlfolder + 'json.json')
        celljson = dlfolder +'json.json'
        plan = dlfolder + 'pdf.pdf'
        # plan = files['pdffile'].read()
        # celljson = files['jsonfile'].read()

        colors = set()
        # temp = (cell.text,cell.x1,cell.y1,cell.x2,cell.y2,i,j,ii,r,g,b)
        global cellinfo
        with open(celljson) as f:
            cellinfo = [dict(x) for x in json.load(f)]
        # print(cellinfo)
        print(len(cellinfo))

        cellcolors = []

        x1=186
        y1=419
        x2=233
        y2=436

        BOX = (x1,y1,x2,y2)
        global s

        pagenumber = 0

        buffer = 1

        with open(plan,"rb") as doc:
            document = minecart.Document(doc)
            # print(document)
            for page in document.iter_pages():
                # print("pagenumber: " + str(pagenumber))
                for shape in page.shapes:
                    for cell in cellinfo:
                        left = cell['x1'] - buffer
                        bottom = cell['y1'] - buffer
                        right = cell['x2'] + buffer
                        top = cell['y2'] + buffer
                        box = (left,bottom,right,top)
                        # box = (0,0,600,600)
                        # box = (696.9200331584948, 486.8216768762596, 745.4800353705815, 506.09819469971785)
                        if shape.check_inside_bbox(box):
                            # print("check")
                            r, g, b = shape.fill.color.as_rgb()
                            shift = getShiftByColor((r,g,b))
                            if(len(shift) > 1):
                                # print(cell['shifttype'] + 'pre')
                                if(cell['table'] == pagenumber):
                                    cell['shifttype'] = shift
                                    # if pagenumber == 0: print(cell['text'],shift,cell['table'],cell['row'],cell['col'])
                                # print(cell['shifttype'] + 'post')
                            # ls[8] = r
                            # ls[9] = g
                            # ls[10] = b
                            # cell[8] = r
                            # cell[9] = g
                            # cell[10] = b
                            # cell = tuple(ls)
                            # print(cell)
                            cellcolors.append(cell)
                            # i5 j6 ii7 r8 g9 b10
                        # if shape.fill:
                        #     color = shape.fill.color.as_rgb()
                        #     colors.add(color)
                        #     def allZero(c):
                        #         if c[0] == 0:
                        #             if c[1] == 0:
                        #                 if c[2] == 0:
                        #                     return True
                        #         else:
                        #             return False
                        #     if not allZero(color):
                        #         print(color)
                        #         print(shape.get_bbox())
                                # s = shape
                            # print(shape.fill.color.as_rgb())
                            # print(shape.get_bbox())
                pagenumber +=1
            # page = document.get_page(0)
            # for shape in page.shapes:
            #     if shape.fill:
            #         colors.add(shape.fill.color.as_rgb())
        # for cell in cellcolors:
        #     print(cell['shifttype'])
        with open(app.config['UPLOAD_FOLDER'] + '/out/' + 'celldatawcolors.json', 'w') as f:
                json.dump(cellcolors,f)
        output = {
            'shifts': cellcolors
        }
        return jsonify(output)
        # f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))tif
        # return 'Succeeded!'

@app.route('/get', methods=['POST','GET'])
def uploadimages():
    file_names=[]
    curr_path=os.getcwd()
    inputpath = app.config['UPLOAD_FOLDER']
    files_in_dir=os.listdir(inputpath)

    # for file in file_names:
    #     if file.split('.')[-1] is in ['jpeg','png','jpg','pdf']:
    #         os.remove(file)
    # uploaded_files=request.files.getlist("files") 
    # for file in uploaded_files:  
    #     if file.filename.split('.')[-1] is in ['jpeg','png','jpg']:
    #         file.save(file.filename)
    # imagetopdf_obj=imagetopdf.Imagetopdf()
    # imagetopdf.convert()
    try:
        return send_from_directory(inputpath,files_in_dir[0],
                                             as_attachment=True)
    except Exception:
        abort(404)             

@app.route("/minecart", methods=['POST','GET'])
def c():
    # filenames = []
    print("starting minecart" + '\n')
    if request.method == 'POST':
        print("is post request" + '\n')
        f = request.files['file']
        print("file = " + file + '\n')
        filename = f.filename
        print("filename = " + filename + '\n')
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        return 'Succeeded!'
    
    # csvout = cleanuptables(tables,docs)
    # csvout.to_csv(outputpath + 'output.csv')

    # try:
    #     return send_from_directory(filepath + '/out/','output.csv',as_attachment=True)
    # except Exception:
    #     abort(404)


if __name__ == '__main__':     
#    app.run(host='0.0.0.0',port=5001,debug=True)
    app.run(port=process.env.port,host='0.0.0.0')