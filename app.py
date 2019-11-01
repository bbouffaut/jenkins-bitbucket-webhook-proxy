from flask import Flask
from flask import request
from flask import make_response
from unirest import post

app = Flask(__name__)

@app.route('/build', methods = ['POST'])
def build():

  jenkins = request.args.get('jenkins')
  jenkins = jenkins if jenkins.startswith('http://') or jenkins.startswith('https://') else 'http://%s' % jenkins
  jenkins = jenkins[:-1] if jenkins.endswith('/') else jenkins
  token = request.args.get('token', None)
  query = '' if token is None else 'token=%s' % token

  json = request.json
  git_hash = json['push']['changes'][0]['new']['target']['hash']
  git_project = json['repository']['name'].lower()
  print git_project + "/" + git_hash

  # forward the request
  jenkins_url = '%s/generic-webhook-trigger/invoke?%s' % (jenkins, query)
  print jenkins_url

  response = post(jenkins_url,
    headers={"Accept": "application/json"},
    params = { 'GIT_PROJECT': git_project }

  if (response.code in range(400, 500)):
    return "Request error"
  elif (response.code >= 500):
    return "Server error"
  else:
    return make_response(response.raw_body, response.code, {})

@app.route('/', methods = ['GET'])
def index():
  return "OK"


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
