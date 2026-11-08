from fastapi import FastAPI,Depends,HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal, init_db, get_db
from backend.model import Patient
from backend.schemas import PatientCreate, PatientResponse
from backend.ai_service import generate_health_remarks
app = FastAPI()

init_db()

@app.post("/patients", response_model=PatientResponse)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db)
):

    # STEP 1: Check for duplicate patient
    existing_patient = db.query(Patient).filter(
        Patient.full_name == patient.full_name,
        Patient.dob == patient.dob,
        Patient.email == patient.email
    ).first()

    # Do not create a second record with the same patient identity.
    if existing_patient:
        raise HTTPException(
            status_code=409,
            detail="A patient with the same full name, date of birth, and email already exists."
        )

    # STEP 2: Generate AI remarks
    try:
        remarks = generate_health_remarks(
            glucose=patient.glucose,
            haemoglobin=patient.haemoglobin,
            cholesterol=patient.cholesterol
        )

        # STEP 3: Create new patient
        new_patient = Patient(
            full_name=patient.full_name,
            dob=patient.dob,
            email=patient.email,
            glucose=patient.glucose,
            haemoglobin=patient.haemoglobin,
            cholesterol=patient.cholesterol,
            remarks=remarks
        )

        # STEP 4: Save to database
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        return new_patient

    except RuntimeError as error:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create patient record."
        )


@app.get("/patients",response_model=list[PatientResponse])
def get_all_patients(db:Session = Depends(get_db)):
    patients = db.query(Patient).all()
    return patients

@app.put("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_data: PatientCreate,
    db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id
    ).first()

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    try:
        # Generate fresh AI remarks using updated blood values
        remarks = generate_health_remarks(
            glucose=patient_data.glucose,
            haemoglobin=patient_data.haemoglobin,
            cholesterol=patient_data.cholesterol
        )

        # Update patient details
        patient.full_name = patient_data.full_name
        patient.dob = patient_data.dob
        patient.email = patient_data.email
        patient.glucose = patient_data.glucose
        patient.haemoglobin = patient_data.haemoglobin
        patient.cholesterol = patient_data.cholesterol
        patient.remarks = remarks

        db.commit()
        db.refresh(patient)

        return patient

    except RuntimeError as error:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail=str(error)
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to update patient record."
        )


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id:int,db:Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404,detail="Patient not found")
    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}