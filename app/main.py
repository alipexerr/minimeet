from fastapi import FastAPI

# Create the FastAPI application instance
app = FastAPI(title="MiniMeet")


@app.get("/")
def read_root():
    """Root endpoint welcoming the user."""
    return {"message": "Welcome to MiniMeet!"}


@app.get("/health")
def health_check():
    """Health check endpoint to verify the server is running."""
    return {"status": "ok"}

