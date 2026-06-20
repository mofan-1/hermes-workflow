from setuptools import setup, find_packages

setup(
    name="hermes-workflow",
    version="0.2.0",
    description="飞书 + AI + Obsidian 知识管理工作流 - 一键部署的飞书机器人",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "hermes-workflow=server.main:main",
        ],
    },
)
