#!/usr/bin/python
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from google.cloud import automl
import urllib.parse
import os

PORT_NUMBER = 8080
project_id = os.getenv('PROJECT_ID')
model_id = os.getenv('MODEL_ID')
location = os.getenv('LOCATION')


class myHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests
    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            parsed_query = urllib.parse.urlparse(self.path).query
            parameters = urllib.parse.parse_qs(parsed_query)
            if 'message' in parameters:
                message = ''.join(parameters['message'])
            else:
                message = ''

            self.wfile.write(b"Date/Time: " +
                             datetime.now().strftime("%m/%d/%Y, %H:%M:%S").
                             encode() + b"<br>")
            self.wfile.write(
                b"<br>Let's classify the following movie plot:<br><br>")
            self.wfile.write(b'''<form>
            <textarea name="message" rows="14" cols="60" wrap="soft">
            </textarea><br><br>
            <input type="submit" value="Classify">
            </form>''')

            # TODO(developer): Uncomment and set the following variables
            text_snippet = automl.types.TextSnippet(
                content=message,
                mime_type='text/plain')  # Types: 'text/plain', 'text/html'

            if message != '':
                payload = automl.types.ExamplePayload(
                    text_snippet=text_snippet)
                response = prediction_client.predict(model_full_id, payload)

                self.wfile.write(b'<br><br>' + message.encode())
                self.wfile.write(b'<br><br><table border="1 px solid black">' +
                                 b'<tr><th>Predicted Class</th><th>Scpre</th>'
                                 + b'</tr>')

                for annotation_payload in response.payload:
                    self.wfile.write(b'<tr><td>' + annotation_payload.
                                     display_name.encode() + b'</td><td>' +
                                     str(round(annotation_payload.
                                         classification.score, 2)).encode()
                                     + b'</td></td>')

        except IOError:
            self.wfile.write(b"There seems to be some problem! " +
                             datetime.now().strftime("%m/%d/%Y, %H:%M:%S").
                             encode())


if __name__ == '__main__':
    try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print ('Started httpserver on port ', PORT_NUMBER)

        prediction_client = automl.PredictionServiceClient()
        # Get the full path of the model.
        model_full_id = prediction_client.model_path(
            project_id, 'us-central1', model_id)

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        server.socket.close()
