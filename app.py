import gradio as gr
import tensorflow as tf
import numpy as np
from PIL import Image
import os

model = tf.keras.models.load_model("hemolysis_model.h5")

def predict(img):
    img = img.resize((224,224))
    img_array = np.array(img)/255
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)[0][0]

    if prediction > 0.5:
        label = "Normal Sample"
        confidence = prediction
    else:
        label = "Possible Hemolysis"
        confidence = 1-prediction

    return f"Prediction: {label}\nConfidence: {confidence:.2f}"

demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.Textbox(lines=8),
    title="AI Blood Sample Hemolysis Detector"
)

port = int(os.environ.get("PORT", 7860))

demo.launch(server_name="0.0.0.0", server_port=port)
