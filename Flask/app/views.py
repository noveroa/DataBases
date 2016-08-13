from flask import Flask, request, jsonify, render_template
import random

# Create flask app
app = Flask("My test server", template_folder='templates')

@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/search/<param1>/<param2>', methods=['GET'])
def search_params(param1, param2):
    print "*"*44
    print "param1", param1
    print "param2", param2

    # make some fake data
    result = {}
    data = []
    for i in range(int(random.random() * 100)):
        data.append({"year":1950 + i, "title":"this is a title %s"%i})
    print data
    return jsonify({"data":data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)
        
