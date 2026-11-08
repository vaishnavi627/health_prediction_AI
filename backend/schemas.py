
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    field_validator
)

from datetime import date, datetime
import re


class PatientCreate(BaseModel):

    full_name: str
    dob: date
    email: EmailStr

    glucose: float = Field(gt=0)
    haemoglobin: float = Field(gt=0)
    cholesterol: float = Field(gt=0)

    # Validate date format and calendar date
    @field_validator("dob", mode="before")
    @classmethod
    def validate_dob_format(cls, value):

        # If the value is already a date object,
        # return it without converting again.
        if isinstance(value, date):
            return value

        # Accept multiple date formats
        formats = [
            ("%d/%m/%Y", r"\d{2}/\d{2}/\d{4}"),
            ("%d.%m.%Y", r"\d{2}\.\d{2}\.\d{4}")
        ]

        for fmt, pattern in formats:

            try:
                return datetime.strptime(
                    value, fmt
                ).date()

            except ValueError:

                # Check whether the input follows
                # the expected date format structure.
                if isinstance(value, str) and re.fullmatch(
                    pattern, value
                ):
                    raise ValueError(
                        "Invalid calendar date. Please enter a real date."
                    )

            except TypeError:
                break

        raise ValueError(
            "DOB must be in DD/MM/YYYY or DD.MM.YYYY format."
        )

    # Validate future date
    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value):

        if value > date.today():
            raise ValueError(
                "Date of birth cannot be in the future."
            )

        return value


class PatientResponse(BaseModel):

    # Allows Pydantic to read values from SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    dob: date
    email: str
    glucose: float
    haemoglobin: float
    cholesterol: float
    remarks: str | None = None
