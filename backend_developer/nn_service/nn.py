#!/usr/bin/python3 

# -*- coding:utf-8 -*-

# сервис фильтрации и распознования картинок
# на вход методом POST json формата {"image": data}, где data - закодированная в base64 картинка
# выход json формата {"status": "error", "result": string},
# где status принимает значение либо "ok", либо "error"
# result - результат классфикации изображения, либо текст ошибки

import os
import base64
import sys
import logging
from fastapi import FastAPI
import uvicorn
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stderr),],
    format="%(levelname)s:     %(message)s"
)

AUTOENCODER_THRESHOLD = float(os.environ["AUTOENCODER_THRESHOLD"])
AUTOENCODER_FILE = "/models/autoencoder.keras"
MODEL_CLASSIFIRE_FILE = "/models/classifire.keras"
PORT = 8008

autoencoder = load_model(AUTOENCODER_FILE)
classifire = load_model(MODEL_CLASSIFIRE_FILE)

app = FastAPI()
@app.post("/predict")
def predict(input_data:dict):
    result = {"status": "error", "result": None}
    if 'image' not in input_data.keys():
        logging.error(msg='No filed `image` in request')
        result["result"] = "No filed `image` in request"
        return result
    try:
        image_arr = np.fromstring(base64.b64decode(input_data['image']), np.uint8)
        input_image = Image.fromarray(image_arr)
        input_image = input_image.resize((28, 28))
        input_image = input_image.convert("L")
        input_image_arr = np.array(input_image)
        input_image_arr = 255 - input_image_arr
        input_image_arr = input_image_arr / 255.
        input_image_arr = input_image_arr[np.newaxis, :, :, np.newaxis]
        logging.info(msg='Start predict autoencoder')
        pred_ae = autoencoder.predict(input_image_arr, verbose=0)
        mse = (input_image_arr - pred_ae)
        mse = mse * mse
        mse = mse.mean()
        logging.info(msg=f'MSE image: {mse}')
        if mse > AUTOENCODER_THRESHOLD:
            result["result"] = "not digit"
            logging.info(msg='Not digit in image')
            return result
        logging.info(msg='Start predict classifire')
        pred = classifire.predict(input_image_arr, verbose=0)[0]
        pred_digit = np.argmax(pred)
        result["status"] = "ok"
        result["result"] = str(pred_digit)
        logging.info(msg='End predict. Successful')
        return result
    except Exception as ex:
        logging.error(msg=f'End predict. Fail {ex}')
        result["result"] = str(ex)
        return result

uvicorn.run(app, host="0.0.0.0", port=PORT)
