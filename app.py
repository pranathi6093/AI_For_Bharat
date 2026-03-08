import os
import gradio as gr
import numpy as np
import tensorflow as tf
from PIL import Image
import h5py
import json
from tensorflow.keras.models import model_from_json

# ---- Fix incompatible model config ----
with h5py.File("hemolysis_model.h5", "r") as f:
    model_config = f.attrs.get("model_config")

model_config = json.loads(model_config.decode("utf-8"))

# replace batch_shape with batch_input_shape
for layer in model_config["config"]["layers"]:
    if "batch_shape" in layer["config"]:
        layer["config"]["batch_input_shape"] = layer["config"].pop("batch_shape")

model = model_from_json(json.dumps(model_config))
model.load_weights("hemolysis_model.h5")

# ---- Prediction function ----
def predict(img):
    img = img.resize((224,224))
    img_array = np.array(img)/255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0][0]

    if prediction > 0.5:
        label = "Normal Sample"
        confidence = prediction
    else:
        label = "Possible Hemolysis"
        confidence = 1 - prediction

    return f"Prediction: {label}\nConfidence: {confidence:.2f}"

demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.Textbox(),
    title="AI Blood Sample Hemolysis Detector"
)

port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
