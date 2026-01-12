import { InvokeModelCommand } from "@aws-sdk/client-bedrock-runtime";
import { bedrockClient } from "../config/aws.js";

export const invokeBedrock = async (prompt) => {
  const command = new InvokeModelCommand({
    modelId: "anthropic.claude-v2",
    contentType: "application/json",
    accept: "application/json",
    body: JSON.stringify({
      prompt,
      max_tokens_to_sample: 1000
    })
  });

  const response = await bedrockClient.send(command);
  return JSON.parse(new TextDecoder().decode(response.body));
};
