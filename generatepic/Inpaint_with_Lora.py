from diffusers import StableDiffusionXLInpaintPipeline
from PIL import Image
import torch
import os
import numpy as np
import matplotlib.pyplot as plt

def inpaint_image(init_image_path, mask_image_path, prompt, steps):
    # Set fixed step image path
    step_image_path = "generatepic/step.png"
    os.makedirs("generatepic", exist_ok=True)

    pipe = StableDiffusionXLInpaintPipeline.from_single_file(
        "dreamshaperXL_lightningInpaint.safetensors", #Download from github
        torch_dtype=torch.float16,
        use_safetensors=True,
    ).to("cuda")

    pipe.load_lora_weights(
        "./clothes_2.safetensors" 
    )
    pipe.fuse_lora()

    init_image = Image.open(init_image_path).convert("RGB")
    mask_image = Image.open(mask_image_path).convert("L")

    def round_down_to_multiple(x, base=8):
        return x - (x % base)

    width, height = init_image.size
    width = round_down_to_multiple(width)
    height = round_down_to_multiple(height)
    init_image = init_image.resize((width, height), Image.LANCZOS)
    mask_image = mask_image.resize((width, height), Image.LANCZOS)

    # Setup matplotlib for live display
    plt.ion()
    fig, ax = plt.subplots()
    image_display = None

    def save_and_display(latents):
        latents = 1 / 0.18215 * latents
        with torch.no_grad():
            image = pipe.vae.decode(latents).sample
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).numpy()[0]
        image = (image * 255).astype("uint8")
        img_pil = Image.fromarray(image)
        img_pil.save(step_image_path)  # overwrite

        # Show in matplotlib
        nonlocal image_display
        if image_display is None:
            image_display = ax.imshow(np.asarray(img_pil))
            plt.axis("off")
        else:
            image_display.set_data(np.asarray(img_pil))
        fig.canvas.draw()
        fig.canvas.flush_events()

    def callback_fn(step, timestep, latents):
        print(f"Step {step}, Timestep {timestep}")
        save_and_display(latents)

    # Run the pipe with callback
    image = pipe(
        prompt=prompt,
        image=init_image,
        mask_image=mask_image,
        strength=0.75,
        guidance_scale=8.0,
        num_inference_steps=steps,
        width=width,
        height=height,
        callback=callback_fn,
        callback_steps=1
    ).images[0]

    image.save("generatepic/output_image.png")
    plt.ioff()
    plt.show()