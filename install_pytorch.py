"""
Smart PyTorch installer that detects CUDA version and installs the correct build
"""
import subprocess
import sys
import re
import platform

def run_command(command, check=True):
    """Run a command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.returncode

def detect_cuda_version():
    """Detect installed CUDA version"""
    print("Detecting CUDA version...")
    
    # Try nvidia-smi first (most reliable)
    output, code = run_command("nvidia-smi", check=False)
    if code == 0:
        # Extract CUDA version from nvidia-smi output
        match = re.search(r"CUDA Version:\s*(\d+\.\d+)", output)
        if match:
            version = match.group(1)
            print(f"✓ Detected CUDA {version} via nvidia-smi")
            return version
    
    # Try nvcc (CUDA compiler)
    output, code = run_command("nvcc --version", check=False)
    if code == 0:
        match = re.search(r"release (\d+\.\d+)", output)
        if match:
            version = match.group(1)
            print(f"✓ Detected CUDA {version} via nvcc")
            return version
    
    # Check CUDA_PATH environment variable (Windows)
    if platform.system() == "Windows":
        output, code = run_command("echo %CUDA_PATH%", check=False)
        if output and "CUDA" in output:
            match = re.search(r"v(\d+\.\d+)", output)
            if match:
                version = match.group(1)
                print(f"✓ Detected CUDA {version} via CUDA_PATH")
                return version
    
    print("✗ No CUDA installation detected")
    return None

def get_pytorch_cuda_version(cuda_version):
    """Map detected CUDA version to PyTorch CUDA version"""
    if not cuda_version:
        return None
    
    major, minor = map(int, cuda_version.split('.'))
    
    # PyTorch CUDA version mapping (as of February 2025)
    # PyTorch supports: cu118, cu121, cu124, cu126, cu128, cu129, cu130
    # Reference: https://pytorch.org/ and https://download.pytorch.org/whl/
    
    if major >= 13:
        # CUDA 13.x uses cu130 (CUDA 13.0+ binaries)
        print(f"✓ CUDA {cuda_version} detected, using PyTorch CUDA 13.0 binaries")
        return "cu130"
    elif major == 12:
        # CUDA 12.x mapping
        if minor >= 9:
            return "cu129"  # CUDA 12.9+
        elif minor >= 8:
            return "cu128"  # CUDA 12.8
        elif minor >= 6:
            return "cu126"  # CUDA 12.6
        elif minor >= 4:
            return "cu124"  # CUDA 12.4
        elif minor >= 1:
            return "cu121"  # CUDA 12.1-12.3
        else:
            return "cu118"  # CUDA 12.0 uses 11.8 binaries
    elif major == 11:
        if minor >= 8:
            return "cu118"  # CUDA 11.8+
        else:
            print(f"⚠ CUDA {cuda_version} is too old (requires 11.8+)")
            return None
    else:
        print(f"⚠ CUDA {cuda_version} not supported, defaulting to latest")
        return "cu130"  # Default to latest

def install_pytorch(cuda_version_code):
    """Install PyTorch with appropriate CUDA support"""
    if cuda_version_code:
        print(f"\nInstalling PyTorch with CUDA {cuda_version_code} support...")
        url = f"https://download.pytorch.org/whl/{cuda_version_code}"
        command = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url {url}"
    else:
        print("\nInstalling CPU-only PyTorch...")
        command = f"{sys.executable} -m pip install torch torchvision torchaudio"
    
    print(f"Running: {command}")
    output, code = run_command(command)
    
    if code != 0:
        print("✗ Installation failed!")
        return False
    
    print("✓ PyTorch installed successfully")
    return True

def verify_pytorch():
    """Verify PyTorch installation and CUDA availability"""
    print("\nVerifying PyTorch installation...")
    
    verify_script = """
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version (PyTorch): {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'GPU count: {torch.cuda.device_count()}')
"""
    
    output, code = run_command(f'{sys.executable} -c "{verify_script}"')
    if code == 0:
        print(output)
        return True
    else:
        print("✗ PyTorch verification failed")
        return False

def main():
    print("=" * 60)
    print("Smart PyTorch Installer")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"Platform: {platform.system()} {platform.machine()}")
    print("=" * 60)
    
    # Detect CUDA
    cuda_version = detect_cuda_version()
    
    # Get appropriate PyTorch CUDA version
    pytorch_cuda = get_pytorch_cuda_version(cuda_version)
    
    if cuda_version and not pytorch_cuda:
        print("\n⚠ Your CUDA version is not compatible with PyTorch")
        print("Installing CPU version instead...")
        pytorch_cuda = None
    
    # Install PyTorch
    success = install_pytorch(pytorch_cuda)
    
    if not success:
        print("\nAttempting CPU fallback installation...")
        success = install_pytorch(None)
    
    if success:
        # Verify installation
        verify_pytorch()
        print("\n" + "=" * 60)
        print("✓ PyTorch installation complete!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ PyTorch installation failed!")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
