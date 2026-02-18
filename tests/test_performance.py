
import pytest
import time
import uuid
import random
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.cmr.building_eval import evaluate_building
from src.cmr.paper_eval import evaluate_paper
from src.services.web_persistence import WebPersistenceService
from src.cmr.models import Base, TemplateRecord

# Helper to generate random building inputs
def generate_random_building_inputs() -> tuple[dict, dict, dict]:
    """Generates valid random building inputs for load testing."""
    building_context = {
        "building_id": f"PERF-{uuid.uuid4()}",
        "building_name": f"Perf Test Building {random.randint(1000, 9999)}",
    }
    
    occupant_profile = {
        "occupant_age": random.randint(5, 80),
        "primary_role": "student"
    }
    
    measured_features = {
        "ceiling_height_m": random.uniform(2.4, 5.0),
        "floor_area_m2": random.uniform(10.0, 100.0),
        "has_nature_view": random.choice([True, False]),
        "view_content": random.choice(["nature", "urban", "parking_lot", "forest", "ocean"]),
        "walking_paths_available": random.choice([True, False]),
        "wayfinding_clear": random.choice([True, False]),
        "wall_colors": random.sample(["white", "blue", "green", "red", "beige", "grey"], k=random.randint(1, 3)),
        "color_sequence_varied": random.choice([True, False]),
        "floor_surface": random.choice(["wood", "carpet", "tile", "concrete"]),
        "stair_dimensions_standard": random.choice([True, False]),
        "thermal_system": random.choice(["hvac", "natural_ventilation", "mixed"]),
        "primary_material": random.choice(["wood", "stone", "concrete", "drywall"]),
        "max_group_size": random.randint(1, 20),
    }
    
    return building_context, measured_features, occupant_profile

class TestPerformance:
    """
    AG-1: TASK 12.13 — Load Testing
    """
    
    @pytest.fixture
    def db_session(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Seed a dummy template so paper eval has something to match against
        template = TemplateRecord(
            template_id="TEST_001",
            display_id="TEST1",
            name="Test Template",
            series="TEST",
            generation=1,
            dedup_status="active",
            pe_contribution="predictive",
            maturity="established",
            calibration_status="protocol",
            practical_accessibility="A",
            json_path="test.json",
            source_docs="1"
        )
        session.add(template)
        session.commit()
        
        yield session
        session.close()

    def test_single_building_eval_performance(self, db_session):
        """Standard single evaluation should be under 5 seconds."""
        ctx, feats, profile = generate_random_building_inputs()
        
        start_time = time.time()
        # Pass the shared session
        result = evaluate_building(ctx, feats, profile, session=db_session)
        duration = time.time() - start_time
        
        print(f"\nSingle Eval Duration: {duration:.4f}s")
        assert duration < 5.0, f"Single evaluation took too long: {duration:.4f}s"
        assert result['status'] == 'complete'
        assert result['overall_wis'] != 50.0  # Should not be placeholder

    def test_sequential_building_eval_load(self, db_session):
        """20 sequential evaluations should be under 60 seconds (avg < 3s)."""
        N = 20
        start_time = time.time()
        
        for _ in range(N):
            ctx, feats, profile = generate_random_building_inputs()
            result = evaluate_building(ctx, feats, profile, session=db_session)
            assert result['status'] == 'complete'
            
        total_duration = time.time() - start_time
        avg_duration = total_duration / N
        
        print(f"\nSeq Batch ({N}) Duration: {total_duration:.4f}s (Avg: {avg_duration:.4f}s)")
        assert total_duration < 60.0, f"Batch evaluation took too long: {total_duration:.4f}s"

    def test_paper_eval_performance(self, db_session):
        """Single paper evaluation (5 claims) should be under 10 seconds."""
        citation = "Performance Test 2026"
        claims = [
            {"iv": "ceiling height", "dv": "creativity", "significance": "significant", "direction": "positive"},
            {"iv": "nature view", "dv": "stress recovery", "significance": "significant", "direction": "positive"},
            {"iv": "noise level", "dv": "concentration", "significance": "significant", "direction": "negative"},
            {"iv": "daylight", "dv": "sleep quality", "significance": "significant", "direction": "positive"},
            {"iv": "wood material", "dv": "heart rate", "significance": "significant", "direction": "negative"}
        ]
        
        start_time = time.time()
        # Pass the shared session
        result = evaluate_paper(structured_claims=claims, citation=citation, session=db_session)
        duration = time.time() - start_time
        
        print(f"\nPaper Eval Duration: {duration:.4f}s")
        assert duration < 10.0, f"Paper evaluation took too long: {duration:.4f}s"
        assert result.get("status") == "complete"

    def test_web_of_belief_query_performance(self):
        """Web query for constraints should be under 2 seconds."""
        # Use existing production DB if available to test real query speed
        db_path = "data/web_persistence.db"
        if not os.path.exists(db_path):
            pytest.skip("Production web persistence DB not found for load test")
            
        service = WebPersistenceService(db_path=db_path)
        
        start_time = time.time()
        
        try:
             master_id = service.get_master_web_id()
             if not master_id:
                 pytest.skip("No master web ID found")
             
             constraints = service.get_constraints_for_web(master_id)
        except Exception as e:
            pytest.fail(f"Web query failed: {e}")
        
        duration = time.time() - start_time
        
        print(f"\nWeb Query (Constraints) Duration: {duration:.4f}s. Count: {len(constraints)}")
        assert duration < 2.0, f"Web constraint query took too long: {duration:.4f}s"
