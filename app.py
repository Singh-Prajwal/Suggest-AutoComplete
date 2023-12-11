from flask import jsonify, request, redirect, render_template, session
import requests
from flask import Flask
from elasticsearch import Elasticsearch
app = Flask(__name__)

es = Elasticsearch(hosts=["https://127.0.0.1:9200"],
                   basic_auth=("elastic", "eXun5Zuz5ctLbko-ktQ+"), verify_certs=False)

print("Connected to Elasticsearch cluster")
# print({es.info().body["cluster_name"]})


@app.route("/")
def main():
    return render_template("index.html")


@app.route("/search")
def search_autocomplete():
    query = request.args["q"].lower()
    tokens = query.split(" ")
    clauses = [

        {
            "span_multi": {
                "match": {
                    "fuzzy":
                        {
                            "title":
                            {
                                "value": token,
                                "fuzziness": "AUTO"
                            }
                        }
                }
            }
        }

        for token in tokens
    ]
    Max_size = 10
    payload = {
        "query": {
            "bool": {
                "must": [
                    {
                        "span_near": {
                            "clauses": clauses,
                            "slop": 0,
                        }
                    }
                ]
            }
        }
    }
    print("payload", payload)
    try:
        indices = ["netflix_titles"]
        response = es.search(index=indices,
                             size=Max_size, body=payload)
        hits = response.get("hits", {}).get("hits", [])
        results = [{"_source": hit["_source"]['title']}
                   for hit in hits]
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(port=4000, host="0.0.0.0", debug=True)
