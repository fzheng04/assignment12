# main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator  # Use @validator for Pydantic 1.x
from fastapi.exceptions import RequestValidationError
from app.operations import add, subtract, multiply, divide  # Ensure correct import path
import uvicorn
import logging

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User, Calculation
from app.schemas import (
    UserCreate,
    UserRead,
    UserLogin,
    CalculationCreate,
    CalculationRead,
)
from app.calculation_factory import CalculationFactory
from fastapi import Response
from app.security import hash_password, verify_password

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Pydantic model for request data
class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator('a', 'b')  # Correct decorator for Pydantic 1.x
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError('Both a and b must be numbers.')
        return value

# Pydantic model for successful response
class OperationResponse(BaseModel):
    result: float = Field(..., description="The result of the operation")

# Pydantic model for error response
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

# Custom Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extracting error messages
    error_messages = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    logger.error(f"ValidationError on {request.url.path}: {error_messages}")
    return JSONResponse(
        status_code=400,
        content={"error": error_messages},
    )

@app.get("/")
async def read_root(request: Request):
    """
    Serve the index.html template.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def add_route(operation: OperationRequest):
    """
    Add two numbers.
    """
    try:
        result = add(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Add Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def subtract_route(operation: OperationRequest):
    """
    Subtract two numbers.
    """
    try:
        result = subtract(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Subtract Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def multiply_route(operation: OperationRequest):
    """
    Multiply two numbers.
    """
    try:
        result = multiply(operation.a, operation.b)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Multiply Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def divide_route(operation: OperationRequest):
    """
    Divide two numbers.
    """
    try:
        result = divide(operation.a, operation.b)
        return OperationResponse(result=result)
    except ValueError as e:
        logger.error(f"Divide Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Divide Operation Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/users", response_model=UserRead, status_code=201, include_in_schema=False)
@app.post("/users/register", response_model=UserRead, status_code=201)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user with a hashed password."""

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists",
        )

    return new_user


@app.post("/users/login", response_model=UserRead)
def login_user(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    """Verify user login credentials."""

    user = db.query(User).filter_by(
        username=user_data.username
    ).first()

    if user is None or not verify_password(
        user_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    return user


@app.get("/calculations", response_model=list[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).order_by(Calculation.id).all()

@app.get("/calculations/{id}", response_model=CalculationRead)
def read_calculation(id: int, db: Session = Depends(get_db)):
    calculation = db.get(Calculation, id)

    if calculation is None:
        raise HTTPException(
            status_code=404,
            detail="Calculation not found",
        )

    return calculation


@app.post("/calculations", response_model=CalculationRead, status_code=201)
def add_calculation(
    data: CalculationCreate,
    db: Session = Depends(get_db),
):
    calculation = CalculationFactory.create(data)

    db.add(calculation)
    db.commit()
    db.refresh(calculation)

    return calculation

@app.put("/calculations/{id}", response_model=CalculationRead)
def edit_calculation(
    id: int,
    data: CalculationCreate,
    db: Session = Depends(get_db),
):
    calculation = db.get(Calculation, id)

    if calculation is None:
        raise HTTPException(
            status_code=404,
            detail="Calculation not found",
        )

    updated = CalculationFactory.create(data)

    calculation.a = updated.a
    calculation.b = updated.b
    calculation.type = updated.type
    calculation.result = updated.result

    db.commit()
    db.refresh(calculation)

    return calculation

@app.delete("/calculations/{id}", status_code=204)
def delete_calculation(
    id: int,
    db: Session = Depends(get_db),
):
    calculation = db.get(Calculation, id)

    if calculation is None:
        raise HTTPException(
            status_code=404,
            detail="Calculation not found",
        )

    db.delete(calculation)
    db.commit()

    return Response(status_code=204)
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
