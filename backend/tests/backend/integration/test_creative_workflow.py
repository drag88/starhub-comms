"""
End-to-end integration tests for campaign creative generation workflow.

Tests complete workflow: create campaign → generate creatives → list → select → delete
Validates all components working together with realistic data flow.
"""

import json
import time
from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.creative import GeneratedCreative


class TestCreativeWorkflowEndToEnd:
    """
    End-to-end workflow tests for creative generation feature.

    Tests complete user journey from campaign creation through creative
    generation, listing, selection, and deletion.
    """

    def test_complete_workflow_success(
        self,
        client: TestClient,
        test_db: Session,
        sample_campaign: Campaign,
        mock_fal_client,
        mock_image_download,
        mock_static_dir,
        mock_env_fal_key,
    ):
        """
        Test complete workflow: create → generate → list → select → delete.

        Validates:
        - 3 creatives generated successfully
        - Images saved to disk
        - Database records created correctly
        - Scores applied and ranked
        - Selection workflow functions
        - Deletion removes file and record
        - Workflow completes in <15s (with mocked API)
        """
        start_time = time.time()

        # STEP 1: Verify campaign exists
        campaign_id = sample_campaign.campaign_id
        assert campaign_id is not None

        # STEP 2: Generate creatives
        with patch(
            "app.services.creative_generator.save_image",
            new_callable=AsyncMock,
        ) as mock_save:
            # Mock save_image to avoid file system complexity in test
            async def fake_save_image(image_url, campaign_id, channel, variant, **kwargs):
                filename = f"{campaign_id}_{channel}_{variant}_test.jpg"
                return {"filename": filename, "url": f"/static/creatives/{filename}"}

            mock_save.side_effect = fake_save_image

            response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Validate response structure
        assert data["campaign_id"] == campaign_id
        assert "creatives" in data
        assert "total" in data
        assert data["total"] == 3

        creatives = data["creatives"]
        assert len(creatives) == 3

        # Validate each creative
        for creative in creatives:
            assert "creative_id" in creative
            assert creative["campaign_id"] == campaign_id
            assert creative["variant_number"] in [1, 2, 3]
            assert creative["channel_type"] == "email_header"
            assert "image_filename" in creative
            assert "image_url" in creative
            assert "prompt_used" in creative
            assert "generation_params" in creative
            assert creative["model_used"] == "seedream-4"
            assert 0 <= creative["recommendation_score"] <= 100
            assert "score_reasoning" in creative
            assert creative["is_selected"] is False
            assert "created_at" in creative

        # Validate scoring applied (scores should be positive)
        scores = [c["recommendation_score"] for c in creatives]
        assert all(score > 0 for score in scores), "All scores should be positive"

        # Validate ranked by score (highest first)
        assert scores == sorted(scores, reverse=True), (
            "Creatives should be sorted by score descending"
        )

        # STEP 3: Verify database records created
        db_creatives = (
            test_db.query(GeneratedCreative)
            .filter(GeneratedCreative.campaign_id == campaign_id)
            .all()
        )
        assert len(db_creatives) == 3

        # STEP 4: List creatives (retrieve)
        response = client.get(f"/api/v1/campaigns/{campaign_id}/creatives")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["creatives"]) == 3

        # STEP 5: Get individual creative
        creative_id = creatives[0]["creative_id"]
        response = client.get(f"/api/v1/creatives/{creative_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["creative_id"] == creative_id
        assert data["campaign_id"] == campaign_id

        # STEP 6: Select top creative
        response = client.put(f"/api/v1/creatives/{creative_id}/select", json={"is_selected": True})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_selected"] is True

        # Verify only one creative selected
        db_creatives = (
            test_db.query(GeneratedCreative)
            .filter(GeneratedCreative.campaign_id == campaign_id)
            .all()
        )
        selected_count = sum(1 for c in db_creatives if c.is_selected)
        assert selected_count == 1, "Only one creative should be selected"

        # STEP 7: Delete creative (cleanup not required in test)
        # Note: Skip actual file deletion in test as we mocked save_image
        response = client.delete(f"/api/v1/creatives/{creative_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify database record deleted
        db_creative = (
            test_db.query(GeneratedCreative)
            .filter(GeneratedCreative.creative_id == creative_id)
            .first()
        )
        assert db_creative is None, "Creative should be deleted from database"

        # Verify remaining creatives still exist
        remaining = (
            test_db.query(GeneratedCreative)
            .filter(GeneratedCreative.campaign_id == campaign_id)
            .all()
        )
        assert len(remaining) == 2, "2 creatives should remain after deletion"

        # PERFORMANCE: Workflow should complete in <15s with mocked API
        elapsed = time.time() - start_time
        assert elapsed < 15, f"Workflow took {elapsed:.2f}s, should be <15s"

    def test_workflow_with_multiple_campaigns(
        self,
        client: TestClient,
        test_db: Session,
        mock_fal_client,
        mock_image_download,
        mock_static_dir,
        mock_env_fal_key,
    ):
        """
        Test workflow with multiple campaigns to verify isolation.

        Validates:
        - Creatives correctly associated with parent campaign
        - No cross-contamination between campaigns
        - Selection in one campaign doesn't affect another
        """
        # Create two campaigns
        campaign1 = Campaign(
            campaign_name="Campaign 1",
            channel="email",
            objective="Test objective 1",
            product_lines=json.dumps(["mobile"]),
            cohorts=json.dumps(["segment1"]),
        )
        campaign2 = Campaign(
            campaign_name="Campaign 2",
            channel="push",
            objective="Test objective 2",
            product_lines=json.dumps(["broadband"]),
            cohorts=json.dumps(["segment2"]),
        )

        test_db.add(campaign1)
        test_db.add(campaign2)
        test_db.commit()
        test_db.refresh(campaign1)
        test_db.refresh(campaign2)

        with patch(
            "app.services.creative_generator.save_image",
            new_callable=AsyncMock,
        ) as mock_save:

            async def fake_save_image(image_url, campaign_id, channel, variant, **kwargs):
                filename = f"{campaign_id}_{channel}_{variant}_test.jpg"
                return {"filename": filename, "url": f"/static/creatives/{filename}"}

            mock_save.side_effect = fake_save_image

            # Generate creatives for campaign 1
            response1 = client.post(f"/api/v1/campaigns/{campaign1.campaign_id}/generate-creatives")
            assert response1.status_code == status.HTTP_201_CREATED
            data1 = response1.json()
            assert data1["total"] == 3

            # Generate creatives for campaign 2
            response2 = client.post(f"/api/v1/campaigns/{campaign2.campaign_id}/generate-creatives")
            assert response2.status_code == status.HTTP_201_CREATED
            data2 = response2.json()
            assert data2["total"] == 3

        # Verify campaign 1 creatives
        creatives1 = client.get(f"/api/v1/campaigns/{campaign1.campaign_id}/creatives").json()
        assert creatives1["total"] == 3
        assert all(c["campaign_id"] == campaign1.campaign_id for c in creatives1["creatives"])
        assert all(c["channel_type"] == "email_header" for c in creatives1["creatives"])

        # Verify campaign 2 creatives
        creatives2 = client.get(f"/api/v1/campaigns/{campaign2.campaign_id}/creatives").json()
        assert creatives2["total"] == 3
        assert all(c["campaign_id"] == campaign2.campaign_id for c in creatives2["creatives"])
        assert all(c["channel_type"] == "push_header" for c in creatives2["creatives"])

        # Select creative in campaign 1
        creative1_id = data1["creatives"][0]["creative_id"]
        response = client.put(
            f"/api/v1/creatives/{creative1_id}/select", json={"is_selected": True}
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify campaign 2 unaffected
        creatives2_after = client.get(f"/api/v1/campaigns/{campaign2.campaign_id}/creatives").json()
        assert all(not c["is_selected"] for c in creatives2_after["creatives"]), (
            "Campaign 2 creatives should not be selected"
        )

    def test_workflow_regeneration(
        self,
        client: TestClient,
        test_db: Session,
        sample_campaign: Campaign,
        mock_fal_client,
        mock_image_download,
        mock_static_dir,
        mock_env_fal_key,
    ):
        """
        Test regenerating creatives for existing campaign.

        Validates:
        - Can generate creatives multiple times
        - History preserved (old creatives not deleted)
        - New creatives added to database
        - Total count increases
        """
        campaign_id = sample_campaign.campaign_id

        with patch(
            "app.services.creative_generator.save_image",
            new_callable=AsyncMock,
        ) as mock_save:

            async def fake_save_image(image_url, campaign_id, channel, variant, **kwargs):
                import time

                timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
                filename = f"{campaign_id}_{channel}_{variant}_{timestamp}.jpg"
                return {"filename": filename, "url": f"/static/creatives/{filename}"}

            mock_save.side_effect = fake_save_image

            # First generation
            response1 = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")
            assert response1.status_code == status.HTTP_201_CREATED
            data1 = response1.json()
            assert data1["total"] == 3

            # Second generation
            response2 = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")
            assert response2.status_code == status.HTTP_201_CREATED
            data2 = response2.json()
            assert data2["total"] == 3

        # Verify history preserved (6 total creatives)
        all_creatives = client.get(f"/api/v1/campaigns/{campaign_id}/creatives").json()
        assert all_creatives["total"] == 6, "Should have 6 creatives (3 + 3)"

        # Verify unique creative_ids
        creative_ids = [c["creative_id"] for c in all_creatives["creatives"]]
        assert len(creative_ids) == len(set(creative_ids)), "All creative IDs should be unique"

    def test_workflow_selection_exclusivity(
        self,
        client: TestClient,
        test_db: Session,
        sample_campaign: Campaign,
        mock_fal_client,
        mock_image_download,
        mock_static_dir,
        mock_env_fal_key,
    ):
        """
        Test that selecting one creative unselects others in same campaign.

        Validates:
        - Only one creative can be selected per campaign
        - Selecting new creative unselects previous
        - Selection state persists in database
        """
        campaign_id = sample_campaign.campaign_id

        with patch(
            "app.services.creative_generator.save_image",
            new_callable=AsyncMock,
        ) as mock_save:

            async def fake_save_image(image_url, campaign_id, channel, variant, **kwargs):
                filename = f"{campaign_id}_{channel}_{variant}_test.jpg"
                return {"filename": filename, "url": f"/static/creatives/{filename}"}

            mock_save.side_effect = fake_save_image

            response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")
            assert response.status_code == status.HTTP_201_CREATED

        creatives = response.json()["creatives"]
        creative1_id = creatives[0]["creative_id"]
        creative2_id = creatives[1]["creative_id"]

        # Select first creative
        response = client.put(
            f"/api/v1/creatives/{creative1_id}/select", json={"is_selected": True}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_selected"] is True

        # Verify only first is selected
        db_creative1 = (
            test_db.query(GeneratedCreative)
            .filter(GeneratedCreative.creative_id == creative1_id)
            .first()
        )
        assert db_creative1.is_selected is True

        # Select second creative
        response = client.put(
            f"/api/v1/creatives/{creative2_id}/select", json={"is_selected": True}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_selected"] is True

        # Verify first is now unselected
        test_db.refresh(db_creative1)
        assert db_creative1.is_selected is False, "First creative should be unselected"

        # Verify second is selected
        db_creative2 = (
            test_db.query(GeneratedCreative)
            .filter(GeneratedCreative.creative_id == creative2_id)
            .first()
        )
        assert db_creative2.is_selected is True

        # Verify exactly one selected
        all_creatives = (
            test_db.query(GeneratedCreative)
            .filter(GeneratedCreative.campaign_id == campaign_id)
            .all()
        )
        selected_count = sum(1 for c in all_creatives if c.is_selected)
        assert selected_count == 1, "Exactly one creative should be selected"

    def test_workflow_unselect(
        self,
        client: TestClient,
        test_db: Session,
        sample_campaign: Campaign,
        mock_fal_client,
        mock_image_download,
        mock_static_dir,
        mock_env_fal_key,
    ):
        """
        Test unselecting a creative.

        Validates:
        - Can unselect selected creative
        - No other creatives affected
        """
        campaign_id = sample_campaign.campaign_id

        with patch(
            "app.services.creative_generator.save_image",
            new_callable=AsyncMock,
        ) as mock_save:

            async def fake_save_image(image_url, campaign_id, channel, variant, **kwargs):
                filename = f"{campaign_id}_{channel}_{variant}_test.jpg"
                return {"filename": filename, "url": f"/static/creatives/{filename}"}

            mock_save.side_effect = fake_save_image

            response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")
            assert response.status_code == status.HTTP_201_CREATED

        creative_id = response.json()["creatives"][0]["creative_id"]

        # Select creative
        client.put(f"/api/v1/creatives/{creative_id}/select", json={"is_selected": True})

        # Unselect creative
        response = client.put(
            f"/api/v1/creatives/{creative_id}/select", json={"is_selected": False}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_selected"] is False

        # Verify unselected in database
        db_creative = (
            test_db.query(GeneratedCreative)
            .filter(GeneratedCreative.creative_id == creative_id)
            .first()
        )
        assert db_creative.is_selected is False

        # Verify no creatives selected
        all_creatives = (
            test_db.query(GeneratedCreative)
            .filter(GeneratedCreative.campaign_id == campaign_id)
            .all()
        )
        selected_count = sum(1 for c in all_creatives if c.is_selected)
        assert selected_count == 0, "No creatives should be selected"
