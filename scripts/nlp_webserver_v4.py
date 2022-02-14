#!/usr/bin/python
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import urllib.parse

PORT_NUMBER = 8080


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
            self.wfile.write(b"<br>Let's analyse the following " +
                             b"text block:<br><br>")
            self.wfile.write(b'''<form>
            <textarea name="message" rows="14" cols="60" wrap="soft">
            </textarea><br><br>
            <input type="submit" value="Document + Entity Sentiment Analysis">
            </form>''')

            text = message
            document = types.Document(
                content=text,
                type=enums.Document.Type.PLAIN_TEXT)
            sentiment = client.analyze_sentiment(document).document_sentiment

            self.wfile.write(message.encode() + b'<br><br>Document Sentiment: '
                             + str(sentiment.score).encode() + b' Magnitude: '
                             + str(sentiment.magnitude).encode())

            entity_sentiment_response = client.analyze_entity_sentiment(
                    document)

            self.wfile.write(b'<br><br><table border="1 px solid black">' +
                             b'<tr><th>Entity Name</th><th>Type</th>' +
                             b'<th>Salience</th><th>Sentiment Score</th>' +
                             b'<th>Sentiment Magnitude</th><th>Meta Data' +
                             b'</th><th>Mention</th><th>Type</th></tr>')

            # Loop through entitites returned from the API
            for entity in entity_sentiment_response.entities:
                # to keep things simple, display only wikipedia metadata
                # resource
                metadata_name = ''
                metadata_value = ''
                if entity.metadata["wikipedia_url"]:
                    metadata_name = entity.metadata["wikipedia_url"]
                    # metadata_value = entity.metadata[0].value
                else:
                    metadata_name = ''
                    metadata_value = ''

                for mention in entity.mentions:
                    self.wfile.write(b'<tr><td>' + entity.name.encode() +
                                     b'</td>')
                    self.wfile.write(b'<td>' + enums.Entity.Type(entity.type).
                                     name.encode() + b'</td>')
                    self.wfile.write(b'<td>' + str(entity.salience).encode() +
                                     b'</td>')
                    self.wfile.write(b'<td>' + str(entity.sentiment.score).
                                     encode() + b'</td>')
                    self.wfile.write(b'<td>' + str(entity.sentiment.magnitude)
                                     .encode() + b'</td>')
                    self.wfile.write(b'<td>' + metadata_name.encode() + b' ' +
                                     metadata_value.encode() + b'</td>')
                    self.wfile.write(b'<td>' + mention.text.content.encode() +
                                     b'</td>')
                    self.wfile.write(b'<td>' + enums.EntityMention.Type
                                     (mention.type).name.encode() +
                                     b'</td></tr>')

            self.wfile.write(b'</table>')
            self.wfile.write(b'<br>Language ' + entity_sentiment_response
                             .language.encode())

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

        client = language.LanguageServiceClient()

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        server.socket.close()
