from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import markdown2
from openai import OpenAI
import base64
import cv2
import mss
import numpy as np
import keyboard
from PIL import Image
import io
import time
import os

api_key = os.getenv("OPENAI_API_KEY")
# assert api_key, "Please set the OPENAI_API_KEY environment variable."


class ScreenCapture:
    def __init__(self):
        self.monitor = None  # Default to full screen

    def adjust_box(self):
        """Allows the user to select a bounding box from the current screenshot."""
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])  # Capture primary screen
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Convert to BGR
            img = cv2.resize(img, (1920, 1080))
            # Create a resizable selection window
            r = cv2.selectROI("Select Region", img, showCrosshair=True)
            cv2.destroyAllWindows()
            if r[2] > 0 and r[3] > 0:
                self.monitor = {
                    "top": int(r[1]),
                    "left": int(r[0]),
                    "width": int(r[2]),
                    "height": int(r[3]),
                }
                print(f"Selected Region: {self.monitor}")
            else:
                print("No region selected.")

    def capture(self):
        """Captures a screenshot using the defined bounding box or full screen."""
        with mss.mss() as sct:
            monitor = (
                self.monitor if self.monitor else sct.monitors[1]
            )  # Use selected box or full screen
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)  # Convert for OpenAI API

            return img

    def get_image_base64(self):
        """Returns the captured image in PNG format (bytes) for API requests."""
        img = self.capture()
        pil_img = Image.fromarray(img)  # Convert to PIL
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format="PNG")
        return base64.b64encode(img_bytes.getvalue()).decode("utf-8")

    def save_screenshot(self):
        """Captures a screenshot and saves it to the current directory with a timestamp."""
        img = self.capture()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        Image.fromarray(img).save(filename)
        print(f"Screenshot saved: {filename}")


class ProblemSolver:
    def __init__(self, api_key, dev_prompt):
        self.client = OpenAI(api_key=api_key)
        self.dev_prompt = dev_prompt

    def ask(self, image) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "developer", "content": self.dev_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                        },
                    ],
                },
            ],
        )
        if not response.choices[0].message.content:
            return "I'm sorry, I don't know the answer to that question."
        return response.choices[0].message.content


sc = ScreenCapture()
ps = ProblemSolver(
    api_key,
    "Solve the following chemistry problem. The problem is uploaded as image. If there are multiple problems in the image, please solve the first one only. Please use concise language.",
)
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to be more restrictive if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve React static files
frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(frontend_path, "assets")),
    name="assets",
)


@app.get("/answer", response_class=JSONResponse)
async def solve():
    print("Start solving")
    image = sc.get_image_base64()
    content = ps.ask(image)
    return JSONResponse(content={"image": image, "content": content})


# Serve the index.html for all other routes (SPA fallback)
@app.get("/")
@app.get("/{full_path:path}")
async def serve_react(full_path: str = ""):
    return FileResponse(os.path.join(frontend_path, "index.html"))


if __name__ == "__main__":
    # sc.adjust_box()
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
