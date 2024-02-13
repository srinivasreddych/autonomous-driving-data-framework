# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from json import JSONDecodeError

import pytest


@pytest.fixture(scope="function")
def stack_defaults():
    os.environ["ADDF_DEPLOYMENT_NAME"] = "test-project"
    os.environ["ADDF_MODULE_NAME"] = "test-deployment"

    os.environ["CDK_DEFAULT_ACCOUNT"] = "111111111111"
    os.environ["CDK_DEFAULT_REGION"] = "us-east-1"

    os.environ["ADDF_PARAMETER_VPC_ID"] = "vpc-id"
    os.environ["ADDF_PARAMETER_PRIVATE_SUBNET_IDS"] = '["subnet-12345", "subnet-54321"]'
    os.environ["ADDF_PARAMETER_FULL_ACCESS_POLICY_ARN"] = "full-access-policy-arn"
    os.environ["ADDF_PARAMETER_SOURCE_BUCKET"] = "source-bucket"
    os.environ["ADDF_PARAMETER_INTERMEDIATE_BUCKET"] = "intermediate-bucket"
    os.environ["ADDF_PARAMETER_LOGS_BUCKET_NAME"] = "logs-bucket"
    os.environ["ADDF_PARAMETER_ARTIFACTS_BUCKET_NAME"] = "artifacts-bucket"

    os.environ["ADDF_PARAMETER_ON_DEMAND_JOB_QUEUE_ARN"] = "on-demand-job-queue-arn"
    os.environ["ADDF_PARAMETER_SPOT_JOB_QUEUE_ARN"] = "spot-job-queue-arn"
    os.environ["ADDF_PARAMETER_FARGATE_JOB_QUEUE_ARN"] = "fargate-job-queue-arn"
    os.environ["ADDF_PARAMETER_PARQUET_BATCH_JOB_DEF_ARN"] = "parquet-batch-job-def-arn"
    os.environ["ADDF_PARAMETER_PNG_BATCH_JOB_DEF_ARN"] = "png-batch-job-def-arn"
    os.environ["ADDF_PARAMETER_OBJECT_DETECTION_IMAGE_URI"] = "object-detection-image-uri"
    os.environ["ADDF_PARAMETER_OBJECT_DETECTION_IAM_ROLE"] = "object-detection-iam-role"

    os.environ["ADDF_PARAMETER_LANE_DETECTION_IMAGE_URI"] = "lane-detection-image-uri"
    os.environ["ADDF_PARAMETER_LANE_DETECTION_IAM_ROLE"] = "lane-detection-iam-role"
    os.environ["ADDF_PARAMETER_IMAGE_TOPICS"] = "{}"
    os.environ["ADDF_PARAMETER_SENSOR_TOPICS"] = "{}"
    os.environ["ADDF_PARAMETER_EMR_APP_ID"] = "emrappid"
    os.environ["EMR_JOB_EXEC_ROLE"] = "emrrole"
    os.environ["ROSBAG_SCENE_METADATA_TABLE"] = "scene-metadata-table"


    # Unload the app import so that subsequent tests don't reuse
    if "app" in sys.modules:
        del sys.modules["app"]


def test_app(stack_defaults):
    import app  # noqa: F401


def test_png_batch_job_def_arn(stack_defaults):
    del os.environ["ADDF_PARAMETER_PNG_BATCH_JOB_DEF_ARN"]

    with pytest.raises(Exception) as e:
        import app  # noqa: F401

        assert "missing input parameter png-batch-job-def-arn" in str(e)


def test_parquet_batch_job_def_arn(stack_defaults):
    del os.environ["ADDF_PARAMETER_PARQUET_BATCH_JOB_DEF_ARN"]

    with pytest.raises(Exception) as e:
        import app  # noqa: F401

        assert "missing input parameter parquet-batch-job-def-arn" in str(e)


def test_object_detection_role(stack_defaults):
    del os.environ["ADDF_PARAMETER_OBJECT_DETECTION_IAM_ROLE"]

    with pytest.raises(Exception) as e:
        import app  # noqa: F401

        assert "missing input parameter object-detection-iam-role" in str(e)


def test_object_detection_image_uri(stack_defaults):
    del os.environ["ADDF_PARAMETER_LANE_DETECTION_IMAGE_URI"]

    with pytest.raises(Exception) as e:
        import app  # noqa: F401

        assert "missing input parameter lane-detection-image-uri" in str(e)


def test_lane_detection_role(stack_defaults):
    del os.environ["ADDF_PARAMETER_LANE_DETECTION_IAM_ROLE"]

    with pytest.raises(Exception) as e:
        import app  # noqa: F401

        assert "missing input parameter lane-detection-iam-role" in str(e)


def test_lane_detection_image_uri(stack_defaults):
    del os.environ["ADDF_PARAMETER_LANE_DETECTION_IMAGE_URI"]

    with pytest.raises(Exception) as e:
        import app  # noqa: F401

        assert "missing input parameter lane-detection-image-uri" in str(e)


def test_vpc_id(stack_defaults):
    del os.environ["ADDF_PARAMETER_VPC_ID"]

    with pytest.raises(Exception) as e:
        import app  # noqa: F401

        assert "missing input parameter vpc-id" in str(e)


def test_private_subnet_ids(stack_defaults):
    del os.environ["ADDF_PARAMETER_PRIVATE_SUBNET_IDS"]

    with pytest.raises(Exception) as e:
        import app  # noqa: F401

        assert "missing input parameter private-subnet-ids" in str(e)


def test_full_access_policy(stack_defaults):
    del os.environ["ADDF_PARAMETER_FULL_ACCESS_POLICY_ARN"]

    with pytest.raises(ValueError) as e:
        import app  # noqa: F401

        assert "S3 Full Access Policy ARN is missing." in str(e)


def test_no_queue_provided():
    del os.environ["ADDF_PARAMETER_ON_DEMAND_JOB_QUEUE_ARN"]
    del os.environ["ADDF_PARAMETER_SPOT_JOB_QUEUE_ARN"]
    del os.environ["ADDF_PARAMETER_FARGATE_JOB_QUEUE_ARN"]

    with pytest.raises(ValueError) as e:
        import app  # noqa: F401

        assert "Requires at least one job queue." in str(e)


def test_solution_description(stack_defaults):
    os.environ["ADDF_PARAMETER_SOLUTION_ID"] = "SO123456"
    os.environ["ADDF_PARAMETER_SOLUTION_NAME"] = "MY GREAT TEST"
    os.environ["ADDF_PARAMETER_SOLUTION_VERSION"] = "v1.0.0"

    import app

    ver = app.generate_description()
    assert ver == "(SO123456) MY GREAT TEST. Version v1.0.0"


def test_solution_description_no_version(stack_defaults):
    os.environ["ADDF_PARAMETER_SOLUTION_ID"] = "SO123456"
    os.environ["ADDF_PARAMETER_SOLUTION_NAME"] = "MY GREAT TEST"
    del os.environ["ADDF_PARAMETER_SOLUTION_VERSION"]

    import app

    ver = app.generate_description()
    assert ver == "(SO123456) MY GREAT TEST"
