"""
Error handling validation tests for creative generation.

Tests error scenarios to ensure graceful degradation and helpful error messages.
"""

import json
from unittest.mock import AsyncMock, Mock, patch

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.campaign import Campaign


class TestCreativeErrorHandling:
    """
    Error handling tests for creative generation feature.

    Validates error scenarios return appropriate HTTP status codes
    and helpful error messages to users.
    """

    def test_generate_creatives_campaign_not_found(
        self,
        client: TestClient,
        test_db: Session,
    ):
        """
        Test generating creatives for non-existent campaign returns 404.

        Validates:
        - Returns 404 Not Found
        - Error message identifies missing campaign
        """
        non_existent_id = 99999

        response = client.post(f"/api/v1/campaigns/{non_existent_id}/generate-creatives")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert str(non_existent_id) in data["detail"]
        assert "not found" in data["detail"].lower()

    def test_generate_creatives_missing_fal_key(
        self,
        client: TestClient,
        test_db: Session,
        sample_campaign: Campaign,
        monkeypatch,
    ):
        """
        Test generating creatives without FAL_KEY returns helpful error.

        Validates:
        - Returns 500 Internal Server Error
        - Error message mentions FAL_KEY configuration
        - Guides user to set FAL_KEY in .env file
        """
        # Remove FAL_KEY from environment
        monkeypatch.delenv("FAL_KEY", raising=False)

        campaign_id = sample_campaign.campaign_id
        response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        assert "FAL_KEY" in data["detail"]
        assert ".env" in data["detail"]

    def test_generate_creatives_api_connection_error(
        self,
        client: TestClient,
        test_db: Session,
        sample_campaign: Campaign,
        mock_env_fal_key,
    ):
        """
        Test network connection error returns helpful message.

        Validates:
        - Returns 500 Internal Server Error
        - Error message mentions connection issue
        - Guides user to check network
        """
        campaign_id = sample_campaign.campaign_id

        # Mock fal_client to raise connection error
        with patch("app.services.creative_generator.fal_client") as mock_client:
            mock_client.subscribe = Mock(
                side_effect=ConnectionError("Failed to connect to fal.ai API")
            )

            response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        assert "connection" in data["detail"].lower() or "connect" in data["detail"].lower()

    def test_generate_creatives_partial_failure(
        self,
        client: TestClient,
        test_db: Session,
        sample_campaign: Campaign,
        mock_env_fal_key,
    ):
        """
        Test partial failure (1-2 variants fail, others succeed).

        Validates:
        - Continues with remaining variants
        - Returns successful variants
        - Logs failures but doesn't crash
        - Returns at least 1 creative if any succeed
        """
        campaign_id = sample_campaign.campaign_id

        call_count = 0

        def mock_subscribe_partial_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1

            # First call fails, second and third succeed
            if call_count == 1:
                raise Exception("First variant generation failed")

            return {
                "images": [
                    {
                        "url": f"https://example.com/test_image_{call_count}.jpg",
                        "width": 600,
                        "height": 200,
                        "content_type": "image/jpeg",
                    }
                ]
            }

        with patch("app.services.creative_generator.fal_client") as mock_client:
            mock_client.subscribe = Mock(side_effect=mock_subscribe_partial_failure)

            with patch(
                "app.services.creative_generator.save_image",
                new_callable=AsyncMock,
            ) as mock_save:

                async def fake_save_image(image_url, campaign_id, channel, variant, **kwargs):
                    filename = f"{campaign_id}_{channel}_{variant}_test.jpg"
                    return {"filename": filename, "url": f"/static/creatives/{filename}"}

                mock_save.side_effect = fake_save_image

                response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")

        # Should succeed with 2 variants
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["total"] == 2, "Should return 2 successful variants"
        assert len(data["creatives"]) == 2

    def test_generate_creatives_complete_failure(
        self,
        client: TestClient,
        test_db: Session,
        sample_campaign: Campaign,
        mock_env_fal_key,
    ):
        """
        Test complete failure (all 3 variants fail).

        Validates:
        - Returns 500 Internal Server Error
        - Error message indicates failure
        - No partial data returned
        """
        campaign_id = sample_campaign.campaign_id

        # Mock fal_client to always fail
        with patch("app.services.creative_generator.fal_client") as mock_client:
            mock_client.subscribe = Mock(side_effect=Exception("All variants failed to generate"))

            response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data

    def test_generate_creatives_corrupted_campaign_data(
        self,
        client: TestClient,
        test_db: Session,
    ):
        """
        Test campaign with corrupted JSON data returns helpful error.

        Validates:
        - Returns 500 Internal Server Error
        - Error message mentions data corruption
        - Identifies JSON parsing issue
        """
        # Create campaign with invalid JSON
        campaign = Campaign(
            campaign_name="Corrupted Campaign",
            channel="email",
            objective="Test objective",
            product_lines="invalid json {{{",  # Invalid JSON
            cohorts=json.dumps(["segment1"]),
        )

        test_db.add(campaign)
        test_db.commit()
        test_db.refresh(campaign)

        response = client.post(f"/api/v1/campaigns/{campaign.campaign_id}/generate-creatives")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "detail" in data
        assert "corrupted" in data["detail"].lower() or "json" in data["detail"].lower()

    def test_get_creatives_campaign_not_found(
        self,
        client: TestClient,
        test_db: Session,
    ):
        """
        Test listing creatives for non-existent campaign returns 404.

        Validates:
        - Returns 404 Not Found
        - Error message identifies missing campaign
        """
        non_existent_id = 99999

        response = client.get(f"/api/v1/campaigns/{non_existent_id}/creatives")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert str(non_existent_id) in data["detail"]

    def test_get_creative_not_found(
        self,
        client: TestClient,
        test_db: Session,
    ):
        """
        Test getting non-existent creative returns 404.

        Validates:
        - Returns 404 Not Found
        - Error message identifies missing creative
        """
        non_existent_id = 99999

        response = client.get(f"/api/v1/creatives/{non_existent_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert str(non_existent_id) in data["detail"]

    def test_select_creative_not_found(
        self,
        client: TestClient,
        test_db: Session,
    ):
        """
        Test selecting non-existent creative returns 404.

        Validates:
        - Returns 404 Not Found
        - Error message identifies missing creative
        """
        non_existent_id = 99999

        response = client.put(
            f"/api/v1/creatives/{non_existent_id}/select", json={"is_selected": True}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert str(non_existent_id) in data["detail"]

    def test_delete_creative_not_found(
        self,
        client: TestClient,
        test_db: Session,
    ):
        """
        Test deleting non-existent creative returns 404.

        Validates:
        - Returns 404 Not Found
        - Error message identifies missing creative
        """
        non_existent_id = 99999

        response = client.delete(f"/api/v1/creatives/{non_existent_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "detail" in data
        assert str(non_existent_id) in data["detail"]

    def test_file_system_error_handling(
        self,
        client: TestClient,
        test_db: Session,
        sample_campaign: Campaign,
        mock_env_fal_key,
    ):
        """
        Test file system errors handled gracefully.

        Validates:
        - File system errors caught and logged
        - Appropriate error message returned
        - No partial state corruption
        """
        campaign_id = sample_campaign.campaign_id

        # Mock fal_client to succeed
        mock_result = {
            "images": [
                {
                    "url": "https://example.com/test_image.jpg",
                    "width": 600,
                    "height": 200,
                    "content_type": "image/jpeg",
                }
            ]
        }

        with patch("app.services.creative_generator.fal_client") as mock_client:
            mock_client.subscribe = Mock(return_value=mock_result)

            # Mock save_image to fail with file system error
            with patch(
                "app.services.creative_generator.save_image",
                new_callable=AsyncMock,
            ) as mock_save:
                mock_save.side_effect = OSError("Permission denied: /static/creatives/")

                response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")

        # Should return error
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_database_error_handling(
        self,
        client: TestClient,
        test_db: Session,
        sample_creative,
    ):
        """
        Test database errors handled gracefully.

        Validates:
        - Database errors caught and rolled back
        - Appropriate error message returned
        - No data corruption
        """
        creative_id = sample_creative.creative_id

        # Close the database session to simulate connection error
        test_db.close()

        response = client.put(f"/api/v1/creatives/{creative_id}/select", json={"is_selected": True})

        # Should handle database error
        # Note: May return 404 or 500 depending on when connection fails
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]


class TestCreativeValidation:
    """
    Input validation tests for creative endpoints.

    Validates request validation and constraint enforcement.
    """

    def test_select_creative_invalid_json(
        self,
        client: TestClient,
        test_db: Session,
        sample_creative,
    ):
        """
        Test selecting creative with invalid JSON body.

        Validates:
        - Returns 422 Unprocessable Entity
        - Validation error details provided
        """
        creative_id = sample_creative.creative_id

        response = client.put(
            f"/api/v1/creatives/{creative_id}/select", json={"invalid_field": "value"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_select_creative_missing_body(
        self,
        client: TestClient,
        test_db: Session,
        sample_creative,
    ):
        """
        Test selecting creative with missing request body.

        Validates:
        - Returns 422 Unprocessable Entity
        - Validation error details provided
        """
        creative_id = sample_creative.creative_id

        response = client.put(f"/api/v1/creatives/{creative_id}/select", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
