import { S3Client } from "@aws-sdk/client-s3";
import { BedrockRuntimeClient } from "@aws-sdk/client-bedrock-runtime";

export const s3Client = new S3Client({
  region: process.env.AWS_REGION
});

export const bedrockClient = new BedrockRuntimeClient({
  region: process.env.AWS_REGION
});
