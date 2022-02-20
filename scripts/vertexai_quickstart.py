
## Prerequsite:
#  $ pip3 install google-cloud-aiplatform

# [START aiplatform_predict_text_classification_single_label_sample]
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


def predict_text_classification_single_label_sample(
    project, location, endpoint_id, content):
    aiplatform.init(project=project, location=location)
    endpoint = aiplatform.Endpoint(endpoint_id)

    response = endpoint.predict(instances=[{"content": content}], parameters={})
    print('\nClassification for ' + content + ': ')

    for prediction_ in response.predictions:
        #print(prediction_['displayNames'])
        #print(prediction_['confidences'])
        displayNames = prediction_['displayNames']
        confidences = prediction_['confidences']
        for i in range(0 , len(displayNames)):
            print(displayNames[i], confidences[i])


content = "After a soccer game with my old buddies, we have  delightful meal and drinks the whole night."



##TO DO ##
# paste the Python codes here #
# replace the parameter content="YOUR_TEXT_CONTENT" with content=content
# To test further, provide new text for the content variable




