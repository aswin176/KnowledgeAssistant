import pandas as pd

from app.etl.csv_excel import ExcelETLPipeline


def test_excel_pipeline_maps_person_columns_to_graph_payload():
    pipeline = ExcelETLPipeline(graph_repo=None)  # type: ignore[arg-type]
    df = pd.DataFrame(
        [
            {
                "Roll Number": "2024001",
                "Name": "Asha Verma",
                "Class": "BCA 2024",
                "Father Name": "Ravi Verma",
                "DOB": "2002-05-11",
                "Address": "123 Main Street",
                "Hometown": "Jaipur",
                "Mobile": "9876543210",
                "Email": "asha@example.com",
                "7th Semester Employment": "TCS",
                "10th Semester Employment": "Infosys",
                "Current employment": "Google",
                "Relationship Status": "Married",
                "Marraige Date": "2024-07-01",
                "Kids": 1,
                "Spouse Roll Number ( if present in same data)": "2024002",
                "Spouse name": "Rahul Verma",
                "Linkedin URL": "https://linkedin.com/in/asha",
                "Current City": "Bengaluru",
            }
        ]
    )

    records = pipeline._dataframe_to_records(df)

    assert len(records) == 1
    record = records[0]
    assert record["roll_number"] == "2024001"
    assert record["name"] == "Asha Verma"
    assert record["dob"] == "2002-05-11"
    assert record["mobile"] == "9876543210"
    assert record["email"] == "asha@example.com"
    assert record["relationship_status"] == "Married"
    assert record["kids"] == 1
    assert "class" not in record
    assert "father_name" not in record
    assert "address" not in record
    assert "hometown" not in record
    assert "current_employment" not in record
    assert "marriage_date" not in record
    assert "spouse_roll_number" not in record
    assert "spouse_name" not in record
    assert "linkedin_url" not in record
    assert "current_city" not in record
    assert any(rel["type"] == "BELONGS_TO_CLASS" for rel in record["relationships"])
    assert any(rel["type"] == "WORKED_AT" for rel in record["relationships"])
    assert any(rel["type"] == "WORKS_AT" for rel in record["relationships"])
    assert any(rel["type"] == "MARRIED_TO" for rel in record["relationships"])
    marriage_rel = next(rel for rel in record["relationships"] if rel["type"] == "MARRIED_TO")
    assert marriage_rel["target_properties"]["roll_number"] == "2024002"
    assert marriage_rel["properties"]["marriage_date"] == "2024-07-01"
