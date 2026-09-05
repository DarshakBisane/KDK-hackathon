import io
import time
import httpx


def create_sample_resume_pdf() -> bytes:
    """
    Creates a valid in-memory text-based PDF resume for end-to-end testing.
    """
    pdf_content = (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        b"4 0 obj << /Length 420 >> stream\n"
        b"BT /F1 12 Tf 50 720 Td (Darshak Bisane - Machine Learning Engineer Aspirant) Tj ET\n"
        b"BT /F1 10 Tf 50 700 Td (Education: B.Tech in Computer Engineering, GPA: 8.9/10) Tj ET\n"
        b"BT /F1 10 Tf 50 670 Td (Technical Skills: Python, SQL, Pandas, NumPy, Scikit-learn, Git, Linux, REST API) Tj ET\n"
        b"BT /F1 10 Tf 50 640 Td (Projects: Customer Churn Prediction using Pandas and Scikit-learn) Tj ET\n"
        b"BT /F1 10 Tf 50 620 Td (Built exploratory data analysis notebooks with NumPy and SQL queries) Tj ET\n"
        b"BT /F1 10 Tf 50 590 Td (Certifications: Python for Data Science and Machine Learning) Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        b"xref\n"
        b"0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000244 00000 n \n"
        b"0000000717 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\n"
        b"startxref\n"
        b"786\n"
        b"%%EOF\n"
    )
    return pdf_content


def test_complete_e2e_pipeline():
    base_url = "http://127.0.0.1:8000/api"
    print("\n--- STARTING COMPLETE E2E FLOW TEST ---")

    with httpx.Client(base_url=base_url, timeout=40.0) as client:
        # 1. Health check
        h_res = client.get("/health")
        assert h_res.status_code == 200, f"Health check failed: {h_res.text}"
        print("[OK] 1. Backend health check passed.")

        # 2. Register
        user_email = f"darshak_e2e_{int(time.time())}@kdk.edu"
        reg_res = client.post("/auth/register", json={
            "name": "Darshak Bisane",
            "email": user_email,
            "password": "Password@123",
            "education": "B.Tech Computer Engineering"
        })
        assert reg_res.status_code == 201, f"Register failed: {reg_res.text}"
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"[OK] 2. Registered new student: {user_email}")

        # 3. Get profile
        prof_res = client.get("/users/me", headers=headers)
        assert prof_res.status_code == 200
        assert prof_res.json()["name"] == "Darshak Bisane"
        print("[OK] 3. Retrieved student profile.")

        # 4. Careers list & choose "ML Engineer"
        careers_res = client.get("/careers")
        assert careers_res.status_code == 200
        careers = careers_res.json()
        assert len(careers) >= 10
        ml_career = next(c for c in careers if c["name"] == "ML Engineer")
        print(f"[OK] 4. Retrieved {len(careers)} seeded careers. ML Engineer ID={ml_career['id']}.")

        select_res = client.post("/users/target-career", json={"career_id": ml_career["id"]}, headers=headers)
        assert select_res.status_code == 200
        assert select_res.json()["target_career_name"] == "ML Engineer"
        print("[OK] 5. Selected target career: ML Engineer.")

        # 5. Upload resume PDF and run Gemini AI analysis
        pdf_bytes = create_sample_resume_pdf()
        files = {"file": ("Darshak_Resume.pdf", pdf_bytes, "application/pdf")}
        
        print("-> Uploading PDF and running Gemini AI structured skill extraction...")
        upload_res = client.post("/resumes/analyze", files=files, headers=headers)
        assert upload_res.status_code == 200, f"Resume analysis failed: {upload_res.text}"
        upload_data = upload_res.json()
        print(f"[OK] 6. Gemini extracted skills: {upload_data['extracted_skills']}")
        print(f"     Match Score: {upload_data['readiness_score']}%")

        # 6. Verify deterministic skill gap
        gap_res = client.get("/skills/gap", headers=headers)
        assert gap_res.status_code == 200
        gap = gap_res.json()
        print(f"[OK] 7. Deterministic Skill Gap: {gap['readiness_score']}% readiness")
        print(f"     Matched Skills ({len(gap['matched_skills'])}): {gap['matched_skills']}")
        print(f"     Missing Skills ({len(gap['missing_skills'])}): {[m['name'] for m in gap['missing_skills']]}")

        # Verify mathematical correctness: score == round(matched / total * 100, 1)
        expected_score = round((len(gap['matched_skills']) / gap['total_required_skills']) * 100, 1)
        assert gap['readiness_score'] == expected_score, f"Expected {expected_score}, got {gap['readiness_score']}"

        # 7. Verify student dashboard
        dash_res = client.get("/dashboard", headers=headers)
        assert dash_res.status_code == 200
        dash = dash_res.json()
        assert dash["target_career_name"] == "ML Engineer"
        assert dash["strong_skills_count"] == len(gap['matched_skills'])
        assert len(dash["next_steps"]) > 0
        print(f"[OK] 8. Dashboard metrics verified. Next steps: {dash['next_steps']}")

        # 8. Verify roadmap and progress tracking
        road_res = client.get("/roadmap", headers=headers)
        assert road_res.status_code == 200
        roadmap = road_res.json()
        assert roadmap["total_items"] > 0
        print(f"[OK] 9. Roadmap generated with {roadmap['total_items']} weekly milestones.")

        first_item = roadmap["items"][0]
        # Toggle status to Learning
        upd_1 = client.put(f"/roadmap/{first_item['id']}", json={"status": "Learning"}, headers=headers)
        assert upd_1.status_code == 200
        assert upd_1.json()["learning_items"] == 1
        print("[OK] 10. Updated milestone status to 'Learning'.")

        # Toggle status to Completed
        upd_2 = client.put(f"/roadmap/{first_item['id']}", json={"status": "Completed"}, headers=headers)
        assert upd_2.status_code == 200
        assert upd_2.json()["completed_items"] == 1
        assert upd_2.json()["progress_percentage"] > 0.0
        print(f"[OK] 11. Updated milestone status to 'Completed'. Progress: {upd_2.json()['progress_percentage']}%")

        # 9. Test error cases
        # Invalid PDF extension
        bad_file = {"file": ("malicious.exe", b"fake binary", "application/octet-stream")}
        bad_res = client.post("/resumes/analyze", files=bad_file, headers=headers)
        assert bad_res.status_code == 400
        print("[OK] 12. Non-PDF upload correctly rejected with HTTP 400.")

        # Empty PDF
        empty_file = {"file": ("empty.pdf", b"", "application/pdf")}
        empty_res = client.post("/resumes/analyze", files=empty_file, headers=headers)
        assert empty_res.status_code == 400
        print("[OK] 13. Empty PDF upload correctly rejected with friendly message.")

        print("\n=== ALL E2E PIPELINE TESTS PASSED 100% SUCCESSFULLY ===")


if __name__ == "__main__":
    test_complete_e2e_pipeline()
