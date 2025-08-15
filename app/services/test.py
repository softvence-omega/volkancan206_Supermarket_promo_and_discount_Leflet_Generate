# test_device.py
import torch

print("PyTorch version:", torch.__version__)

# Check if CUDA is available
if torch.cuda.is_available():
    print("CUDA is available!")
    print("Device count:", torch.cuda.device_count())
    print("Current device:", torch.cuda.current_device())
    print("Device name:", torch.cuda.get_device_name(torch.cuda.current_device()))
else:
    print("CUDA is NOT available. Running on CPU only.")

# Optional: Check Torch can allocate a small tensor on GPU
try:
    x = torch.tensor([1.0, 2.0, 3.0]).to("cuda")
    print("Tensor successfully allocated on GPU:", x)
except Exception as e:
    print("GPU test failed:", e)
