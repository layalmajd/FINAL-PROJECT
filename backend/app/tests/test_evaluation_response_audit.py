from app.utils.evaluation_response_audit import (
    RequirementAuditItem,
    append_points_breakdown_to_feedback,
    audit_consistency_errors,
    cap_score_by_audit_consistency,
    cap_score_by_explicit_evidence,
    normalized_score_to_points,
)


CLINIC_REQUIREMENTS = (
    "Explains the clinic booking problem, target users, project scope, at least 5 clear "
    "functional requirements, and 2 measurable non-functional requirements"
)
CLINIC_DATA_MODEL = (
    "Defines the main entities/tables Users, Doctors, ClinicServices, TimeSlots, and "
    "Appointments, including primary keys, foreign keys, relationships, and "
    "booking/cancellation/capacity rules"
)
CLINIC_TESTING = (
    "Provides at least 4 test cases with expected results, covering success, failure, "
    "boundary/edge, and role/security or validation behavior"
)


def test_caps_absent_explicit_items_without_zeroing() -> None:
    submission = (
        "Campus Clinic Appointment Booking System Report Student ID: 20261010. "
        "A clinic website is useful. Students can use it. The report does not explain "
        "the problem, users, scope, or clear requirements. A database may be used to "
        "store information. No real entities, keys, relationships, or booking rules are "
        "provided. The project will be tested after it is finished."
    )

    data_score, _ = cap_score_by_explicit_evidence(
        criterion_description=CLINIC_DATA_MODEL,
        submission_text=submission,
        normalized_score=100,
        grade_scale=100,
        response_language="en",
    )
    testing_score, _ = cap_score_by_explicit_evidence(
        criterion_description=CLINIC_TESTING,
        submission_text=submission,
        normalized_score=100,
        grade_scale=100,
        response_language="en",
    )

    assert data_score == 5.0
    assert testing_score == 5.0


def test_does_not_cap_complete_requirement_text_for_missing_exact_soft_phrases() -> None:
    submission = (
        "The project solves appointment crowding by replacing phone scheduling. Students, "
        "doctors, reception staff, and administrators are supported. It includes booking, "
        "cancellation, reminders, and administrative setup. Functional requirements FR1, "
        "FR2, FR3, FR4, FR5, and FR6 are described. Non-functional requirements NFR1 and "
        "NFR2 define response time and role-based access."
    )

    score, note = cap_score_by_explicit_evidence(
        criterion_description=CLINIC_REQUIREMENTS,
        submission_text=submission,
        normalized_score=100,
        grade_scale=100,
        response_language="en",
    )

    assert score == 100
    assert note is None


def test_full_score_conflicts_with_missing_audit_item() -> None:
    errors = audit_consistency_errors(
        criterion_name="Testing and Validation Plan",
        audit_items=[
            RequirementAuditItem(
                requirement="4 test cases",
                status="missing",
                evidence="The project will be tested after it is finished.",
                missing_or_weak_reason="No actual test cases or expected results are provided.",
            )
        ],
        normalized_score=100,
        grade_scale=100,
        is_manual=False,
    )

    assert errors


def test_caps_high_score_when_audit_has_no_met_items() -> None:
    score, note = cap_score_by_audit_consistency(
        criterion_name="Testing and Validation Plan",
        audit_items=[
            RequirementAuditItem(
                requirement="4 test cases",
                status="partial",
                evidence="Three test cases are listed.",
                missing_or_weak_reason="One required test case and expected results are missing.",
            )
        ],
        normalized_score=90,
        grade_scale=100,
        is_manual=False,
        response_language="en",
    )

    assert score == 55
    assert note


def test_normalized_score_converts_to_criterion_points() -> None:
    assert (
        normalized_score_to_points(
            normalized_score=50,
            criterion_weight=20,
            grade_scale=100,
        )
        == 10
    )


def test_feedback_includes_deducted_points() -> None:
    feedback = append_points_breakdown_to_feedback(
        "Missing expected results for two test cases.",
        normalized_score=75,
        criterion_weight=20,
        grade_scale=100,
        response_language="en",
        is_manual=False,
    )

    assert "Points: 15 out of 20" in feedback
    assert "Deducted: 5 out of 20" in feedback
    assert "Missing expected results" in feedback


def test_arabic_feedback_includes_deducted_points() -> None:
    feedback = append_points_breakdown_to_feedback(
        "ينقص الملف شرح العلاقات.",
        normalized_score=50,
        criterion_weight=10,
        grade_scale=100,
        response_language="ar",
        is_manual=False,
    )

    assert "النقاط: 5 من 10" in feedback
    assert "مقدار الخصم: 5 من 10" in feedback
