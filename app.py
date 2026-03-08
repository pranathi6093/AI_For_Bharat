import os
import numpy as np
import gradio as gr
import tensorflow as tf
from tensorflow.keras.layers import InputLayer

print("Starting app...")

# ── THE FIX ─────────────────────────────────────────────────────────────────
# Your model was saved with old Keras which used 'batch_shape'.
# TF 2.11+ renamed it to 'batch_input_shape' and crashes on load.
# This shim silently renames the key during deserialization.
class FixedInputLayer(InputLayer):
    def __init__(self, **kwargs):
        if "batch_shape" in kwargs:
            kwargs["batch_input_shape"] = kwargs.pop("batch_shape")
        super().__init__(**kwargs)

print("Loading model...")
try:
    model = tf.keras.models.load_model(
        "hemolysis_model.h5",
        custom_objects={"InputLayer": FixedInputLayer},
        compile=False,
    )
    print("Model loaded successfully.")
except Exception as e:
    print("FATAL: Model failed to load:", e)
    raise  # Re-raise so you see the real error in Render logs

def predict(img):
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)[0][0]
    if prediction > 0.5:
        label = "Normal Sample"
        confidence = float(prediction)
    else:
        label = "Possible Hemolysis"
        confidence = float(1 - prediction)
    return f"Prediction: {label}\nConfidence: {confidence:.2f}"

demo = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="pil"),
    outputs=gr.Textbox(lines=4),
    title="AI Blood Sample Hemolysis Detector",
)

port = int(os.environ.get("PORT", 7860))
print(f"Launching on 0.0.0.0:{port}")
demo.launch(server_name="0.0.0.0", server_port=port)
