import os
import gradio as gr
import numpy as np
import tensorflow as tf
from PIL import Image

print("Starting app...")

model = None

# Load model safely
try:
    print("Loading model...")
    model = tf.keras.models.load_model("hemolysis_model.h5", compile=False)
    print("Model loaded successfully")
except Exception as e:
    print("Model failed to load:", e)


def predict(img):
    if model is None:
        return "Model failed to load on server."

    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
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

# Render requires this port
port = int(os.environ.get("PORT", 10000))

print("Launching Gradio on port:", port)

demo.launch(
    server_name="0.0.0.0",
    server_port=port
)
