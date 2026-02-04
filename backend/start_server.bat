@echo off
echo Starting FastAPI MongoDB Authentication Server...
echo.
echo Make sure MongoDB is running before starting the server.
echo.
echo The server will be available at: http://localhost:8000
echo API Documentation will be available at: http://localhost:8000/docs
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
