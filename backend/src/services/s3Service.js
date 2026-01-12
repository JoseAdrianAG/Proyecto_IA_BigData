import { GetObjectCommand } from "@aws-sdk/client-s3";
import { s3Client } from "../config/aws.js";

export const getPdfFromS3 = async (key) => {
  const command = new GetObjectCommand({
    Bucket: process.env.S3_BUCKET,
    Key: key
  });

  const response = await s3Client.send(command);
  return response.Body;
};
