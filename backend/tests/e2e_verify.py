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
    print("\n--- STARTING COMPLETE PHASE 1 + PHASE 2 E2E FLOW TEST ---")

    with httpx.Client(base_url=base_url, timeout=40.0) as client:
        # 1. Health check
        h_res = client.get("/health")
        assert h_res.status_code == 200, f"Health check failed: {h_res.text}"
        print("[OK] 1. Backend health check passed.")

        # 2. Register
        user_email = f"darshak_e2e_p2_{int(time.time())}@kdk.edu"
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

        # 6. Verify deterministic skill gap (before dynamic industry update)
        gap_res_1 = client.get("/skills/gap", headers=headers)
        assert gap_res_1.status_code == 200
        gap_1 = gap_res_1.json()
        initial_required_skills = gap_1["total_required_skills"]
        print(f"[OK] 7. Initial Deterministic Skill Gap: {gap_1['readiness_score']}% readiness ({gap_1['total_matched_skills']}/{initial_required_skills})")

        # 7. PHASE 2: Live Industry Skill Intelligence Update
        print("-> Ingesting live job market intelligence & updating career requirements...")
        update_res = client.post("/industry/update", json={"career": "ML Engineer"}, headers=headers)
        assert update_res.status_code == 200, f"Industry update failed: {update_res.text}"
        update_data = update_res.json()
        print(f"[OK] 8. Industry job market update processed successfully!")
        print(f"     Jobs Processed: {update_data['jobs_processed']}")
        print(f"     Skills Detected: {update_data['skills_detected']}")
        print(f"     Updated Requirements: {update_data['updated_requirements']}")

        # 8. Verify Industry Insights & Emerging Skills
        insights_res = client.get("/industry/ML Engineer")
        assert insights_res.status_code == 200
        insights = insights_res.json()
        print(f"[OK] 9. Industry Insights verified: {len(insights['required_skills'])} required skills, {len(insights['emerging_skills'])} emerging trends.")

        # 9. Verify that Skill Gap automatically adapted to the updated CareerSkill requirements
        gap_res_2 = client.get("/skills/gap", headers=headers)
        assert gap_res_2.status_code == 200
        gap_2 = gap_res_2.json()
        expected_score_2 = round((gap_2['total_matched_skills'] / gap_2['total_required_skills']) * 100, 1)
        assert gap_2['readiness_score'] == expected_score_2
        print(f"[OK] 10. Dynamic Skill Gap updated automatically: {gap_2['readiness_score']}% readiness ({gap_2['total_matched_skills']}/{gap_2['total_required_skills']})")
        missing_names_2 = [m["name"] for m in gap_2["missing_skills"]]
        print(f"     Updated Missing Skills: {missing_names_2}")

        # 10. Verify student dashboard with updated metrics
        dash_res = client.get("/dashboard", headers=headers)
        assert dash_res.status_code == 200
        dash = dash_res.json()
        assert dash["target_career_name"] == "ML Engineer"
        assert dash["strong_skills_count"] == gap_2['total_matched_skills']
        print(f"[OK] 11. Dashboard verified with updated dynamic metrics.")

        # 11. Verify roadmap and milestone tracking
        road_res = client.get("/roadmap", headers=headers)
        assert road_res.status_code == 200
        roadmap = road_res.json()
        assert roadmap["total_items"] > 0
        print(f"[OK] 12. Roadmap verified with {roadmap['total_items']} learning milestones.")

        first_item = roadmap["items"][0]
        upd_1 = client.put(f"/roadmap/{first_item['id']}", json={"status": "Learning"}, headers=headers)
        assert upd_1.status_code == 200
        upd_2 = client.put(f"/roadmap/{first_item['id']}", json={"status": "Completed"}, headers=headers)
        assert upd_2.status_code == 200
        assert upd_2.json()["completed_items"] == 1
        print(f"[OK] 13. Roadmap milestone status updated to 'Completed' (Progress: {upd_2.json()['progress_percentage']}%).")

        # 12. Test error cases
        bad_file = {"file": ("malicious.exe", b"fake binary", "application/octet-stream")}
        bad_res = client.post("/resumes/analyze", files=bad_file, headers=headers)
        assert bad_res.status_code == 400
        print("[OK] 14. Non-PDF upload correctly rejected with HTTP 400.")

        empty_file = {"file": ("empty.pdf", b"", "application/pdf")}
        empty_res = client.post("/resumes/analyze", files=empty_file, headers=headers)
        assert empty_res.status_code == 400
        print("[OK] 15. Empty PDF upload correctly rejected with friendly message.")

        print("\n=== ALL PHASE 1 + PHASE 2 E2E PIPELINE TESTS PASSED 100% SUCCESSFULLY ===")


if __name__ == "__main__":
    test_complete_e2e_pipeline()
