from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseSettings
from routes import base_routes
from core.auth.controller.authcontroller import auth_routes
from core.user.controller.usercontroller import user_routes
from core.business.controller.businesscontroller import business_routes
from core.notification.controller.notificationcontroller import notification_routes
from dotenv import load_dotenv
import os

# Initialize FastAPI app
app = FastAPI(
    title="LambdarCore API",
    version="1.0",
    description="""**LambdarCore API** An ML focused app infrastructure deployed with python.
    
    Default Endpoints
    
    "Authentication",
    "File and Document Management",
    "Message and Task Queuing",
    "Notifications",
    """,
    contact={
        "name": "API Support",
        "url": "http://support@lambdarcorp.com",
        "email": "mail@lambdarcorp.com",
    },
    license_info={
        "name": "MIT",
    },
)
from utilities.dbconfig import Base, engine

# print("Creating tables...")
# Base.metadata.create_all(bind=engine)
# print("Tables created successfully.")

# Add middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the routes
app.include_router(base_routes, prefix="/api/v1", tags=["Base Routes"])
app.include_router(auth_routes, prefix="/api/v1/auth", tags=["Auth Routes"])
app.include_router(user_routes, prefix="/api/v1/user", tags=["User Routes"])
app.include_router(business_routes, prefix="/api/v1/business", tags=["Business Routes"])
app.include_router(notification_routes, prefix="/api/v1/notification", tags=["Notification Routes"])


# Load environment variables
load_dotenv()

# AuthJWT Configuration
class Settings(BaseSettings):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY")


@AuthJWT.load_config
def get_config():
    return Settings()

# Run the app (if using `uvicorn`)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
