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
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            parsed_query = urllib.parse.urlparse(self.path).query
            parameters = urllib.parse.parse_qs(parsed_query)
            if 'message' in parameters:
                message = ''.join(parameters['message'])
            else:
                message = ''
                return

            self.wfile.write(b"Date/Time: " +
                             datetime.now().strftime("%m/%d/%Y, %H:%M:%S").
                             encode() + b"\n\n")
            self.wfile.write(b"Let's classify the following: " + message.
                             encode() + b"\n")

            # TODO(developer): Uncomment and set the following variables
            text_snippet = automl.types.TextSnippet(
                content=message,
                mime_type='text/plain')  # Types: 'text/plain', 'text/html'

            payload = automl.types.ExamplePayload(text_snippet=text_snippet)
            response = prediction_client.predict(model_full_id, payload)

            for annotation_payload in response.payload:
                self.wfile.write(b'\nPredicted class name: ' +
                                 annotation_payload.display_name.encode() +
                                 b'\n')
                self.wfile.write(b'\nPredicted class score: ' +
                                 str(annotation_payload.classification.score).
                                 encode() + b'\n')

        except IOError:
            self.wfile.write("There seems to be some problem! " +
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
