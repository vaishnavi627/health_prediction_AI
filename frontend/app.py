
import streamlit as st
import requests
from datetime import datetime

# ==========================================
# CONFIGURATION
# ==========================================

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Health Prediction Application",
    page_icon="🏥",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f4fbfc 0%, #eef7f3 100%);
        color: #20343b;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        color: #176b78;
        letter-spacing: -0.02em;
    }

    h2, h3 {
        color: #245c63;
    }

    [data-testid="stForm"],
    [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.78);
        border: 1px solid #d5e9e5;
        border-radius: 14px;
        box-shadow: 0 4px 16px rgba(34, 92, 99, 0.06);
    }

    [data-testid="stForm"] {
        padding: 1rem 1.25rem 0.5rem;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input {
        background-color: #fbffff;
        border-color: #c8e1de;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus {
        border-color: #4aa6a1;
        box-shadow: 0 0 0 1px #4aa6a1;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background-color: #3d9b96;
        color: white;
        border: 0;
        border-radius: 8px;
        font-weight: 600;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background-color: #277d7b;
        color: white;
        border: 0;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #d5e9e5;
        border-radius: 10px;
        overflow: hidden;
    }

    hr {
        border-color: #d5e9e5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# SESSION STATE
# ==========================================

if "success_message" not in st.session_state:
    st.session_state.success_message = None

if "new_remarks" not in st.session_state:
    st.session_state.new_remarks = None


# ==========================================
# DISPLAY SUCCESS MESSAGE
# ==========================================

if st.session_state.success_message:
    st.toast(
        st.session_state.success_message,
        icon="✅"
    )
    st.session_state.success_message = None


# ==========================================
# APPLICATION TITLE
# ==========================================

st.title("🏥 Health Prediction Application")

st.write(
    "Manage patient records and generate "
    "AI-powered health remarks using blood test results."
)


# ==========================================
# ADD PATIENT
# ==========================================

st.header("➕ Add New Patient")

with st.form("patient_form"):

    full_name = st.text_input("Full Name")

    dob = st.text_input(
        "Date of Birth",
        placeholder="DD/MM/YYYY"
    )

    email = st.text_input("Email")

    col1, col2, col3 = st.columns(3)

    with col1:
        glucose = st.number_input(
            "Glucose",
            min_value=0.1,
            value=100.0
        )

    with col2:
        haemoglobin = st.number_input(
            "Haemoglobin",
            min_value=0.1,
            value=13.5
        )

    with col3:
        cholesterol = st.number_input(
            "Cholesterol",
            min_value=0.1,
            value=180.0
        )

    submitted = st.form_submit_button("Add Patient")

    if submitted:

        patient_data = {
            "full_name": full_name,
            "dob": dob,
            "email": email,
            "glucose": glucose,
            "haemoglobin": haemoglobin,
            "cholesterol": cholesterol
        }

        try:
            response = requests.post(
                f"{API_URL}/patients",
                json=patient_data,
                timeout=60
            )

            if response.status_code == 200:

                result = response.json()

                st.session_state.success_message = (
                    "Patient added successfully!"
                )

                st.session_state.new_remarks = result.get(
                    "remarks", ""
                )

                st.rerun()

            else:
                st.error(
                    f"Unable to add patient: {response.text}"
                )

        except requests.exceptions.RequestException as error:
            st.error(f"Backend connection error: {error}")


# ==========================================
# DISPLAY AI REMARKS FOR NEW PATIENT
# ==========================================

if st.session_state.new_remarks:

    st.divider()

    st.subheader("🤖 AI-Generated Health Remarks")

    st.markdown(st.session_state.new_remarks)

    if st.button("Close AI Remarks"):
        st.session_state.new_remarks = None
        st.rerun()


# ==========================================
# GET ALL PATIENTS
# ==========================================

def get_patients():

    try:
        response = requests.get(
            f"{API_URL}/patients",
            timeout=30
        )

        if response.status_code == 200:
            return response.json()

        st.error(
            f"Unable to fetch patients: {response.text}"
        )
        return None

    except requests.exceptions.RequestException as error:
        st.error(f"Backend connection error: {error}")
        return None


# ==========================================
# VIEW PATIENT RECORDS
# ==========================================

st.divider()

st.header("📋 Patient Records")

patients = get_patients()

if patients is not None:

    if patients:

        st.success(
            f"Total patient records: {len(patients)}"
        )

        # Format patient details for display
        display_patients = []

        for patient in patients:

            formatted_dob = datetime.strptime(
                patient["dob"],
                "%Y-%m-%d"
            ).strftime("%d/%m/%Y")

            display_patients.append({
                "ID": patient["id"],
                "Full Name": patient["full_name"],
                "DOB": formatted_dob,
                "Email": patient["email"],
                "Glucose": patient["glucose"],
                "Haemoglobin": patient["haemoglobin"],
                "Cholesterol": patient["cholesterol"]
            })

        # Display patient table
        st.dataframe(
            display_patients,
            use_container_width=True,
            hide_index=True
        )

        # Display previously saved AI remarks
        st.subheader("🤖 Patient Health Remarks")

        for patient in patients:

            with st.expander(
                f"{patient['id']} - {patient['full_name']} - View AI Remarks"
            ):

                st.markdown(
                    patient.get("remarks")
                    or "No AI remarks available."
                )

    else:
        st.info("No patient records found.")


# ==========================================
# EDIT PATIENT
# ==========================================

st.divider()

st.header("✏️ Edit Patient")

if patients:

    patient_options = {
        f"{patient['id']} - {patient['full_name']}": patient
        for patient in patients
    }

    selected_patient_name = st.selectbox(
        "Select a patient to edit",
        options=list(patient_options.keys()),
        key="edit_patient_select"
    )

    selected_patient = patient_options[selected_patient_name]

    # Convert API date into DD/MM/YYYY
    edit_dob_display = datetime.strptime(
        selected_patient["dob"],
        "%Y-%m-%d"
    ).strftime("%d/%m/%Y")

    with st.form("edit_patient_form"):

        edit_name = st.text_input(
            "Full Name",
            value=selected_patient["full_name"]
        )

        edit_dob = st.text_input(
            "Date of Birth",
            value=edit_dob_display
        )

        edit_email = st.text_input(
            "Email",
            value=selected_patient["email"]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            edit_glucose = st.number_input(
                "Glucose",
                min_value=0.1,
                value=float(selected_patient["glucose"])
            )

        with col2:
            edit_haemoglobin = st.number_input(
                "Haemoglobin",
                min_value=0.1,
                value=float(selected_patient["haemoglobin"])
            )

        with col3:
            edit_cholesterol = st.number_input(
                "Cholesterol",
                min_value=0.1,
                value=float(selected_patient["cholesterol"])
            )

        update_button = st.form_submit_button(
            "Update Patient"
        )

        if update_button:

            updated_data = {
                "full_name": edit_name,
                "dob": edit_dob,
                "email": edit_email,
                "glucose": edit_glucose,
                "haemoglobin": edit_haemoglobin,
                "cholesterol": edit_cholesterol
            }

            try:
                update_response = requests.put(
                    f"{API_URL}/patients/{selected_patient['id']}",
                    json=updated_data,
                    timeout=60
                )

                if update_response.status_code == 200:

                    st.session_state.success_message = (
                        "Patient updated successfully!"
                    )

                    st.rerun()

                else:
                    st.error(
                        f"Update failed: {update_response.text}"
                    )

            except requests.exceptions.RequestException as error:
                st.error(
                    f"Backend connection error: {error}"
                )

else:
    st.info("Add a patient before editing records.")


# ==========================================
# DELETE PATIENT
# ==========================================

st.divider()

st.header("🗑️ Delete Patient")

if patients:

    delete_options = {
        f"{patient['id']} - {patient['full_name']}": patient["id"]
        for patient in patients
    }

    selected_delete_name = st.selectbox(
        "Select a patient to delete",
        options=list(delete_options.keys()),
        key="delete_patient_select"
    )

    selected_delete_id = delete_options[selected_delete_name]

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this patient record.",
        key="confirm_delete"
    )

    if st.button("Delete Patient"):

        if not confirm_delete:

            st.warning(
                "Please confirm before deleting the patient."
            )

        else:

            try:
                delete_response = requests.delete(
                    f"{API_URL}/patients/{selected_delete_id}",
                    timeout=30
                )

                if delete_response.status_code == 200:

                    st.session_state.success_message = (
                        "Patient deleted successfully!"
                    )

                    st.rerun()

                else:
                    st.error(
                        f"Delete failed: {delete_response.text}"
                    )

            except requests.exceptions.RequestException as error:
                st.error(
                    f"Backend connection error: {error}"
                )

else:
    st.info("No patient records available to delete.")
