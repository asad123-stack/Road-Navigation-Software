from app import app


if __name__ == "__main__":
    print("[demo_mode] launching backend demo server")
    app.run(host="0.0.0.0", port=5000, debug=False)
