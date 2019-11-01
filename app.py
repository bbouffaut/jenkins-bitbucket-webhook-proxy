from __future__ import print_function # In python 2.7
import sys
from flask import Flask
from flask import request
from flask import make_response
import requests
import json

app = Flask(__name__)

@app.route('/build', methods = ['POST'])
def build():

  jenkins = request.args.get('jenkins')
  jenkins = jenkins if jenkins.startswith('http://') or jenkins.startswith('https://') else 'https://%s' % jenkins
  jenkins = jenkins[:-1] if jenkins.endswith('/') else jenkins
  token = request.args.get('token', None)
  query = '' if token is None else 'token=%s' % token

  json = request.get_json()
  git_hash = json['push']['changes'][0]['new']['target']['hash']
  git_project = json['repository']['name'].lower()

  # forward the request
  jenkins_url = '%s/generic-webhook-trigger/invoke?%s' % (jenkins, query)
  payload = { 'GIT_PROJECT': git_project }
  print("Incoming WebHooks on %s / %s triggers jenkins on %s" % (git_project, git_hash, jenkins_url), file=sys.stderr)

  response = requests.post(jenkins_url,
    headers={"Content-Type": "application/json"},
    json=payload)

  if (response.status_code in range(400, 500)):
    return "Request error"
  elif (response.status_code >= 500):
    return "Server error"
  else:
    return make_response(response.text, response.status_code, {})

@app.route('/', methods = ['GET'])
def index():
  return "OK"


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
