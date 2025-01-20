from setuptools import setup

setup(
    name="whisper-gui",
    version="1.0.0",
    packages=["whisper_gui"],
    install_requires=[
        "openai-whisper",
        "torch",
        "torchvision",
        "torchaudio"
    ],
    entry_points={
        "console_scripts": [
            "whisper-gui=whisper_gui.main:main",
        ],
    },
)