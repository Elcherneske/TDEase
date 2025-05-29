# 🧪 TDEase - Top-Down Proteomics Tools

## Language
[English](README.md) | [中文](README_zh.md)

## ✨ Introduction
✨ TDEase is an automated data processing and interactive visualization toolkit designed specifically for Top-Down proteomics research.

It helps laboratories quickly build the data processing and visualization components of a Top-Down proteomics workflow.

It consists of two core modules:
- 🛠️ **TDpipe**: Automated data processing pipeline
- 📊 **TDvis**: Interactive data visualization platform

## 🌟 Key Features

1. **One-Click Deployment** 🚀  
   Both modules provide ready-to-use exe packages, requiring no complex configuration.
2. **Thoughtful UI Design**:
    - TDpipe uses PyQt to create a sophisticated workflow control interface, allowing platform administrators high flexibility.
    - TDvis uses Streamlit to provide a minimalist, almost parameter-free interface, making it easy for users to quickly get started with data viewing.
3. **Intranet Web Deployment**:
    - The visualization module can be deployed on an intranet using Python's [http.server](https://docs.python.org/3.13/library/http.server.html), allowing collaborators to access results remotely without transferring large mass spectrometry files.
    - ⚠️ Note: Due to HTTP's plaintext nature, public internet deployment is not recommended.
    - For external collaborators, you can simply send the result files, and users can view them locally with TDvis.

---

## Quick Start

### 📥 Installation
Download the release package, unzip it, and double-click the corresponding exe to run:
- `TDvis.exe`: Standalone version (no user management)
- `TDvis_web.exe`: Web version with user authentication

🌐 Access:  
`http://{your_ip}:8501`

TDvis provides two parallel exe entry points:
**TDvis.exe:**  
Run the local version without user management (collaborators can view your data on the intranet, but files must be selected manually; visitors cannot choose files).

**TDvis_web.exe:**  
Provides a version with user management. After configuring the user management database, you can deploy the test platform.

Both versions map the program to port 8501. Users can access your shared data via your IP and port:
