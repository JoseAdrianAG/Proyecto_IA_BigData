import {
  BedrockAgentRuntimeClient,
  InvokeAgentCommand
} from "@aws-sdk/client-bedrock-agent-runtime";

const agentClient = new BedrockAgentRuntimeClient({
  region: process.env.AWS_REGION
});

export const invokeAgent = async (inputText, sessionId) => {
  const command = new InvokeAgentCommand({
    agentId: process.env.BEDROCK_AGENT_ID,
    agentAliasId: process.env.BEDROCK_AGENT_ALIAS_ID,
    sessionId,
    inputText
  });

  const response = await agentClient.send(command);
  return response;
};