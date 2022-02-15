#!/usr/bin/python
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from google.cloud import language_v1

#from google.cloud.language import enums
#from google.cloud.language import types
import urllib.parse

PORT_NUMBER = 8080


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

            self.wfile.write(b"Date/Time: " +
                             datetime.now().strftime("%m/%d/%Y, %H:%M:%S").
                             encode() + b"\n\n")
            self.wfile.write(b"Let analyse the following: " + message.encode())

            text = message.encode()
          
            document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)            
            sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment

            self.wfile.write(b'\n\nSentiment: ' + str(sentiment.score).encode()
                             + b' Magnitude: ' + str(sentiment.magnitude).
                             encode())

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

        client = language_v1.LanguageServiceClient()

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        server.socket.close()
