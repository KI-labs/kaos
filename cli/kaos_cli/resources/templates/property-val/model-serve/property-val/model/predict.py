import logging
import multiprocessing
import os
import sys

import flask

# flask app for serving predictions
app = flask.Flask(__name__)

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

# ============================== #
# REQUIRED ENVIRONMENT VARIABLES #
# ============================== #
model_server_workers = int(os.environ.get('MODEL_SERVER_WORKERS', multiprocessing.cpu_count()))  # dynamic cpu num

# ===================== #
# START OF FIXED INPUTS #
# ===================== #
try:
    from model import load_model, predict
except ImportError:
    print('Could not import load_model and predict')
    sys.exit(1)

# TODO -> enforce this structure
ctx = load_model("model.pkl")  # load trained model


@app.route('/invocations', methods=['POST'])
def invocations():
    """
    A flask handler for predictions

    Returns:
        A flask response with either a prediction or an error
    """

    # pre-process request
    data = flask.request.get_json()  # read data

    # make predictions
    try:
        out = predict(data, ctx)  # extract prediction
        logging.info("Predict: {}".format(out))
        return flask.jsonify(result=out)

    except Exception as ex:
        logging.error(ex)
        return flask.Response(response='Error while processing the request',
                              status=500,
                              mimetype='text/plain')
