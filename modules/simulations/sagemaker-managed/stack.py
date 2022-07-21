#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
from typing import Any, Optional, cast

import aws_cdk.iam as iam
import cdk_nag
from aws_cdk import Aspects, Stack, Tags
from cdk_nag import NagSuppressions
from constructs import Construct, IConstruct

_logger: logging.Logger = logging.getLogger(__name__)


class SagemakerDags(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        deployment_name: str,
        module_name: str,
        mwaa_exec_role: str,
        bucket_policy_arn: Optional[str] = None,
        permission_boundary_arn: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        # ADDF Env vars
        self.deployment_name = deployment_name
        self.module_name = module_name
        self.mwaa_exec_role = mwaa_exec_role

        super().__init__(scope, id, description="This stack deploys AWS SageMaker DAGs resources for ADDF", **kwargs)
        Tags.of(scope=cast(IConstruct, self)).add(key="Deployment", value=f"addf-{deployment_name}")

        dep_mod = f"addf-{deployment_name}-{module_name}"

        # Create Dag IAM Role and policy
        policy_statements = [
            iam.PolicyStatement(
                actions=["sqs:*"],
                effect=iam.Effect.ALLOW,
                resources=[f"arn:aws:sqs:{self.region}:{self.account}:{dep_mod}*"],
            ),
            iam.PolicyStatement(
                actions=["ecr:*"],
                effect=iam.Effect.ALLOW,
                resources=[f"arn:aws:ecr:{self.region}:{self.account}:repository/{dep_mod}*"],
            ),
            iam.PolicyStatement(
                actions=[
                    "batch:UntagResource",
                    "batch:DeregisterJobDefinition",
                    "batch:TerminateJob",
                    "batch:CancelJob",
                    "batch:SubmitJob",
                    "batch:RegisterJobDefinition",
                    "batch:TagResource",
                ],
                effect=iam.Effect.ALLOW,
                resources=[
                    f"arn:aws:batch:{self.region}:{self.account}:job-queue/addf*",
                    f"arn:aws:batch:{self.region}:{self.account}:job-definition/*",
                    f"arn:aws:batch:{self.region}:{self.account}:job/*",
                ],
            ),
            iam.PolicyStatement(
                actions=[
                    "iam:PassRole",
                ],
                effect=iam.Effect.ALLOW,
                resources=[
                    f"arn:aws:iam::{self.account}:role/addf*",
                ],
            ),
            iam.PolicyStatement(
                actions=[
                    "batch:Describe*",
                    "batch:List*",
                ],
                effect=iam.Effect.ALLOW,
                resources=[
                    "*",
                ],
            ),
        ]
        dag_document = iam.PolicyDocument(statements=policy_statements)

        managed_policies = (
            [iam.ManagedPolicy.from_managed_policy_arn(self, "bucket-policy", bucket_policy_arn)]
            if bucket_policy_arn
            else []
        )

        # Role with Permission Boundary
        r_name = f"addf-{self.deployment_name}-{self.module_name}-dag-role"
        self.dag_role = iam.Role(
            self,
            f"dag-role-{self.deployment_name}-{self.module_name}",
            assumed_by=iam.ArnPrincipal(self.mwaa_exec_role),
            inline_policies={"DagPolicyDocument": dag_document},
            managed_policies=managed_policies,
            permissions_boundary=iam.ManagedPolicy.from_managed_policy_arn(
                self,
                f"perm-boundary-{self.deployment_name}-{self.module_name}",
                permission_boundary_arn,
            )
            if permission_boundary_arn
            else None,
            role_name=r_name,
            path="/",
        )

        Aspects.of(self).add(cdk_nag.AwsSolutionsChecks())

        NagSuppressions.add_stack_suppressions(
            self,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "Resource access restriced describe only",
                    "applies_to": "*",
                },
            ],
        )
