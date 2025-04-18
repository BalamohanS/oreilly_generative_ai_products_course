from fastapi import FastAPI
import uvicorn
from routers import knowledge_base, general_advice, sql_query, recommend_image, recommend_tour
# from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# (Optional) Set up middleware if needed
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Include routers
app.include_router(knowledge_base.router)
app.include_router(general_advice.router)
app.include_router(sql_query.router)
app.include_router(recommend_image.router)
app.include_router(recommend_tour.router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the API. Refer to the documentation for available endpoints."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)