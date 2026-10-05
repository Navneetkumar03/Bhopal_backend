from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import objection, auth, activity
from middleware.auth_middleware import AuthMiddleware

app = FastAPI(
    title="Bhopal Backend API",
    description="Fast API for Bhopal Project",
    version="0.1.0",
)

# ---------------------------------------------------------
# Middlewares
# Auth is added FIRST, CORS is added AFTER it.
# (The last one added runs first, so CORS wraps everything,
#  including 401 errors, and your frontend won't see fake CORS errors.)
# ---------------------------------------------------------
app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Routers  (Registers route on a "sub-app" (router)
  # Endpoint	Needs
    # /auth/login	username and password
    # /auth/force_logout	username and password
    # /auth/refresh	refresh token in the body
    # /auth/logout	access token in the header
    # /objection/history	access token in the header
# ---------------------------------------------------------
app.include_router(auth.router, tags=["Auth"])
app.include_router(objection.router, tags=["Objection"])
app.include_router(activity.router, tags=["Activity"])

# ---------------------------------------------------------
# Test URLs  (Registers route directly on the FastAPI app)
# ---------------------------------------------------------
@app.get("/", tags=["Testing"])
def root():
    return {"message": "Hello From Bhopal Backend API"}


